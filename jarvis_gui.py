#!/usr/bin/env python3
"""
Interface gráfica do Jarvis — Painel de Controle.
Lista os comandos de voz e permite ativar/desativar gestos.
"""

import tkinter as tk
import threading

# ── Paleta ────────────────────────────────────────────────────────────────────
BG      = "#0d0d0d"
BG2     = "#1a1a1a"
BG3     = "#252525"
FG      = "#e0e0e0"
GREEN   = "#00ff88"
RED     = "#ff4444"
ACCENT  = "#00aaff"

COMMANDS_INFO = [
    ("teste",        "Verifica se o Jarvis está funcionando"),
    ("hora",         "Fala a hora atual"),
    ("data",         "Mostra a data atual"),
    ("ajuda",        "Lista todos os comandos disponíveis"),
    ("olá / ola",    "Saudação com hora do dia pelo nome"),
    ("navegador",    "Abre o Google Chrome"),
    ("status",       "Mostra o uptime do sistema"),
    ("trabalho",     "Abre Slack, Spotify, Cursor e Chrome"),
    ("música",       "Abre o Spotify"),
    ("ligar aura",   "Toca Aura no Spotify"),
    ("desliga",      "Desliga o computador (aguarda 5 s)"),
    ("fechar",       "Encerra o Jarvis"),
]

GESTURES_INFO = [
    ("✊  Pinça",                             "Segura Alt + abre Alt+Tab para trocar janelas"),
    ("✊ →  Pinça + mover direita",           "Seta direita (navega no Alt+Tab)"),
    ("✊ ←  Pinça + mover esquerda",          "Seta esquerda (navega no Alt+Tab)"),
    ("✌ ↑  Dois dedos + mover pra cima",     "Volume  +10 %  (mais sensível)"),
    ("✌ ↓  Dois dedos + mover pra baixo",    "Volume  −10 %"),
]


class JarvisGUI:
    def __init__(self, jarvis_instance=None):
        self.jarvis = jarvis_instance
        self.root = tk.Tk()
        self.root.title("Jarvis — Painel de Controle")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self._build()
        self._update_gesture_btn()

    # ── Construção da UI ──────────────────────────────────────────────────────

    def _build(self):
        r = self.root

        # Header
        tk.Frame(r, bg=ACCENT, height=2).pack(fill="x")
        hdr = tk.Frame(r, bg=BG, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⬡  JARVIS", font=("Consolas", 18, "bold"),
                 bg=BG, fg=ACCENT).pack()
        tk.Label(hdr, text="Painel de Controle", font=("Consolas", 9),
                 bg=BG, fg="#555555").pack()
        tk.Frame(r, bg="#222", height=1).pack(fill="x", padx=16)

        # Seção: comandos de voz
        self._section_label(r, "COMANDOS DE VOZ")
        self._build_table(r, COMMANDS_INFO, col1_width=16, col1_color=GREEN)

        tk.Frame(r, bg="#222", height=1).pack(fill="x", padx=16, pady=6)

        # Seção: gestos
        gesture_hdr = tk.Frame(r, bg=BG)
        gesture_hdr.pack(fill="x", padx=16, pady=(4, 4))
        tk.Label(gesture_hdr, text="GESTOS", font=("Consolas", 12, "bold"),
                 bg=BG, fg=ACCENT).pack(side="left")
        self._btn_gesture = tk.Button(
            gesture_hdr,
            font=("Consolas", 9, "bold"),
            bg=BG, activebackground=BG,
            bd=0, cursor="hand2", relief="flat",
            command=self._toggle_gestures,
        )
        self._btn_gesture.pack(side="right")

        self._build_table(r, GESTURES_INFO, col1_width=34, col1_color="#aaaaaa")

        # Footer
        tk.Frame(r, bg=ACCENT, height=1).pack(fill="x", padx=16, pady=(8, 0))
        tk.Label(r, text='diga  "Jarvis <comando>"  para ativar',
                 font=("Consolas", 8), bg=BG, fg="#444").pack(pady=6)

    def _section_label(self, parent, text):
        tk.Label(parent, text=text, font=("Consolas", 12, "bold"),
                 bg=BG, fg=ACCENT, anchor="w").pack(fill="x", padx=16, pady=(12, 4))

    def _build_table(self, parent, rows, col1_width, col1_color):
        frame = tk.Frame(parent, bg=BG2)
        frame.pack(fill="x", padx=16, pady=(0, 4))
        for i, (col1, col2) in enumerate(rows):
            bg = BG2 if i % 2 == 0 else BG3
            row = tk.Frame(frame, bg=bg)
            row.pack(fill="x")
            tk.Label(row, text=f"  {col1}", font=("Consolas", 10, "bold"),
                     bg=bg, fg=col1_color, width=col1_width, anchor="w"
                     ).pack(side="left", pady=5)
            tk.Label(row, text=col2, font=("Consolas", 10),
                     bg=bg, fg=FG, anchor="w"
                     ).pack(side="left", padx=10, pady=5)

    # ── Lógica do botão de gestos ─────────────────────────────────────────────

    def _toggle_gestures(self):
        if not self.jarvis or not self.jarvis.gesture_controller:
            return
        gc = self.jarvis.gesture_controller
        if gc.running:
            gc.stop()
        else:
            gc.start()
        self._update_gesture_btn()

    def _update_gesture_btn(self):
        active = (
            self.jarvis is not None
            and self.jarvis.gesture_controller is not None
            and self.jarvis.gesture_controller.running
        )
        if active:
            self._btn_gesture.config(text="● ATIVO",  fg=GREEN, activeforeground=GREEN)
        else:
            self._btn_gesture.config(text="○ INATIVO", fg=RED,   activeforeground=RED)
        self.root.after(1000, self._update_gesture_btn)

    # ── Execução ──────────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()

    def run_in_thread(self):
        t = threading.Thread(target=self.run, daemon=True)
        t.start()
