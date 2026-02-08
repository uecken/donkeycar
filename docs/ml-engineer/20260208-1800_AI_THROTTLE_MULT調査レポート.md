# AI_THROTTLE_MULT が効かない問題の調査レポート

**作成日**: 2026年2月8日 18:00
**担当**: ml-engineer + robotcar-engineer
**問題**: AI_THROTTLE_MULT を1以上に設定しても自動運転モード（local）で速度が上がらない

---

## 1. 問題の概要

### 1.1 症状

- `AI_THROTTLE_MULT = 2.0` や `3.0` に設定しても速度が変わらない
- `local` モード（完全自動運転）でスロットルが低いまま

### 1.2 期待される動作

```
AI_THROTTLE_MULT = 2.0 の場合:
モデル出力 0.3 × 2.0 = 0.6 → 速度上昇
```

### 1.3 実際の動作

```
モデル出力が元々非常に低い（0.1〜0.2程度）
0.15 × 2.0 = 0.3 → ESCデッドバンド付近、ほぼ動かない
```

---

## 2. 調査結果

### 2.1 AI_THROTTLE_MULT の実装

```python
# donkeycar/templates/complete.py:637-662

class DriveMode:
    def __init__(self, ai_throttle_mult=1.0):
        self.ai_throttle_mult = ai_throttle_mult

    def run(self, mode, user_steering, user_throttle,
            pilot_steering, pilot_throttle):
        if mode == 'user':
            return user_steering, user_throttle
        elif mode == 'local_angle':
            return pilot_steering, user_throttle  # ← スロットルは手動
        return (pilot_steering,
                pilot_throttle * self.ai_throttle_mult)  # ← ここで掛け算
```

**重要**: AI_THROTTLE_MULT は **モデル出力（pilot_throttle）に掛け算するだけ**

### 2.2 学習時の設定（根本原因）

database.json より、学習時の設定:

```json
{
    "JOYSTICK_MAX_THROTTLE": 0.5,    // 最大スロットル = 0.5
    "JOYSTICK_THROTTLE_DIR": -1.0    // スロットル反転（バグ）
}
```

### 2.3 問題の構造

```
【学習データの問題】
1. JOYSTICK_MAX_THROTTLE = 0.5 → 学習データの最大値が0.5
2. JOYSTICK_THROTTLE_DIR = -1.0 → スロットル値が反転

【結果】
- モデルは -0.5〜+0.5 の範囲で学習
- さらに反転しているため、意味のある値を出力しない
- モデル出力は低い値（0.1〜0.3）に収束

【AI_THROTTLE_MULT の限界】
- 元の値が小さいため、掛け算しても効果が限定的
- 0.15 × 3.0 = 0.45 → ESCデッドバンドを超えない
```

---

## 3. 検証データ

### 3.1 モデルの学習履歴

```
val_n_outputs1_loss (Throttle):
  最終値: 0.327 → RMSE ≈ 0.57

解釈: スロットル予測の平均誤差が ±0.57
      → モデルはスロットルを正しく学習できていない
```

### 3.2 スロットル出力の推定

学習データが反転していたため:
- 前進シーン → throttle = -0.3 として記録
- 停止シーン → throttle = +0.5 として記録

モデルが学習した内容:
- 「コース画像」→ 低い/負のスロットル
- 「壁/停止画像」→ 高いスロットル

---

## 4. 解決策

### 4.1 即時対応: `local_angle` モード

**設定不要、今すぐ試せる**

| モード | Steering | Throttle | 用途 |
|--------|----------|----------|------|
| `user` | 手動 | 手動 | データ収集 |
| `local_angle` | **モデル** | **手動** | ステアリングのみ自動 |
| `local` | モデル | モデル | 完全自動（今は使えない） |

```bash
# Raspberry Pi で実行
python manage.py drive --model models/mypilot.tflite --type tflite_linear

# WebUI または コントローラーで "local_angle" モードに切り替え
# L1ボタン（PlayStation）または LB（Xbox）でモード切替
```

**操作方法**:
- ステアリング: モデルが自動制御
- スロットル: 右スティックまたはトリガーで手動操作

### 4.2 即時対応: 固定スロットル

```python
# myconfig.py に追加
USE_CONSTANT_THROTTLE = True
CONSTANT_THROTTLE = 0.35  # 固定値（0.0〜1.0）
```

**注意**: ステアリングがモデル、スロットルは常に固定値

### 4.3 根本解決: データ再収集・再学習

#### Step 1: myconfig.py 確認（修正済み）

```python
# picopico_racers/mycar/myconfig.py
JOYSTICK_THROTTLE_DIR = 1.0   # ✅ 修正済み
JOYSTICK_MAX_THROTTLE = 1.0   # ✅ 修正済み（または 0.8）
```

