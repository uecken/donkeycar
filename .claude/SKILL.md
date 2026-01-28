# Claude Code 動作設定

## 基本ルール
- 資料はタイムスタンプ付き（YYYYMMDD-HHMM_タイトル.md）で日本語作成
- 同じコマンドは自動的に許可
- ファイル命名規則: `yyyymmdd-hhmm_日本語タイトル.md`
  - 例: `20260122-1430_学習用PC要件.md`

## Git ブランチ運用

| リポジトリ | 作業ブランチ | リモート |
|-----------|-------------|---------|
| donkeycar | `main` | uecken/donkeycar |
| picopico_racers | `feature/add-m5c-joycon` | fumipi/picopico_racers |

```bash
# picopico_racersでの作業時
cd picopico_racers
git checkout feature/add-m5c-joycon
# ... 作業 ...
git push origin feature/add-m5c-joycon
```

## エージェント構成

| エージェント | 役割 | 定義ファイル |
|-------------|------|-------------|
| system-architect | 設計・技術決定 | `.claude/agents/system-architect.md` |
| robotcar-engineer | HW・車両制御 | `.claude/agents/robotcar-engineer.md` |
| ml-engineer | モデル開発 | `.claude/agents/ml-engineer.md` |
| data-engineer | データ管理 | `.claude/agents/data-engineer.md` |
| devops-engineer | 環境・デプロイ | `.claude/agents/devops-engineer.md` |

## 開発環境

### WSL2 学習環境
| 項目 | 値 |
|------|-----|
| ディストリビューション | Ubuntu-22.04 |
| ユーザー名 | kenji |
| Miniconda | `/home/kenji/miniconda3/` |
| Conda環境名 | `donkey` |
| Python | 3.11 |
| Donkey Car | 5.2.0 |
| TensorFlow | 2.15.1 (GPU対応) |
| GPU | GTX 1660 Ti |
| プロジェクトパス | `/home/kenji/mycar/` |

### WSL2コマンド実行方法
```bash
# 直接実行
wsl -d Ubuntu-22.04 -- bash -c "..."

# conda環境使用時
wsl -d Ubuntu-22.04 -- bash -c "source /home/kenji/miniconda3/etc/profile.d/conda.sh && conda activate donkey && <コマンド>"
```

### パス対応表
| Windows | WSL2 |
|---------|------|
| `C:\Users\thefu\Documents\donkeycar\` | `/mnt/c/Users/thefu/Documents/donkeycar/` |
| WSL2ホーム | `/home/kenji/` |
| Windowsからアクセス | `\\wsl$\Ubuntu-22.04\home\kenji\` |

### Raspberry Pi
| 項目 | 値 |
|------|-----|
| IP | 192.168.50.3 |
| ユーザー | koito |
| SSH | `ssh koito@192.168.50.3` |

## ユーティリティスクリプト

| スクリプト | パス | 用途 |
|-----------|------|------|
| start-tunnel.sh | `/home/kenji/scripts/` | Cloudflare Quick Tunnel起動 |
| import-data.sh | `/home/kenji/scripts/` | 学習データインポート |

### Cloudflare Tunnel（外部アクセス）
```bash
# SSHトンネル起動
/home/kenji/scripts/start-tunnel.sh ssh

# Donkey Car UIトンネル起動
/home/kenji/scripts/start-tunnel.sh web
```

### 学習データインポート
```bash
# Raspberry Piからインポート
/home/kenji/scripts/import-data.sh pi@192.168.1.100:~/mycar/data/tub_*

# Windows側からインポート
/home/kenji/scripts/import-data.sh /mnt/c/Users/thefu/Downloads/tub_data
```
