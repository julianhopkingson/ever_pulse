from PySide6.QtWidgets import (QPushButton, QFrame, QGraphicsDropShadowEffect, 
                               QWidget, QLabel, QHBoxLayout, QCheckBox)
from PySide6.QtCore import (Qt, QPropertyAnimation, QRect, QEasingCurve, 
                            QSize, Property, QPoint, QRectF, QPointF)
from PySide6.QtGui import (QColor, QCursor, QPainter, QBrush, QPen, QFont, 
                           QLinearGradient, QPainterPath)

from ui.themes import THEMES

def parse_color(color_str):
    if isinstance(color_str, QColor): return color_str
    if color_str.startswith("#"):
        return QColor(color_str)
    return QColor(Qt.white)

class CrystalCard(QFrame):
    def __init__(self, theme_name="Light", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.theme_name = theme_name
        self.theme = THEMES.get(theme_name, THEMES["Light"])
        self.setAttribute(Qt.WA_StyledBackground, False)
        
        self.shadow = QGraphicsDropShadowEffect(self)
        self.set_shadow_normal()
        self.setGraphicsEffect(self.shadow)
        
    def set_theme(self, theme_name):
        if self.theme_name == theme_name: return
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        self.set_shadow_normal()
        self.update() 

    def set_shadow_normal(self):
        if self.theme_name == "Light":
             self.shadow.setColor(QColor(31, 38, 135, 30))
             self.shadow.setBlurRadius(25)
             self.shadow.setOffset(0, 8)
        else:
             self.shadow.setColor(QColor(0, 0, 0, 120))
             self.shadow.setBlurRadius(25)
             self.shadow.setOffset(0, 8)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        draw_rect = QRectF(rect).adjusted(1, 1, -1, -1)
        
        bg_color = parse_color(self.theme['glass_bg'])
        border_color = parse_color(self.theme['glass_border'])
        
        p.setBrush(QBrush(bg_color))
        p.setPen(QPen(border_color, 1))
        
        p.drawRoundedRect(draw_rect, 20, 20)

class GreenPillButton(QPushButton):
    def __init__(self, text, theme_name="Light", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.theme = THEMES.get(theme_name, THEMES["Light"])
        self.setFixedHeight(50)
        self.update_gradient()
        
        # Shadow
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setOffset(0, 5)
        self.shadow.setColor(parse_color(self.theme['primary_shadow']))
        self.setGraphicsEffect(self.shadow)
        
    def update_gradient(self):
        t = self.theme
        self.setStyleSheet(f"""
            QPushButton {{
                background: {t['primary_gradient']};
                border-radius: 25px;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border: 1px solid rgba(255,255,255,0.2);
            }}
            QPushButton:hover {{
                border: 1px solid rgba(255,255,255,0.6);
            }}
            QPushButton:pressed {{
                background: {t['accent']};
                padding-top: 3px;
                padding-left: 2px;
            }}
        """)

    def set_theme(self, theme_name):
        self.theme = THEMES[theme_name]
        self.shadow.setColor(parse_color(self.theme['primary_shadow']))
        self.update_gradient()

class SunMoonToggle(QCheckBox):
    def __init__(self, theme_name="Light", parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(68, 36)
        
        self.theme_name = theme_name
        self._thumb_pos = 36.0 if theme_name == "Dark" else 4.0
        
        self.anim = QPropertyAnimation(self, b"thumb_pos", self)
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

        if theme_name == "Dark": self.setChecked(True)

    def get_thumb_pos(self): return self._thumb_pos
    def set_thumb_pos(self, pos):
        self._thumb_pos = pos
        self.update()
    thumb_pos = Property(float, get_thumb_pos, set_thumb_pos)

    def checkStateSet(self):
        super().checkStateSet()
        self.anim.stop()
        self.anim.setEndValue(36.0 if self.isChecked() else 4.0)
        self.anim.start()

    def set_theme_state(self, theme_name):
        self.theme_name = theme_name
        self.blockSignals(True)
        self.setChecked(theme_name == "Dark")
        self.blockSignals(False)
        self._thumb_pos = 36.0 if theme_name == "Dark" else 4.0
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        
        # Track
        track_color = QColor("#2D3748") if self.isChecked() else QColor("#EDF2F7")
        p.setBrush(QBrush(track_color))
        p.setPen(QPen(QColor(0,0,0,15), 1))
        p.drawRoundedRect(0, 0, w, h, h/2, h/2)
        
        thumb_size = h - 6
        icon_color_inactive = QColor("#718096") if self.isChecked() else QColor("#A0AEC0")
        
        # Static Background Icons (Simpler drawing, no paths subtraction)
        sun_center = QPointF(4 + thumb_size/2, h/2)
        moon_center = QPointF(w - 4 - thumb_size/2, h/2)
        
        if self.isChecked(): self._draw_sun_simple(p, sun_center, 5, icon_color_inactive)
        else: self._draw_moon_simple(p, moon_center, 7, icon_color_inactive)

        # Thumb
        p.setBrush(QBrush(QColor("#2ECC71")))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QRectF(self._thumb_pos, 3, thumb_size, thumb_size))
        
        # Active Icon
        thumb_center = QPointF(self._thumb_pos + thumb_size/2, 3 + thumb_size/2)
        if self.isChecked(): self._draw_moon_simple(p, thumb_center, 7, Qt.white)
        else: self._draw_sun_simple(p, thumb_center, 5, Qt.white)

    def _draw_sun_simple(self, p, center, r, color):
        p.save()
        p.setPen(QPen(color, 1.5))
        p.setBrush(Qt.NoBrush) # Sun as ring + rays (Hollow style)
        p.drawEllipse(center, r-1, r-1)
        p.translate(center)
        for _ in range(8):
            p.drawLine(0, -r-1, 0, -r-3)
            p.rotate(45)
        p.restore()

    def _draw_moon_simple(self, p, center, r, color):
        p.save()
        # Hollow Moon: Stroke only, no fill
    def _draw_moon_simple(self, p, center, r, color):
        p.save()
        # Hollow Moon: Stroke only, no fill
        p.setBrush(Qt.NoBrush)
        pen = QPen(color, 2.0) 
        pen.setCapStyle(Qt.RoundCap) # Rounded tips
        p.setPen(pen)
        
        # Rotate for tilt
        p.translate(center)
        p.rotate(-45)
        p.translate(-center)
        
        m_path = QPainterPath()
        m_path.addEllipse(center, r, r)
        
        m_inner = QPainterPath()
        # Adjusted for "super thin" look: equal radius, small offset
        m_inner.addEllipse(center.x() + r*0.25, center.y(), r, r)
        
        crescent = m_path.subtracted(m_inner)
        p.drawPath(crescent)
        p.restore()

    def hitButton(self, pos): return self.rect().contains(pos)
