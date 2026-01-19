# GPUサーバー構成ガイド - Donkey Car学習環境

**作成日**: 2026年1月19日
**対象**: Donkey Car >= 5.1 モデル学習用環境

---

## 1. Donkey Carモデルと必要なGPUスペック

### 利用可能なモデルタイプ

| モデル名 | クラス名 | 説明 | 入力形状 |
|---------|---------|------|----------|
| **linear** | `KerasLinear` | 基本的なCNNモデル、連続値出力 | (120, 160, 3) |
| **categorical** | `KerasCategorical` | 離散カテゴリ出力（15ビン操舵、20ビンスロットル） | (120, 160, 3) |
| **memory** | `KerasMemory` | 過去の操作履歴を入力として使用 | (120, 160, 3) + memory |
| **lstm** | `KerasLSTM` | LSTM層を使用した時系列モデル | (seq_length, 120, 160, 3) |
| **3d_cnn** | `Keras3D_CNN` | 3D畳み込み時系列モデル（20フレーム） | (20, 120, 160, 3) |
| **imu** | `KerasIMU` | IMUデータを追加入力として使用 | (120, 160, 3) + IMU |
| **behavioral** | `KerasBehavioral` | 行動条件付きモデル | (120, 160, 3) + behavior |
| **latent** | `KerasLatent` | オートエンコーダベースモデル | (120, 160, 3) |

### モデル別GPU要件

| モデル | 最小VRAM | 推奨VRAM | 備考 |
|--------|----------|----------|------|
| linear | 2GB | 4GB | 最も軽量、エントリーGPU可 |
| categorical | 2GB | 4GB | linear同等 |
| memory | 2GB | 4GB | linear + 追加入力 |
| lstm | 4GB | 8GB | シーケンス処理で追加メモリ必要 |
| 3d_cnn | 6GB | 8-12GB | 最もメモリ消費大 |
| imu/behavioral | 2GB | 4GB | linear同等 |

---

## 2. 推奨GPU構成

### エントリーレベル（個人・趣味向け）

| GPU | VRAM | 価格帯 | 対応モデル |
|-----|------|--------|-----------|
| **NVIDIA GeForce RTX 3060** | 12GB | 約3-4万円 | 全モデル対応 |
| **NVIDIA GeForce GTX 1660 Ti** | 6GB | 約2-3万円（中古） | linear/categorical |
| **Intel Arc A770** | 16GB | 約4万円 | TensorFlowサポート限定 |

### ミドルレベル（チーム・教育機関向け）

| GPU | VRAM | 価格帯 | 特徴 |
|-----|------|--------|------|
| **NVIDIA GeForce RTX 4070** | 12GB | 約8-10万円 | 全モデル快適 |
| **NVIDIA GeForce RTX 4080** | 16GB | 約15-18万円 | 3D-CNN、LSTM高速 |
| **AMD Radeon RX 7900 XT** | 20GB | 約12-14万円 | PyTorchサポート良好 |

### ハイエンドレベル（研究・大規模プロジェクト向け）

| GPU | VRAM | 価格帯 | 特徴 |
|-----|------|--------|------|
| **NVIDIA GeForce RTX 4090** | 24GB | 約25-30万円 | コンシューマ最高性能 |
| **NVIDIA A100** | 40/80GB | 約100-200万円 | データセンター向け |
| **NVIDIA H100** | 80GB | 約400万円以上 | 最高性能、クラウド推奨 |

---

## 3. 推奨システム構成

### ローカルPC構成

| コンポーネント | エントリー | ミドル | ハイエンド |
|--------------|-----------|--------|-----------|
| **GPU** | RTX 3060 12GB | RTX 4070 12GB | RTX 4090 24GB |
| **CPU** | Core i5 / Ryzen 5 | Core i7 / Ryzen 7 | Core i9 / Ryzen 9 |
| **RAM** | 16GB | 32GB | 64GB |
| **ストレージ** | SSD 512GB | NVMe 1TB | NVMe 2TB |
| **価格帯** | 約15-20万円 | 約25-35万円 | 約50-70万円 |

### 推奨構成例（ミドルレベル）

