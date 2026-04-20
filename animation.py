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
    "landing": ["shime19"],  # frame 3
}

# ── Velocidade por estado ────────────────────────────────────────────────
STATE_ANIM_SPEED = {
    "idle":        30,
    "walk":        25,
    "fall":        0,   # não usado
    "climb":       6,
    "go_to_climb": 25,
    "idle_b":      30,
    "drag":        20,
}

DEFAULT_SPEED = 10

# ── Estados que NÃO usam loop ────────────────────────────────────────────
NON_LOOPING_STATES = {"fall"}


class AnimationSystem:
    def __init__(self, sprites_dir: str):
        self.sprites_dir = sprites_dir
        self._cache: dict[str, QPixmap] = {}
        self._load_all()
        self.fall_stage = 0
        self.landing_timer = 0
        self.landing_lock = False

        self.current_state = "idle"
        self.frame_index   = 0
        self.frame_counter = 0

        # 🔥 controle da queda (anti flicker)
        self.fall_stage = 0

    # ── Carregamento ─────────────────────────────────────────────────────
    def _load_all(self):
        all_names = {name for frames in STATE_FRAMES.values() for name in frames}

        for name in all_names:
            path = os.path.join(self.sprites_dir, f"{name}.png")
            if os.path.exists(path):
                self._cache[name] = QPixmap(path)
            else:
                print(f"[AnimationSystem] sprite não encontrado: {path}")

    # ── Update ───────────────────────────────────────────────────────────
    def update(self, state: str, pet):
    # Troca de estado
        if state != self.current_state:
            self.current_state = state
            self.frame_index = 0
            self.frame_counter = 0

            # reset queda
            if state != "fall":
                self.fall_stage = 0
                self.landing_lock = False
                self.landing_timer = 0

            return

        # 🔥 DETECTAR IMPACTO
        if state == "fall" and pet.on_ground:
            self.landing_lock = True

        # 🔥 CONTAR TEMPO NO CHÃO
        if self.landing_lock:
            self.landing_timer += 1

            # 60fps → ~120 frames = 2 segundos
            if self.landing_timer > 120:
                self.landing_lock = False
                self.landing_timer = 0
                self.fall_stage = 0  # reset

        # não animar fall normal
        if state in NON_LOOPING_STATES:
            return

        # animação normal
        speed = STATE_ANIM_SPEED.get(state, DEFAULT_SPEED)
        self.frame_counter += 1

        if self.frame_counter >= speed:
            self.frame_counter = 0
            frames = STATE_FRAMES.get(state, ["shime1"])
            self.frame_index = (self.frame_index + 1) % len(frames)

    # ── Frame atual ───────────────────────────────────────────────────────
    def current_pixmap(self, pet):
        # FALL (controlado por distância)
        if self.current_state == "fall":
            frames = STATE_FRAMES["fall"]

            distance = pet.ground_y - pet.pos_y
            screen_height = pet.ground_y

            if self.fall_stage == 0:
                if distance < screen_height * 0.6:
                    self.fall_stage = 1

            elif self.fall_stage == 1:
                if distance < screen_height * 0.1:
                    self.fall_stage = 2

            return self._cache.get(frames[self.fall_stage])

        # LANDING (travado no frame 3)
        if self.current_state == "landing":
            return self._cache.get(STATE_FRAMES["landing"][0])

        # NORMAL
        frames = STATE_FRAMES.get(self.current_state, ["shime1"])
        name = frames[self.frame_index % len(frames)]
        return self._cache.get(name)