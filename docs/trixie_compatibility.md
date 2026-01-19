# Raspberry Pi OS Trixie (Debian 13) 互換性調査

**調査日**: 2026年1月19日
**対象**: Donkey Car >= 5.1 + Raspberry Pi 4

---

## 1. Trixie概要

| 項目 | 内容 |
|------|------|
| **ベース** | Debian 13 "Trixie" |
| **Debianリリース** | 2025年8月9日 |
| **Raspberry Pi OSリリース** | 2025年10月2日 |
| **Linuxカーネル** | 6.12 LTS |
| **Python** | 3.13（デフォルト） |
| **サポート期限** | 2030年6月30日（LTS含む） |

### 主な変更点（Bookwormからの差分）

- **Python**: 3.11 → 3.13
- **カーネル**: 6.6 → 6.12 LTS
- **デスクトップ**: 新テーマ（PiXtrix/PiXonyx）、Control Centre導入
- **設定アプリ**: 個別設定アプリ → 統合Control Centreに移行

---

## 2. Donkey Car動作可否の判定

### 総合判定: ⚠️ **条件付きで動作可能**

| コンポーネント | 状態 | 備考 |
|---------------|------|------|
| **Raspberry Pi 4** | ✅ 対応 | 32bit/64bit両対応 |
| **Python 3.13** | ⚠️ 注意 | Donkey Car 5.1はPython 3.11向け設計 |
| **TensorFlow** | ✅ 対応 | TensorFlow 2.20.0+ でPython 3.13対応 |
| **PyTorch** | ✅ 対応 | 公式ARM64 wheel提供 |
| **Picamera2** | ✅ 対応 | `apt install python3-picamera2` |
| **lgpio (GPIO)** | ⚠️ 要対策 | Python 3.13用パッケージ未提供 |
| **pigpio** | ✅ 対応 | システムパッケージ利用 |
| **OpenCV** | ✅ 対応 | apt / pip両方可 |
| **MediaPipe** | ❌ 非対応 | Python 3.13未対応 |
| **AI HAT/AI Kit** | ❌ 未対応 | Trixie用パッケージ未提供 |

---

## 3. 主な課題と対策

### 課題1: Python 3.13互換性

**問題**:
- Donkey Car 5.1はPython 3.11 + TensorFlow 2.15.Xで設計されている
- 一部の依存パッケージがPython 3.13に未対応

**対策**:
```bash
# TensorFlow 2.20.0以上をインストール（Python 3.13対応）
pip install tensorflow>=2.20.0

# または PyTorchベースのモデルを使用
pip install torch torchvision
```

**補足**: TensorFlow 2.20.0は2025年8月13日リリース、Python 3.13対応済み

---

### 課題2: GPIO (lgpio) 問題

**問題**:
- lgpio Python 3.13向けパッケージがpipで未提供
- Donkey CarのGPIO制御に影響

**対策**:
```bash
# 仮想環境作成時に --system-site-packages を必ず指定
python3 -m venv --system-site-packages ~/donkey_env
source ~/donkey_env/bin/activate

# システムのlgpioパッケージを使用
sudo apt install python3-lgpio python3-rpi-lgpio
```

**重要**: `--system-site-packages`を指定しないと、システムのGPIOパッケージにアクセスできない

---

### 課題3: Picamera2 初期不具合（解決済み）

**問題**:
- libpisp/libcamera間のリンク問題（Trixieリリース初期）
- カメラが認識されない症状

**対策**: 現在は修正済み
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-picamera2

# 動作確認
rpicam-hello
```

**補足**: libcameraパッケージがlibpispの更新に合わせて再ビルドされ、問題解決

---

### 課題4: MediaPipe非対応

**問題**:
- MediaPipe（手・顔・ポーズ検出等）がPython 3.13に未対応
- 物体検出機能が使用不可

**対策**:
```bash
# 代替1: YOLOv8 + Ultralytics（Python 3.13対応）
pip install ultralytics

