# annotation_training_d2j 詳細ガイド

**作成日**: 2026年1月19日
**リポジトリ**: https://github.com/Romihi/annotation_training_d2j
**ライセンス**: GNU General Public License v3.0
**ローカルパス**: `refs/annotation_training_d2j/`

---

## 1. 概要

**annotation_training_d2j** は、Romihi氏によって開発されたAIミニカー向けの高機能アノテーション・学習統合ツールです。Donkey CarやJetRacerなどの自律走行プラットフォーム向けに、画像データセットのアノテーション作成と機械学習モデルの学習を統合管理するGUIアプリケーションです。

### 主な特徴

| 特徴 | 説明 |
|------|------|
| **GUIベースアノテーション** | PyQt5による直感的な操作 |
| **40+モデル対応** | MobileViT, ResNet, Swin Transformer等 |
| **将来予測学習** | 5/10フレーム先の予測学習 |
| **オートアノテーション** | 学習済みモデルによる自動アノテーション |
| **GradCAM可視化** | モデル判断根拠の可視化 |
| **クラウド連携** | Google Colab / Databricks統合 |

### 対応環境

| 環境 | OS | Python |
|------|-----|--------|
| PC | Windows 11 | 3.11 |
| PC | Ubuntu 22.04 | 3.10 |
| Jetson | JetPack 6.2 | 3.10 |

---

## 2. ディレクトリ構造

```
annotation_training_d2j/
├── main.py                          # メインアプリケーション（22,881行）
├── config.py                        # アプリケーション設定
├── config_colab.py                  # Google Colab連携設定
├── config_databricks.py             # Databricks連携設定
├── requirements.txt                 # Python依存パッケージ
├── data_analysis.py                 # データ分析ダイアログ
├── model_catalog.py                 # モデル定義・カタログ
├── model_info.py                    # モデルメタデータ
├── model_training.py                # モデルトレーニング
├── styles.py                        # UIスタイル定義
├── theme.py                         # テーマ管理
│
├── managers/                        # 管理クラス
│   ├── annotation_data_manager.py   # アノテーションデータ管理
│   ├── datasetmanager.py            # データセット管理
│   └── mlflow_manager.py            # MLflow統合
│
├── utils/                           # ユーティリティ
│   ├── color_utils.py               # 色管理
│   ├── databricks_transfer.py       # Databricks転送
│   ├── export_utils.py              # Donkey/Jetracer/YOLO形式エクスポート
│   ├── file_utils.py                # ファイル操作
│   ├── geometry_utils.py            # 幾何学計算
│   ├── gradcam_utils.py             # GradCAM可視化
│   ├── image_utils.py               # 画像処理
│   ├── inference_utils.py           # 推論実行
│   ├── colab_transfer.py            # Google Colab転送
│   └── yolo_utils.py                # YOLO統合
│
├── tools/                           # 高度なツール
│   ├── train.py                     # 訓練スクリプト
│   ├── evaluate.py                  # 評価スクリプト
│   ├── multi_image_models.py        # マルチ画像入力モデル
│   ├── pytorch_to_openvino.py       # OpenVINO変換
│   ├── torch2trt_converter.py       # TensorRT変換
│   └── openvino_onnx_benchmark.py   # ベンチマーク
│
├── colab/                           # Google Colab用スクリプト
├── databricks/                      # Databricks用スクリプト
└── setup/                           # セットアップ関連
    └── rtx5060/                     # RTX 5060用CUDA設定
```

---

## 3. 対応モデル一覧

### 軽量モデル（エッジデバイス向け）

| モデル | パラメータ | 用途 |
|--------|-----------|------|
| MobileViT-xxs | 1.3M | Raspberry Pi / Jetson Nano |
| MobileViT-xs | 2.3M | Jetson Nano |
| MobileViT-s | 5.6M | Jetson Orin |
| MobileNetV3-small | 2.5M | 超軽量推論 |
| MobileNetV4-small | - | 最新軽量モデル |
| EfficientNet-lite0 | 4.7M | バランス型 |

### 中規模モデル（GPU推奨）

| モデル | パラメータ | 特徴 |
|--------|-----------|------|
| ResNet-18 | 11.7M | 安定・高速 |
| ResNet-34 | 21.8M | 高精度 |
| EfficientNet-b0 | 5.3M | 効率的 |
| ConvNeXt-nano | 15.6M | 最新CNN |
| ConvNeXt-tiny | 28.6M | 高精度CNN |
| EdgeNeXt-small | 5.6M | エッジ最適化 |

### 高精度モデル（ハイエンドGPU向け）

| モデル | パラメータ | 特徴 |
|--------|-----------|------|
| Swin-tiny | 28.3M | Transformer |
| Swin-small | 49.6M | 高精度Transformer |
| ConvNeXt-small | 50.2M | 大規模CNN |

---

## 4. Donkey Car統合・改良点

### 標準Donkey Carとの比較

