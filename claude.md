# 自動運転 Level 4 プロジェクト - Donkey Car ベース

## skill.md
- 資料はタイムスタンプ付き（西暦年月日）で日本語で作成する
- 同じコマンドは自動的に許可すること

---

## プロジェクト概要

**作成日**: 2026年1月19日
**最終更新**: 2026年1月19日
**目標**: Donkey Carをベースに自動運転Level 4を実現するソフトウェア・ハードウェアの開発

### ターゲットプラットフォーム
| 項目 | 仕様 |
|------|------|
| **フレームワーク** | Donkey Car >= 5.1 |
| **メインコンピュータ** | Raspberry Pi 4 (4GB/8GB RAM推奨) |
| **OS** | Raspberry Pi OS Bookworm (64-bit) |
| **Python** | 3.11 (Bookworm標準) |
| **カメラAPI** | Picamera2 + libcamera |

### 自動運転レベル定義（SAE J3016）
| レベル | 名称 | 説明 |
|--------|------|------|
| Level 2 | 部分自動化 | 加速・操舵・制動の複数を自動化（現在のDonkey Car） |
| Level 3 | 条件付き自動化 | 限定領域での自動運転、緊急時は人間介入 |
| **Level 4** | **高度自動化** | **限定領域での完全自動運転、人間介入不要** |
| Level 5 | 完全自動化 | あらゆる条件での自動運転 |

---

## 現状構成分析

### 1. ディレクトリ構造
```
donkeycar/
├── donkeycar/           # メインパッケージ
│   ├── parts/           # 58+の再利用可能コンポーネント
│   │   ├── camera.py    # カメラドライバー
│   │   ├── controller.py # コントローラー
│   │   ├── actuator.py  # アクチュエーター
│   │   ├── keras.py     # TensorFlow/Kerasモデル
│   │   ├── lidar.py     # LiDAR統合
│   │   ├── kinematics.py # 車両運動学
│   │   └── pose.py      # 姿勢推定
│   ├── pipeline/        # 学習パイプライン
│   ├── management/      # 車両管理・UI
│   ├── templates/       # ドライブスクリプトテンプレート
│   ├── utilities/       # ユーティリティ
│   └── gym/             # シミュレータ統合
```

### 2. コアアーキテクチャ

#### Vehicle.py - 中央制御エンジン
- 設定可能なHz（通常20Hz）でドライブループを管理
- メモリシステムによるパーツ間データ交換
- 同期・非同期（スレッド）パーツをサポート
- パフォーマンスモニタリング用プロファイラー搭載

#### 現在のシステムフロー
```
ドライブループ (20Hz):
  1. カメラ → 画像キャプチャ
  2. コントローラー → ユーザー入力読み取り
  3. オドメトリ → 速度・位置計算（オプション）
  4. IMU → 加速度・ジャイロ読み取り（オプション）
  5. LiDAR → 距離計測（オプション）
  6. モード決定 → ユーザー/自動操縦選択
  7. 自動操縦時: モデル推論 → 操舵・スロットル予測
  8. アクチュエーター → PWM信号送信
  9. データ記録
```

### 3. ハードウェアサポート（現状）

#### カメラ
- PiCamera (Picamera2)
- CSICamera (Jetson Nano IMX219)
- Intel RealSense D435/D435i（深度+IMU）
- OAK-D（ステレオ深度）
- Webカメラ（pygame経由）

#### センサー
- **IMU**: MPU6050, IMU6000, IMU9250
- **LiDAR**: RPLidar, TFMini
- **エンコーダー**: GPIO, Arduino Serial, pigpio
- **GPS**: フレームワークあり

#### アクチュエーター
- PWMサーボ + ESC（標準RCカー）
- HBridge DCモーター（差動駆動）
- VESC モーターコントローラー
- L298N モータードライバー

### 4. AI/MLモデル（現状）

| モデルタイプ | 説明 |
|-------------|------|
| linear | 単純な操舵角・スロットル予測 |
| categorical | 離散操舵ビン |
| memory | LSTM時系列モデル |
| imu | 視覚+IMU統合 |
| behavior | 行動認識モデル |
| localizer | トラック位置推定 |
| 3d_cnn | 時間的視覚用3D畳み込み |

**フレームワーク**: TensorFlow/Keras, TFLite, TensorRT, PyTorch

---

## Level 4 達成に向けた課題と提案

### 課題1: 安全システムの欠如

**現状の問題**:
- 緊急停止機能が限定的
- 衝突回避ロジックなし
- フェイルセーフ機構が不十分