#### Step 2: データ再収集

```bash
# Raspberry Pi で
cd ~/mycar
rm -rf data/tub_*                    # 古いデータ削除
python manage.py drive --js          # 新規データ収集
```

#### Step 3: 再学習

```bash
# WSL2/GPU環境で
cd ~/mycar
python train.py --tub data/tub_* --model models/newpilot.h5
```

#### Step 4: 推論テスト

```bash
# Raspberry Pi で
python manage.py drive --model models/newpilot.tflite --type tflite_linear
```

---

## 5. AI_THROTTLE_MULT の正しい使い方

### 5.1 前提条件

AI_THROTTLE_MULT が有効に機能するには:

1. **正しいデータで学習されたモデル**
   - JOYSTICK_THROTTLE_DIR = 1.0
   - JOYSTICK_MAX_THROTTLE = 0.5〜1.0

2. **モデルが適切なスロットル値を出力**
   - 直進時: 0.3〜0.5
   - コーナー時: 0.2〜0.3
   - 停止時: 0.0

### 5.2 推奨設定

```python
# myconfig.py

# データ収集時
JOYSTICK_MAX_THROTTLE = 0.5  # 安全な速度で収集

# 推論時（速度を上げたい場合）
AI_THROTTLE_MULT = 1.5  # 1.5倍速
# または
AI_THROTTLE_MULT = 2.0  # 2倍速
```

### 5.3 計算例（正しく学習されたモデル）

```
モデル出力: 0.4（直進時）

AI_THROTTLE_MULT = 1.0: 0.4 × 1.0 = 0.4
AI_THROTTLE_MULT = 1.5: 0.4 × 1.5 = 0.6
AI_THROTTLE_MULT = 2.0: 0.4 × 2.0 = 0.8

→ 速度が上がる
```

### 5.4 上限値

```python
# donkeycar/parts/actuator.py:369
throttle = utils.clamp(throttle, -1.0, 1.0)
```

**スロットルは -1.0〜1.0 にクランプされる**

AI_THROTTLE_MULT を大きくしすぎると、1.0 で頭打ちになる。

---

## 6. ドライブモード一覧

| モード | キー/ボタン | Steering | Throttle | 用途 |
|--------|------------|----------|----------|------|
| `user` | デフォルト | 手動 | 手動 | データ収集 |
| `local_angle` | L1/LB | モデル | 手動 | 半自動（推奨） |
| `local` | R1/RB | モデル | モデル×AI_THROTTLE_MULT | 完全自動 |

### 6.1 モード切替方法

**WebUI**: ドロップダウンから選択

**コントローラー**:
- PlayStation: L1 = local_angle, R1 = local
- Xbox: LB = local_angle, RB = local

---

## 7. トラブルシューティング

### 7.1 local_angle でステアリングが動かない

**原因**: モデルがロードされていない

**確認**:
```bash
python manage.py drive --model models/mypilot.tflite --type tflite_linear
# ログに "Loading model..." が表示されるか確認
```

### 7.2 local モードで全く動かない

**原因**: モデル出力がほぼ 0

**対処**:
1. `local_angle` モードを使用
2. または `USE_CONSTANT_THROTTLE = True`

### 7.3 AI_THROTTLE_MULT を設定しても反映されない

**確認**:
1. myconfig.py で `AI_THROTTLE_MULT = X.X` が設定されているか
2. コメントアウトされていないか
3. Donkey Car を再起動したか

---

## 8. まとめ

### 8.1 現状の問題

| 項目 | 状態 |
|------|------|
| 学習データ | 反転バグ（JOYSTICK_THROTTLE_DIR = -1.0） |
| モデル出力 | 低い値（0.1〜0.2） |
| AI_THROTTLE_MULT | 効果限定的 |

### 8.2 推奨アクション

| 優先度 | アクション | 担当 |
|--------|-----------|------|
| **即時** | `local_angle` モードで動作確認 | robotcar-engineer |
| **高** | データ再収集（正しい設定で） | data-engineer |
| **高** | モデル再学習 | ml-engineer |
| 中 | AI_THROTTLE_MULT の効果確認（再学習後） | ml-engineer |

---

## 9. 関連資料

- [20260203-1520_モデル推論データ解析レポート.md](20260203-1520_モデル推論データ解析レポート.md) - スロットル反転バグの詳細
- [20260203-1700_DonkeyCar学習推論詳細ガイド.md](20260203-1700_DonkeyCar学習推論詳細ガイド.md) - 学習・推論の仕組み
- [donkeycar/templates/complete.py](../../donkeycar/templates/complete.py) - DriveMode 実装

---

## 10. 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-02-08 18:00 | 初版作成 |
