import sys
import random
import os

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor


class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(64, 64)
        self.state = "fall"           # começa caindo
        self.target_side = None       # para o climb: "left" ou "right"
        self.climb_target_x = 0.0     # posição x alvo durante a ida pro climb

        # Posição e física
        self.pos_x = 400.0
        self.pos_y = 100.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.gravity = 0.5
        self.friction = 0.92

        # Comportamento
        self.direction = 1
        self.speed = 2.5
        self.walk_target = 0
        self.behavior_timer = 0
        self.on_ground = False

        # Animação (simples por enquanto)
        self.anim_frame = 0
        self.anim_counter = 0
        self.anim_speed = 8

        # Drag
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Timer principal (~60 fps)
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

        self.show()

    def tick(self):
        if self.dragging:
            self.update()
            return

        self.update_physics()
        self.update_state()           # detecta chão, bordas, etc.

        if self.state == "climb":
            self.climb()

        self.update_behavior()        # decide ações
        #self.update_animation()

        self.move(int(self.pos_x), int(self.pos_y))
        self.update()

    def update_physics(self):
        screen = QApplication.primaryScreen().availableGeometry()
        left = screen.left()
        right = screen.right() - self.width()
        bottom = screen.bottom() - self.height()
        

        self.vel_y += self.gravity
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y

        turned = False
            
        if self.pos_x <= left:
            self.pos_x = left
            if self.state in ("walk", "go_to_climb"):
                self.direction *= -1           # vira para o outro lado
                self.vel_x = self.direction * self.speed
                turned = True
            else:
                self.vel_x = 0

        elif self.pos_x >= right:
            self.pos_x = right
            if self.state in ("walk", "go_to_climb"):
                self.direction *= -1
                self.vel_x = self.direction * self.speed
                turned = True
            else:
                self.vel_x = 0

        # Chão
        if self.pos_y >= bottom:
            self.pos_y = bottom
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Paredes (durante walk ou indo pro climb)
        if self.pos_x <= left:
            self.pos_x = left
            self.vel_x = 0  # para de andar

        if self.pos_x >= right:
            self.pos_x = right
            self.vel_x = 0  # para de andar

        if self.on_ground and self.state not in ("walk", "go_to_climb", "climb"):
            self.vel_x *= self.friction

    def update_state(self):
        screen = QApplication.primaryScreen().availableGeometry()
        left = screen.left()
        right = screen.right() - self.width()
        bottom = screen.bottom() - self.height()

        # Se está indo pro climb e já chegou na parede alvo
        if self.state == "go_to_climb":
            if self.target_side == "left" and self.pos_x <= left + 5:
                self.state = "climb"
                self.vel_x = 0
                self.vel_y = 0
            elif self.target_side == "right" and self.pos_x >= right - 5:
                self.state = "climb"
                self.vel_x = 0
                self.vel_y = 0

        # Chegou no chão durante fall → idle
        if self.on_ground and self.state == "fall":
            self.state = "idle"
            self.vel_x = 0

    def climb(self):
        self.vel_y = 0
        screen = QApplication.primaryScreen().availableGeometry()
        top = screen.top()
        bottom = screen.bottom() - self.height()

        climb_speed = 3.5

        self.pos_y -= climb_speed

        # Gruda na parede
        if self.target_side == "left":
            self.pos_x = screen.left()
        else:
            self.pos_x = screen.right() - self.width()

        # Chegou no topo
        if self.pos_y <= top + 10:
            self.pos_y = top
            self.state = "fall"
            self.vel_y = 1.5                # cai devagar no começo
            self.vel_x = 5 if self.target_side == "left" else -5  # empurra pra longe da parede
            self.target_side = None

    def update_behavior(self):
        if self.state in ("walk", "go_to_climb", "climb", "fall", "drag"):
            # Durante essas ações, não decide nada novo
            if self.state == "walk":
                # Mantém a velocidade constante durante walk
                self.vel_x = self.direction * self.speed
                
                    # Diminui o target baseado na distância real percorrida
                self.walk_target -= abs(self.vel_x)  # usa abs para contar positivo
            
                if self.walk_target <= 0:
                    self.state = "idle"
                    self.vel_x = 0
            return
        
        if self.state == "go_to_climb":
            self.vel_x = self.direction * self.speed
            return
        
        if self.state == "climb":
            # Continua subindo até o topo, sem decidir nada novo
            return

        # Só decide quando idle + no chão
        if not self.on_ground or self.state != "idle":
            return

        self.behavior_timer += 1
        if self.behavior_timer < 80:  # ~1.3s de pausa mínima entre decisões
            return

        self.behavior_timer = 0

        choices = ["idle"] * 3 + ["walk"] * 4 + ["jump"] * 2 + ["climb"] * 1
        choice = random.choice(choices)

        screen = QApplication.primaryScreen().availableGeometry()
        left = screen.left()
        right = screen.right() - self.width()

        if choice == "idle":
            self.state = "idle"
            self.vel_x = 0

        elif choice == "walk":
            self.state = "walk"
            self.direction = random.choice([-1, 1])
            self.walk_target = random.randint(100, 1000)
            self.vel_x = self.direction * self.speed

        elif choice == "jump" and self.on_ground:
            self.vel_y = -10
            self.state = "fall"
            self.on_ground = False

        elif choice == "climb":
            self.state = "go_to_climb"
            self.target_side = random.choice(["left", "right"])
            self.climb_target_x = left if self.target_side == "left" else right

            # Anda em direção à parede escolhida
            self.direction = -1 if self.target_side == "left" else 1
            self.vel_x = self.direction * self.speed
            # Distância grande o suficiente pra garantir que vá até a borda
            self.walk_target = 2000  # valor alto, mas será interrompido pela colisão

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = {
            "idle": QColor(180, 100, 255),
            "walk": QColor(80, 180, 255),
            "fall": QColor(255, 80, 120),
            "go_to_climb": QColor(255, 180, 0),   # laranja durante a ida
            "climb": QColor(0, 220, 180),
            "drag": QColor(255, 220, 0)
        }
        color = colors.get(self.state, QColor(200, 200, 200))

        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 64, 64, 16, 16)

        # Olhinhos (mantendo por fofura)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(16, 18, 14, 20)
        painter.drawEllipse(34, 18, 14, 20)
        painter.setBrush(QColor(0, 0, 0))
        painter.drawEllipse(20, 22, 8, 12)
        painter.drawEllipse(38, 22, 8, 12)

    # Drag
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.state = "drag"
            pos = event.globalPosition().toPoint()
            self.drag_offset_x = pos.x() - self.pos().x()
            self.drag_offset_y = pos.y() - self.pos().y()

    def mouseMoveEvent(self, event):
        if self.dragging:
            pos = event.globalPosition().toPoint()
            new_x = pos.x() - self.drag_offset_x
            new_y = pos.y() - self.drag_offset_y
            self.pos_x = float(new_x)
            self.pos_y = float(new_y)
            self.move(new_x, new_y)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.state = "fall"
    
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Escape, Qt.Key_Q):
            print("Tecla de saída pressionada")
            self.close()
            QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec())