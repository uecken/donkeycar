# 自動運転 Level 4 プロジェクト - Donkey Car ベース

https://github.com/uecken/donkeycar/

Donkey Carフレームワークをベースに、自動運転Level 4の実現を目指すプロジェクトです。

## プロジェクト構成

```
donkeycar/
├── CLAUDE.md                    # プロジェクト概要・アーキテクチャ
├── README.md                    # このファイル
│
├── .claude/                     # Claude Code設定
│   ├── SKILL.md                 # 動作ルール・環境設定
│   ├── settings.local.json      # ローカル設定
│   └── agents/                  # エージェント定義
│       ├── system-architect.md
│       ├── robotcar-engineer.md
│       ├── ml-engineer.md
│       ├── data-engineer.md
│       └── devops-engineer.md
│
├── docs/                        # ドキュメント（エージェント別）
│   ├── system-architect/        # 設計・技術調査
│   ├── robotcar-engineer/       # ハードウェア
│   ├── ml-engineer/             # 機械学習
│   ├── data-engineer/           # データ管理
│   └── devops-engineer/         # 環境構築
│
├── picopico_racers/             # サブモジュール: Team 10 ミニカーチャレンジ
│   └── M5C_JOYCON/              # サブモジュール: BLEコントローラ
│
├── donkeycar/                   # Donkey Car本体（オリジナル）
└── refs/                        # 参照用外部リポジトリ
```

## クイックスタート

### リポジトリのクローン

```bash
# サブモジュールを含めてクローン
git clone --recurse-submodules https://github.com/uecken/donkeycar.git
cd donkeycar
```

### エージェント構成

5名のチームで以下のエージェントロールを分担：

| エージェント | 役割 |
|-------------|------|
| **system-architect** | 全体設計・技術決定・統合 |
| **robotcar-engineer** | HWキャリブレーション・センサー統合 |
| **ml-engineer** | モデル開発・学習・最適化 |
| **data-engineer** | データ収集・前処理・品質管理 |
| **devops-engineer** | 環境構築・デプロイ・運用 |

## Git ブランチ運用

| リポジトリ | 作業ブランチ | リモート |
|-----------|-------------|---------|
| donkeycar | `main` | uecken/donkeycar |
| picopico_racers | `feature/add-m5c-joycon` | fumipi/picopico_racers |

## 関連ドキュメント

| ドキュメント | 内容 |
|-------------|------|
| [CLAUDE.md](CLAUDE.md) | プロジェクト概要、ロードマップ、ハードウェア構成 |
| [.claude/SKILL.md](.claude/SKILL.md) | Claude Code動作設定、環境情報 |
| [docs/](docs/) | エージェント別技術ドキュメント |

## サブモジュール

### picopico_racers
Team 10の自動運転ミニカーチャレンジプロジェクト。

- リポジトリ: https://github.com/fumipi/picopico_racers
- 作業ブランチ: `feature/add-m5c-joycon`

### M5C_JOYCON
M5StickC/XIAO ESP32 + Grove JoyStickを使用したBLEゲームパッドコントローラ。

- リポジトリ: https://github.com/uecken/M5C_JOYCON
- 状態: Raspberry PiでBLE認識済、Donkey Car統合は未完了

## 開発環境

### 実車環境
- Raspberry Pi 4
- SSH: `ssh koito@192.168.50.3`

### 学習環境
- WSL2 Ubuntu 22.04
- GPU: GTX 1660 Ti
- TensorFlow 2.15.1 (GPU対応)

詳細は [.claude/SKILL.md](.claude/SKILL.md) を参照。

## 参考リンク

- [Donkey Car 公式ドキュメント](https://docs.donkeycar.com/)
- [Donkey Car GitHub (オリジナル)](https://github.com/autorope/donkeycar)

## ライセンス

MIT License (Donkey Car準拠)
