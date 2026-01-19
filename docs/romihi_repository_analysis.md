# Romihi GitHubリポジトリ調査報告書

**調査日**: 2026年1月19日
**調査対象**: https://github.com/Romihi
**目的**: Donkey Car + Raspberry Pi 4 + Level 4自動運転プロジェクトへの参考要素抽出

---

## 1. リポジトリ一覧と分類

### 自動運転・ロボティクス関連（最重要）

| リポジトリ名 | 説明 | 言語 | 関連度 |
|------------|------|------|--------|
| **donkeycar** | autorope/donkeycarのフォーク | Python | ★★★ |
| **jetracer** | NVIDIA Jetson Nano自律走行AIレースカー | Jupyter Notebook | ★★★ |
| **RumiCar** | 自動運転アルゴリズム教育プラットフォーム | C++ | ★★★ |
| **donkey-my-sim** | Donkey Car用Unityシミュレーション環境 | ShaderLab/C# | ★★☆ |

### コンピュータビジョン・画像処理関連

| リポジトリ名 | 説明 | 言語 | 活用可能性 |
|------------|------|------|-----------|
| **segmentation_tool** | セグメンテーションGUIツール（学習・推論） | Python | レーン認識 |
| **segformer** | SegFormerセグメンテーション実装 | Python | 道路認識 |
| **lcnn** | End-to-End Wireframeパーシング | Python | エッジ検出 |
| **kakuzato** | テクスチャ物体エッジ検出 | Python | 研究用 |

### ハードウェア・センサー統合関連

| リポジトリ名 | 説明 | 言語 | 活用可能性 |
|------------|------|------|-----------|
| **ultrasonic_jetson_orinnano_jetpack6.2** | 超音波センサー統合（Jetson） | Python | 障害物検知 |
| **bno055-python-i2c** | BNO055 IMUセンサー（Raspberry Pi） | Python | 姿勢推定 |
| **ArduinoUsbCtr** | Arduino USBコントローラー | C++ | 制御系 |

### データ管理・ユーティリティ

| リポジトリ名 | 説明 | 言語 | 活用可能性 |
|------------|------|------|-----------|
| **data_viewer** | Donkey Car学習データ可視化Webアプリ | HTML/Flask | データ分析 |
| **video_comparison_viewer** | マルチパネル動画比較ツール | Python | デバッグ |
| **annotation_training_d2j** | アノテーション学習ツール | Python | データ準備 |

---

## 2. 主要プロジェクト詳細分析

### 2.1 donkeycar（フォーク）

| 項目 | 内容 |
|------|------|
| **リポジトリ** | https://github.com/Romihi/donkeycar |
| **元リポジトリ** | autorope/donkeycar |
| **言語構成** | Python 86.6%, JavaScript 7.4%, HTML 2.2% |
| **コミット数** | 2,181 |

**特徴**:
- 公式Donkey Carのフォーク
- Webインターフェース（localhost:8887）対応
- 現時点で大きな独自カスタマイズは未確認

---

### 2.2 JetRacer

| 項目 | 内容 |
|------|------|
| **リポジトリ** | https://github.com/Romihi/jetracer |
| **ハードウェア** | NVIDIA Jetson Nano |
| **言語** | Jupyter Notebook |

**対応車両**:
| 車両 | スケール | 価格帯 |
|------|---------|--------|
| Latrax Rally | 1/18 | 約$400 |
| Tamiya TT02 | 1/10 | 約$600 |

**機能**:
- Jupyter Notebookでの基本モーション制御
- AIによる道路追従（Road Following）
- NVIDIA TensorRTによる高速推論最適化

**Level 4への参考点**:
- TensorRT最適化手法
- Jupyter Notebookでの開発ワークフロー

---

### 2.3 RumiCar

| 項目 | 内容 |
|------|------|
| **リポジトリ** | https://github.com/Romihi/RumiCar |
| **目的** | 自動運転アルゴリズム教育 |
| **言語** | C++ |

**対応コンピューティングモジュール**:
| モジュール | 特徴 | 用途 |
|-----------|------|------|
| Arduino Nano | 低コスト | 初心者向け |
| ESP32 | WiFi/Bluetooth搭載 | IoT連携 |
| Raspberry Pi Zero W | 画像認識・AI対応 | 高度な処理 |

**センサー構成**:
- 前面に3つのレーザー距離測定モジュール

