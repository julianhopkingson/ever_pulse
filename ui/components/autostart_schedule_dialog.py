import datetime
from PySide6.QtWidgets import (QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont

from ui.themes import THEMES
from ui.window_effect import window_effect


class WeekDayToggleButton(QPushButton):
    """
    单个星期的胶囊切换按钮 (WeekDayToggleButton)
    尺寸 48x34，圆角 8px。
    点亮态：翡翠绿底色 (#2ECC71 / #10B981) + 纯白加粗文字；
    变暗态：浅色下为半透明微灰，深色下为半透明暗灰，文字为次级灰色。
    """
    def __init__(self, text, is_checked=True, theme_name="Light", parent=None):
        super().__init__(text, parent)
        self.theme_name = theme_name
        self.setCheckable(True)
        self.setChecked(is_checked)
        self.setFixedSize(48, 34)
        self.setCursor(Qt.PointingHandCursor)
        
        self.shadow = QGraphicsDropShadowEffect(self)
        self.setGraphicsEffect(self.shadow)
        
        self.toggled.connect(self._update_style)
        self._update_style()

    def set_theme(self, theme_name):
        self.theme_name = theme_name
        self._update_style()

    def _update_style(self):
        is_dark = self.theme_name == "Dark"
        
        if self.isChecked():
            # 点亮态（翡翠绿）
            self.shadow.setColor(QColor(46, 204, 113, 140))
            self.shadow.setBlurRadius(10)
            self.shadow.setOffset(0, 2)
            
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2ECC71;
                    color: #FFFFFF;
                    border: 1px solid #27AE60;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 0px;
                    font-family: 'Segoe UI Variable Display', 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
                }
                QPushButton:hover {
                    background-color: #27AE60;
                }
            """)
        else:
            # 变暗态（次级灰）
            if is_dark:
                self.shadow.setColor(QColor(0, 0, 0, 50))
                self.shadow.setBlurRadius(6)
                self.shadow.setOffset(0, 1)
                bg_color = "rgba(255, 255, 255, 0.08)"
                border_color = "rgba(255, 255, 255, 0.12)"
                text_color = "#A0AEC0"
                hover_bg = "rgba(255, 255, 255, 0.14)"
            else:
                self.shadow.setColor(QColor(0, 0, 0, 15))
                self.shadow.setBlurRadius(6)
                self.shadow.setOffset(0, 1)
                bg_color = "rgba(0, 0, 0, 0.06)"
                border_color = "rgba(0, 0, 0, 0.10)"
                text_color = "#718096"
                hover_bg = "rgba(0, 0, 0, 0.10)"
            
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: normal;
                    padding: 0px;
                    font-family: 'Segoe UI Variable Display', 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
                }}
                QPushButton:hover {{
                    background-color: {hover_bg};
                    color: {text_color};
                }}
            """)


