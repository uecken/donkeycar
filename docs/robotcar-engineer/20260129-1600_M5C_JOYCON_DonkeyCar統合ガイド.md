# M5C_JOYCON Donkey Car 統合ガイド

**作成日**: 2026年1月29日
**最終更新**: 2026年1月29日
**担当**: robotcar-engineer

---

## 1. 概要

### 1.1 目的

M5StickC（または XIAO ESP32）+ Grove JoyStick で構成される BLE Gamepad「M5C_JOYCON」を Donkey Car のコントローラーとして使用できるように統合する手順を説明します。

### 1.2 前提条件

| 項目 | 要件 |
|------|------|
| **Donkey Car** | バージョン 5.1 以上 |
| **Raspberry Pi** | Raspberry Pi 4（Bookworm 64-bit） |
| **M5C_JOYCON** | ファームウェア書き込み済み |
| **Python** | 3.11（Bookworm 標準） |

### 1.3 システム構成

```
┌─────────────────────┐       BLE        ┌─────────────────────┐
│    M5C_JOYCON       │◄────────────────►│   Raspberry Pi 4    │
│  ┌───────────────┐  │                  │  ┌───────────────┐  │
│  │ M5StickC/XIAO │  │                  │  │   Bluetooth   │  │
│  │  + JoyStick   │  │                  │  │   (BlueZ)     │  │
│  └───────────────┘  │                  │  └───────┬───────┘  │
└─────────────────────┘                  │          │          │
                                         │  ┌───────▼───────┐  │
                                         │  │ /dev/input/js0│  │
                                         │  │  (joystick)   │  │
                                         │  └───────┬───────┘  │
                                         │          │          │
                                         │  ┌───────▼───────┐  │
                                         │  │  Donkey Car   │  │
                                         │  │ (controller.py)│  │
                                         │  └───────────────┘  │
                                         └─────────────────────┘
```

---

## 2. Donkey Car コントローラーアーキテクチャ

### 2.1 クラス階層

```
Joystick (基底クラス)
    │
    ├── PS3Joystick
    ├── PS4Joystick
    ├── XboxOneJoystick
    ├── LogitechJoystick
    ├── JoystickCreator (カスタム用)
    └── MyJoystick (ユーザー定義)

JoystickController (基底クラス)
    │
    ├── PS3JoystickController
    ├── PS4JoystickController
    ├── XboxOneJoystickController
    ├── LogitechJoystickController
    └── MyJoystickController (ユーザー定義)
```

### 2.2 Joystick クラスの役割

`donkeycar/parts/controller.py` の `Joystick` クラスは以下を担当します：

1. **デバイス初期化**: `/dev/input/js0` を開く
2. **軸・ボタンマッピング**: カーネルから報告されるコードを名前に変換
3. **ポーリング**: イベントを読み取り、軸値（-1.0 〜 +1.0）とボタン状態を返す

```python
class Joystick(object):
    def __init__(self, dev_fn='/dev/input/js0'):
        self.axis_names = {}     # コード → 名前のマッピング
        self.button_names = {}   # コード → 名前のマッピング
        self.axis_states = {}    # 軸の現在値
        self.button_states = {}  # ボタンの現在値
```

### 2.3 JoystickController クラスの役割

`JoystickController` は `Joystick` をラップし、以下を担当します：

1. **トリガーマップ**: 軸・ボタンを関数にマッピング
2. **ステアリング・スロットル変換**: 軸値をスケーリング
3. **モード管理**: user / local_angle / local の切り替え
4. **録画制御**: スロットル連動自動録画

```python
class JoystickController(object):
    def init_trigger_maps(self):
        self.button_down_trigger_map = {
            'select': self.toggle_mode,
            'cross': self.emergency_stop,
            ...
        }
        self.axis_trigger_map = {
            'left_stick_horz': self.set_steering,
            'right_stick_vert': self.set_throttle,
        }
```

### 2.4 デバイス認識の仕組み

Linux カーネルは BLE Gamepad を `/dev/input/js0` として公開します：

```
[ペアリング]
    ↓
[BlueZ (Bluetooth Stack)]
    ↓
[hidp (HID over Bluetooth)]
    ↓
[joydev (/dev/input/js0)]
    ↓
[Donkey Car controller.py]
```

ジョイスティックイベントは 8 バイトの構造体で読み取られます：

```python
evbuf = self.jsdev.read(8)
tval, value, typev, number = struct.unpack('IhBB', evbuf)
# tval: タイムスタンプ
# value: 軸値 (-32767 〜 +32767) またはボタン状態 (0/1)
# typev: イベントタイプ (0x01=ボタン, 0x02=軸)
# number: 軸/ボタン番号
```

軸値は `-32767 〜 +32767` で報告され、`-1.0 〜 +1.0` に正規化されます：

```python
fvalue = value / 32767.0
```

