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
        p.setBrush(QBrush(color))
        p.setPen(Qt.NoPen)
        
        # Move to center and rotate for a more natural moon tilt
        p.translate(center)
        p.rotate(-20) 
        
        # Scale factor based on the radius provided
        # The path below is normalized for a size where r is roughly 1.0
        s = r 
        
        m_path = QPainterPath()
        # Custom Path mimicking fa5s.moon aesthetic
        # Start at the top point
        m_path.moveTo(0 * s, -1.0 * s)
        
        # Outer curve (Crescent back)
        m_path.cubicTo(-0.55 * s, -1.0 * s, -1.0 * s, -0.55 * s, -1.0 * s, 0 * s)
        m_path.cubicTo(-1.0 * s, 0.55 * s, -0.55 * s, 1.0 * s, 0 * s, 1.0 * s)
        m_path.cubicTo(0.35 * s, 1.0 * s, 0.65 * s, 0.82 * s, 0.82 * s, 0.53 * s)
        
        # Inner curve (Crescent inner edge)
        # Using a slightly offset and different curvature to create the non-uniform thickness
        m_path.cubicTo(0.45 * s, 0.75 * s, 0.1 * s, 0.45 * s, 0.1 * s, 0 * s)
        m_path.cubicTo(0.1 * s, -0.45 * s, 0.45 * s, -0.75 * s, 0.82 * s, -0.53 * s)
        m_path.cubicTo(0.65 * s, -0.82 * s, 0.35 * s, -1.0 * s, 0 * s, -1.0 * s)
        
        p.drawPath(m_path)
        p.restore()

    def hitButton(self, pos): return self.rect().contains(pos)