```
CPU: AMD Ryzen 7 7700X (8コア/16スレッド)
GPU: NVIDIA GeForce RTX 4070 12GB
RAM: DDR5 32GB (16GB x 2)
SSD: NVMe 1TB (PCIe 4.0)
PSU: 750W 80+ Gold
OS: Ubuntu 22.04 LTS

合計: 約30万円
```

---

## 4. ソフトウェア要件

### TensorFlow/PyTorchバージョン

| フレームワーク | 推奨バージョン | CUDA | cuDNN |
|---------------|---------------|------|-------|
| TensorFlow | 2.15.x | 12.2 | 8.9 |
| PyTorch | 2.1.x | 11.8/12.1 | 8.7+ |

### Donkey Car設定（setup.cfg抜粋）

```ini
# TensorFlow (Keras)
tensorflow==2.15.*          # PC版
tensorflow-aarch64==2.15.*  # Raspberry Pi版

# PyTorch
torch==2.1.*
pytorch-lightning
torchvision
torchaudio
```

### CUDA互換性マトリックス

| TensorFlow | CUDA | cuDNN | Python |
|------------|------|-------|--------|
| 2.15.x | 12.2 | 8.9 | 3.9-3.11 |
| 2.14.x | 12.1 | 8.9 | 3.9-3.11 |
| 2.13.x | 11.8 | 8.6 | 3.8-3.11 |

**重要**: Donkey Car 5.1は Python 3.11 を要求（`python_requires = >=3.11.0,<3.12`）

---

## 5. 学習データ量と学習時間

### デフォルト学習設定

```python
BATCH_SIZE = 128            # バッチサイズ
TRAIN_TEST_SPLIT = 0.8      # 学習/検証分割
MAX_EPOCHS = 100            # 最大エポック数
USE_EARLY_STOP = True       # 早期終了
EARLY_STOP_PATIENCE = 5     # 改善なし許容エポック数
```

### データ量の目安

| 用途 | 画像数 | データサイズ | 走行時間目安 |
|------|--------|-------------|-------------|
| テスト・練習 | 1,000枚 | 約3MB | 約1分 |
| 基本学習 | 5,000-10,000枚 | 約15-30MB | 約5-10分 |
| 実用レベル | 15,000-30,000枚 | 約50-100MB | 約15-30分 |
| 高精度 | 50,000枚以上 | 150MB以上 | 50分以上 |

### 学習時間の比較

| ハードウェア | 1,000枚 | 10,000枚 | 50,000枚 |
|-------------|---------|----------|----------|
| **Raspberry Pi 4 (CPU)** | 8-10時間 | 非推奨 | 非推奨 |
| **MacBook Air M1 (CPU)** | 約2分 | 約20分 | 約100分 |
| **Intel Core i7 (CPU)** | 約16分 | 約160分 | 約13時間 |
| **RTX 2080 (GPU)** | 約10秒 | 約1-2分 | 約8分 |
| **RTX 4070 (GPU)** | 約7秒 | 約50秒 | 約5分 |
| **RTX 4090 (GPU)** | 約5秒 | 約30秒 | 約3分 |
| **AWS g4dn.xlarge T4** | 約15秒 | 約2-3分 | 約12分 |

---

## 6. クラウドGPUオプション

### 無料・低コストオプション

| サービス | GPU | 無料枠 | 制限 |
|---------|-----|-------|------|
| **Google Colab** | T4/V100 | 週30時間程度 | セッション12時間 |
| **Kaggle Notebooks** | T4 | 週30時間 | セッション9時間 |
| **AWS SageMaker Studio Lab** | T4 | 無料 | 4時間/セッション |

### 有料クラウドオプション

| サービス | GPU | 価格/時間 | 月額目安 |
|---------|-----|----------|---------|
| **Google Colab Pro** | T4/V100 | $10/月 | $10 |
| **Google Colab Pro+** | V100/A100 | $50/月 | $50 |
| **AWS g4dn.xlarge** | T4 (16GB) | $0.50-0.70 | 使用量次第 |
| **GCP T4 Spot** | T4 | $0.12-0.20 | 使用量次第 |
| **Runpod RTX 4090** | RTX 4090 | $0.44 | 使用量次第 |
| **Runpod A100** | A100 80GB | $0.80 | 使用量次第 |
| **Runpod H100** | H100 | $1.24 | 使用量次第 |
| **Vast.ai A100** | A100 | ~$0.66 | 使用量次第 |