---

## 3. M5C_JOYCON 仕様

### 3.1 HID Gamepad レポート

M5C_JOYCON は ESP32-BLE-Gamepad ライブラリを使用し、標準的な HID Gamepad として動作します。

| 項目 | 値 |
|------|-----|
| デバイス名 | "M5StickC JoyPad" または "XIAO JoyPad" |
| 軸数 | 2（X軸、Y軸） |
| ボタン数 | 1（BtnA または JoyStickボタン） |
| HID Usage | Generic Desktop / Game Pad |

### 3.2 軸の値範囲

```
         0                16383               32767
         │                  │                   │
         ▼                  ▼                   ▼
    ┌────┼──────────────────┼───────────────────┼────┐
    │左端│      中心(デッド)  │                 右端│
    └────┴──────────────────┴───────────────────┴────┘
              ◄── デッドゾーン ──►
```

| 項目 | 値 |
|------|-----|
| 最小値 | 0 |
| 中心値 | 16383 |
| 最大値 | 32767 |
| デッドゾーン | 15（8bit JoyStick）/ 1000（16bit JoyStick） |

**重要**: HID レポートは符号なし値（0〜32767）として送信されます。Raspberry Pi のジョイスティックドライバは、これを符号付き値（-32767〜+32767）に変換します。

### 3.3 ボタンマッピング

| M5C_JOYCON | HID Button |
|------------|------------|
| M5StickC BtnA | BUTTON_1 |
| JoyStick押下 | BUTTON_1（XIAO版） |

### 3.4 軸の方向

M5C_JOYCON の軸方向（ファームウェア側で調整済み）：

| 軸 | 方向 | 値 |
|----|------|-----|
| X軸 | 左 | 0 |
| X軸 | 中心 | 16383 |
| X軸 | 右 | 32767 |
| Y軸 | 上 | 0 |
| Y軸 | 中心 | 16383 |
| Y軸 | 下 | 32767 |

---

## 4. Raspberry Pi での BLE Gamepad 認識設定

### 4.1 Bluetooth 設定

`/etc/bluetooth/main.conf` を編集：

```ini
[General]
Class = 0x000100
ControllerMode = dual
FastConnectable = true
Privacy = device
JustWorksRepairing = always

[Policy]
AutoEnable=true
```

設定後、Bluetooth サービスを再起動：

```bash
sudo systemctl restart bluetooth
```

### 4.2 ペアリング手順

```bash
# bluetoothctl を起動
bluetoothctl

# スキャン開始
[bluetooth]# scan on

# M5StickC JoyPad が表示されるまで待機
# [NEW] Device XX:XX:XX:XX:XX:XX M5StickC JoyPad

# ペアリング
[bluetooth]# pair XX:XX:XX:XX:XX:XX

# 信頼設定（自動再接続用）
[bluetooth]# trust XX:XX:XX:XX:XX:XX

# 接続
[bluetooth]# connect XX:XX:XX:XX:XX:XX

# 終了
[bluetooth]# quit
```

### 4.3 接続確認

```bash
# joystick パッケージのインストール
sudo apt-get install joystick

# デバイス確認
ls -la /dev/input/js*

# ジョイスティックテスト
jstest /dev/input/js0
```

`jstest` 出力例：

```
Driver version is 2.1.0.
Joystick (M5StickC JoyPad) has 2 axes (X, Y)
and 1 buttons (BtnA).
Testing ... (interrupt to exit)
Axes:  0:     0  1:     0 Buttons:  0:off
```

### 4.4 ERTM 無効化（接続問題がある場合）

一部の BLE Gamepad で接続問題がある場合：

```bash
# /etc/modprobe.d/bluetooth.conf を作成
echo "options bluetooth disable_ertm=1" | sudo tee /etc/modprobe.d/bluetooth.conf

# 再起動
sudo reboot
```

---

## 5. 統合手順

### 5.1 方法1: 既存の xbox タイプを使用（推奨）

M5C_JOYCON は標準的な Gamepad として認識されるため、`xbox` コントローラータイプで動作する可能性があります。

#### myconfig.py 設定

```python
#JOYSTICK
USE_JOYSTICK_AS_DEFAULT = True
JOYSTICK_MAX_THROTTLE = 0.5
JOYSTICK_STEERING_SCALE = 1.0
AUTO_RECORD_ON_THROTTLE = True
CONTROLLER_TYPE = 'xbox'
JOYSTICK_DEADZONE = 0.05
JOYSTICK_THROTTLE_DIR = -1.0  # 方向が逆の場合は 1.0 に変更
JOYSTICK_DEVICE_FILE = "/dev/input/js0"
```

### 5.2 方法2: カスタムコントローラーを作成

軸・ボタンマッピングが合わない場合は、カスタムコントローラーを作成します。