**実装アルゴリズム**:
1. 距離測定・障害物検出
2. ステアリング・速度制御
3. 基本的な自律ナビゲーション
4. 安全停止機構
5. 都市コースナビゲーション

**Level 4への参考点**:
- 段階的なアルゴリズム実装アプローチ
- 安全停止機構の実装
- 複数センサーによる障害物検出

---

### 2.4 segmentation_tool

| 項目 | 内容 |
|------|------|
| **リポジトリ** | https://github.com/Romihi/segmentation_tool |
| **用途** | 汎用セグメンテーションワークフローGUIツール |
| **言語** | Python |

**対応モデル**:
| カテゴリ | モデル |
|---------|--------|
| CNN系 | UNet, SegNet, DeepLabV3, SimpleSegNet |
| Transformer系 | Vision Transformer for Segmentation |
| YOLO系 | YOLOv8/v11（インスタンスセグメンテーション） |

**特徴**:
- GUIによるアノテーション・学習・推論
- OpenVINO変換対応（エッジデバイス最適化）
- MLflow統合による実験管理

**Level 4への参考点**:
- レーン検出・道路領域認識に活用可能
- OpenVINOによるRaspberry Pi向け最適化
- 複数モデルアーキテクチャの比較検証

---

### 2.5 data_viewer

| 項目 | 内容 |
|------|------|
| **リポジトリ** | https://github.com/Romihi/data_viewer |
| **用途** | Donkey Car学習データ可視化 |
| **技術** | HTML/Flask |

**機能一覧**:
- フォルダブラウザによるデータディレクトリ選択
- セッションフィルタリング
- インタラクティブタイムラインチャート（ズーム・パン対応）
- リアルタイムヒストグラム
- マルチカメラフィード表示
- 双方向再生（順方向/逆方向）
- 統計計算（平均、標準偏差、最小/最大、中央値、四分位数）

**Level 4への参考点**:
- 学習データ品質管理に直接活用可能
- 異常データの検出・除外
- 走行パターン分析

---

### 2.6 bno055-python-i2c

| 項目 | 内容 |
|------|------|
| **リポジトリ** | https://github.com/Romihi/bno055-python-i2c |
| **センサー** | BNO055 IMU（9軸） |
| **対応** | Raspberry Pi I2C |

**センサー機能**:
- 加速度計
- ジャイロスコープ
- 磁力計

**技術的注意点**:
- I2Cクロック速度: 50KHz推奨（高速では不安定）
- Raspberry Pi設定: `/boot/config.txt`で`dtparam=i2c_baudrate=50000`

**Level 4への参考点**:
- 車両姿勢推定（ロール、ピッチ、ヨー）
- Donkey CarのIMUパーツとの統合
- センサーフュージョンの基盤

---

### 2.7 ultrasonic_jetson_orinnano_jetpack6.2

| 項目 | 内容 |
|------|------|
| **リポジトリ** | https://github.com/Romihi/ultrasonic_jetson_orinnano_jetpack6.2 |
| **センサー** | HC-SR04超音波センサー×5 |
| **対応** | Jetson Orin Nano + JetPack 6.2 |

**センサー配置**:
```
        [FrLH]  [Fr]  [FrRH]
           \     |     /
            \    |    /
             \   |   /
    [LH] ---- [車両] ---- [RH]
```

| 位置 | 名称 | 用途 |
|------|------|------|
| FrLH | 前方左 | 左前方障害物 |
| Fr | 前方中央 | 正面障害物 |
| FrRH | 前方右 | 右前方障害物 |
| LH | 左側 | 左側障害物 |
| RH | 右側 | 右側障害物 |

**回路構成**:
- 電圧変換: 5V→3.3V分圧回路（1kΩ + 2kΩ抵抗）
- ライブラリ: JETGPIOを使用

**Level 4への参考点**:
- 複数方向からの障害物検知
- Raspberry Pi向けにpigpioで移植可能
- 衝突回避システムの基盤

---

## 3. 本プロジェクトへの活用提案

### 3.1 直接活用可能なリポジトリ

| 優先度 | リポジトリ | 活用内容 |
|--------|-----------|---------|
| **高** | data_viewer | 学習データの可視化・品質管理 |
| **高** | bno055-python-i2c | Raspberry Pi用IMU統合 |
| **高** | segmentation_tool | レーン・道路認識モデル開発 |
| **中** | donkey-my-sim | シミュレーション環境構築 |
| **中** | RumiCar | 安全停止アルゴリズム参考 |

