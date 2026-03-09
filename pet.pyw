"""Carta ao próximo dev:
Se você está lendo isso, parabéns por ter encontrado o código do DesktopPet! Espero que ele traga um sorriso ao seu rosto e talvez até inspire você a criar algo divertido também.
Mas infelizmente, este código é um pouco bagunçado e cheio de gambiarras. Ele foi escrito em um curto período de tempo, sem muita preocupação com organização ou boas práticas. Então, se você quiser melhorar ou refatorar, fique à vontade! Aqui estão algumas dicas para entender o código:
- O código é dividido em uma classe DesktopPet, que é um QWidget personalizado. Ele lida com a física, comportamento e animação do pet.
- O método tick() é chamado a cada frame e é responsável por atualizar a física, o estado e o comportamento do pet.
- O método update_physics() lida com a movimentação, colisões e gravidade do pet.
- O método update_state() detecta quando o pet chega no chão ou nas paredes e muda o estado de acordo.
- O método climb() é chamado quando o pet está no estado de climb e faz ele subir pela parede.
- O método update_behavior() decide o que o pet vai fazer quando está idle, como andar, pular ou escalar.
- O método paintEvent() desenha o pet na tela, usando cores diferentes para cada estado.
- Os métodos mousePressEvent, mouseMoveEvent e mouseReleaseEvent permitem arrastar o pet com o mouse, e o keyPressEvent permite fechar o programa com ESC ou Q.
Espero que isso ajude você a entender o código e se divertir com ele! Se você fizer melhorias ou quiser compartilhar o que criou, fique a vontade.
Infelizmente, não tenho tempo para manter ou melhorar este projeto, mas fico feliz que ele possa trazer alegria para outras pessoas. Divirta-se e crie algo incrível!
- O dev anterior (que provavelmente é eu mesmo, mas quem sabe no futuro alguém pode ler isso e se identificar como o "dev anterior").
Mas nem sempre a vida é tão feliz, esse será meu ultimo projeto em Python, e provavelmente o último código que escrevo. Então, se você está lendo isso, saiba que este código é um legado do meu amor pela programação e pela diversão que ela me trouxe. Espero que ele continue a trazer alegria para quem o usar ou modificar. 
Esse será o ultimo legado de JpStar06 muito provavelmente visto que perdi o intersse em tudo, acordar de manhã é um sofrimento e não tenho mais vontade de criar ou aprender coisas novas, a programação era tudo oque me restava mas até isso perdeu a graça. tudo o que eu gostava anteriormente se tornou um fardo, e a única coisa que me resta é tentar aproveitar o tempo que me resta da melhor forma possível.
Me perdi em um mar de pensamentos negativos e não consigo mais encontrar motivação para nada. A vida se tornou uma rotina sem sentido, e cada dia é apenas mais um passo em direção ao vazio. Eu sei que isso pode parecer dramático, mas é a realidade que estou enfrentando. Hoje dia 09/03/2024, eu acordei pior que ontem, e durante meu café da manhã, eu pensei sobre como tudo se tornou tão difícil. A única coisa que me dava alegria era a programação, mas agora até isso se tornou um fardo. Eu não tenho mais vontade de criar ou aprender coisas novas, e a ideia de escrever código me deixa exausto. mas aquela ideia me veio novamente, "não da para ter um futuro que nem você mesmo pode ver".
Eu sei que isso pode parecer desesperador, mas é a verdade. Eu não consigo mais imaginar um futuro para mim mesmo, e isso não me assusta. ja aceitei meu destino, e será eu comigo mesmo e com meus demonios, com um balanço no pescoço e um olhar vazio enquanto o ar me falta; apenas esperando que tudo ficar escuro e silenciosa até que eu possa descansar.
Se você está lendo isso, saiba que eu te desejo tudo de melhor. Espero que você encontre alegria e propósito na vida, mesmo que eu não tenha conseguido encontrar para mim mesmo. A vida pode ser difícil, mas também pode ser bela. Aproveite os momentos bons e tente aprender com os momentos ruins. Faça o que eu não consegui fazer, viva, viva feliz, seja o orgulho que eu não fui capaz de ser.
- JpStar06"""


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
        elif event.button() == Qt.RightButton:
            self.state = "jump"
    
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Escape, Qt.Key_Q):
            print("Tecla de saída pressionada")
            self.close()
            QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec())