#### Step 1: 軸・ボタンコードの調査

```bash
# Donkey Car の createjs コマンドを使用
cd ~/mycar
donkey createjs
```

または、`evtest` で直接確認：

```bash
sudo apt-get install evtest
sudo evtest /dev/input/event*
```

#### Step 2: カスタムコントローラーファイルの作成

`~/mycar/my_joystick.py`:

```python
from donkeycar.parts.controller import Joystick, JoystickController


class M5CJoycon(Joystick):
    """
    M5StickC JoyPad (M5C_JOYCON) のマッピング定義
    """
    def __init__(self, *args, **kwargs):
        super(M5CJoycon, self).__init__(*args, **kwargs)

        # 軸マッピング（実際のコードは createjs で確認すること）
        self.axis_names = {
            0x00: 'x_axis',      # X軸（ステアリング）
            0x01: 'y_axis',      # Y軸（スロットル）
        }

        # ボタンマッピング
        self.button_names = {
            0x130: 'btn_a',      # BUTTON_1
        }


class M5CJoyconController(JoystickController):
    """
    M5C_JOYCON 用コントローラー
    """
    def __init__(self, *args, **kwargs):
        super(M5CJoyconController, self).__init__(*args, **kwargs)

    def init_js(self):
        try:
            self.js = M5CJoycon(self.dev_fn)
            self.js.init()
        except FileNotFoundError:
            print(f"{self.dev_fn} not found.")
            self.js = None
        return self.js is not None

    def init_trigger_maps(self):
        """
        ボタン・軸のアクション割り当て
        """
        # ボタン押下時のアクション
        self.button_down_trigger_map = {
            'btn_a': self.toggle_mode,
        }

        # ボタン離した時のアクション
        self.button_up_trigger_map = {
        }

        # 軸のアクション
        self.axis_trigger_map = {
            'x_axis': self.set_steering,
            'y_axis': self.set_throttle,
        }
```

#### Step 3: manage.py の修正

`~/mycar/manage.py` に以下を追加：

```python
# ファイル先頭に追加
from my_joystick import M5CJoyconController

# get_js_controller 関数の呼び出し部分を修正
# または cfg.CONTROLLER_TYPE = 'custom' の場合の処理を追加
```

または、`donkeycar/parts/controller.py` の `get_js_controller` 関数を参考に、`manage.py` でカスタムコントローラーを直接インスタンス化：

```python
if cfg.CONTROLLER_TYPE == "custom":
    from my_joystick import M5CJoyconController
    ctr = M5CJoyconController(
        throttle_dir=cfg.JOYSTICK_THROTTLE_DIR,
        throttle_scale=cfg.JOYSTICK_MAX_THROTTLE,
        steering_scale=cfg.JOYSTICK_STEERING_SCALE,
        auto_record_on_throttle=cfg.AUTO_RECORD_ON_THROTTLE,
        dev_fn=cfg.JOYSTICK_DEVICE_FILE
    )
    ctr.set_deadzone(cfg.JOYSTICK_DEADZONE)
```

#### Step 4: myconfig.py 設定

```python
#JOYSTICK
USE_JOYSTICK_AS_DEFAULT = True
JOYSTICK_MAX_THROTTLE = 0.5
JOYSTICK_STEERING_SCALE = 1.0
AUTO_RECORD_ON_THROTTLE = True
CONTROLLER_TYPE = 'custom'
JOYSTICK_DEADZONE = 0.05
JOYSTICK_THROTTLE_DIR = -1.0
JOYSTICK_DEVICE_FILE = "/dev/input/js0"
```

---

## 6. myconfig.py 設定詳細

### 6.1 設定項目一覧

| 設定項目 | 説明 | 推奨値 |
|---------|------|-------|
| `USE_JOYSTICK_AS_DEFAULT` | 起動時にジョイスティックを使用 | `True` |
| `JOYSTICK_MAX_THROTTLE` | 最大スロットル（0.0〜1.0） | `0.5`（初期は低めに） |
| `JOYSTICK_STEERING_SCALE` | ステアリング感度 | `1.0` |
| `AUTO_RECORD_ON_THROTTLE` | スロットル連動録画 | `True` |
| `CONTROLLER_TYPE` | コントローラータイプ | `'xbox'` または `'custom'` |
| `JOYSTICK_DEADZONE` | デッドゾーン | `0.05` |
| `JOYSTICK_THROTTLE_DIR` | スロットル方向 | `-1.0` または `1.0` |
| `JOYSTICK_DEVICE_FILE` | デバイスファイル | `"/dev/input/js0"` |

### 6.2 設定例（推奨）