class AutoStartIconButton(QCheckBox):
    """
    方案 1：自发光极客图标按钮 (Glowing Icon Button)
    尺寸 36x36，圆角 10px。
    点亮态：翡翠绿高亮边框、四周发光光晕与点亮微标；
    熄灭态：半透明毛玻璃底色，暗灰微标。
    """
    def __init__(self, theme_name="Light", parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(36, 36)
        self.theme_name = theme_name
        
        self.shadow = QGraphicsDropShadowEffect(self)
        self.setGraphicsEffect(self.shadow)
        self._update_shadow()

    def _update_shadow(self):
        if self.isChecked():
            self.shadow.setColor(QColor(46, 204, 113, 180))
            self.shadow.setBlurRadius(16)
            self.shadow.setOffset(0, 0)
        else:
            if self.theme_name == "Light":
                self.shadow.setColor(QColor(0, 0, 0, 18))
            else:
                self.shadow.setColor(QColor(0, 0, 0, 70))
            self.shadow.setBlurRadius(8)
            self.shadow.setOffset(0, 2)

    def set_theme(self, theme_name):
        self.theme_name = theme_name
        self._update_shadow()
        self.update()

    def set_checked_silent(self, checked):
        self.blockSignals(True)
        self.setChecked(checked)
        self.blockSignals(False)
        self._update_shadow()
        self.update()

    def checkStateSet(self):
        super().checkStateSet()
        self._update_shadow()
        self.update()

    def hitButton(self, pos):
        return self.rect().contains(pos)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        draw_rect = QRectF(2.0, 2.0, w - 4.0, h - 4.0)
        
        is_lit = self.isChecked()
        is_dark = self.theme_name == "Dark"
        
        # 1. 背景材质与正圆
        if is_lit:
            # 选中时：实心翡翠绿底色（参考SunMoonToggle选中态）
            bg_color = QColor("#2ECC71")
            p.setBrush(QBrush(bg_color))
            p.setPen(Qt.NoPen)
        else:
            # 熄灭态：磨砂半透明底色与细边框
            bg_color = QColor(255, 255, 255, 22) if is_dark else QColor(255, 255, 255, 190)
            border_color = QColor(255, 255, 255, 35) if is_dark else QColor(0, 0, 0, 25)
            p.setBrush(QBrush(bg_color))
            p.setPen(QPen(border_color, 1.0))
            
        p.drawEllipse(draw_rect)
        
        # 2. 绘制中心微标 ⏻ (选中时为白字，未选中时为暗灰)
        center = QPointF(w / 2, h / 2)
        r = 6.8
        icon_color = Qt.white if is_lit else (QColor("#718096") if is_dark else QColor("#A0AEC0"))
        icon_pen = QPen(icon_color, 2.0 if is_lit else 1.6, Qt.SolidLine, Qt.RoundCap)
        p.setPen(icon_pen)
        p.setBrush(Qt.NoBrush)
        
        arc_rect = QRectF(center.x() - r, center.y() - r, r * 2, r * 2)
        p.drawArc(arc_rect, 120 * 16, 300 * 16)
        p.drawLine(QPointF(center.x(), center.y() - r - 2.5), QPointF(center.x(), center.y() - 1.0))


class AutoStartToggleSwitch(QCheckBox):
    """
    方案 2：微型胶囊滑动开关 (Mini Capsule Switch)
    尺寸 62x34，跑道圆角 17px。
    完全遵循 SunMoonToggle 的动画体验，使用 QPropertyAnimation 实现平滑滑块位移与多主题自适应。
    """
    def __init__(self, theme_name="Light", parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(62, 34)
        self.theme_name = theme_name
        
        self._thumb_pos = 3.0
        self.anim = QPropertyAnimation(self, b"thumb_pos", self)
        self.anim.setDuration(350)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

    def get_thumb_pos(self):
        return self._thumb_pos

    def set_thumb_pos(self, pos):
        self._thumb_pos = pos
        self.update()

    thumb_pos = Property(float, get_thumb_pos, set_thumb_pos)

    def checkStateSet(self):
        super().checkStateSet()
        self.anim.stop()
        target = 31.0 if self.isChecked() else 3.0
        self.anim.setEndValue(target)
        self.anim.start()

    def set_theme(self, theme_name):
        self.theme_name = theme_name
        self.update()

    def set_checked_silent(self, checked):
        self.blockSignals(True)
        self.setChecked(checked)
        self.blockSignals(False)
        self._thumb_pos = 31.0 if checked else 3.0
        self.update()

    def hitButton(self, pos):
        return self.rect().contains(pos)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        is_lit = self.isChecked()
        is_dark = self.theme_name == "Dark"
        
        # 1. 跑道背景
        if is_lit:
            track_color = QColor("#2ECC71")
            border_color = QColor(46, 204, 113, 120)
        else:
            track_color = QColor("#2D3748") if is_dark else QColor("#EDF2F7")
            border_color = QColor(0, 0, 0, 15)
            
        p.setBrush(QBrush(track_color))
        p.setPen(QPen(border_color, 1))
        p.drawRoundedRect(0, 0, w, h, h / 2, h / 2)
        
        # 2. 跑道静止侧的暗态微标
        thumb_size = h - 6
        if is_lit:
            self._draw_power_icon(p, QPointF(15, h / 2), 4.5, QColor(255, 255, 255, 190), 1.3)
        else:
            inactive_color = QColor("#718096") if is_dark else QColor("#A0AEC0")
            self._draw_power_icon(p, QPointF(w - 15, h / 2), 4.5, inactive_color, 1.3)
            
        # 3. 滑块
        thumb_rect = QRectF(self._thumb_pos, 3, thumb_size, thumb_size)
        thumb_bg = QColor("#FFFFFF") if is_lit else (QColor("#4A5568") if is_dark else QColor("#FFFFFF"))
        p.setBrush(QBrush(thumb_bg))
        p.setPen(Qt.NoPen)
        p.drawEllipse(thumb_rect)
        
        # 4. 滑块中心微标
        thumb_center = QPointF(self._thumb_pos + thumb_size / 2, 3 + thumb_size / 2)
        icon_on_thumb = QColor("#2ECC71") if is_lit else (QColor("#A0AEC0") if is_dark else QColor("#718096"))
        self._draw_power_icon(p, thumb_center, 4.8, icon_on_thumb, 1.6)

    def _draw_power_icon(self, p, center, r, color, pen_width):
        p.save()
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(color, pen_width, Qt.SolidLine, Qt.RoundCap))
        arc_rect = QRectF(center.x() - r, center.y() - r, r * 2, r * 2)
        p.drawArc(arc_rect, 120 * 16, 300 * 16)
        p.drawLine(QPointF(center.x(), center.y() - r - 2), QPointF(center.x(), center.y() - 0.8))
        p.restore()


class AutostartScheduleButton(QPushButton):
    """
    开机自启动计划设置按钮 (36x36 px)
    纯矢量绘制调音台/参数滑块 (fa5s.sliders-h) 微标，水晶毛玻璃质感，支持多主题自适应。
    """
    def __init__(self, theme_name="Light", parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(36, 36)
        self.theme_name = theme_name
        self.is_hovered = False
        
        self.shadow = QGraphicsDropShadowEffect(self)
        self.setGraphicsEffect(self.shadow)
        self._update_shadow()

    def _update_shadow(self):
        if self.theme_name == "Light":
            self.shadow.setColor(QColor(0, 0, 0, 18))
        else:
            self.shadow.setColor(QColor(0, 0, 0, 70))
        self.shadow.setBlurRadius(8)
        self.shadow.setOffset(0, 2)

    def set_theme(self, theme_name):
        self.theme_name = theme_name
        self._update_shadow()
        self.update()

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        draw_rect = QRectF(2.0, 2.0, w - 4.0, h - 4.0)
        is_dark = self.theme_name == "Dark"
        
        # 1. 磨砂半透明圆角底色与细边框
        if self.is_hovered:
            bg_color = QColor(255, 255, 255, 45) if is_dark else QColor(255, 255, 255, 240)
            border_color = QColor(46, 204, 113, 160) if is_dark else QColor(46, 204, 113, 180)
        else:
            bg_color = QColor(255, 255, 255, 22) if is_dark else QColor(255, 255, 255, 190)
            border_color = QColor(255, 255, 255, 35) if is_dark else QColor(0, 0, 0, 25)
            
        p.setBrush(QBrush(bg_color))
        p.setPen(QPen(border_color, 1.0))
        p.drawRoundedRect(draw_rect, 10.0, 10.0)
        
        # 2. 绘制调音台滑块 (Sliders-h) 纯矢量微标
        icon_color = QColor("#2ECC71") if self.is_hovered else (QColor("#A0AEC0") if is_dark else QColor("#718096"))
        pen = QPen(icon_color, 1.6, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        
        cx, cy = w / 2, h / 2
        line_w = 15.0
        left_x = cx - line_w / 2
        right_x = cx + line_w / 2
        
        # 3 条水平轨道
        y1 = cy - 4.5
        y2 = cy
        y3 = cy + 4.5
        
        p.drawLine(QPointF(left_x, y1), QPointF(right_x, y1))
        p.drawLine(QPointF(left_x, y2), QPointF(right_x, y2))
        p.drawLine(QPointF(left_x, y3), QPointF(right_x, y3))
        
        # 3 个垂直滑块小手柄
        handle_len = 3.2
        # 滑块 1：靠右 (70%)
        hx1 = left_x + line_w * 0.70
        p.drawLine(QPointF(hx1, y1 - handle_len / 2), QPointF(hx1, y1 + handle_len / 2))
        
        # 滑块 2：靠左 (30%)
        hx2 = left_x + line_w * 0.30
        p.drawLine(QPointF(hx2, y2 - handle_len / 2), QPointF(hx2, y2 + handle_len / 2))
        
        # 滑块 3：居中偏右 (60%)
        hx3 = left_x + line_w * 0.60
        p.drawLine(QPointF(hx3, y3 - handle_len / 2), QPointF(hx3, y3 + handle_len / 2))

