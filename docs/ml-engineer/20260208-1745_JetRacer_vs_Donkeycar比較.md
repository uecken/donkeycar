# JetRacer vs Donkeycar 学習方式比較

**作成日**: 2026年2月8日 17:45
**担当**: ml-engineer
**目的**: JetRacer方式とDonkeycar方式の違いを理解し、適切な手法を選択する

---

## 1. 概要比較

| 項目 | Donkeycar | JetRacer |
|------|-----------|----------|
| **開発元** | DIYRobocars コミュニティ | NVIDIA |
| **主要ハードウェア** | Raspberry Pi 4 | Jetson Nano |
| **学習方式** | End-to-End 模倣学習 | 分類/回帰 + ルールベース |
| **アノテーション** | 不要（自動記録） | 必要（手動ラベリング） |
| **推論速度** | 12-25Hz (Pi4) | 30-60Hz (Jetson) |
| **GPU活用** | なし（CPU推論） | あり（CUDA/TensorRT） |

---

## 2. 学習方式の違い

### 2.1 Donkeycar: End-to-End 模倣学習

```
【データ収集】
カメラ画像 + 人間の操作（Steering, Throttle）
     ↓ 自動記録（アノテーション不要）
【学習】
入力: 画像 → 出力: Steering, Throttle（連続値）
     ↓
【推論】
画像 → モデル → Steering, Throttle を直接出力
```

**特徴**:
- 人間が運転するだけでデータ収集完了
- 画像から操作量を直接予測
- 中間表現（レーン検出等）なし
- シンプルだが、学習データの質に依存

### 2.2 JetRacer: 分類/回帰 + ルールベース

```
【データ収集】
カメラ画像を撮影
     ↓ 手動アノテーション（ラベリング）
【学習】
入力: 画像 → 出力: クラス（左/中央/右）または座標
     ↓
【推論】
画像 → モデル → クラス/座標 → ルールベースで Steering 計算
```

**特徴**:
- 手動でアノテーション（ラベル付け）が必要
- モデルは「どこを見るべきか」を学習
- 出力をルールで操作量に変換
- 解釈可能だが、アノテーション工数が発生

---

## 3. アノテーションの違い

### 3.1 Donkeycar: 自動アノテーション

```python
# Tubデータ構造（自動記録）
{
    "cam/image_array": "<画像>",
    "user/angle": 0.35,      # ← 人間が操作した値が自動記録
    "user/throttle": 0.5,    # ← 人間が操作した値が自動記録
    "_timestamp_ms": 1234567890
}
```

| 項目 | 内容 |
|------|------|
| **アノテーション方法** | 自動（運転中に記録） |
| **工数** | なし |
| **ラベル種類** | Steering, Throttle（連続値） |
| **精度** | 人間の運転精度に依存 |

### 3.2 JetRacer: 手動アノテーション

```
【Road Following（レーン追従）】
1. 画像を撮影
2. 「目標点」を画像上でクリック（x, y座標をラベル付け）
3. モデルは座標を回帰で学習

【Classification（分類）】
1. 画像を撮影
2. クラスを割り当て（"left", "center", "right", "stop"等）
3. モデルはクラスを分類で学習
```

| 項目 | 内容 |
|------|------|
| **アノテーション方法** | 手動（画像ごとにラベル付け） |
| **工数** | 高い（1枚ずつ作業） |
| **ラベル種類** | 座標 or クラス |
| **精度** | アノテーションの質に依存 |

---

## 4. JetRacer の代表的手法

### 4.1 Road Following（座標回帰）

```python
# JetRacer Road Following
# 画像から「目標点(x, y)」を予測

model = torchvision.models.resnet18(pretrained=True)
model.fc = torch.nn.Linear(512, 2)  # 出力: x, y座標

# 推論時
x, y = model(image)
steering = (x - 0.5) * 2  # 座標 → Steering に変換
```

**アノテーション作業**:
1. Jupyter Notebook で画像を表示
2. 「車が向かうべき点」をクリック
3. (x, y) 座標がラベルとして保存

### 4.2 Classification（クラス分類）

```python
# JetRacer Classification
# 画像から「行動クラス」を予測

classes = ["free", "blocked", "left", "right"]
model = torchvision.models.alexnet(pretrained=True)
model.classifier[6] = torch.nn.Linear(4096, len(classes))

# 推論時
class_id = model(image).argmax()
if class_id == 0:  # free
    throttle = 0.5
elif class_id == 1:  # blocked
    throttle = 0.0
# ...
```

**アノテーション作業**:
1. 画像を撮影
2. フォルダに分類（`free/`, `blocked/`, `left/`, `right/`）
3. フォルダ名がラベルになる

---

## 5. メリット・デメリット比較

### 5.1 Donkeycar（模倣学習）

| メリット | デメリット |
|---------|-----------|
| アノテーション不要 | 学習データの質に依存 |
| 運転するだけでデータ収集 | ショートカット等の新規行動が難しい |
| シンプルな実装 | モデルの判断根拠が不明確 |
| 連続値出力で滑らか | 過学習しやすい |

### 5.2 JetRacer（分類/回帰）

| メリット | デメリット |
|---------|-----------|
| 判断根拠が明確 | アノテーション工数が高い |
| ルールベースで調整可能 | データ収集に時間がかかる |
| 物体検出との組み合わせ容易 | ルール設計が必要 |
| 転移学習が効きやすい | 連続値出力に追加処理が必要 |