class AutoStartScheduleDialog(QDialog):
    """
    模态排程设置弹窗 (AutoStartScheduleDialog)
    设计规范与 Flow Track 100% 对齐，并完美融入 Ever Pulse 水晶毛玻璃美学。
    """
    def __init__(self, schedule_days, i18n, theme_name="Light", parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.theme_name = theme_name
        
        # schedule_days: 7项 bool 列表，索引 0~6 对应周一至周日
        if not schedule_days or len(schedule_days) != 7:
            self.schedule_days = [True, True, True, True, True, False, False]
        else:
            self.schedule_days = list(schedule_days)
            
        self.result_schedule = None
        
        _ = self.i18n.get
        title = _("dialog_autostart_schedule_title")
        self.setWindowTitle(title if title and title != "dialog_autostart_schedule_title" else "Autostart Schedule Settings")
        self.setFixedSize(480, 270)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setObjectName("AutoStartScheduleDialog")
        
        # 窗口与标题栏主题初始化
        t = THEMES.get(self.theme_name, THEMES["Light"])
        self.setStyleSheet(f"""
            QDialog#AutoStartScheduleDialog {{
                background-color: {t['bg_color']};
            }}
        """)
        try:
            window_effect.set_title_bar_color(self.winId(), t['bg_color'])
        except Exception:
            pass
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)
        
        # 1. 悬浮毛玻璃主卡片
        self.card_frame = QFrame()
        self.card_frame.setObjectName("AutoStartScheduleCard")
        self._apply_card_style()
        
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)
        
        # 卡片环境光晕
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 45) if self.theme_name == "Dark" else QColor(0, 0, 0, 20))
        self.card_frame.setGraphicsEffect(shadow)
        
        # 提示文案
        hint_text = _("autostart_schedule_hint")
        if not hint_text or hint_text == "autostart_schedule_hint":
            hint_text = _("tooltip_autostart_settings")
        self.lbl_hint = QLabel(hint_text)
        self.lbl_hint.setStyleSheet(f"font-size: 13px; color: {t['text_secondary']}; font-family: 'Segoe UI Variable Display', 'Segoe UI', 'Microsoft YaHei UI', sans-serif;")
        card_layout.addWidget(self.lbl_hint)
        
        # 2. 星期切换胶囊组 (周一至周日)
        days_layout = QHBoxLayout()
        days_layout.setContentsMargins(0, 4, 0, 4)
        days_layout.setSpacing(8)
        
        weekday_keys = [
            ("weekday_mon", "Mon"),
            ("weekday_tue", "Tue"),
            ("weekday_wed", "Wed"),
            ("weekday_thu", "Thu"),
            ("weekday_fri", "Fri"),
            ("weekday_sat", "Sat"),
            ("weekday_sun", "Sun")
        ]
        
        self.day_buttons = []
        for i, (key, fallback) in enumerate(weekday_keys):
            day_name = _(key)
            if not day_name or day_name == key:
                day_name = fallback
            is_active = self.schedule_days[i]
            btn = WeekDayToggleButton(day_name, is_checked=is_active, theme_name=self.theme_name)
            self.day_buttons.append(btn)
            days_layout.addWidget(btn)
            
        card_layout.addLayout(days_layout)
        
        # 3. 快捷预设按钮组 (工作日一键开启 / 每天开启)
        quick_layout = QHBoxLayout()
        quick_layout.setContentsMargins(0, 2, 0, 0)
        quick_layout.setSpacing(16)
        
        workdays_text = _("btn_quick_workdays")
        self.btn_workdays = QPushButton(workdays_text if workdays_text and workdays_text != "btn_quick_workdays" else "Workdays (Mon-Fri)")
        self.btn_workdays.setCursor(Qt.PointingHandCursor)
        self.btn_workdays.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #2ECC71;
                border: none;
                font-size: 13px;
                font-weight: 500;
                text-decoration: underline;
                font-family: 'Segoe UI Variable Display', 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
            }
            QPushButton:hover {
                color: #27AE60;
            }
        """)
        self.btn_workdays.clicked.connect(self.set_quick_workdays)
        
        everyday_text = _("btn_quick_everyday")
        self.btn_everyday = QPushButton(everyday_text if everyday_text and everyday_text != "btn_quick_everyday" else "Everyday")
        self.btn_everyday.setCursor(Qt.PointingHandCursor)
        self.btn_everyday.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #2ECC71;
                border: none;
                font-size: 13px;
                font-weight: 500;
                text-decoration: underline;
                font-family: 'Segoe UI Variable Display', 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
            }
            QPushButton:hover {
                color: #27AE60;
            }
        """)
        self.btn_everyday.clicked.connect(self.set_quick_everyday)
        
        quick_layout.addWidget(self.btn_workdays)
        quick_layout.addWidget(self.btn_everyday)
        quick_layout.addStretch()
        
        card_layout.addLayout(quick_layout)
        layout.addWidget(self.card_frame)
        
        # 4. 底部标准操作按钮 (Cancel / Save)
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(12)
        btn_layout.addStretch()
        
        cancel_text = _("btn_cancel")
        self.btn_cancel = QPushButton(cancel_text if cancel_text and cancel_text != "btn_cancel" else "Cancel")
        self.btn_cancel.setFixedSize(105, 36)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self._apply_cancel_button_style()
        self.btn_cancel.clicked.connect(self.reject)
        
        save_text = _("btn_save")
        self.btn_save = QPushButton(save_text if save_text and save_text != "btn_save" else "Save")
        self.btn_save.setFixedSize(105, 36)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self._apply_save_button_style()
        self.btn_save.clicked.connect(self.save_and_close)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def _apply_card_style(self):
        t = THEMES.get(self.theme_name, THEMES["Light"])
        is_dark = self.theme_name == "Dark"
        bg = "rgba(27, 38, 59, 0.70)" if is_dark else "rgba(255, 255, 255, 0.75)"
        border = "rgba(255, 255, 255, 0.30)" if is_dark else "rgba(255, 255, 255, 0.85)"
        self.card_frame.setStyleSheet(f"""
            QFrame#AutoStartScheduleCard {{
                background-color: {bg};
                border: 1.5px solid {border};
                border-radius: 16px;
            }}
        """)

    def _apply_cancel_button_style(self):
        is_dark = self.theme_name == "Dark"
        bg = "rgba(255, 255, 255, 0.10)" if is_dark else "rgba(0, 0, 0, 0.08)"
        color = "#A0AEC0" if is_dark else "#4A5568"
        hover_bg = "rgba(255, 255, 255, 0.16)" if is_dark else "rgba(0, 0, 0, 0.12)"
        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {color};
                border: none;
                border-radius: 18px;
                font-size: 13px;
                font-weight: 500;
                font-family: 'Segoe UI Variable Display', 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
        """)

    def _apply_save_button_style(self):
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2ECC71, stop:1 #27AE60);
                color: #FFFFFF;
                border: none;
                border-radius: 18px;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Segoe UI Variable Display', 'Segoe UI', 'Microsoft YaHei UI', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #27AE60, stop:1 #219653);
            }
        """)

    def set_quick_workdays(self):
        """一键设置为工作日开启 (周一至周五亮起，周六日暗沉)"""
        for i, btn in enumerate(self.day_buttons):
            btn.setChecked(i < 5)

    def set_quick_everyday(self):
        """一键设置为全周每天开启"""
        for btn in self.day_buttons:
            btn.setChecked(True)

    def save_and_close(self):
        self.result_schedule = [btn.isChecked() for btn in self.day_buttons]
        self.accept()

    def get_schedule(self):
        return self.result_schedule if self.result_schedule is not None else self.schedule_days
