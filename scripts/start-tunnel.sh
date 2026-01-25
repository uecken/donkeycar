#!/bin/bash
# Cloudflare Quick Tunnel 起動スクリプト
# 使用方法: ./start-tunnel.sh [ssh|jupyter|tensorboard|ui|all]

CLOUDFLARED="/home/kenji/.local/bin/cloudflared"

start_ssh_tunnel() {
    echo "========================================"
    echo "SSH Tunnel を起動しています..."
    echo "========================================"
    sudo service ssh start
    echo ""
    $CLOUDFLARED tunnel --url ssh://localhost:22 2>&1 | while read line; do
        echo "[SSH] $line"
    done
}

start_jupyter() {
    echo "========================================"
    echo "Jupyter Notebook を起動しています..."
    echo "========================================"
    source /home/kenji/miniconda3/etc/profile.d/conda.sh
    conda activate donkey
    cd /home/kenji/mycar
    jupyter notebook --no-browser --ip=0.0.0.0 --port=8888 --NotebookApp.token='' --NotebookApp.password='' 2>&1 | while read line; do
        echo "[Jupyter:8888] $line"
    done
}

start_tensorboard() {
    echo "========================================"
    echo "TensorBoard を起動しています..."
    echo "========================================"
    source /home/kenji/miniconda3/etc/profile.d/conda.sh
    conda activate donkey
    cd /home/kenji/mycar
    tensorboard --logdir=./models --host=0.0.0.0 --port=6006 2>&1 | while read line; do
        echo "[TensorBoard:6006] $line"
    done
}

start_jupyter_tunnel() {
    source /home/kenji/miniconda3/etc/profile.d/conda.sh
    conda activate donkey
    cd /home/kenji/mycar

    jupyter notebook --no-browser --ip=0.0.0.0 --port=8888 --NotebookApp.token='' --NotebookApp.password='' > /tmp/jupyter.log 2>&1 &
    sleep 5

    if curl -s http://localhost:8888 > /dev/null; then
        echo "[Jupyter] 起動成功 (port 8888)"
        $CLOUDFLARED tunnel --url http://localhost:8888 2>&1 | while read line; do
            echo "[Jupyter Tunnel] $line"
        done
    else
        echo "[Jupyter] ERROR: 起動失敗"
        cat /tmp/jupyter.log
    fi
}

start_tensorboard_tunnel() {
    source /home/kenji/miniconda3/etc/profile.d/conda.sh
    conda activate donkey
    cd /home/kenji/mycar

    tensorboard --logdir=./models --host=0.0.0.0 --port=6006 > /tmp/tensorboard.log 2>&1 &
    sleep 5

    if curl -s http://localhost:6006 > /dev/null; then
        echo "[TensorBoard] 起動成功 (port 6006)"
        $CLOUDFLARED tunnel --url http://localhost:6006 2>&1 | while read line; do
            echo "[TensorBoard Tunnel] $line"
        done
    else
        echo "[TensorBoard] ERROR: 起動失敗"
        cat /tmp/tensorboard.log
    fi
}

start_ssh_tunnel_bg() {
    sudo service ssh start
    $CLOUDFLARED tunnel --url ssh://localhost:22 > /tmp/ssh_tunnel.log 2>&1 &
    sleep 3
    SSH_URL=$(grep -o 'https://[^[:space:]]*\.trycloudflare\.com' /tmp/ssh_tunnel.log | head -1)
    echo "[SSH Tunnel] $SSH_URL"
}