**提案**:
```
新規パーツ: parts/safety/
├── emergency_stop.py      # 緊急停止システム
├── collision_avoidance.py # 衝突回避（LiDAR連携）
├── watchdog.py           # ウォッチドッグタイマー
└── boundary_detector.py  # ODD境界検出
```

### 課題2: 高度な認識能力の不足

**現状の問題**:
- 単純な画像認識のみ
- 物体検出が限定的（停止標識のみ）
- セマンティックセグメンテーションなし

**提案**:
```
強化パーツ: parts/perception/
├── multi_object_detector.py  # マルチオブジェクト検出
├── semantic_segmentation.py  # セマンティックセグメンテーション
├── depth_estimation.py       # 単眼深度推定
├── lane_detector.py          # レーン検出
└── motion_predictor.py       # 動き予測
```

### 課題3: 計画・制御の未実装

**現状の問題**:
- エンドツーエンド学習のみ
- 経路計画機能なし
- 予測制御なし

**提案**:
```
新規パーツ: parts/planning/
├── trajectory_planner.py  # 軌道計画
├── behavior_planner.py    # 行動計画
├── mpc_controller.py      # モデル予測制御
└── path_follower.py       # 経路追従
```

### 課題4: 自己位置推定・地図作成

**現状の問題**:
- GPS依存（精度不足）
- SLAM未実装
- 高精度地図未対応

**提案**:
```
新規パーツ: parts/localization/
├── visual_slam.py        # 視覚SLAM
├── rtk_gps.py           # RTK-GPS統合
├── particle_filter.py    # パーティクルフィルタ
└── map_manager.py        # 地図管理
```

---

## 実装ロードマップ

### Phase 1: 安全基盤構築（優先度: 最高）
1. [ ] 緊急停止システム実装
2. [ ] LiDAR連携衝突回避
3. [ ] ウォッチドッグタイマー
4. [ ] ODD（運行設計領域）定義と境界検出

### Phase 2: 認識能力強化
1. [ ] YOLOv8統合によるマルチオブジェクト検出
2. [ ] レーン検出・追従
3. [ ] 深度推定統合（RealSense/OAK-D活用）
4. [ ] 道路標識認識

### Phase 3: 計画・制御実装
1. [ ] 経路計画アルゴリズム
2. [ ] モデル予測制御（MPC）
3. [ ] 行動決定ロジック
4. [ ] スムーズな軌道生成

### Phase 4: 自己位置推定強化
1. [ ] Visual Odometry実装
2. [ ] センサーフュージョン（カメラ+IMU+GPS）
3. [ ] 簡易SLAM
4. [ ] 高精度地図対応

### Phase 5: 統合・検証
1. [ ] シミュレータでの統合テスト
2. [ ] 実車での段階的テスト
3. [ ] 安全性検証
4. [ ] ODD内での自律走行実証

---

## ハードウェア構成

### 基本構成（Raspberry Pi 4ベース）

| コンポーネント | 製品 | 備考 |
|---------------|------|------|
| **メインコンピュータ** | Raspberry Pi 4 (8GB) | Bookworm 64-bit |
| **カメラ** | Raspberry Pi Camera Module 3 | Picamera2対応、オートフォーカス |
| **PWMボード** | PCA9685 | I2C接続、16ch PWM |
| **サーボ** | 標準RCサーボ | ステアリング用 |
| **ESC** | ブラシレスESC | スロットル制御 |

### Level 4拡張構成（推奨追加）

| コンポーネント | 推奨製品 | 用途 |
|---------------|---------|------|
| **深度カメラ** | OAK-D Lite | ステレオ深度・物体検出（DepthAI） |
| **LiDAR** | RPLidar A1M8 | 360°距離計測 |
| **IMU** | MPU6050 / BNO055 | 慣性計測 |
| **GPS** | u-blox NEO-M8N | 測位（RTK対応はZED-F9P） |
| **エンコーダー** | ロータリーエンコーダー | 速度・距離計測 |
| **緊急停止** | 無線リレースイッチ | 安全停止機構 |

### センサー配置図
```
            [Pi Camera 3 / OAK-D Lite]
                     ↓
    ┌─────────────────────────────┐
    │      [前方視野カメラ]        │
    │             ↓               │
    │    ┌─────────────────┐      │
    │    │  Raspberry Pi 4 │      │
    │    │    Bookworm     │      │ ← [RPLidar A1M8 (360°)]
    │    └─────────────────┘      │
    │    [MPU6050] [PCA9685]      │
    │         [GPS NEO-M8N]       │
    └─────────────────────────────┘
              ↓
    [サーボ] ←→ [ESC/モーター]
         [エンコーダー]
```

