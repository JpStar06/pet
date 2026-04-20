from PySide6.QtGui import QPainter, QColor, QTransform
from PySide6.QtCore import Qt


# Cor de fallback por estado (caso o sprite não carregue)
STATE_COLORS = {
    "idle":        QColor(180, 100, 255),
    "walk":        QColor(80,  180, 255),
    "fall":        QColor(255,  80, 120),
    "go_to_climb": QColor(255, 180,   0),
    "climb":       QColor(0,   220, 180),
    "drag":        QColor(255, 220,   0),
    "idle_b":      QColor(200, 150, 255),
}
DEFAULT_COLOR = QColor(200, 200, 200)


class Renderer:
    def paint(self, pet, event):
        painter = QPainter(pet)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        pixmap = pet.anim.current_pixmap(pet)

        if pixmap and not pixmap.isNull():
            # Espelha horizontalmente quando andando para a esquerda
            if pet.state in ("walk", "go_to_climb") and pet.direction == 1:
                pixmap = pixmap.transformed(QTransform().scale(-1, 1))

            painter.drawPixmap(0, 0, pet.width(), pet.height(), pixmap)
        else:
            # Fallback: quadrado colorido + olhinhos
            color = STATE_COLORS.get(pet.state, DEFAULT_COLOR)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(0, 0, 64, 64, 16, 16)

            painter.setBrush(QColor(255, 255, 255))
            painter.drawEllipse(16, 18, 14, 20)
            painter.drawEllipse(34, 18, 14, 20)
            painter.setBrush(QColor(0, 0, 0))
            painter.drawEllipse(20, 22,  8, 12)
            painter.drawEllipse(38, 22,  8, 12)