start_all() {
    echo "========================================"
    echo "全サービスを起動しています..."
    echo "========================================"
    echo ""

    # conda環境を有効化
    source /home/kenji/miniconda3/etc/profile.d/conda.sh
    conda activate donkey
    cd /home/kenji/mycar

    # SSH
    echo "1. SSH サーバー起動中..."
    sudo service ssh start

    # Jupyter
    echo "2. Jupyter Notebook 起動中..."
    jupyter notebook --no-browser --ip=0.0.0.0 --port=8888 --NotebookApp.token='' --NotebookApp.password='' > /tmp/jupyter.log 2>&1 &
    JUPYTER_PID=$!

    # TensorBoard
    echo "3. TensorBoard 起動中..."
    tensorboard --logdir=./models --host=0.0.0.0 --port=6006 > /tmp/tensorboard.log 2>&1 &
    TB_PID=$!

    sleep 5

    echo ""
    echo "========================================"
    echo "ローカルサービス状態"
    echo "========================================"

    # 状態確認
    if curl -s http://localhost:8888 > /dev/null; then
        echo "✅ Jupyter Notebook: http://localhost:8888 (PID: $JUPYTER_PID)"
    else
        echo "❌ Jupyter Notebook: 起動失敗"
    fi

    if curl -s http://localhost:6006 > /dev/null; then
        echo "✅ TensorBoard: http://localhost:6006 (PID: $TB_PID)"
    else
        echo "❌ TensorBoard: 起動失敗"
    fi

    echo ""
    echo "========================================"
    echo "Cloudflare Tunnel を起動中..."
    echo "========================================"
    echo ""
    echo "※ 各トンネルのURLが表示されます"
    echo "※ 終了するには Ctrl+C"
    echo ""

    # SSHトンネル
    $CLOUDFLARED tunnel --url ssh://localhost:22 > /tmp/ssh_tunnel.log 2>&1 &
    SSH_TUNNEL_PID=$!

    # Jupyterトンネル
    $CLOUDFLARED tunnel --url http://localhost:8888 > /tmp/jupyter_tunnel.log 2>&1 &
    JUPYTER_TUNNEL_PID=$!

    # TensorBoardトンネル
    $CLOUDFLARED tunnel --url http://localhost:6006 > /tmp/tb_tunnel.log 2>&1 &
    TB_TUNNEL_PID=$!

    sleep 5

    echo "========================================"
    echo "外部アクセスURL"
    echo "========================================"

    SSH_URL=$(grep -o 'https://[^[:space:]]*\.trycloudflare\.com' /tmp/ssh_tunnel.log | head -1)
    JUPYTER_URL=$(grep -o 'https://[^[:space:]]*\.trycloudflare\.com' /tmp/jupyter_tunnel.log | head -1)
    TB_URL=$(grep -o 'https://[^[:space:]]*\.trycloudflare\.com' /tmp/tb_tunnel.log | head -1)

    echo ""
    echo "📡 SSH:         $SSH_URL"
    echo "📓 Jupyter:     $JUPYTER_URL"
    echo "📊 TensorBoard: $TB_URL"
    echo ""
    echo "========================================"
    echo ""
    echo "接続コマンド例（SSH）:"
    echo "ssh -o ProxyCommand=\"cloudflared access ssh --hostname $SSH_URL\" kenji@$SSH_URL"
    echo ""
    echo "終了するには Ctrl+C を押してください"
    echo ""

    # トラップでクリーンアップ
    trap "echo '終了中...'; kill $JUPYTER_PID $TB_PID $SSH_TUNNEL_PID $JUPYTER_TUNNEL_PID $TB_TUNNEL_PID 2>/dev/null; exit" INT TERM

    # ログを監視
    tail -f /tmp/ssh_tunnel.log /tmp/jupyter_tunnel.log /tmp/tb_tunnel.log 2>/dev/null
}

start_donkey_ui() {
    echo "========================================"
    echo "Donkey Car UI を起動しています..."
    echo "========================================"
    echo "※ これはローカルGUIアプリです（WSLg必要）"
    echo ""
    source /home/kenji/miniconda3/etc/profile.d/conda.sh
    conda activate donkey
    cd /home/kenji/mycar
    donkey ui
}

case "${1:-help}" in
    ssh)
        start_ssh_tunnel
        ;;
    jupyter)
        start_jupyter_tunnel
        ;;
    tensorboard)
        start_tensorboard_tunnel
        ;;
    ui)
        start_donkey_ui
        ;;
    all)
        start_all
        ;;
    *)
        echo "使用方法: $0 [ssh|jupyter|tensorboard|ui|all]"
        echo ""
        echo "  ssh        - SSHトンネル（データ転送用）"
        echo "  jupyter    - Jupyter Notebook（データ閲覧・学習実行）"
        echo "  tensorboard - TensorBoard（学習結果可視化）"
        echo "  ui         - Donkey Car UI（ローカルGUI）"
        echo "  all        - SSH + Jupyter + TensorBoard を同時起動"
        ;;
esac
