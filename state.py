from PySide6.QtWidgets import QApplication


class StateMachine:
    """Detecta transições de estado com base na física."""

    def update(self, pet):
        screen = QApplication.primaryScreen().availableGeometry()
        left  = screen.left()
        right = screen.right() - pet.width()

        # 🚫 drag
        if pet.state == "drag":
            return

        # ── climb ─────────────────────
        if pet.state == "go_to_climb":
            if pet.target_side == "left" and pet.pos_x <= left + 5:
                pet.state = "climb"
                pet.vel_x = 0
                pet.vel_y = 0
            elif pet.target_side == "right" and pet.pos_x >= right - 5:
                pet.state = "climb"
                pet.vel_x = 0
                pet.vel_y = 0

        # ── queda ─────────────────────
        if pet.on_ground:
            if pet.state == "fall":
                pet.state = "landing"
        else:
            if pet.state not in ("climb", "landing"):
                pet.state = "fall"