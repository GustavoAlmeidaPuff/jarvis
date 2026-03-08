#!/usr/bin/env python3
"""
Controle por gestos com uma mão usando MediaPipe Tasks + webcam.

Gestos:
  - Pinça (polegar + indicador juntos) → Alt+Tab
"""

import os
import time
import logging
import threading
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import pyautogui

pyautogui.FAILSAFE = False

logger = logging.getLogger("Gestures")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")
def _dist(p1, p2) -> float:
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5


def _is_pinch(lm) -> bool:
    return _dist(lm[4], lm[8]) < 0.08


class GestureController:

    def __init__(self):
        self.running    = False
        self._thread    = None
        self._lock      = threading.Lock()
        self._landmarks = []
        self._alt_held  = False

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
