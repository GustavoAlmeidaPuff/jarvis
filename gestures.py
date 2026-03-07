#!/usr/bin/env python3
"""
Controle por gestos com uma mão usando MediaPipe Tasks + webcam.

Fluxo:
  1. Pinça (polegar + indicador juntos) → ativa modo de navegação
  2. Levanta indicador + médio e inclina → seta direita ou esquerda
  3. Fecha a mão (punho) ou some a mão → desativa
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

TILT_THRESHOLD = 0.5   # ratio dx/dy para contar como diagonal
COOLDOWN       = 0.4   # segundos entre setas


# ── helpers ────────────────────────────────────────────────────────────

def _dist(p1, p2) -> float:
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5


def _is_pinch(lm) -> bool:
    """Polegar (4) perto do indicador (8)."""
    return _dist(lm[4], lm[8]) < 0.08


def _is_fist(lm) -> bool:
    """Todos os dedos dobrados (punho)."""
    tips  = [8, 12, 16, 20]
    bases = [5,  9, 13, 17]
    return all(lm[t].y > lm[b].y for t, b in zip(tips, bases))


def _two_fingers_up(lm) -> bool:
    """Indicador (8) e médio (12) estendidos, anelar e mínimo dobrados."""
    index_up   = lm[8].y  < lm[6].y  < lm[5].y
    middle_up  = lm[12].y < lm[10].y < lm[9].y
    ring_down  = lm[16].y > lm[14].y
    pinky_down = lm[20].y > lm[18].y
    return index_up and middle_up and ring_down and pinky_down


def _tilt_ratio(lm) -> float:
    """
    Inclinação lateral do par de dedos levantados.
    Positivo = direita, negativo = esquerda.
    """
    dx = ((lm[8].x - lm[5].x) + (lm[12].x - lm[9].x)) / 2
    dy = (abs(lm[8].y - lm[5].y) + abs(lm[12].y - lm[9].y)) / 2
    return dx / dy if dy > 0.01 else 0.0


# ── controller ─────────────────────────────────────────────────────────

class GestureController:

    def __init__(self):
        self.running = False
        self._thread = None
        self._lock = threading.Lock()
        self._latest_landmarks = []

        # Estados: "idle" → "active"
        self._state = "idle"
        self._last_tilt_state = "neutral"
        self._last_trigger = 0.0
        self._pinch_confirmed_at = 0.0   # evita ativar com flash de pinça

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
            self._latest_landmarks = result.hand_landmarks or []

    def _check_gestures(self):
        with self._lock:
            hands = list(self._latest_landmarks)

        lm = hands[0] if hands else None

        # ── IDLE: aguardando pinça ──────────────────────────────────────
        if self._state == "idle":
            if lm is None:
                return
            if _is_pinch(lm):
                if self._pinch_confirmed_at == 0.0:
                    self._pinch_confirmed_at = time.time()
                # Exige pinça sustentada por 0.2s para evitar falso positivo
                elif time.time() - self._pinch_confirmed_at >= 0.2:
                    logger.info("🤙 Pinça detectada → modo de navegação ativado")
                    self._state = "active"
                    self._last_tilt_state = "neutral"
                    self._pinch_confirmed_at = 0.0
            else:
                self._pinch_confirmed_at = 0.0

        # ── ACTIVE: monitorando inclinação dos dedos ────────────────────
        elif self._state == "active":
            # Sem mão ou punho → desativa
            if lm is None or _is_fist(lm):
                logger.info("✊ Desativado")
                self._state = "idle"
                self._last_tilt_state = "neutral"
                self._pinch_confirmed_at = 0.0
                return

            if not _two_fingers_up(lm):
                return  # aguarda a pose correta sem desativar

            ratio = _tilt_ratio(lm)
            now = time.time()

            if ratio > TILT_THRESHOLD:
                tilt = "right"
            elif ratio < -TILT_THRESHOLD:
                tilt = "left"
            else:
                tilt = "neutral"

            # Dispara na borda (mudança de estado) com cooldown
            if tilt != "neutral" and tilt != self._last_tilt_state:
                if now - self._last_trigger >= COOLDOWN:
                    if tilt == "right":
                        logger.info(f"👉 Seta direita (ratio={ratio:.2f})")
                        pyautogui.press("right")
                    else:
                        logger.info(f"👈 Seta esquerda (ratio={ratio:.2f})")
                        pyautogui.press("left")
                    self._last_trigger = now

            self._last_tilt_state = tilt

    # ── loop ───────────────────────────────────────────────────────────

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

        logger.info("✅ Gestos iniciados — faça a pinça para ativar")
        timestamp = 0

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            self.landmarker.detect_async(mp_image, timestamp)
            timestamp += 33

            self._check_gestures()
            time.sleep(0.03)

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
