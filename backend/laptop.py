#!/usr/bin/env python3
"""
Send laptop camera frames to FastAPI /predict/bytes.

Usage:
  python send_cam_to_api.py --url http://127.0.0.1:8000/predict/bytes --cam 0 --interval 2 --preview 0
"""

import argparse
import time
import sys
import json

import cv2
import requests

def main():
    parser = argparse.ArgumentParser(description="Send webcam frames to FastAPI /predict/bytes")
    parser.add_argument("--url", type=str, default="http://127.0.0.1:8000/predict/bytes",
                        help="FastAPI endpoint (POST) for raw JPEG bytes")
    parser.add_argument("--cam", type=int, default=0, help="Camera index (0 = default webcam)")
    parser.add_argument("--interval", type=float, default=2.0,
                        help="Seconds between sends (e.g., 0.5 for ~2 fps, 2.0 for one every 2s)")
    parser.add_argument("--quality", type=int, default=90, help="JPEG quality (0–100)")
    parser.add_argument("--preview", type=int, default=0, help="Show a preview window (1=yes, 0=no)")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.cam)
    if not cap.isOpened():
        print(f"[ERROR] Could not open camera index {args.cam}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Sending frames to: {args.url}")
    print(f"[INFO] Press Ctrl+C to stop.")

    headers = {"Content-Type": "image/jpeg"}
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), int(args.quality)]

    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                print("[WARN] Failed to read frame from camera; retrying...")
                time.sleep(args.interval)
                continue

            # Optional preview
            if args.preview:
                cv2.imshow("Preview - Press Q to quit", frame)
                if (cv2.waitKey(1) & 0xFF) in (ord('q'), ord('Q')):
                    break

            # JPEG encode
            ok, buf = cv2.imencode(".jpg", frame, encode_params)
            if not ok:
                print("[WARN] JPEG encode failed; skipping frame.")
                time.sleep(args.interval)
                continue

            # Send
            try:
                resp = requests.post(args.url, data=buf.tobytes(), headers=headers, timeout=10)
                if resp.status_code == 200:
                    try:
                        j = resp.json()
                        # Pretty-print key fields if present
                        label = j.get("label", "?")
                        idx = j.get("index", "?")
                        probs = j.get("probs", [])
                        print(f"[OK] label={label} index={idx} probs={probs}")
                    except json.JSONDecodeError:
                        print(f"[OK] Non-JSON response: {resp.text}")
                else:
                    print(f"[HTTP {resp.status_code}] {resp.text}")
            except requests.RequestException as e:
                print(f"[ERROR] Request failed: {e}")

            time.sleep(max(0.0, args.interval))
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user.")
    finally:
        cap.release()
        if args.preview:
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
