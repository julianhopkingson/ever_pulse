import sys
import os
import datetime
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QSpinBox, QComboBox, 
                               QFrame, QCheckBox, QPushButton, QScrollArea,
                               QGraphicsDropShadowEffect, QApplication, QListView)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon

from core.config_mgr import ConfigManager, resource_path
from core.i18n import I18n
from ui.themes import get_stylesheet, THEMES
from ui.widgets import GreenPillButton, CrystalCard, SunMoonToggle, parse_color
from ui.worker import AutomationWorker
from ui.window_effect import window_effect

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Default development path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        config_root = project_root
        asset_root = project_root

        if getattr(sys, 'frozen', False):
            # Frozen (EXE) Mode:
            # 1. Config Persistence: Use executable dir (Writeable)
            config_root = os.path.dirname(sys.executable)
            # 2. Assets: Use temp dir (Read-only bundled resources)
            asset_root = sys._MEIPASS 

        self.config_mgr = ConfigManager(config_root)
        self.i18n = I18n(os.path.join(asset_root, "assets"))
        
        self.setWindowTitle("Ever Pulse")
        self.resize(500, 780) 
        
        icon_path = resource_path(os.path.join("assets", "ever-pulse.ico"))
        self.setWindowIcon(QIcon(icon_path))

        self.worker = None
        self.current_theme_name = self.config_mgr.get("theme") or "Light"

        self.init_ui()
        self.load_settings_to_ui()
        self.retranslateUi()
        self.apply_theme(self.current_theme_name, force=True) 

    def init_ui(self):
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(12) 
        self.main_layout.setContentsMargins(15, 20, 15, 15) # Reverted to Narrow Margins (Wide Cards)

        # 1. Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(5, 10, 5, 10)
        
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        
        self.title_label = QLabel("Mouse Mover")
        self.title_label.setObjectName("Title")
        self.subtitle_label = QLabel("Keep your session active")
        self.subtitle_label.setObjectName("Subtitle")
        
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.subtitle_label)
        
        self.theme_toggle = SunMoonToggle(theme_name=self.current_theme_name)
        self.theme_toggle.clicked.connect(self.toggle_theme)

        header_layout.addLayout(title_box)
        header_layout.addStretch()
        header_layout.addWidget(self.theme_toggle)
        self.main_layout.addLayout(header_layout)

        self.lang_card = CrystalCard(self.current_theme_name)
        l_layout = QHBoxLayout(self.lang_card)
        l_layout.setContentsMargins(30, 25, 30, 25) # Large Internal Padding
        self.lbl_lang = QLabel("Language")
        self.combo_lang = QComboBox()
        self.combo_lang.setView(QListView())
        self.combo_lang.addItems(self.i18n.get_available_languages())
        self.combo_lang.currentTextChanged.connect(self.change_language)
        l_layout.addWidget(self.lbl_lang); l_layout.addStretch(); l_layout.addWidget(self.combo_lang)
        self.main_layout.addWidget(self.lang_card)

        self.time_card = CrystalCard(self.current_theme_name)
        t_layout = QVBoxLayout(self.time_card)
        t_layout.setContentsMargins(30, 25, 30, 25) # Large Internal Padding
        
        def add_row(parent, label_text, widgets):
            row = QHBoxLayout()
            lbl = QLabel(label_text); row.addWidget(lbl); row.addStretch()
            for w in widgets: row.addWidget(w)
            parent.addLayout(row); return lbl

        self.start_h = self.create_sb(0, 23); self.start_m = self.create_sb(0, 59); self.start_s = self.create_sb(0, 59)
        self.lbl_start = add_row(t_layout, "Start", [self.start_h, QLabel(":"), self.start_m, QLabel(":"), self.start_s])
        self.end_h = self.create_sb(0, 23); self.end_m = self.create_sb(0, 59); self.end_s = self.create_sb(0, 59)
        self.lbl_end = add_row(t_layout, "End", [self.end_h, QLabel(":"), self.end_m, QLabel(":"), self.end_s])
        self.interval_spin = self.create_sb(1, 3600, 75); self.lbl_interval = add_row(t_layout, "Interval", [self.interval_spin])
        self.threshold_spin = self.create_sb(1, 600, 75); self.lbl_idle = add_row(t_layout, "Idle", [self.threshold_spin])
        self.main_layout.addWidget(self.time_card)

        self.mouse_card = CrystalCard(self.current_theme_name)
        m_layout = QHBoxLayout(self.mouse_card)
        m_layout.setContentsMargins(30, 25, 30, 25) # Large Internal Padding
        self.lbl_dir = QLabel("Direction"); self.combo_dir = QComboBox(); self.combo_dir.setView(QListView()); self.combo_dir.setFixedWidth(90)
        self.lbl_pix = QLabel("Pixels"); self.pixel_spin = self.create_sb(1, 100, 60)
        m_layout.addWidget(self.lbl_dir); m_layout.addWidget(self.combo_dir); m_layout.addStretch()
        m_layout.addWidget(self.lbl_pix); m_layout.addWidget(self.pixel_spin)
        self.main_layout.addWidget(self.mouse_card)
        
        # 3. Action
        self.start_btn = GreenPillButton("START", self.current_theme_name)
        self.start_btn.clicked.connect(self.toggle_automation)
        self.main_layout.addWidget(self.start_btn)
        
        self.log_card = CrystalCard(self.current_theme_name)
        log_card_layout = QVBoxLayout(self.log_card)
        log_card_layout.setContentsMargins(25, 20, 25, 20)
        
        self.lbl_log_title = QLabel("Activity Log")
        self.lbl_log_title.setObjectName("Subtitle")
        log_card_layout.addWidget(self.lbl_log_title)
        
        self.log_area = QScrollArea()
        self.log_area.setWidgetResizable(True)
        self.log_area.setFixedHeight(120) 
        self.log_content = QLabel("Ready.")
        self.log_content.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.log_content.setWordWrap(True)
        self.log_area.setWidget(self.log_content)
        
        log_card_layout.addWidget(self.log_area)
        self.main_layout.addWidget(self.log_card)
        
    def create_sb(self, mi, ma, w=55):
        s = QSpinBox(); s.setRange(mi, ma); s.setButtonSymbols(QSpinBox.NoButtons); s.setAlignment(Qt.AlignCenter); s.setFixedWidth(w); return s

    def retranslateUi(self):
        _ = self.i18n.get
        self.setWindowTitle(_("app_title")); self.title_label.setText(_("app_title"))
        sub = _("subtitle"); self.subtitle_label.setText(sub if sub and sub != "subtitle" else "Keep active")
        self.lbl_lang.setText(_("language")); self.lbl_start.setText(_("start_time")); self.lbl_end.setText(_("end_time"))
        self.lbl_interval.setText(_("interval")); self.lbl_idle.setText(_("inactivity_time"))
        self.lbl_dir.setText(_("direction")); self.lbl_pix.setText(_("pixels"))
        self.start_btn.setText(_("stop") if self.worker and self.worker.isRunning() else _("start"))
        self.lbl_log_title.setText(_("log_title"))
        # Refresh current log line if it's a fixed state
        current_log = self.log_content.text().split('\n')[-1]
        if "Ready" in current_log or "就绪" in current_log:
             self.log_content.setText(_("log_ready"))
        
        self.combo_dir.blockSignals(True); self.combo_dir.clear(); self.combo_dir.addItems([_("up"), _("down"), _("left"), _("right")]); self.combo_dir.blockSignals(False)
        
    def change_language(self, text):
        if self.i18n.set_language(text): 
            self.retranslateUi()
            self.config_mgr.set("language", text)
            self.log_message(f"Language changed to {text}")

    def toggle_theme(self):
        new_theme = "Dark" if self.theme_toggle.isChecked() else "Light"
        self.apply_theme(new_theme)
        self.log_message(f"Theme changed to {new_theme}")

    def apply_theme(self, theme_name, force=False):
        if not force and self.current_theme_name == theme_name: return
        self.current_theme_name = theme_name
        self.config_mgr.set("theme", theme_name)
        
        # Atomic styling update
        self.setStyleSheet(get_stylesheet(theme_name))
        for card in self.findChildren(CrystalCard): card.set_theme(theme_name)
        self.start_btn.set_theme(theme_name)
        self.theme_toggle.set_theme_state(theme_name)
        
        t = THEMES[theme_name]
        self.log_content.setStyleSheet(f"color: {t['text_primary']}; padding: 8px;")

        # Apply Title Bar Color (Windows DWM)
        try:
            window_effect.set_title_bar_color(self.winId(), t['bg_color'])
        except Exception as e:
            print(f"DWM Error: {e}")

    def load_settings_to_ui(self):
        c = self.config_mgr
        self.start_h.setValue(c.get('start_hour', int)); self.start_m.setValue(c.get('start_minute', int)); self.start_s.setValue(c.get('start_second', int))
        self.end_h.setValue(c.get('end_hour', int)); self.end_m.setValue(c.get('end_minute', int)); self.end_s.setValue(c.get('end_second', int))
        self.interval_spin.setValue(c.get('interval', int)); self.threshold_spin.setValue(c.get('activity_threshold', int))
        lang = c.get('language'); idx = self.combo_lang.findText(lang)
        if idx >= 0: self.combo_lang.setCurrentIndex(idx)
        dirs = ["Up", "Down", "Left", "Right"]
        try: self.combo_dir.setCurrentIndex(dirs.index(c.get('direction')))
        except: pass
        self.pixel_spin.setValue(c.get('pixels', int))
        
        # Restore window position
        x = c.get('window_x', int)
        y = c.get('window_y', int)
        if x is not None and y is not None:
            self.move(x, y)

    def save_ui_to_config(self):
        c = self.config_mgr
        c.set("start_hour", self.start_h.value()); c.set("start_minute", self.start_m.value()); c.set("start_second", self.start_s.value())
        c.set("end_hour", self.end_h.value()); c.set("end_minute", self.end_m.value()); c.set("end_second", self.end_s.value())
        c.set("interval", self.interval_spin.value()); c.set("activity_threshold", self.threshold_spin.value())
        c.set("language", self.combo_lang.currentText())
        dirs = ["Up", "Down", "Left", "Right"]
        idx = self.combo_dir.currentIndex()
        if 0 <= idx < 4: c.set("direction", dirs[idx])
        c.set("pixels", self.pixel_spin.value()); c.set("theme", self.current_theme_name)
        
        # Save window position
        c.set("window_x", self.pos().x())
        c.set("window_y", self.pos().y())

    def toggle_automation(self):
        if self.worker and self.worker.isRunning(): self.stop_automation()
        else: self.start_automation()

    def start_automation(self):
        self.save_ui_to_config(); self.config_mgr.save()
        self.worker = AutomationWorker(self.config_mgr)
        self.worker.status_updated.connect(self.log_message)
        self.worker.error_occurred.connect(self.log_error)
        self.worker.start(); self.retranslateUi(); self.log_message("Started.")

    def stop_automation(self):
        if self.worker: self.worker.stop(); self.worker = None
        self.retranslateUi(); self.log_message("Stopped.")

    def log_message(self, msg):
        # Localization Hook
        ts = datetime.datetime.now().strftime("[%H:%M:%S]")
        translated_msg = self._translate_log(msg)
        
        txt = self.log_content.text()
        if len(txt) > 2000: txt = txt[-1000:] 
        self.log_content.setText(txt + f"\n{ts} {translated_msg}")
        vsb = self.log_area.verticalScrollBar(); vsb.setValue(vsb.maximum())

    def _translate_log(self, msg):
        _ = self.i18n.get
        if msg == "Started.": return _("log_started")
        if msg == "Stopped.": return _("log_stopped")
        if msg == "Ready.": return _("log_ready")
        if "Moved at" in msg: return _("log_moved").format(msg.split(" at ")[-1])
        if "Outside working hours" in msg: return _("log_waiting")
        if "Theme changed to" in msg: return _("log_theme_changed").format(msg.split(" to ")[-1])
        if "Language changed to" in msg: return _("log_lang_changed").format(msg.split(" to ")[-1])
        if "User active" in msg: 
            # Parse "User active (idle 0.0s), skipping..."
            try:
                parts = msg.split("idle ")[1].split("s)")[0]
                return _("status_skipped").format(parts)
            except:
                return msg
        return msg

    def log_error(self, msg): 
        if msg.startswith("Config Error: "):
            content = msg.split(": ", 1)[1]
            translated = self.i18n.get("log_config_error").format(content)
            self.log_message(translated)
        else:
            prefix = self.i18n.get("log_error_prefix")
            self.log_message(f"{prefix}{msg}")
        self.stop_automation()
    def closeEvent(self, ev): self.stop_automation(); self.save_ui_to_config(); self.config_mgr.save(); super().closeEvent(ev)
