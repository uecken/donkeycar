#!/usr/bin/env python3
"""
パイロット値リアルタイム監視スクリプト
======================================
作成: robotcar-engineer + ml-engineer
目的: 自動運転中のpilot/angle, pilot/throttleをリアルタイム監視

使用方法:
    # Raspberry Pi で別ターミナルから実行
    # （Donkey Car 起動中に別ウィンドウで）
    python ~/donkeycar/scripts/monitor_pilot_values.py

    # カスタムポート
    python ~/donkeycar/scripts/monitor_pilot_values.py --port 8887

    # CSVログ出力
    python ~/donkeycar/scripts/monitor_pilot_values.py --log pilot_log.csv

注意:
    Donkey Car の WebUI が起動している状態で実行すること。
    WebSocket経由でテレメトリデータを取得する。
"""

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime

try:
    import websockets
except ImportError:
    print("Error: websockets が必要です")
    print("  pip install websockets")
    sys.exit(1)


class PilotMonitor:
    def __init__(self, host, port, log_file=None):
        self.host = host
        self.port = port
        self.log_file = log_file
        self.ws_url = f"ws://{host}:{port}/wsDrive"
        self.running = True
        self.csv_file = None
        self.sample_count = 0
        self.start_time = None

    def format_bar(self, value, width=20):
        """値を視覚的なバーで表示"""
        # value: -1.0 〜 +1.0
        center = width // 2
        filled = int(abs(value) * center)

        bar = [' '] * width
        bar[center] = '|'

        if value >= 0:
            for i in range(filled):
                if center + 1 + i < width:
                    bar[center + 1 + i] = '█'
        else:
            for i in range(filled):
                if center - 1 - i >= 0:
                    bar[center - 1 - i] = '█'

        return '[' + ''.join(bar) + ']'

    def print_header(self):
        """ヘッダーを表示"""
        print("\n" + "=" * 70)
        print("Donkey Car パイロット値モニター")
        print("=" * 70)
        print(f"接続先: {self.ws_url}")
        print(f"ログファイル: {self.log_file or 'なし'}")
        print("-" * 70)
        print("Ctrl+C で終了")
        print("=" * 70)
        print()

    def print_values(self, data):
        """値を表示"""
        # テレメトリデータを解析
        tele = data.get('tele', {})
        pilot = tele.get('pilot', {})
        user = tele.get('user', {})

        angle = pilot.get('angle', 0)
        throttle = pilot.get('throttle', 0)
        user_angle = user.get('angle', 0)
        user_throttle = user.get('throttle', 0)

        drive_mode = data.get('driveMode', 'unknown')
        recording = data.get('recording', False)

        # 画面クリア（ANSI エスケープ）
        print('\033[2J\033[H', end='')

        self.print_header()

        # モード表示
        mode_display = {
            'user': 'User (手動)',
            'local': 'Full Auto (完全自動)',
            'local_angle': 'Auto Steer (ステアリングのみ自動)'
        }
        print(f"モード: {mode_display.get(drive_mode, drive_mode)}")
        print(f"録画: {'● REC' if recording else '○ OFF'}")
        print()

        # パイロット値（モデル出力）
        print("【パイロット値（モデル出力）】")
        print(f"  angle:    {angle:+.4f}  {self.format_bar(angle)}")
        print(f"  throttle: {throttle:+.4f}  {self.format_bar(throttle)}")
        print()

        # ユーザー入力値
        print("【ユーザー入力値】")
        print(f"  angle:    {user_angle:+.4f}  {self.format_bar(user_angle)}")
        print(f"  throttle: {user_throttle:+.4f}  {self.format_bar(user_throttle)}")
        print()

        # PWM変換値（HBX 2192設定）
        THROTTLE_FORWARD = 330
        THROTTLE_STOPPED = 307
        THROTTLE_REVERSE = 281

        if throttle >= 0:
            throttle_pwm = int(throttle * (THROTTLE_FORWARD - THROTTLE_STOPPED) + THROTTLE_STOPPED)
        else:
            throttle_pwm = int((throttle + 1) * (THROTTLE_STOPPED - THROTTLE_REVERSE) + THROTTLE_REVERSE)

        throttle_us = throttle_pwm / 4096 * 20000

        print("【PWM変換（HBX 2192）】")
        print(f"  スロットル: PWM={throttle_pwm}, パルス幅={throttle_us:.0f}μs")
        print()

        # 動作解釈
        if angle < -0.3:
            steer_dir = "← 左旋回"
        elif angle > 0.3:
            steer_dir = "→ 右旋回"
        else:
            steer_dir = "↑ 直進"

        if throttle > 0.1:
            throttle_dir = "▲ 前進"
        elif throttle < -0.1:
            throttle_dir = "▼ 後退"
        else:
            throttle_dir = "■ 停止"

        print("【動作解釈】")
        print(f"  ステアリング: {steer_dir}")
        print(f"  スロットル:   {throttle_dir}")
        print()

        # 統計
        self.sample_count += 1
        elapsed = time.time() - self.start_time if self.start_time else 0
        fps = self.sample_count / elapsed if elapsed > 0 else 0

        print("-" * 70)
        print(f"サンプル数: {self.sample_count}  経過時間: {elapsed:.1f}秒  受信レート: {fps:.1f}Hz")

        # CSVログ
        if self.csv_file:
            timestamp = datetime.now().isoformat()
            self.csv_file.write(
                f"{timestamp},{drive_mode},{recording},"
                f"{angle:.6f},{throttle:.6f},"
                f"{user_angle:.6f},{user_throttle:.6f}\n"
            )
            self.csv_file.flush()

    async def connect_and_monitor(self):
        """WebSocketに接続して監視"""
        print(f"接続中: {self.ws_url}")

        try:
            async with websockets.connect(self.ws_url) as ws:
                print("接続成功!")
                self.start_time = time.time()

                # CSVファイル初期化
                if self.log_file:
                    self.csv_file = open(self.log_file, 'w')
                    self.csv_file.write(
                        "timestamp,drive_mode,recording,"
                        "pilot_angle,pilot_throttle,"
                        "user_angle,user_throttle\n"
                    )

                while self.running:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(message)
                        self.print_values(data)
                    except asyncio.TimeoutError:
                        continue
                    except json.JSONDecodeError:
                        continue

        except ConnectionRefusedError:
            print(f"\nError: 接続拒否されました")
            print(f"  Donkey Car が起動しているか確認してください")
            print(f"  python manage.py drive --model ... --type ...")
        except Exception as e:
            print(f"\nError: {e}")
        finally:
            if self.csv_file:
                self.csv_file.close()
                print(f"\nログ保存: {self.log_file}")

    def run(self):
        """監視を開始"""
        try:
            asyncio.run(self.connect_and_monitor())
        except KeyboardInterrupt:
            print("\n\n監視終了")
            self.running = False


def main():
    parser = argparse.ArgumentParser(description="Donkey Car パイロット値モニター")
    parser.add_argument("--host", default="localhost", help="Donkey Car のホスト")
    parser.add_argument("--port", type=int, default=8887, help="WebUI のポート")
    parser.add_argument("--log", help="CSVログファイルのパス")
    args = parser.parse_args()

    monitor = PilotMonitor(args.host, args.port, args.log)
    monitor.run()


if __name__ == "__main__":
    main()