# 代替2: TensorFlow Lite + カスタムモデル
pip install tflite-runtime
```

**物体検出の代替手段**:
| ライブラリ | Python 3.13 | 用途 |
|-----------|-------------|------|
| YOLOv8 (Ultralytics) | ✅ 対応 | 汎用物体検出 |
| TFLite | ✅ 対応 | 軽量モデル推論 |
| OpenCV DNN | ✅ 対応 | ONNX/Caffe推論 |
| MediaPipe | ❌ 非対応 | - |

---

### 課題5: Raspberry Pi AI HAT/AI Kit

**問題**:
- Trixie用パッケージが未提供
- Hailo NPUアクセラレータが使用不可

**対策**:
- 現時点では対策なし
- Bookwormを使用するか、パッケージ提供を待つ

---

## 4. Trixie vs Bookworm 比較

| 項目 | Bookworm (推奨) | Trixie |
|------|----------------|--------|
| **安定性** | ✅ 高い | ⚠️ 一部パッケージ未整備 |
| **Python** | 3.11 | 3.13 |
| **Donkey Car互換** | ✅ 完全対応 | ⚠️ 要調整 |
| **TensorFlow** | 2.15.x | 2.20.0+ |
| **PyTorch** | ✅ 対応 | ✅ 対応 |
| **MediaPipe** | ✅ 対応 | ❌ 非対応 |
| **AI HAT/AI Kit** | ✅ 対応 | ❌ 未対応 |
| **サポート期限** | 2028年 | 2030年 |
| **カーネル** | 6.6 | 6.12 LTS |
| **新機能** | - | 新UI、Control Centre等 |

---

## 5. Trixieインストール手順

### 5.1 OSイメージ取得

**推奨**: Raspberry Pi Imagerを使用
- Raspberry Pi OS (64-bit) Trixieを選択
- インプレースアップグレードは非推奨

### 5.2 初期設定

```bash
# 1. システム更新
sudo apt update && sudo apt upgrade -y

# 2. I2C/SPI/カメラ有効化
sudo raspi-config
# → Interface Options → I2C, SPI, Camera を有効化

# 3. 再起動
sudo reboot
```

### 5.3 Donkey Car環境構築

```bash
# 1. 必要なシステムパッケージ
sudo apt install -y python3-pip python3-venv python3-dev \
    python3-lgpio python3-rpi-lgpio python3-picamera2 \
    libatlas-base-dev libopenjp2-7 libtiff6 libcap-dev

# 2. 仮想環境作成（--system-site-packages 必須）
python3 -m venv --system-site-packages ~/donkey_env
source ~/donkey_env/bin/activate

# 3. TensorFlow 2.20+インストール
pip install tensorflow>=2.20.0

# 4. Donkey Car インストール
pip install donkeycar[pi]

# 5. アプリ作成
donkey createcar --path ~/mycar
```

### 5.4 動作確認

```bash
# Python/TensorFlowバージョン確認
python -c "import sys; print(f'Python: {sys.version}')"
python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')"

# Picamera2確認
python -c "from picamera2 import Picamera2; print('Picamera2 OK')"

# GPIO確認
python -c "import lgpio; print('lgpio OK')"

# Donkey Car確認
python -c "import donkeycar as dk; print(f'Donkey Car: {dk.__version__}')"
```

---

## 6. 推奨判定

| ユースケース | 推奨OS | 理由 |
|-------------|--------|------|
| **安定運用・本番環境** | Bookworm | 完全互換、全パッケージ安定 |
| **最新機能検証・実験** | Trixie | 条件付きで可、要対策 |
| **MediaPipe使用** | Bookworm | Trixie非対応のため必須 |
| **AI HAT/AI Kit使用** | Bookworm | Trixie未対応のため必須 |
| **長期サポート重視** | Trixie | 2030年までサポート |
| **最新カーネル必要** | Trixie | 6.12 LTS搭載 |

---

## 7. 結論

### 現時点での推奨: **Raspberry Pi OS Bookworm (64-bit)**

**理由**:
1. Donkey Car 5.1との完全互換性
2. すべての依存パッケージが安定動作
3. MediaPipe、AI HAT等の追加機能も利用可能
4. 十分なサポート期間（2028年まで）

### 将来の展望

Trixieは将来的に主流となるため、以下のアプローチを推奨:

1. **現在**: Bookwormで開発・安定動作確認
2. **移行準備**: Trixie環境で動作テスト実施
3. **移行判断**: MediaPipe等の対応状況を確認後、Trixieへ移行

---

## 8. 参考資料

### 公式ドキュメント
- [Raspberry Pi OS Trixie リリースノート](https://www.raspberrypi.com/news/trixie-the-new-version-of-raspberry-pi-os/)
- [Debian 13 Trixie リリース情報](https://www.debian.org/releases/trixie/)
- [Picamera2 GitHub](https://github.com/raspberrypi/picamera2)

### 互換性情報
- [TensorFlow PyPI](https://pypi.org/project/tensorflow/)
- [PyTorch ARM64](https://mathinf.eu/pytorch/arm64/)
- [Donkey Car Raspberry Pi Setup](https://docs.donkeycar.com/guide/robot_sbc/setup_raspberry_pi/)

### コミュニティ
- [Raspberry Pi Forums - Trixie](https://forums.raspberrypi.com/viewtopic.php?t=390767)
- [Donkey Car GitHub Issues](https://github.com/autorope/donkeycar/issues)

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026年1月19日 | 初版作成 |
