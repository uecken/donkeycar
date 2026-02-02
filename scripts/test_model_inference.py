#!/usr/bin/env python3
"""
モデル推論テストスクリプト
==========================
作成: robotcar-engineer + ml-engineer
目的: TFLiteモデルの推論出力を直接確認する

使用方法:
    # Raspberry Pi で実行
    cd ~/mycar
    python ~/donkeycar/scripts/test_model_inference.py --model models/mypilot.tflite

    # ダミー画像でテスト
    python ~/donkeycar/scripts/test_model_inference.py --model models/mypilot.tflite --dummy

    # 実際のカメラ画像でテスト
    python ~/donkeycar/scripts/test_model_inference.py --model models/mypilot.tflite --camera

    # 連続推論テスト（10回）
    python ~/donkeycar/scripts/test_model_inference.py --model models/mypilot.tflite --camera --count 10
"""

import argparse
import time
import sys
import os

import numpy as np

# TFLite インタープリタのインポート
try:
    import tflite_runtime.interpreter as tflite
    TFLITE_RUNTIME = True
except ImportError:
    try:
        import tensorflow.lite as tflite
        TFLITE_RUNTIME = False
    except ImportError:
        print("Error: tflite_runtime または tensorflow が必要です")
        print("  pip install tflite-runtime")
        print("  または")
        print("  pip install tensorflow")
        sys.exit(1)


def load_model(model_path):
    """モデルを読み込む"""
    if not os.path.exists(model_path):
        print(f"Error: モデルファイルが見つかりません: {model_path}")
        sys.exit(1)

    print(f"モデル読み込み中: {model_path}")
    start_time = time.time()

    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    load_time = time.time() - start_time
    print(f"モデル読み込み完了: {load_time:.2f}秒")

    return interpreter


def get_model_info(interpreter):
    """モデルの入出力情報を取得"""
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print("\n" + "=" * 50)
    print("モデル情報")
    print("=" * 50)

    print(f"\n【入力テンソル】")
    for i, inp in enumerate(input_details):
        print(f"  入力{i}:")
        print(f"    名前: {inp['name']}")
        print(f"    形状: {inp['shape']}")
        print(f"    dtype: {inp['dtype']}")

    print(f"\n【出力テンソル】")
    for i, out in enumerate(output_details):
        print(f"  出力{i}:")
        print(f"    名前: {out['name']}")
        print(f"    形状: {out['shape']}")
        print(f"    dtype: {out['dtype']}")

    return input_details, output_details


def create_dummy_image(input_shape):
    """ダミー画像を生成"""
    # input_shape: [1, height, width, channels]
    return np.random.rand(*input_shape).astype(np.float32)


def capture_camera_image(input_shape):
    """カメラから画像をキャプチャ"""
    try:
        from picamera2 import Picamera2
        import cv2
    except ImportError:
        print("Error: picamera2 または opencv が必要です")
        print("  sudo apt install python3-picamera2 python3-opencv")
        return None

    # 期待されるサイズ
    height, width = input_shape[1], input_shape[2]

    print(f"カメラ初期化中... (期待サイズ: {width}x{height})")

    try:
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(
            main={"size": (width, height), "format": "RGB888"}
        )
        picam2.configure(config)
        picam2.start()
        time.sleep(0.5)  # カメラ安定化

        # 画像キャプチャ
        image = picam2.capture_array()
        picam2.stop()
        picam2.close()

        # 正規化 (0-255 -> 0-1)
        image = image.astype(np.float32) / 255.0

        # バッチ次元追加
        image = np.expand_dims(image, axis=0)

        print(f"カメラ画像取得: shape={image.shape}, dtype={image.dtype}")
        return image

    except Exception as e:
        print(f"カメラエラー: {e}")
        return None


def run_inference(interpreter, input_data, input_details, output_details):
    """推論を実行"""
    # 入力データをセット
    interpreter.set_tensor(input_details[0]['index'], input_data)

    # 推論実行
    start_time = time.time()
    interpreter.invoke()
    inference_time = (time.time() - start_time) * 1000  # ms

    # 出力を取得
    outputs = []
    for out in output_details:
        result = interpreter.get_tensor(out['index'])
        outputs.append(result)

    return outputs, inference_time


