import sys

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer

from physics   import Physics
from state     import StateMachine
from behavior  import Behavior
from renderer  import Renderer
from animation import AnimationSystem


# ── Configure o caminho para a pasta de sprites aqui ──────────────────────
SPRITES_DIR = "sprites/miku"   # ex: "sprites/teto" para trocar de personagem


class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        self.last_mouse_pos = None
        self.fall_time = 0

        # ── Janela ────────────────────────────────────────────────────────
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(120, 120)   # tamanho maior para os sprites da Miku

        # ── Estado ────────────────────────────────────────────────────────
        self.state       = "fall"
        self.target_side = None
        self.on_ground   = False

        # Posição e física
        self.pos_x = 400.0
        self.pos_y = 100.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.speed = 2.5

        # Comportamento
        self.direction      = 1
        self.walk_target    = 0
        self.behavior_timer = 0

        # Drag
        self.dragging      = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # ── Módulos ───────────────────────────────────────────────────────
        self.physics       = Physics(self)
        self.state_machine = StateMachine()
        self.behavior      = Behavior()
        self.renderer      = Renderer()
        self.anim          = AnimationSystem(SPRITES_DIR)

        # ── Timer principal (~60 fps) ─────────────────────────────────────
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)

        self.show()

    # ── Loop principal ────────────────────────────────────────────────────
    def tick(self):
        if self.dragging:
            self.fall_time = 0  # 🔥 evita bug de animação
            self.anim.update(self.state, self)
            self.update()
            return
        if self.state == "fall":
            self.fall_time += 1
        else:
            self.fall_time = 0

        self.physics.update()
        self.state_machine.update(self)
        self.behavior.update(self)
        self.anim.update(self.state, self)   # ← atualiza frame da animação
        self.move(int(self.pos_x), int(self.pos_y))
        self.update()


    # ── Renderização ──────────────────────────────────────────────────────
    def paintEvent(self, event):
        self.renderer.paint(self, event)

    # ── Drag com mouse ────────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.state    = "drag"
            self.vel_x = 0
            self.vel_y = 0
            pos = event.globalPosition().toPoint()
            self.drag_offset_x = pos.x() - self.pos().x()
            self.drag_offset_y = pos.y() - self.pos().y()

    def mouseMoveEvent(self, event):
        if self.dragging:
            pos = event.globalPosition().toPoint()

            # 🔥 mover o pet com o mouse
            self.pos_x = float(pos.x() - self.drag_offset_x)
            self.pos_y = float(pos.y() - self.drag_offset_y)
            self.move(int(self.pos_x), int(self.pos_y))

            # 🔥 calcular velocidade (pra jogar depois)
            if self.last_mouse_pos:
                dx = pos.x() - self.last_mouse_pos.x()
                dy = pos.y() - self.last_mouse_pos.y()

                self.vel_x = dx * 0.3
                self.vel_y = dy * 0.3

            self.last_mouse_pos = pos
        

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.state    = "fall"
            self.vel_y = 2

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Escape, Qt.Key_Q):
            self.close()
            QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec())