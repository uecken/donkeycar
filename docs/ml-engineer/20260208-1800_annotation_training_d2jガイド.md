# annotation_training_d2j ガイド

**作成日**: 2026年2月8日 18:00
**担当**: ml-engineer
**目的**: Romihi氏のannotation_training_d2jツールを理解し、Donkeycarでの手動アノテーションを可能にする

---

## 1. 概要

**annotation_training_d2j**は、Romihi氏が開発した**Donkeycar/Jetracer用アノテーション・学習統合ツール**です。

| 項目 | 内容 |
|------|------|
| **GitHub** | https://github.com/Romihi/annotation_training_d2j |
| **ライセンス** | GPL v3.0 |
| **対応OS** | Windows, Ubuntu 22.04, Jetson Nano |
| **GUI** | PyQt5ベース |

### 1.1 このツールで何ができるか

```
【標準Donkeycar】
実車走行 → 自動記録（アノテーション不要）
     ↓
   学習

【annotation_training_d2j】
画像収集 → 手動アノテーション（GUI操作）
     ↓
   学習（50+モデルから選択可能）
     ↓
   Grad-CAMで可視化・検証
```

**結論**: Donkeycarでも**JetRacerスタイルの手動アノテーション**が可能になる。

---

## 2. 標準Donkeycarとの比較

| 項目 | Donkeycar（標準） | annotation_training_d2j |
|------|-------------------|-------------------------|
| **アノテーション方式** | 自動記録（実車走行時） | 手動（事後処理） |
| **ツール形式** | スクリプト | PyQt5 GUI |
| **モデル選択** | 固定（linear等） | 50+モデル |
| **物体検知** | オプション | YOLO統合 |
| **可視化** | 限定的 | **Grad-CAM対応** |
| **クラウド統合** | 限定的 | Google Colab対応 |

---

## 3. アノテーション機能

### 3.1 運転制御アノテーション（クリックベース）

画像上をクリックするだけで、位置から自動計算:

```
画像
┌─────────────────────────────┐
│         ↑ throttle = 1.0    │
│                             │
│ ← angle = -1.0    → angle = +1.0
│                             │
│         ↓ throttle = -1.0   │
└─────────────────────────────┘
         クリック点 → (angle, throttle) を自動計算
```

| 出力値 | 計算方法 | 範囲 |
|--------|---------|------|
| angle | X座標から計算 | -1.0 〜 +1.0 |
| throttle | Y座標から計算 | -1.0 〜 +1.0 |
| location | 手動で0-7を選択 | 0 〜 7 |

### 3.2 将来予測アノテーション

| 出力パターン | 内容 |
|-------------|------|
| 2出力（標準） | angle, throttle |
| 3出力 | + speed |
| 6出力 | + t+5フレーム先予測 |
| 9出力 | + speed + t+5 + t+10予測 |

### 3.3 物体検知アノテーション

- バウンディングボックス描画
- セグメンテーションマスク
- YOLOv8/v11形式でエクスポート

---

## 4. 出力形式

### 4.1 Donkey形式（Donkeycarと完全互換）

```
data/
├── catalog.json
└── images/
    ├── 0_cam_image_array_.jpg
    ├── 1_cam_image_array_.jpg
    └── ...
```

**catalog.json**:
```json
{
  "_index": 0,
  "_timestamp_ms": 1707393600000,
  "user/angle": 0.25,
  "user/throttle": 0.5,
  "user/loc": 2,
  "cam/image_array_": "images/0_cam_image_array_.jpg"
}
```

### 4.2 Jetracer形式

ファイル名に値を埋め込む形式:
```
{index}_{location}_{angle}_{throttle}_image.jpg
例: 15_180_080_045_image.jpg
```

---

## 5. モデル学習機能

### 5.1 利用可能なモデル（50+）

| カテゴリ | モデル例 |
|---------|---------|
| Donkeycar標準 | linear, categorical |
| 軽量CNN | MobileNetV2, MobileNetV3, EfficientNet |
| 高精度CNN | ResNet18/50, DenseNet |
| Transformer | Vision Transformer (ViT), MobileViT |
| Edge向け | EdgeNeXt (推奨) |

### 5.2 推奨モデル

| 用途 | 推奨モデル | 理由 |
|------|-----------|------|
| **精度重視** | edgenext_small | 高精度かつ軽量 |
| **速度重視** | mobilenetv3_small | 高速推論 |
| **バランス** | mobilevit_s | 精度と速度のバランス |

### 5.3 学習機能

- Early Stopping（過学習防止）
- データ拡張（回転、ノイズ、明るさ調整）
- クラウド学習（Google Colab対応）

---

## 6. Grad-CAM 可視化

**独自機能**: モデルが画像のどこに注目しているかをヒートマップで表示。

### 6.1 CAM手法

| 手法 | 特徴 | 速度 |
|------|------|------|
| GradCAM | 標準 | 高速 |
| GradCAM++ | 複数領域対応 | 高速 |
| EigenCAM | 勾配不使用 | 高速 |
| ScoreCAM | 最高精度 | 低速 |

### 6.2 色分け表示（bothモード）

```
赤色: 正の寄与（右に切る/加速）
青色: 負の寄与（左に切る/減速）
紫色: 両方の寄与が重なる
```

---

## 7. 自動アノテーション機能

手動アノテーションの工数を大幅削減:

```
【従来】
1000枚の手動アノテーション → 5-10時間

【自動アノテーション活用】
1. 初期10-50枚を手動アノテーション
2. 高精度モデルで学習
3. 残りを自動アノテーション
4. 信頼度低い箇所のみ手動修正
→ 1-2時間に削減
```

---

## 8. ワークフロー

### 8.1 新規データセット作成

```
【ステップ1】 画像収集
   実車で走行 → 画像フォルダ作成

【ステップ2】 アノテーション（GUI）
   annotation_training_d2j起動
   → 画像クリックで(angle, throttle)を付与

【ステップ3】 学習
   50+モデルから選択して学習

【ステップ4】 検証
   Grad-CAMで注目領域を確認

【ステップ5】 エクスポート
   Donkey形式で出力 → Donkeycarで使用
```

### 8.2 既存Donkeycarデータの精密化

```
【ステップ1】 既存Tubデータを読み込み

【ステップ2】 手動修正
   - 理想ラインと異なる箇所を修正
   - ノイズの多いデータをクリーニング

【ステップ3】 再学習
   修正後のデータで精度向上
```

---

## 9. インストール

### 9.1 Windows

```bash
# リポジトリ取得
git clone https://github.com/Romihi/annotation_training_d2j.git
cd annotation_training_d2j

# 仮想環境作成
python -m venv venv
venv\Scripts\activate

# 依存パッケージ（GPU版）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt

# 起動
python main.py
```

### 9.2 Ubuntu 22.04

```bash
# システムパッケージ
sudo apt install python3-pip python3-venv python3-pyqt5

# 以降はWindowsと同様
```

---

## 10. Donkeycarとの連携

### 10.1 互換性

| 項目 | 対応 |
|------|------|
| カタログ形式 | ✅ 完全互換 |
| 画像形式 | ✅ JPEG/PNG |
| Tubデータ構造 | ✅ 標準形式 |

### 10.2 ワークフロー例

```
Donkeycar（実車走行でデータ収集）
              ↓
annotation_training_d2j（手動修正・精密化）
              ↓
      再学習（精度向上）
              ↓
     Donkeycarで推論
```

---

## 11. 現プロジェクトでの活用

### 11.1 推奨シーン

| シーン | 推奨度 | 理由 |
|--------|--------|------|
| 精密なライン取り | ★★★★★ | 理想ラインを正確に定義可能 |
| 学習品質の検証 | ★★★★★ | Grad-CAMで可視化 |
| 既存データの修正 | ★★★★☆ | 問題のあるデータを特定・修正 |
| 大規模データ作成 | ★★★★☆ | 自動アノテーションで効率化 |

### 11.2 現状の判断

```
【現状】
- 水曜日までに結果が必要
- 標準Donkeycar方式で3周32秒達成

【判断】
- 今回は標準Donkeycar方式を継続（工数優先）
- 将来的にライン最適化が必要な場合に導入検討
```

---

## 12. まとめ

| 項目 | 内容 |
|------|------|
| **ツール** | annotation_training_d2j |
| **機能** | 手動アノテーション + 学習 + Grad-CAM可視化 |
| **Donkeycar互換** | ✅ 完全互換 |
| **メリット** | 精密なアノテーション、学習品質の可視化 |
| **デメリット** | 手動作業の工数（自動アノテーションで軽減可） |

### 結論

**Donkeycarでも手動アノテーションは可能**。annotation_training_d2jを使えば:

1. JetRacerスタイルのクリックベースアノテーション
2. 50+のモデルから選択して学習
3. Grad-CAMで学習品質を可視化
4. Donkey形式でエクスポート → Donkeycarで直接使用

---

## 13. 関連資料

- [20260208-1745_JetRacer_vs_Donkeycar比較.md](20260208-1745_JetRacer_vs_Donkeycar比較.md) - 学習方式の比較
- [20260203-1700_DonkeyCar学習推論詳細ガイド.md](20260203-1700_DonkeyCar学習推論詳細ガイド.md) - 標準学習の詳細
- [annotation_training_d2jガイド](../ml-engineer/annotation_training_d2j_guide.md) - 詳細ガイド（既存）
- [GitHub: Romihi/annotation_training_d2j](https://github.com/Romihi/annotation_training_d2j) - 公式リポジトリ

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-02-08 18:00 | 初版作成 |
