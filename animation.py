import os
from PySide6.QtGui import QPixmap


# ── Mapeamento estado → frames ───────────────────────────────────────────
STATE_FRAMES = {
    "idle":        ["shime1", "shime1b"],
    "walk":        ["shime2", "shime2b", "shime3", "shime3b"],
    "fall":        ["shime4", "shime18", "shime19"],
    "climb":       ["shime23", "shime24", "shime25"],
    "go_to_climb": ["shime2", "shime2b", "shime3", "shime3b"],
    "idle_b":      ["shime26", "shime27", "shime28", "shime29",
                    "shime30", "shime31", "shime32", "shime33"],
    "drag":        ["shime5", "shime6"],
}

# ── Velocidade por estado ────────────────────────────────────────────────
STATE_ANIM_SPEED = {
    "idle":        30,
    "walk":        25,
    "fall":        0,   # ignorado (mantido só por compatibilidade)
    "climb":       6,
    "go_to_climb": 25,
    "idle_b":      30,
    "drag":        20,
}

DEFAULT_SPEED = 10

# ── Estados que NÃO usam loop (controlados por lógica) ────────────────────
NON_LOOPING_STATES = {"fall"}


class AnimationSystem:
    def __init__(self, sprites_dir: str):
        self.sprites_dir = sprites_dir
        self._cache: dict[str, QPixmap] = {}
        self._load_all()

        self.current_state = "idle"
        self.frame_index   = 0
        self.frame_counter = 0

    # ── Carregamento ─────────────────────────────────────────────────────
    def _load_all(self):
        all_names = {name for frames in STATE_FRAMES.values() for name in frames}

        for name in all_names:
            path = os.path.join(self.sprites_dir, f"{name}.png")
            if os.path.exists(path):
                self._cache[name] = QPixmap(path)
            else:
                print(f"[AnimationSystem] sprite não encontrado: {path}")

    # ── Update (loop apenas para estados normais) ─────────────────────────
    def update(self, state: str):
        # Troca de estado → reset
        if state != self.current_state:
            self.current_state = state
            self.frame_index   = 0
            self.frame_counter = 0
            return

        # ❌ NÃO anima estados controlados por lógica
        if state in NON_LOOPING_STATES:
            return

        speed = STATE_ANIM_SPEED.get(state, DEFAULT_SPEED)
        self.frame_counter += 1

        if self.frame_counter >= speed:
            self.frame_counter = 0
            frames = STATE_FRAMES.get(state, ["shime1"])
            self.frame_index = (self.frame_index + 1) % len(frames)

    # ── Frame atual ───────────────────────────────────────────────────────
    def current_pixmap(self, pet=None) -> QPixmap | None:

        # 🔥 FALL controlado por física (sem loop)
        if self.current_state == "fall" and pet:
            frames = STATE_FRAMES["fall"]
            t = pet.fall_time

            if t != 1:
                frame = frames[1]   # começo
            elif t > 0:
                frame = frames[2]   # meio
            else:
                frame = frames[3]   # impacto

            return self._cache.get(frame)
        

        # 🔄 Estados normais (loop)
        frames = STATE_FRAMES.get(self.current_state, ["shime1"])
        name   = frames[self.frame_index % len(frames)]
        return self._cache.get(name)