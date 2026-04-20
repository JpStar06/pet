from PySide6.QtWidgets import QApplication


class Physics:
    GRAVITY = 0.5
    FRICTION = 0.92

    def __init__(self, pet):
        self.pet = pet

    def update(self):
        screen = QApplication.primaryScreen().availableGeometry()
        left   = screen.left()
        right  = screen.right()  - self.pet.width()
        bottom = screen.bottom() - self.pet.height()

        # Gravidade
        self.pet.vel_y += self.GRAVITY
        self.pet.pos_x += self.pet.vel_x
        self.pet.pos_y += self.pet.vel_y

        # Parede esquerda
        if self.pet.pos_x <= left:
            self.pet.pos_x = left
            if self.pet.state in ("walk", "go_to_climb"):
                self.pet.direction *= -1
                self.pet.vel_x = self.pet.direction * self.pet.speed
            else:
                self.pet.vel_x = 0

        # Parede direita
        elif self.pet.pos_x >= right:
            self.pet.pos_x = right
            if self.pet.state in ("walk", "go_to_climb"):
                self.pet.direction *= -1
                self.pet.vel_x = self.pet.direction * self.pet.speed
            else:
                self.pet.vel_x = 0

        # Chão
        if self.pet.pos_y >= bottom:
            self.pet.pos_y = bottom
            self.pet.vel_y = 0
            self.pet.on_ground = True
        else:
            self.pet.on_ground = False

        # Fricção no chão (apenas em estados passivos)
        if self.pet.on_ground and self.pet.state not in ("walk", "go_to_climb", "climb"):
            self.pet.vel_x *= self.FRICTION