### GPIO/I2C接続マップ
```
Raspberry Pi 4 GPIO:
├── I2C1 (GPIO 2,3)
│   ├── PCA9685 (0x40) - PWMサーボ/ESC
│   ├── MPU6050 (0x68) - IMU
│   └── OLED (0x3C) - ステータス表示（オプション）
├── SPI0 - 予備
├── UART (GPIO 14,15) - GPS / LiDAR
├── GPIO (エンコーダー入力)
└── CSI - Pi Camera 3
```

---

## 開発環境

### Raspberry Pi 4 + Bookworm 環境

#### ソフトウェア要件
| パッケージ | バージョン | 備考 |
|-----------|-----------|------|
| Python | 3.11 | Bookworm標準 |
| Donkey Car | >= 5.1 | pip install donkeycar |
| TensorFlow Lite | 2.x | Pi4向け軽量推論 |
| OpenCV | 4.x | 画像処理 |
| Picamera2 | 0.3+ | libcamera対応 |
| pigpio | 最新 | GPIO制御 |

#### Bookworm特有の注意点
- **カメラ**: `raspistill`/`raspivid`は廃止、`libcamera`/`Picamera2`を使用
- **I2C**: `/boot/config.txt` → `/boot/firmware/config.txt` に変更
- **Python仮想環境**: システムパッケージ保護のためvenv必須
  ```bash
  python -m venv ~/donkey_env --system-site-packages
  source ~/donkey_env/bin/activate
  ```

#### インストール手順
```bash
# 1. システム更新
sudo apt update && sudo apt upgrade -y

# 2. 必要パッケージ
sudo apt install -y python3-pip python3-venv python3-dev \
    libatlas-base-dev libopenjp2-7 libtiff5 libcap-dev

# 3. I2C/SPI有効化
sudo raspi-config  # Interface Options → I2C, SPI, Camera有効化

# 4. 仮想環境作成
python -m venv ~/donkey_env --system-site-packages
source ~/donkey_env/bin/activate

# 5. Donkey Car インストール
pip install donkeycar[pi]

# 6. アプリ作成
donkey createcar --path ~/mycar
```

### 推奨開発フロー
1. **ホストPC**: モデル学習（GPU推奨）
2. **シミュレータ**: Donkey Gymでのテスト
3. **Raspberry Pi**: TFLiteモデルで実車推論
4. **データ収集**: 実車走行でTubデータ収集
5. **反復改善**: データ収集→学習→検証サイクル

### モデル学習・変換フロー
```
[ホストPC (GPU)]
    ↓ 学習
[Keras .h5 モデル]
    ↓ 変換
[TFLite .tflite モデル] ← 量子化（INT8推奨）
    ↓ 転送
[Raspberry Pi 4] → 推論実行
```

---

## Raspberry Pi OS Trixie (Debian 13) 互換性調査

**調査日**: 2026年1月19日

### Trixie概要

| 項目 | 内容 |
|------|------|
| **ベース** | Debian 13 "Trixie" |
| **Debianリリース** | 2025年8月9日 |
| **Raspberry Pi OSリリース** | 2025年10月2日 |
| **Linuxカーネル** | 6.12 LTS |
| **Python** | 3.13（デフォルト） |
| **サポート期限** | 2030年6月30日（LTS含む） |

### Donkey Car動作可否の判定

#### 総合判定: ⚠️ **条件付きで動作可能**

| コンポーネント | 状態 | 備考 |
|---------------|------|------|
| **Raspberry Pi 4** | ✅ 対応 | 32bit/64bit両対応 |
| **Python 3.13** | ⚠️ 注意 | Donkey Car 5.1はPython 3.11向け設計 |
| **TensorFlow** | ✅ 対応 | TensorFlow 2.20.0+ でPython 3.13対応 |
| **PyTorch** | ✅ 対応 | 公式ARM64 wheel提供 |
| **Picamera2** | ✅ 対応 | `apt install python3-picamera2` |
| **lgpio (GPIO)** | ⚠️ 要対策 | Python 3.13用パッケージ未提供 |
| **MediaPipe** | ❌ 非対応 | Python 3.13未対応 |

### 主な課題と対策

#### 課題1: Python 3.13互換性

**問題**: Donkey Car 5.1はPython 3.11 + TensorFlow 2.15.Xで設計されている

**対策**:
```bash
# TensorFlow 2.20.0以上をインストール（Python 3.13対応）
pip install tensorflow>=2.20.0

# または PyTorchベースのモデルを使用
pip install torch torchvision
```

#### 課題2: GPIO (lgpio) 問題

**問題**: lgpio Python 3.13向けパッケージが未提供

