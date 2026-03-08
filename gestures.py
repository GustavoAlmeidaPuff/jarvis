#!/usr/bin/env python3
"""
Controle por gestos com uma mão usando MediaPipe Tasks + webcam.

Gestos:
  - Pinça (polegar + indicador)                  → Alt+Tab (segura enquanto pinçado)
  - Indicador + médio levantados, mover pra cima → volume +10%
  - Indicador + médio levantados, mover pra baixo → volume -10%
"""

import os
import time
import logging
import threading
import collections
import subprocess
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import pyautogui

pyautogui.FAILSAFE = False

logger = logging.getLogger("Gestures")

MODEL_PATH     = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")
VOL_STEP          = 10    # % por gesto
VOL_COOLDOWN      = 0.3   # segundos entre ajustes de volume
VOL_VELOCITY_DOWN = 0.18  # velocidade mínima para volume - (mão pra baixo)
VOL_VELOCITY_UP   = 0.12  # velocidade mínima para volume + (mão pra cima, mais sensível)


def _dist(p1, p2) -> float:
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5


def _is_pinch(lm) -> bool:
    return _dist(lm[4], lm[8]) < 0.08


def _is_two_fingers_up(lm) -> bool:
    """Indicador + médio estendidos, anelar + mínimo dobrados."""
    return (
        lm[8].y  < lm[6].y  < lm[5].y   and  # indicador
        lm[12].y < lm[10].y < lm[9].y   and  # médio
        lm[16].y > lm[14].y              and  # anelar dobrado
        lm[20].y > lm[18].y                   # mínimo dobrado
    )


def _set_volume(delta: int):
    sign = "+" if delta > 0 else "-"
    subprocess.run(
        ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{sign}{abs(delta)}%"],
        capture_output=True
    )
    logger.info(f"🔊 Volume {sign}{abs(delta)}%")


class GestureController:

    def __init__(self):
        self.running    = False
        self._thread    = None
        self._lock      = threading.Lock()
        self._landmarks = []
        self._alt_held    = False
        self._vol_history: collections.deque = collections.deque(maxlen=20)
        self._last_vol_t  = 0.0

        base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=mp_vision.RunningMode.LIVE_STREAM,
            num_hands=1,
            min_hand_detection_confidence=0.65,
            min_hand_presence_confidence=0.65,
            min_tracking_confidence=0.55,
            result_callback=self._on_result
        )
        self.landmarker = mp_vision.HandLandmarker.create_from_options(options)

    def _on_result(self, result, output_image, timestamp_ms):
        with self._lock:
            self._landmarks = result.hand_landmarks or []

    def _check_gestures(self):
        with self._lock:
            hands = list(self._landmarks)

        lm = hands[0] if hands else None
        pinching = lm is not None and _is_pinch(lm)

        if pinching and not self._alt_held:
            logger.info("🤙 Pinça → Alt segurado + Tab")
            pyautogui.keyDown("alt")
            pyautogui.press("tab")
            self._alt_held = True

        elif not pinching and self._alt_held:
            logger.info("✋ Pinça solta → Alt liberado")
            pyautogui.keyUp("alt")
            self._alt_held = False

        # ── Volume: indicador + médio levantados, move pra cima/baixo ───
        if not self._alt_held and lm is not None and _is_two_fingers_up(lm):
            now   = time.time()
            wrist_y = lm[0].y
            self._vol_history.append((now, wrist_y))

            window = [(t, y) for t, y in self._vol_history if now - t <= 0.3]
            if len(window) >= 4:
                dy = window[-1][1] - window[0][1]
                dt = window[-1][0] - window[0][0]
                if dt > 0:
                    velocity = dy / dt  # positivo = mão descendo (y aumenta)
                    going_up   = velocity < 0 and abs(velocity) > VOL_VELOCITY_UP
                    going_down = velocity > 0 and abs(velocity) > VOL_VELOCITY_DOWN
                    if (going_up or going_down) and now - self._last_vol_t >= VOL_COOLDOWN:
                        if going_down:
                            _set_volume(-VOL_STEP)   # mão pra baixo = volume -
                        else:
                            _set_volume(+VOL_STEP)   # mão pra cima = volume +
                        self._last_vol_t = now
                        self._vol_history.clear()
        else:
            self._vol_history.clear()

    def _loop(self):
        cap = None
        for idx in [0, 1, 2]:
            c = cv2.VideoCapture(idx)
            ret, _ = c.read()
            if ret:
                cap = c
                logger.info(f"📷 Usando câmera {idx}")
                break
            c.release()

        if cap is None:
            logger.error("❌ Webcam não encontrada")
            return

        logger.info("✅ Gestos iniciados")
        timestamp = 0

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            rgb      = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            self.landmarker.detect_async(mp_image, timestamp)
            timestamp += 33

            self._check_gestures()
            time.sleep(0.03)

        if self._alt_held:
            pyautogui.keyUp("alt")

        cap.release()
        self.landmarker.close()
        logger.info("🔇 Gestos encerrados")

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
