# Cloudflare Tunnel 設定ガイド

**作成日**: 2026年1月22日
**目的**: 自宅のWSL2学習サーバーに外出先からSSHアクセスする

---

## 1. 概要

### Cloudflare Tunnelとは

自宅サーバーをインターネットに公開するためのサービスです。ポート開放やVPN不要で、安全にリモートアクセスできます。

### メリット

| 項目 | 内容 |
|------|------|
| **コスト** | 無料 |
| **帯域制限** | なし |
| **ポート開放** | 不要 |
| **固定IP** | 不要 |
| **セキュリティ** | Cloudflareが保護 |

### 構成図

```
[外出先PC/スマホ]
       │
       │ HTTPS (443)
       ↓
[Cloudflare Edge]
       │
       │ Tunnel (暗号化)
       ↓
[自宅ルーター] ← ポート開放不要
       │
       ↓
[WSL2 Ubuntu 22.04]
   └─ cloudflared (トンネルクライアント)
   └─ SSH Server (port 22)
```

---

## 2. 前提条件

| 項目 | 要件 |
|------|------|
| Cloudflareアカウント | 無料アカウントでOK |
| 独自ドメイン | 必要（Cloudflareで管理） |
| WSL2 | Ubuntu 22.04 |

### ドメインがない場合

1. 安いドメインを取得（.com約1,500円/年、.xyz約100円/年など）
2. Cloudflareにドメインを追加（ネームサーバー変更）
3. **または Quick Tunnel を使用**（下記参照）

---

## 3. Quick Tunnel（一時的なトンネル）- ドメイン不要

### 概要

**TryCloudflare（Quick Tunnel）** を使えば、アカウント登録もドメインも不要で一時的なトンネルを作成できます。

| 項目 | 内容 |
|------|------|
| アカウント | **不要** |
| ドメイン | **不要** |
| 設定ファイル | **不要** |
| URL | ランダム生成（`xxx.trycloudflare.com`） |
| 用途 | テスト・開発・一時的な共有 |

### 制限事項

| 項目 | 制限 |
|------|------|
| URL | 毎回ランダムに変わる |
| 同時リクエスト | 200リクエストまで |
| SLA | なし（テスト用途） |
| SSE | 非対応 |

### 使用方法

#### Step 1: cloudflaredインストール（初回のみ）

```bash
# WSL2 Ubuntu 22.04で実行
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

#### Step 2: HTTPサービスの一時公開

```bash
# 例: ローカルの8080ポートを公開
cloudflared tunnel --url http://localhost:8080
```

出力例：
```
2026-01-22T12:00:00Z INF +----------------------------+
2026-01-22T12:00:00Z INF |  Your quick tunnel URL is  |
2026-01-22T12:00:00Z INF |  https://random-words.trycloudflare.com  |
2026-01-22T12:00:00Z INF +----------------------------+
```

この URL にアクセスすると、ローカルサービスに接続できます。

#### Step 3: Donkey Car UIの一時公開例

```bash
# Donkey Car UIを起動（ポート8887）
cd ~/mycar
donkey ui &

# Quick Tunnelで公開
cloudflared tunnel --url http://localhost:8887
```

外出先のブラウザから `https://random-words.trycloudflare.com` でアクセス可能。

#### Step 4: Jupyter Notebookの一時公開例

```bash
# Jupyter起動
jupyter notebook --no-browser --port=8888 &

# Quick Tunnelで公開
cloudflared tunnel --url http://localhost:8888
```

### Quick TunnelでSSHを使う方法

Quick TunnelはHTTP向けですが、SSHも可能です（やや複雑）。

#### サーバー側（WSL2）

```bash
# SSHサーバー起動
sudo service ssh start

# Quick Tunnel起動（SSHをHTTPでラップ）
cloudflared tunnel --url ssh://localhost:22
```

出力されたURL（例: `https://random-words.trycloudflare.com`）をメモ。

#### クライアント側