---

## 6. 現プロジェクトでの選択

### 6.1 現状: Donkeycar方式を採用

| 理由 | 詳細 |
|------|------|
| **工数** | アノテーション不要で即座にデータ収集可能 |
| **期限** | 水曜日までに結果を出す必要あり |
| **コース** | 単純なコースでは模倣学習で十分 |
| **ハードウェア** | Raspberry Pi 4 で動作可能 |

### 6.2 JetRacer方式が有効なケース

- 物体回避が必要な場合（障害物検出 + ルール）
- 複雑な判断が必要な場合（信号、標識）
- Jetson Nano を使用する場合（GPU活用）
- 解釈可能性が重要な場合

---

## 7. アノテーションツール

### 7.1 Donkeycar: Tubデータ管理

```bash
# データ確認
donkey tubplot --tub data/tub_xxx

# データクリーニング
donkey tubclean data/tub_xxx
```

**自動記録される情報**:
- `cam/image_array`: カメラ画像
- `user/angle`: ステアリング値
- `user/throttle`: スロットル値
- `_timestamp_ms`: タイムスタンプ

### 7.2 JetRacer: 手動アノテーション

**Jupyter Notebook ベース**:
```python
# JetRacer data collection notebook
from IPython.display import display
import ipywidgets

# 画像表示 + クリックでアノテーション
def on_click(x, y):
    save_annotation(image, x, y)

widget = ipywidgets.Image(value=image_bytes)
widget.on_click(on_click)
display(widget)
```

### 7.3 汎用アノテーションツール

| ツール | 用途 | 特徴 |
|--------|------|------|
| LabelImg | 物体検出 | バウンディングボックス |
| CVAT | 多目的 | Web ベース、チーム作業可能 |
| Labelme | セグメンテーション | ポリゴン描画 |
| VGG Image Annotator | 軽量 | ブラウザで動作 |

---

## 8. ハイブリッド方式の可能性

### 8.1 Donkeycar + 物体検出

```
カメラ画像
    ↓
[物体検出] → 障害物座標
    ↓
[模倣学習モデル] → Steering, Throttle
    ↓
[安全ルール] → 障害物があれば停止
    ↓
最終出力
```

### 8.2 実装例

```python
# Donkeycar に物体検出を追加
class ObstacleAvoidance:
    def __init__(self):
        self.detector = load_yolo_model()

    def run(self, image, pilot_angle, pilot_throttle):
        obstacles = self.detector(image)

        if any_obstacle_close(obstacles):
            return pilot_angle, 0.0  # 停止

        return pilot_angle, pilot_throttle
```

---

## 9. まとめ

| 項目 | Donkeycar | JetRacer |
|------|-----------|----------|
| **学習方式** | End-to-End 模倣学習 | 分類/回帰 + ルール |
| **アノテーション** | 不要（自動） | 必要（手動） |
| **工数** | 低い | 高い |
| **解釈可能性** | 低い | 高い |
| **柔軟性** | 低い | 高い |
| **推奨ケース** | 単純コース、短期間 | 複雑な判断、物体検出 |

### 現プロジェクトの結論

```
【採用】Donkeycar 方式（模倣学習 linear）
【理由】
- アノテーション工数ゼロ
- 期限（水曜日）に間に合う
- 現コースは単純で模倣学習で十分
- ショートカットもデータ収集で対応可能
```

---

## 10. Donkeycarでの手動アノテーション

### 10.1 annotation_training_d2j

Donkeycarでも**JetRacerスタイルの手動アノテーション**が可能。

| 項目 | 内容 |
|------|------|
| **ツール** | [annotation_training_d2j](https://github.com/Romihi/annotation_training_d2j) |
| **開発者** | Romihi氏 |
| **機能** | クリックベースアノテーション + 学習 + Grad-CAM |

```
【annotation_training_d2jの流れ】
画像収集 → GUIで手動アノテーション → 学習 → Donkey形式でエクスポート
                    ↓
         Donkeycarで直接使用可能
```

### 10.2 標準Donkeycarとの使い分け

| シナリオ | 推奨方式 |
|---------|---------|
| 素早くデータ収集 | Donkeycar標準（自動記録） |
| 精密なライン取り | annotation_training_d2j（手動） |
| 既存データの修正 | annotation_training_d2j |
| 学習品質の検証 | annotation_training_d2j（Grad-CAM） |

詳細は [20260208-1800_annotation_training_d2jガイド.md](20260208-1800_annotation_training_d2jガイド.md) を参照。

---

## 11. 関連資料

- [20260203-1700_DonkeyCar学習推論詳細ガイド.md](20260203-1700_DonkeyCar学習推論詳細ガイド.md) - Donkeycar 学習の詳細
- [20260208-1730_プロジェクト現状まとめ.md](20260208-1730_プロジェクト現状まとめ.md) - 現状と優先課題
- [20260208-1800_annotation_training_d2jガイド.md](20260208-1800_annotation_training_d2jガイド.md) - 手動アノテーションツール
- [NVIDIA JetRacer](https://github.com/NVIDIA-AI-IOT/jetracer) - JetRacer 公式リポジトリ
- [JetBot Road Following](https://github.com/NVIDIA-AI-IOT/jetbot/tree/master/notebooks/road_following) - JetBot アノテーション例
- [Romihi/annotation_training_d2j](https://github.com/Romihi/annotation_training_d2j) - Donkeycar用手動アノテーションツール