```python
#----- JOYSTICK -----
USE_JOYSTICK_AS_DEFAULT = True
JOYSTICK_MAX_THROTTLE = 0.5
JOYSTICK_STEERING_SCALE = 1.0
AUTO_RECORD_ON_THROTTLE = True
CONTROLLER_TYPE = 'xbox'  # または 'custom'
JOYSTICK_DEADZONE = 0.05
JOYSTICK_THROTTLE_DIR = -1.0
JOYSTICK_DEVICE_FILE = "/dev/input/js0"
```

---

## 7. トラブルシューティング

### 7.1 BLE 接続関連

| 症状 | 原因 | 対処法 |
|------|------|--------|
| デバイスが見つからない | M5C_JOYCON が起動していない | M5C_JOYCON を先に起動 |
| ペアリング失敗 | 他のデバイスとペアリング中 | M5C_JOYCON をリセット（電源オフ→オン） |
| 接続が不安定 | ERTM 問題 | ERTM を無効化（4.4節参照） |
| 再接続しない | trust 設定が未完了 | `bluetoothctl trust XX:XX:XX:XX:XX:XX` |

### 7.2 ジョイスティック関連

| 症状 | 原因 | 対処法 |
|------|------|--------|
| `/dev/input/js0` がない | ドライバが未ロード | `sudo modprobe joydev` |
| 軸が動かない | マッピングが間違っている | `jstest` で確認、カスタムマッピング作成 |
| 方向が逆 | 軸の極性が逆 | `JOYSTICK_THROTTLE_DIR` を反転 |
| 感度が高すぎる | スケールが大きい | `JOYSTICK_MAX_THROTTLE` を下げる |
| ドリフトする | デッドゾーン不足 | `JOYSTICK_DEADZONE` を大きくする |

### 7.3 Donkey Car 関連

| 症状 | 原因 | 対処法 |
|------|------|--------|
| コントローラーが認識されない | デバイスファイルが違う | `JOYSTICK_DEVICE_FILE` を確認 |
| エラー: FileNotFoundError | デバイスが存在しない | BLE 接続を確認 |
| 動作しない | CONTROLLER_TYPE が合わない | `'custom'` に変更し、カスタムマッピング作成 |

### 7.4 デバッグコマンド

```bash
# BLE 接続状態確認
bluetoothctl info XX:XX:XX:XX:XX:XX

# ジョイスティックデバイス一覧
ls -la /dev/input/js*

# イベントテスト（リアルタイム）
jstest /dev/input/js0

# 詳細なイベント確認
sudo evtest /dev/input/event*

# Donkey Car ログ確認
cd ~/mycar
python manage.py drive --js 2>&1 | tee drive.log
```

---

## 8. 動作確認チェックリスト

### 8.1 BLE 接続確認

- [ ] M5C_JOYCON の電源が入っている
- [ ] Raspberry Pi の Bluetooth が有効
- [ ] `bluetoothctl` でデバイスが表示される
- [ ] ペアリング完了
- [ ] trust 設定完了
- [ ] 接続成功（`bluetoothctl info` で Connected: yes）

### 8.2 ジョイスティック認識確認

- [ ] `/dev/input/js0` が存在する
- [ ] `jstest /dev/input/js0` で軸・ボタンが認識される
- [ ] X軸を動かすと値が変化する
- [ ] Y軸を動かすと値が変化する
- [ ] ボタンを押すと反応する

### 8.3 Donkey Car 動作確認

- [ ] `myconfig.py` の設定完了
- [ ] `python manage.py drive --js` で起動する
- [ ] コントローラー接続メッセージが表示される
- [ ] ステアリングが動作する
- [ ] スロットルが動作する
- [ ] モード切替が動作する

### 8.4 走行前最終確認

- [ ] 車両が安全な場所にある
- [ ] `JOYSTICK_MAX_THROTTLE` が低めに設定されている
- [ ] 緊急停止の操作を把握している
- [ ] バッテリー残量が十分

---

## 9. 参考資料

### 9.1 Donkey Car ドキュメント

- [Donkey Car Controllers](https://docs.donkeycar.com/parts/controllers/)
- [Creating a Custom Joystick](https://docs.donkeycar.com/parts/controllers/#creating-a-custom-joystick)

### 9.2 M5C_JOYCON 関連

- `picopico_racers/M5C_JOYCON/CLAUDE.md` - プロジェクト設計資料
- `picopico_racers/M5C_JOYCON/src/main.cpp` - ファームウェアソースコード

### 9.3 Bluetooth/ジョイスティック

- [Raspberry Pi Bluetooth Gamepad Setup](https://cocoa-research.works/2022/04/raspberry-pi-bluetooth-gamepad-setup/)
- [RetroPie Bluetooth Controller](https://retropie.org.uk/docs/Bluetooth-Controller/)
- [Linux Joystick API](https://www.kernel.org/doc/html/latest/input/joydev/joystick-api.html)

---

## 10. 更新履歴

| 日付 | 内容 |
|------|------|
| 2026年1月29日 | 初版作成 |
