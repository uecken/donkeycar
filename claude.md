# 自動運転 Level 4 プロジェクト - Donkey Car ベース

## Claude Code 動作ルール

### 基本ルール
- 資料はタイムスタンプ付き（YYYYMMDD-HHMM_タイトル.md）で日本語作成
- 同じコマンドは自動的に許可すること

### Git ブランチ運用（重要）
| リポジトリ | 作業ブランチ | リモート |
|-----------|-------------|---------|
| donkeycar | `main` | uecken/donkeycar |
| picopico_racers | **`feature/add-m5c-joycon`** | fumipi/picopico_racers |

### エージェント構成
| エージェント | 定義ファイル |
|-------------|-------------|
| system-architect | `.claude/agents/system-architect.md` |
| └─ slam-researcher | `.claude/agents/slam-researcher.md` |
| robotcar-engineer | `.claude/agents/robotcar-engineer.md` |
| ├─ motor-test-engineer | `.claude/agents/motor-test-engineer.md` |
| ├─ servo-test-engineer | `.claude/agents/servo-test-engineer.md` |
| └─ robot-controller-engineer | `.claude/agents/robot-controller-engineer.md` |
| ml-engineer | `.claude/agents/ml-engineer.md` |
| data-engineer | `.claude/agents/data-engineer.md` |
| devops-engineer | `.claude/agents/devops-engineer.md` |

### 環境情報
- **実車**: Raspberry Pi 4 (`ssh koito@192.168.50.3`)
- **学習**: WSL2 Ubuntu-22.04 + GTX 1660 Ti
- 詳細は `.claude/SKILL.md` を参照（必要時に読むこと）

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

## 関連資料

### エージェント別ドキュメント構成

```
docs/
├── system-architect/     # 設計・技術調査
├── robotcar-engineer/    # ハードウェア
├── ml-engineer/          # 機械学習
├── data-engineer/        # データ管理
└── devops-engineer/      # 環境構築・インフラ
```

### system-architect（設計・技術調査）
| 資料名 | パス |
|--------|------|
| Trixie互換性調査 | [docs/system-architect/trixie_compatibility.md](docs/system-architect/trixie_compatibility.md) |
| Romihiリポジトリ分析 | [docs/system-architect/romihi_repository_analysis.md](docs/system-architect/romihi_repository_analysis.md) |

### ml-engineer（機械学習）
| 資料名 | パス |
|--------|------|
| GPUサーバー構成ガイド | [docs/ml-engineer/gpu_server_guide.md](docs/ml-engineer/gpu_server_guide.md) |
| annotation_training_d2jガイド | [docs/ml-engineer/annotation_training_d2j_guide.md](docs/ml-engineer/annotation_training_d2j_guide.md) |
| 学習環境パフォーマンス比較 | [docs/ml-engineer/20260122-1910_学習環境パフォーマンス比較.md](docs/ml-engineer/20260122-1910_学習環境パフォーマンス比較.md) |
| 自動運転モデル動作確認ガイド | [docs/ml-engineer/20260202-0150_自動運転モデル動作確認ガイド.md](docs/ml-engineer/20260202-0150_自動運転モデル動作確認ガイド.md) |
| モデル検証機能ガイド | [docs/ml-engineer/20260203-1450_Donkey_Car_モデル検証機能ガイド.md](docs/ml-engineer/20260203-1450_Donkey_Car_モデル検証機能ガイド.md) |

### data-engineer（データ管理）
| 資料名 | パス |
|--------|------|
| 外部アクセス・データ転送ガイド | [docs/data-engineer/20260125-1440_外部アクセス・データ転送ガイド.md](docs/data-engineer/20260125-1440_外部アクセス・データ転送ガイド.md) |

### devops-engineer（環境構築・インフラ）
| 資料名 | パス |
|--------|------|
| 学習環境構築ガイド（詳細版） | [docs/devops-engineer/20260122-1200_Donkey_Car学習環境構築ガイド.md](docs/devops-engineer/20260122-1200_Donkey_Car学習環境構築ガイド.md) |
| 学習環境クイックガイド | [docs/devops-engineer/20260122-1230_Donkey_Car学習環境クイックガイド.md](docs/devops-engineer/20260122-1230_Donkey_Car学習環境クイックガイド.md) |
| WSL2環境セットアップ記録 | [docs/devops-engineer/20260122-1510_WSL2学習環境セットアップ記録.md](docs/devops-engineer/20260122-1510_WSL2学習環境セットアップ記録.md) |
| Cloudflare Tunnel設定ガイド | [docs/devops-engineer/20260122-1530_Cloudflare_Tunnel設定ガイド.md](docs/devops-engineer/20260122-1530_Cloudflare_Tunnel設定ガイド.md) |
| Gitサブモジュール管理ガイド | [docs/devops-engineer/20260128-1600_Gitサブモジュール管理ガイド.md](docs/devops-engineer/20260128-1600_Gitサブモジュール管理ガイド.md) |

### 外部リポジトリ（refs/）

| リポジトリ | パス | 説明 |
|-----------|------|------|
| annotation_training_d2j | `refs/annotation_training_d2j/` | Romihi氏のアノテーション・学習ツール |
| picopico_racers | `picopico_racers/` (サブモジュール) | Team 10 自動運転ミニカーチャレンジ |

---

## 参考資料

### Donkey Car
- [Donkey Car 公式ドキュメント](https://docs.donkeycar.com/)
- [Donkey Car GitHub](https://github.com/autorope/donkeycar)
- [Donkey Car Raspberry Pi Setup](https://docs.donkeycar.com/guide/robot_sbc/setup_raspberry_pi/)

### Raspberry Pi
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [Picamera2 Manual](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)

### 機械学習
- [TensorFlow Lite for Raspberry Pi](https://www.tensorflow.org/lite/guide/python)
- [PyTorch ARM64](https://mathinf.eu/pytorch/arm64/)

### 自動運転
- [SAE J3016 自動運転レベル定義](https://www.sae.org/standards/content/j3016_202104/)

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026年1月19日 | 初版作成 - 現状分析・Level 4ロードマップ策定 |
| 2026年1月19日 | ターゲット環境確定: Raspberry Pi 4 + Bookworm + Donkey Car 5.1+ |
| 2026年1月19日 | Trixie互換性調査を別資料として分離 (docs/trixie_compatibility.md) |
| 2026年1月19日 | GPUサーバー構成ガイド追加、Romihiリポジトリ分析追加 |
| 2026年1月19日 | annotation_training_d2jガイド追加（Romihi氏の高機能アノテーションツール） |