def interpret_outputs(outputs):
    """出力値を解釈"""
    print("\n【推論結果】")

    if len(outputs) >= 2:
        # Linear モデル: angle, throttle
        angle = outputs[0].flatten()[0]
        throttle = outputs[1].flatten()[0]

        print(f"  angle:    {angle:+.4f}  (範囲: -1.0 〜 +1.0)")
        print(f"  throttle: {throttle:+.4f}  (範囲: -1.0 〜 +1.0)")

        # PWM値への変換（HBX 2192設定）
        print("\n【PWM変換（HBX 2192）】")

        # ステアリングPWM（仮定: LEFT=280, CENTER=307, RIGHT=330）
        STEERING_LEFT = 280
        STEERING_CENTER = 307
        STEERING_RIGHT = 330

        if angle >= 0:
            steering_pwm = int(angle * (STEERING_RIGHT - STEERING_CENTER) + STEERING_CENTER)
        else:
            steering_pwm = int((angle + 1) * (STEERING_CENTER - STEERING_LEFT) + STEERING_LEFT)

        # スロットルPWM
        THROTTLE_FORWARD = 330
        THROTTLE_STOPPED = 307
        THROTTLE_REVERSE = 281

        if throttle >= 0:
            throttle_pwm = int(throttle * (THROTTLE_FORWARD - THROTTLE_STOPPED) + THROTTLE_STOPPED)
        else:
            throttle_pwm = int((throttle + 1) * (THROTTLE_STOPPED - THROTTLE_REVERSE) + THROTTLE_REVERSE)

        # パルス幅計算
        steering_us = steering_pwm / 4096 * 20000
        throttle_us = throttle_pwm / 4096 * 20000

        print(f"  ステアリング: PWM={steering_pwm}, パルス幅={steering_us:.0f}μs")
        print(f"  スロットル:   PWM={throttle_pwm}, パルス幅={throttle_us:.0f}μs")

        # 動作の解釈
        print("\n【動作解釈】")
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

        print(f"  ステアリング: {steer_dir}")
        print(f"  スロットル:   {throttle_dir}")

        return angle, throttle

    elif len(outputs) == 1:
        # Categorical モデルの場合
        output = outputs[0].flatten()
        print(f"  出力: {output}")
        print(f"  argmax: {np.argmax(output)}")
        return output, None

    return None, None


def main():
    parser = argparse.ArgumentParser(description="TFLiteモデル推論テスト")
    parser.add_argument("--model", required=True, help="モデルファイルのパス (.tflite)")
    parser.add_argument("--dummy", action="store_true", help="ダミー画像で推論")
    parser.add_argument("--camera", action="store_true", help="カメラ画像で推論")
    parser.add_argument("--count", type=int, default=1, help="推論回数（--camera時）")
    parser.add_argument("--interval", type=float, default=0.5, help="推論間隔（秒）")
    args = parser.parse_args()

    print("=" * 50)
    print("TFLite モデル推論テスト")
    print("=" * 50)
    print(f"TFLite Runtime: {'tflite_runtime' if TFLITE_RUNTIME else 'tensorflow.lite'}")

    # モデル読み込み
    interpreter = load_model(args.model)
    input_details, output_details = get_model_info(interpreter)

    input_shape = input_details[0]['shape']

    # 推論テスト
    if args.camera:
        print("\n" + "=" * 50)
        print(f"カメラ推論テスト（{args.count}回）")
        print("=" * 50)

        inference_times = []

        for i in range(args.count):
            print(f"\n--- 推論 {i+1}/{args.count} ---")

            image = capture_camera_image(input_shape)
            if image is None:
                print("カメラ画像取得失敗。ダミー画像で代替します。")
                image = create_dummy_image(input_shape)

            outputs, inference_time = run_inference(
                interpreter, image, input_details, output_details
            )
            inference_times.append(inference_time)

            print(f"推論時間: {inference_time:.1f}ms")
            interpret_outputs(outputs)

            if i < args.count - 1:
                time.sleep(args.interval)

        # 統計
        print("\n" + "=" * 50)
        print("推論時間統計")
        print("=" * 50)
        print(f"  平均: {np.mean(inference_times):.1f}ms")
        print(f"  最小: {np.min(inference_times):.1f}ms")
        print(f"  最大: {np.max(inference_times):.1f}ms")
        print(f"  推定FPS: {1000 / np.mean(inference_times):.1f}")

    else:
        # ダミー画像でテスト
        print("\n" + "=" * 50)
        print("ダミー画像推論テスト")
        print("=" * 50)

        image = create_dummy_image(input_shape)
        print(f"ダミー画像生成: shape={image.shape}, dtype={image.dtype}")

        outputs, inference_time = run_inference(
            interpreter, image, input_details, output_details
        )

        print(f"推論時間: {inference_time:.1f}ms")
        interpret_outputs(outputs)

    print("\n" + "=" * 50)
    print("テスト完了")
    print("=" * 50)


if __name__ == "__main__":
    main()