```bash
# cloudflaredが必要
ssh -o ProxyCommand="cloudflared access ssh --hostname random-words.trycloudflare.com" kenji@random-words.trycloudflare.com
```

### Quick Tunnel vs 通常のTunnel

| 項目 | Quick Tunnel | 通常のTunnel |
|------|-------------|-------------|
| セットアップ | 1コマンド | 設定必要 |
| アカウント | 不要 | 必要 |
| ドメイン | 不要 | 必要 |
| URL | 毎回変わる | 固定 |
| 用途 | テスト・一時利用 | 本番運用 |
| 推奨 | 試してみる段階 | 継続利用 |

### 参考

- [TryCloudflare 公式](https://try.cloudflare.com/)
- [Quick Tunnels ドキュメント](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/do-more-with-tunnels/trycloudflare/)

---

## 4. 通常のTunnel設定（固定URL - 本番向け）

### 4.1 Cloudflare側の設定

### Step 1: Cloudflareアカウント作成

1. [Cloudflare](https://dash.cloudflare.com/sign-up) にアクセス
2. メールアドレスでアカウント作成

### Step 2: ドメイン追加

1. ダッシュボードで「Add a Site」
2. ドメイン名を入力
3. Freeプランを選択
4. 表示されたネームサーバーをドメインレジストラで設定

### Step 3: Zero Trust ダッシュボードへ移動

1. 左メニュー「Zero Trust」をクリック
2. または [dash.teams.cloudflare.com](https://dash.teams.cloudflare.com/) にアクセス

---

### 4.2 WSL2側の設定

### Step 1: cloudflaredインストール

```bash
# WSL2 Ubuntu 22.04で実行
# cloudflaredダウンロード
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared

# 実行権限付与・移動
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# バージョン確認
cloudflared --version
```

### Step 2: Cloudflareにログイン

```bash
cloudflared tunnel login
```

ブラウザが開くので：
1. Cloudflareにログイン
2. 使用するドメインを選択
3. 認証完了

認証情報が `~/.cloudflared/cert.pem` に保存されます。

### Step 3: トンネル作成

```bash
# トンネル作成（名前は任意）
cloudflared tunnel create donkey-server

# 作成確認
cloudflared tunnel list
```

出力例：
```
ID                                   NAME           CREATED
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx donkey-server  2026-01-22T12:00:00Z
```

**TUNNEL_ID**（xxxxxxxx-xxxx-...）をメモしておく。

### Step 4: 設定ファイル作成

```bash
# 設定ディレクトリ確認
ls ~/.cloudflared/

# 設定ファイル作成
nano ~/.cloudflared/config.yml
```

以下の内容を記述（TUNNEL_IDとドメインを置き換え）：

```yaml
tunnel: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
credentials-file: /home/kenji/.cloudflared/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.json

ingress:
  # SSH接続用
  - hostname: ssh.example.com
    service: ssh://localhost:22

  # Donkey Car UI用（オプション）
  - hostname: donkey.example.com
    service: http://localhost:8887

  # Jupyter Notebook用（オプション）
  - hostname: jupyter.example.com
    service: http://localhost:8888

  # デフォルト（必須）
  - service: http_status:404
```

### Step 5: DNSレコード設定

```bash
# SSHホスト用
cloudflared tunnel route dns donkey-server ssh.example.com

# Donkey UI用（オプション）
cloudflared tunnel route dns donkey-server donkey.example.com
```

### Step 6: SSHサーバー確認・起動

```bash
# SSHサーバー状態確認
sudo service ssh status

# 起動していない場合
sudo service ssh start

# 自動起動設定
sudo systemctl enable ssh
```

### Step 7: トンネル起動

```bash
# フォアグラウンドで起動（テスト用）
cloudflared tunnel run donkey-server

# 正常に動作したらCtrl+Cで停止
```

---

## 5. サービス化（自動起動 - 通常Tunnel用）

### systemdサービス作成

```bash
# サービスファイル作成
sudo nano /etc/systemd/system/cloudflared.service
```

以下の内容を記述：

```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=kenji
ExecStart=/usr/local/bin/cloudflared tunnel run donkey-server
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# サービス有効化・起動
sudo systemctl daemon-reload
sudo systemctl enable cloudflared
sudo systemctl start cloudflared

# 状態確認
sudo systemctl status cloudflared
```

---

## 6. クライアント側の設定（外出先PC）

### 方法A: cloudflared経由でSSH（推奨）

#### クライアントにcloudflaredインストール

**Windows:**
```powershell
# wingetでインストール
winget install Cloudflare.cloudflared

# または手動ダウンロード
# https://github.com/cloudflare/cloudflared/releases
```

**Mac:**
```bash
brew install cloudflared
```

**Linux:**
```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

#### SSH設定（~/.ssh/config）

```
Host donkey-server
    HostName ssh.example.com
    User kenji
    ProxyCommand cloudflared access ssh --hostname %h
```

#### 接続

```bash
ssh donkey-server
```

### 方法B: ブラウザ経由でSSH

1. Cloudflare Zero Trust ダッシュボードにアクセス
2. Access → Applications → Add Application
3. Self-hosted を選択
4. Application domain: `ssh.example.com`
5. Policiesでアクセス制御を設定

ブラウザで `https://ssh.example.com` にアクセスするとWebベースのSSHターミナルが使用可能。

---

## 7. セキュリティ設定（推奨）

### Cloudflare Access（認証追加）

1. Zero Trust ダッシュボード → Access → Applications
2. 「Add an application」→ Self-hosted
3. Application name: `Donkey SSH`
4. Session Duration: 24 hours
5. Application domain: `ssh.example.com`
6. Policy作成：
   - Policy name: `Allow me`
   - Action: Allow
   - Include: Emails ending in `@gmail.com`（自分のメール）

これにより、SSHアクセス前にCloudflareの認証が必要になります。

---

## 8. 動作確認

### サーバー側（WSL2）

```bash
# トンネル状態確認
cloudflared tunnel info donkey-server

# ログ確認
sudo journalctl -u cloudflared -f
```

### クライアント側

```bash
# SSH接続テスト
ssh donkey-server

# 接続後、GPU確認
source ~/miniconda3/etc/profile.d/conda.sh
conda activate donkey
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

---

## 9. 使用例：外出先から学習実行

```bash
# 1. SSH接続
ssh donkey-server

# 2. Conda環境有効化
source ~/miniconda3/etc/profile.d/conda.sh
conda activate donkey

# 3. プロジェクトディレクトリへ
cd ~/mycar

# 4. 学習実行（バックグラウンド）
nohup donkey train --tub ./data/tub_* --model ./models/mypilot.h5 > train.log 2>&1 &

# 5. 進捗確認
tail -f train.log

# 6. 切断してもOK（nohupで継続）
exit
```

---

## 10. トラブルシューティング

| 問題 | 解決策 |
|------|--------|
| トンネルが接続できない | `cloudflared tunnel run`でエラー確認 |
| SSHがタイムアウト | WSL2内で`sudo service ssh start`確認 |
| DNSが解決できない | `cloudflared tunnel route dns`の再実行 |
| 認証エラー | `cloudflared tunnel login`で再認証 |
| WSL2が停止する | Windows側で`wsl --list --running`確認 |

### WSL2を常時起動する方法

Windowsタスクスケジューラで起動時に実行：
```powershell
wsl -d Ubuntu-22.04 -- bash -c "sudo service ssh start && cloudflared tunnel run donkey-server"
```

---

## 11. 参考資料

- [Cloudflare Tunnel 公式ドキュメント](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)
- [Cloudflare Zero Trust](https://developers.cloudflare.com/cloudflare-one/)
- [cloudflared GitHub](https://github.com/cloudflare/cloudflared)

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026年1月22日 | 初版作成 |