| 機能 | Donkey Car標準 | annotation_training_d2j |
|------|---------------|------------------------|
| **アノテーション** | 走行データ収集のみ | GUIで手動/自動アノテーション |
| **モデル** | 7層CNN固定 | 40+モデル選択可能 |
| **出力** | angle, throttle | + speed, 将来予測(t+5, t+10) |
| **可視化** | なし | GradCAM判断根拠表示 |
| **実験管理** | なし | MLflow統合 |
| **クラウド学習** | 手動設定 | Colab/Databricks自動連携 |

### 出力形式の拡張

```python
# 標準（2出力）
[angle, throttle]

# 速度含む（3出力）
[angle, throttle, speed]

# 将来予測（6出力）
[angle, throttle, t+5_angle, t+5_throttle, t+10_angle, t+10_throttle]

# フル出力（9出力）
[angle, throttle, speed, t+5_angle, t+5_throttle, t+5_speed,
 t+10_angle, t+10_throttle, t+10_speed]
```

### 将来予測の利点

```
通常モデル:
  現在の画像 → 現在の操作

将来予測モデル:
  現在の画像 → 現在の操作 + 5フレーム後の操作 + 10フレーム後の操作

効果: コーナー進入前の先行操舵が可能
```

---

## 5. 主要機能詳細

### 5.1 アノテーション機能

#### 自動運転アノテーション（ステアリング・スロットル）
```
画像上をクリック
  ↓
X座標 → ステアリング角度 [-1.0, 1.0]
Y座標 → スロットル値 [-1.0, 1.0]
```

#### 物体検知アノテーション（バウンディングボックス）
- マウスドラッグでBbox描画
- マルチクラス対応
- リアルタイム編集（移動・リサイズ）

#### セグメンテーションアノテーション
- ポリゴン点の逐次入力
- 多角形描画サポート

#### 位置情報タグ（0-7）
- コース上の特定位置を識別
- 位置ごとの統計表示

### 5.2 オートアノテーション

**ワークフロー**:
```
1. 初期手動アノテーション（10-50枚）
      ↓
2. 高精度モデル学習（ResNet18, EdgeNeXt等）
      ↓
3. 自動予測 + 信頼度フィルタリング
      ↓
4. 差分ベクトル表示で修正点特定
      ↓
5. 反復改善
```

**効果**: 1000枚アノテーション 5-10時間 → 1-2時間

### 5.3 GradCAM可視化

| 手法 | 特徴 | 用途 |
|------|------|------|
| GradCAM | 標準手法 | 一般的な可視化 |
| GradCAM++ | 改良版 | 複数オブジェクト |
| EigenCAM | 高速 | リアルタイム |
| LayerCAM | 詳細 | 詳細分析 |
| ScoreCAM | 勾配不使用 | 安定した結果 |

**ViT系モデル対応**: MobileViT、Swin Transformer完全対応

### 5.4 データ分析機能

- **統計情報**: 平均、標準偏差、中央値、最小/最大
- **分布グラフ**: angle/throttle/speedのヒストグラム
- **時系列グラフ**: 生データ、移動平均、区間平均
- **センサーデータ**: IMU等のカスタムセンサー値表示
- **インタラクティブ**: グラフクリックで該当画像にジャンプ

---

## 6. キーボードショートカット

| キー | 機能 |
|------|------|
| `B` | モード切替（自動運転/物体検知） |
| `←` / `→` | 画像移動 |
| `Delete` | アノテーション削除 |
| `Space` | 自動再生 |
| `0-7` | 位置情報設定 |
| `Ctrl+S` | 保存 |

---

## 7. クラウド連携

### Google Colab連携

```python
# config_colab.py設定後

1. データをGoogle Driveに転送
2. Colabで学習ノートブック自動生成
3. 学習実行
4. モデルをダウンロード
```

### Databricks連携

```python
# config_databricks.py設定後

1. MLflowで実験追跡
2. Databricksクラスタで分散学習
3. モデルバージョン管理
```

---

## 8. エクスポート形式

### Donkey Car形式
```
data_donkey/
├── images/
│   ├── 0001_cam-image_array_.jpg
│   ├── 0002_cam-image_array_.jpg
│   └── ...
├── catalog.json          # JSON Lines形式
└── myconfig.py           # 設定ファイル
```

### JetRacer形式
```
data_jetracer/
├── images/
└── annotations.json
```

### YOLO形式
```
data_yolo/
├── images/
│   ├── train/
│   └── val/
├── labels/
│   ├── train/
│   └── val/
└── data.yaml
```

---

## 9. インストール手順

### Windows (Python 3.11)

```bash
# 1. リポジトリクローン
git clone https://github.com/Romihi/annotation_training_d2j.git
cd annotation_training_d2j

# 2. 仮想環境作成
python -m venv venv
venv\Scripts\activate

# 3. 依存パッケージインストール
pip install -r requirements.txt

# 4. 起動
python main.py
```