**対策**:
```bash
# 仮想環境作成時に --system-site-packages を必ず指定
python3 -m venv --system-site-packages ~/donkey_env
source ~/donkey_env/bin/activate

# システムのlgpioパッケージを使用
sudo apt install python3-lgpio python3-rpi-lgpio
```

#### 課題3: Picamera2 初期不具合（解決済み）

**問題**: libpisp/libcamera間のリンク問題（Trixieリリース初期）

**対策**: 現在は修正済み
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-picamera2
# rpicam-hello で動作確認
rpicam-hello
```

#### 課題4: MediaPipe非対応

**問題**: MediaPipe（物体検出等）がPython 3.13に未対応

**対策**:
- 物体検出はYOLOv8 + Ultralytics（Python 3.13対応）を使用
- または TensorFlow Lite + カスタムモデルを使用

### Trixie vs Bookworm 比較

| 項目 | Bookworm (推奨) | Trixie |
|------|----------------|--------|
| **安定性** | ✅ 高い | ⚠️ 一部パッケージ未整備 |
| **Python** | 3.11 | 3.13 |
| **Donkey Car互換** | ✅ 完全対応 | ⚠️ 要調整 |
| **TensorFlow** | 2.15.x | 2.20.0+ |
| **MediaPipe** | ✅ 対応 | ❌ 非対応 |
| **サポート期限** | 2028年 | 2030年 |
| **新機能** | - | 新UI、Control Centre等 |

### Trixieインストール手順（使用する場合）

```bash
# 1. システム更新
sudo apt update && sudo apt upgrade -y

# 2. 必要なシステムパッケージ
sudo apt install -y python3-pip python3-venv python3-dev \
    python3-lgpio python3-rpi-lgpio python3-picamera2 \
    libatlas-base-dev libopenjp2-7 libtiff6 libcap-dev

# 3. I2C/SPI/カメラ有効化
sudo raspi-config  # Interface Options

# 4. 仮想環境作成（--system-site-packages 必須）
python3 -m venv --system-site-packages ~/donkey_env
source ~/donkey_env/bin/activate

# 5. TensorFlow 2.20+インストール
pip install tensorflow>=2.20.0

# 6. Donkey Car インストール
pip install donkeycar[pi]

# 7. 動作確認
python -c "import tensorflow as tf; print(tf.__version__)"
python -c "from picamera2 import Picamera2; print('Picamera2 OK')"
```

### 推奨判定

| ユースケース | 推奨OS |
|-------------|--------|
| **安定運用・本番環境** | Bookworm（推奨） |
| **最新機能検証・実験** | Trixie（条件付き可） |
| **MediaPipe使用** | Bookworm（必須） |
| **長期サポート重視** | Trixie（2030年まで） |

### 結論

**現時点での推奨: Raspberry Pi OS Bookworm (64-bit)**

理由:
1. Donkey Car 5.1との完全互換性
2. すべての依存パッケージが安定動作
3. MediaPipe等の追加ライブラリも利用可能
4. 十分なサポート期間（2028年まで）

Trixieは将来的に主流となるため、Bookwormで開発・安定動作確認後、Trixie移行を検討することを推奨。

---

## 参考資料

### Donkey Car
- [Donkey Car 公式ドキュメント](https://docs.donkeycar.com/)
- [Donkey Car GitHub](https://github.com/autorope/donkeycar)
- [Donkey Car Raspberry Pi Setup](https://docs.donkeycar.com/guide/robot_sbc/setup_raspberry_pi/)

### Raspberry Pi OS
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [Raspberry Pi OS Trixie リリースノート](https://www.raspberrypi.com/news/trixie-the-new-version-of-raspberry-pi-os/)
- [Debian 13 Trixie リリース情報](https://www.debian.org/releases/trixie/)
- [Picamera2 Manual](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)

### 機械学習
- [TensorFlow Lite for Raspberry Pi](https://www.tensorflow.org/lite/guide/python)
- [PyTorch ARM64](https://mathinf.eu/pytorch/arm64/)
- [TensorFlow Python 3.13対応 (PyPI)](https://pypi.org/project/tensorflow/)

### 自動運転
- [SAE J3016 自動運転レベル定義](https://www.sae.org/standards/content/j3016_202104/)

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026年1月19日 | 初版作成 - 現状分析・Level 4ロードマップ策定 |
| 2026年1月19日 | ターゲット環境確定: Raspberry Pi 4 + Bookworm + Donkey Car 5.1+ |
| 2026年1月19日 | Trixie (Debian 13) 互換性調査追加 - 条件付き動作可能、Bookworm推奨 |