### クラウドGPU選択ガイド

| ユースケース | 推奨サービス | 推奨GPU | 月額目安 |
|-------------|-------------|---------|----------|
| 趣味・学習 | Google Colab (無料) | T4 | 無料 |
| 本格的な学習 | Colab Pro / Kaggle | T4/V100 | $10-50/月 |
| チーム開発 | GCP/AWS Spot | T4/A10 | $50-100/月 |
| 研究・大規模 | Runpod/Vast.ai | A100/H100 | 使用量次第 |

---

## 7. 環境構築手順

### Ubuntu + NVIDIA GPU

```bash
# 1. NVIDIAドライバーインストール
sudo apt update
sudo ubuntu-drivers autoinstall
sudo reboot

# 2. CUDA Toolkit 12.2インストール
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install cuda-toolkit-12-2

# 3. cuDNN 8.9インストール
sudo apt install libcudnn8 libcudnn8-dev

# 4. 環境変数設定
echo 'export PATH=/usr/local/cuda-12.2/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.2/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# 5. Python仮想環境
python3 -m venv ~/donkey_gpu_env
source ~/donkey_gpu_env/bin/activate

# 6. Donkey Carインストール
pip install donkeycar[pc]
pip install tensorflow[and-cuda]==2.15.*
```

### Google Colab設定

```python
# Colab Notebook先頭に追加
!pip install donkeycar[pc]

# Google Driveマウント（データ保存用）
from google.colab import drive
drive.mount('/content/drive')

# GPU確認
import tensorflow as tf
print(f"GPU Available: {tf.config.list_physical_devices('GPU')}")
```

---

## 8. 学習ワークフロー

### ローカルPC

```bash
# 1. データをPCに転送
scp -r pi@raspberrypi:~/mycar/data/tub_* ~/mycar/data/

# 2. 学習実行
cd ~/mycar
donkey train --tub data/tub_* --model models/mypilot.h5

# 3. TFLite変換（Raspberry Pi用）
donkey makemovie --tub data/tub_* --model models/mypilot.h5 --type tflite

# 4. モデル転送
scp models/mypilot.tflite pi@raspberrypi:~/mycar/models/
```

### クラウド（Colab）

```python
# 1. データアップロード
from google.colab import files
uploaded = files.upload()  # tub.zipをアップロード

# 2. 解凍
!unzip tub.zip -d data/

# 3. 学習
!donkey train --tub data/tub_* --model models/mypilot.h5

# 4. ダウンロード
files.download('models/mypilot.h5')
```

---

## 9. コスト比較

### 初期投資 vs 運用コスト

| 選択肢 | 初期投資 | 月額運用 | 1年間総コスト |
|--------|---------|---------|-------------|
| **ローカルPC（ミドル）** | 30万円 | 電気代約2,000円 | 約32万円 |
| **Google Colab Pro** | 0円 | $10（約1,500円） | 約1.8万円 |
| **AWS g4dn (月20時間)** | 0円 | 約2,000円 | 約2.4万円 |
| **Runpod (月20時間)** | 0円 | 約1,500円 | 約1.8万円 |

### 推奨選択

| 状況 | 推奨 |
|------|------|
| 年間学習時間 < 100時間 | クラウド（Colab Pro / Runpod） |
| 年間学習時間 > 200時間 | ローカルPC投資を検討 |
| チーム利用（5人以上） | ローカルPC + リモートアクセス |
| 実験・研究（大規模） | クラウド（A100/H100） |

---

## 参考資料

- [Donkey Car - Install on Linux](https://docs.donkeycar.com/guide/host_pc/setup_ubuntu/)
- [Donkey Car - Create an Autopilot](https://docs.donkeycar.com/guide/train_autopilot/)
- [TensorFlow GPU Support](https://www.tensorflow.org/install/gpu)
- [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)
- [Google Colab](https://colab.research.google.com/)
- [Runpod](https://www.runpod.io/)
- [Vast.ai](https://vast.ai/)

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026年1月19日 | 初版作成 |