### Ubuntu 22.04 (Python 3.10)

```bash
# 1. システムパッケージ
sudo apt install python3-pyqt5 python3-opencv

# 2. リポジトリクローン
git clone https://github.com/Romihi/annotation_training_d2j.git
cd annotation_training_d2j

# 3. 仮想環境作成
python3 -m venv venv --system-site-packages
source venv/bin/activate

# 4. 依存パッケージインストール
pip install -r requirements.txt

# 5. 起動
python main.py
```

### Jetson (JetPack 6.2)

```bash
# 1. システムパッケージ（apt経由）
sudo apt install python3-pyqt5 python3-numpy python3-opencv python3-matplotlib

# 2. リポジトリクローン
git clone https://github.com/Romihi/annotation_training_d2j.git
cd annotation_training_d2j

# 3. 仮想環境作成
python3 -m venv venv --system-site-packages
source venv/bin/activate

# 4. PyTorch（JetPack付属版使用）
# pip install torch は不要（システムパッケージ使用）

# 5. その他依存パッケージ
pip install timm ultralytics mlflow grad-cam

# 6. 起動
python main.py
```

---

## 10. 依存パッケージ

```
# GUI
PyQt5>=5.15.0

# 機械学習
torch>=1.9.0
torchvision>=0.10.0
timm>=1.0.14              # PyTorch Image Models
ultralytics>=8.0.0        # YOLO

# 画像処理
opencv-python>=4.5.0
Pillow>=8.2.0

# 可視化
matplotlib>=3.3.0
grad-cam>=1.4.0

# 実験管理
mlflow>=1.20.0

# クラウド連携
databricks-sdk>=0.20.0
pydrive2>=1.19.0
google-auth>=2.0.0

# ユーティリティ
numpy>=1.19.0
scikit-learn>=0.24.0
tqdm>=4.62.0
PyYAML>=6.0
```

---

## 11. モデル変換・最適化

### OpenVINO変換（Intel CPU最適化）

```bash
python tools/pytorch_to_openvino.py \
    --model models/my_model.pth \
    --output models/my_model_openvino
```

### TensorRT変換（NVIDIA GPU最適化）

```bash
python tools/torch2trt_converter.py \
    --model models/my_model.pth \
    --output models/my_model.trt
```

### ベンチマーク

```bash
python tools/openvino_onnx_benchmark.py \
    --model models/my_model_openvino \
    --iterations 100
```

---

## 12. Level 4自動運転への活用

### 活用ポイント

| 機能 | Level 4への貢献 |
|------|----------------|
| **将来予測学習** | 先読み制御による安全性向上 |
| **GradCAM可視化** | モデル判断の透明性確保 |
| **マルチモデル対応** | 最適モデル選択による精度向上 |
| **オートアノテーション** | 大規模データセット効率的構築 |
| **MLflow統合** | 実験再現性・モデル管理 |

### 推奨ワークフロー

```
1. 走行データ収集（Donkey Car標準）
      ↓
2. annotation_training_d2jでアノテーション
   - オートアノテーション活用
   - GradCAMで品質確認
      ↓
3. 将来予測モデル学習（6出力 or 9出力）
   - EdgeNeXt-small推奨（精度・速度バランス）
      ↓
4. OpenVINO/TensorRT変換
      ↓
5. Raspberry Pi / Jetsonでデプロイ
      ↓
6. 実車テスト・データ追加収集
      ↓
7. 反復改善
```

---

## 13. 技術的特徴

### 正規化方式

```python
# 採用方式（Donkey Car形式）
transforms.ToTensor()  # [0,255] → [0,1]

# 非採用（ImageNet正規化）
# transforms.Normalize(mean=[0.485, 0.456, 0.406],
#                     std=[0.229, 0.224, 0.225])
```

→ 独自データセットに最適化された正規化で高精度実現

### マルチプロセッシング対策

```python
torch.multiprocessing.set_start_method('spawn')  # 安全なマルチプロセッシング
torch.set_num_threads(2)                         # スレッド数制限
torch.cuda.empty_cache()                         # メモリ効率化
```

---

## 14. ライセンス注意事項

| コンポーネント | ライセンス | 商用利用 |
|--------------|-----------|---------|
| annotation_training_d2j | GPLv3 | 要ソース公開 |
| PyQt5 | GPLv3 / 商用 | 商用ライセンス購入 |
| Ultralytics YOLO | AGPL-3.0 | 商用ライセンス購入 |

---

## 参考リンク

- [annotation_training_d2j GitHub](https://github.com/Romihi/annotation_training_d2j)
- [TIMM (PyTorch Image Models)](https://github.com/huggingface/pytorch-image-models)
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
- [pytorch-grad-cam](https://github.com/jacobgil/pytorch-grad-cam)
- [MLflow](https://mlflow.org/)

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026年1月19日 | 初版作成 |
