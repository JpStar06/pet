import os
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


# Mapeamento estado → lista de frames (nomes dos arquivos sem extensão)
STATE_FRAMES = {
    "idle":        ["shime1", "shime1b"],
    "walk":        ["shime2", "shime2b", "shime3", "shime3b"],
    "fall":        ["shime4", "shime18", "shime19"],
    "climb":       ["shime23", "shime24", "shime25"],
    "go_to_climb": ["shime2", "shime2b", "shime3", "shime3b"],  # reutiliza climb
    "idle_b":      ["shime26", "shime27", "shime28", "shime29",
                    "shime30", "shime31", "shime32", "shime33"],
    "drag":        ["shime5"],   # frame único — ajuste se quiser
}

# Estados que usam idle_b como animação alternativa (sorteado no behavior)
IDLE_B_STATES = {"idle_b"}

# Velocidade de troca de frame (em ticks) por estado
STATE_ANIM_SPEED = {
    "idle":        12,
    "walk":        6,
    "fall":        8,
    "climb":       6,
    "go_to_climb": 6,
    "idle_b":      10,
    "drag":        2,
}
DEFAULT_SPEED = 10


class AnimationSystem:
    def __init__(self, sprites_dir: str):
        """
        sprites_dir: caminho para a pasta com os .png
        ex: "sprites/miku"
        """
        self.sprites_dir = sprites_dir
        self._cache: dict[str, QPixmap] = {}
        self._load_all()

        self.current_state  = "idle"
        self.frame_index    = 0
        self.frame_counter  = 0

    # ── Carregamento ─────────────────────────────────────────────────────
    def _load_all(self):
        all_names = set()
        for frames in STATE_FRAMES.values():
            all_names.update(frames)

        for name in all_names:
            path = os.path.join(self.sprites_dir, f"{name}.png")
            if os.path.exists(path):
                self._cache[name] = QPixmap(path)
            else:
                print(f"[AnimationSystem] sprite não encontrado: {path}")

    # ── Atualização por tick ──────────────────────────────────────────────
    def update(self, state: str):
        # Troca de estado → reinicia animação
        if state != self.current_state:
            self.current_state = state
            self.frame_index   = 0
            self.frame_counter = 0
            return

        speed = STATE_ANIM_SPEED.get(state, DEFAULT_SPEED)
        self.frame_counter += 1

        if self.frame_counter >= speed:
            self.frame_counter = 0
            frames = STATE_FRAMES.get(state, ["shime1"])
            self.frame_index = (self.frame_index + 1) % len(frames)

    # ── Frame atual ───────────────────────────────────────────────────────
    def current_pixmap(self) -> QPixmap | None:
        frames = STATE_FRAMES.get(self.current_state, ["shime1"])
        name   = frames[self.frame_index % len(frames)]
        return self._cache.get(name)