### 3.2 技術スタック参考

| 技術領域 | 参考元 | 活用方法 |
|---------|--------|---------|
| **エッジAI最適化** | segmentation_tool | OpenVINO変換でRaspberry Pi最適化 |
| **推論高速化** | jetracer | TensorRT最適化（Jetson利用時） |
| **センサー配置** | ultrasonic_jetson | 5方向超音波センサー構成 |
| **段階的開発** | RumiCar | アルゴリズムの段階的実装 |

### 3.3 Level 4自動運転への応用ロードマップ

#### Phase 1: データ基盤（data_viewer活用）
```
1. data_viewerをDonkey Carプロジェクトに統合
2. 学習データの品質管理ワークフロー確立
3. 異常データ自動検出機能追加
```

#### Phase 2: センサー統合（bno055-python-i2c活用）
```
1. BNO055 IMUをRaspberry Pi 4に接続
2. Donkey CarのIMUパーツと統合
3. 車両姿勢推定の精度向上
```

#### Phase 3: 知覚システム強化（segmentation_tool活用）
```
1. レーン検出用セグメンテーションモデル作成
2. DeepLabV3またはVision Transformerで学習
3. OpenVINOでRaspberry Pi向け最適化
4. Donkey Carパイプラインに統合
```

#### Phase 4: 安全システム（RumiCar + ultrasonic参考）
```
1. 超音波センサー5方向配置（Raspberry Pi版）
2. 障害物検出アルゴリズム実装
3. 緊急停止機構との連携
4. 安全境界（ODD）検出機能
```

---

## 4. 統合アーキテクチャ提案

### センサー構成（Romihi参考）

```
                [Pi Camera 3]
                     |
        [HC-SR04]  [HC-SR04]  [HC-SR04]
           FrLH       Fr        FrRH
             \        |        /
              \       |       /
    [HC-SR04] ─── [Raspberry Pi 4] ─── [HC-SR04]
       LH          [BNO055]              RH
                   [PCA9685]
                      |
              [サーボ] [ESC]
```

### ソフトウェアスタック

```
┌─────────────────────────────────────────┐
│           アプリケーション層             │
│  ┌─────────────────────────────────┐   │
│  │  data_viewer (データ分析)        │   │
│  │  segmentation_tool (モデル開発)  │   │
│  └─────────────────────────────────┘   │
├─────────────────────────────────────────┤
│           Donkey Car Core              │
│  ┌─────────────────────────────────┐   │
│  │  Vehicle.py (制御ループ)         │   │
│  │  parts/keras.py (推論)          │   │
│  │  parts/actuator.py (駆動)       │   │
│  └─────────────────────────────────┘   │
├─────────────────────────────────────────┤
│           センサー統合層               │
│  ┌─────────────────────────────────┐   │
│  │  bno055-python-i2c (IMU)        │   │
│  │  ultrasonic (障害物検知)         │   │
│  │  Picamera2 (カメラ)             │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## 5. まとめ

### 発見事項

Romihiさんのリポジトリは、自動運転開発に必要な以下の要素を網羅:

1. **プラットフォーム**: Donkey Car、JetRacer、RumiCarの3種類
2. **コンピュータビジョン**: セグメンテーション、アノテーション、学習ツール
3. **センサー統合**: IMU、超音波センサーのライブラリ
4. **データ管理**: Donkey Car専用の可視化・分析ツール

### 推奨アクション

| 優先度 | アクション |
|--------|-----------|
| 1 | data_viewerをフォークして本プロジェクトに統合 |
| 2 | bno055-python-i2cでIMU統合を実装 |
| 3 | segmentation_toolでレーン認識モデルを開発 |
| 4 | 超音波センサー構成をRaspberry Pi向けに移植 |

---

## 参考リンク

- [Romihi GitHub Profile](https://github.com/Romihi)
- [Romihi/donkeycar](https://github.com/Romihi/donkeycar)
- [Romihi/data_viewer](https://github.com/Romihi/data_viewer)
- [Romihi/segmentation_tool](https://github.com/Romihi/segmentation_tool)
- [Romihi/bno055-python-i2c](https://github.com/Romihi/bno055-python-i2c)
- [Romihi/RumiCar](https://github.com/Romihi/RumiCar)

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026年1月19日 | 初版作成 |
