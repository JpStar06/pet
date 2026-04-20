import random
from PySide6.QtWidgets import QApplication


class Behavior:
    """Decide o que o pet vai fazer quando está idle."""

    CLIMB_SPEED = 3.5

    def update(self, pet):
        # ── Estados ativos: apenas mantém a ação em curso ──
        if pet.state == "walk":
            pet.vel_x = pet.direction * pet.speed
            pet.walk_target -= abs(pet.vel_x)
            if pet.walk_target <= 0:
                pet.state = "idle"
                pet.vel_x = 0
            return

        if pet.state == "go_to_climb":
            pet.vel_x = pet.direction * pet.speed
            return

        if pet.state == "climb":
            self._do_climb(pet)
            return

        if pet.state in ("fall", "drag"):
            return

        # idle_b: animação especial — espera terminar e volta pro idle
        if pet.state == "idle_b":
            pet.behavior_timer += 1
            if pet.behavior_timer >= 120:   # ~2s exibindo idle_b
                pet.behavior_timer = 0
                pet.state = "idle"
            return

        # ── Idle + no chão: toma uma nova decisão ──
        if not pet.on_ground or pet.state != "idle":
            return

        pet.behavior_timer += 1
        if pet.behavior_timer < 80:   # ~1.3s de pausa mínima
            return
        pet.behavior_timer = 0

        choices = ["idle"] * 2 + ["walk"] * 4 + ["jump"] * 2 + ["climb"] * 1 + ["idle_b"] * 1
        choice  = random.choice(choices)

        screen = QApplication.primaryScreen().availableGeometry()
        left   = screen.left()
        right  = screen.right() - pet.width()

        if choice == "idle":
            pet.state = "idle"
            pet.vel_x = 0

        elif choice == "idle_b":
            pet.state = "idle_b"
            pet.vel_x = 0

        elif choice == "walk":
            pet.state       = "walk"
            pet.direction   = random.choice([-1, 1])
            pet.walk_target = random.randint(100, 1000)
            pet.vel_x       = pet.direction * pet.speed

        elif choice == "jump":
            pet.vel_y     = -10
            pet.state     = "fall"
            pet.on_ground = False

        elif choice == "climb":
            pet.state       = "go_to_climb"
            pet.target_side = random.choice(["left", "right"])
            pet.direction   = -1 if pet.target_side == "left" else 1
            pet.vel_x       = pet.direction * pet.speed
            pet.walk_target = 2000

    # ── Subida pela parede ────────────────────────────────────────────────
    def _do_climb(self, pet):
        pet.vel_y = 0
        screen    = QApplication.primaryScreen().availableGeometry()

        pet.pos_y -= self.CLIMB_SPEED

        if pet.target_side == "left":
            pet.pos_x = screen.left()
        else:
            pet.pos_x = screen.right() - pet.width()

        # Chegou no topo → cai de volta
        if pet.pos_y <= screen.top() + 10:
            pet.pos_y       = screen.top()
            pet.state       = "fall"
            pet.vel_y       = 1.5
            pet.vel_x       = 5 if pet.target_side == "left" else -5
            pet.target_side = None