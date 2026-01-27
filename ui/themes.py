
THEMES = {
    "Light": {
        "bg_color": "#ECF0F1",          # Light Grey-Blue Base
        "glass_bg": "#AAFFFFFF",        # 66% white
        "glass_border": "#CCFFFFFF",    # 80% white
        
        "text_primary": "#2C3E50",      # Deep Midnight Blue
        "text_secondary": "#7F8C8D",    # Grey
        "text_inverse": "#FFFFFF",
        
        "primary_gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2ECC71, stop:1 #27AE60)", # Emerald Green
        "primary_shadow": "#662ECC71",
        "accent": "#27AE60",
        
        "input_bg": "#80FFFFFF",        # 50% white
        "input_border": "#0D000000"     # 5% black
    },
    "Dark": {
        "bg_color": "#0B192C",          # Deep Navy Blue (More distinct color)
            "glass_bg": "#B31B263B",        # 70% Muted Navy
        "glass_border": "#4DFFFFFF",    # 30% white (High definition edge)
        
        "text_primary": "#E2E8F0",      # Soft Silver-White (Modern tech feel)
        "text_secondary": "#A0AEC0",    # Light Silver/Grey
        "text_inverse": "#121417",
        
        "primary_gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2ECC71, stop:1 #27AE60)",
        "primary_shadow": "#332ECC71",
        "accent": "#2ECC71",
        
        "input_bg": "#0F1A2D",          # Lighter Navy Slot (Clearly blue)
        "input_border": "#12FFFFFF"     # 7% white (Subtle, non-intrusive)
    }
}

def get_stylesheet(theme_name):
    t = THEMES.get(theme_name, THEMES["Light"])
    
    return f"""
    QMainWindow {{
        background-color: {t['bg_color']};
    }}
    QWidget {{
        font-family: 'Segoe UI Variable Display', 'Segoe UI', 'Montserrat', 'Microsoft YaHei UI', sans-serif;
        font-size: 14px;
        color: {t['text_primary']};
    }}
    
    QLabel {{
        background: transparent;
        color: {t['text_primary']};
    }}
    QLabel#Title {{
        font-size: 26px;
        font-weight: 800;
        color: {t['text_primary']};
        background: transparent;
        letter-spacing: 1px;
    }}
    QLabel#Subtitle {{
        font-size: 13px;
        font-weight: 500;
        color: {t['text_secondary']};
    }}
    
    QLineEdit, QSpinBox {{
        background-color: {t['input_bg']};
        border: 1px solid {t['input_border']};
        border-radius: 10px;
        padding: 8px 12px;
        color: {t['text_primary']};
        selection-background-color: {t['accent']};
    }}
    QLineEdit:focus, QSpinBox:focus {{
        border: 1px solid {t['accent']};
    }}
    
    QComboBox {{
        background-color: {t['input_bg']};
        border: 1px solid {t['input_border']};
        border-radius: 10px;
        padding: 5px 12px;
        color: {t['text_primary']};
    }}
    QComboBox:hover {{
        border: 1px solid {t['accent']};
    }}
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 30px;
        border: none;
    }}
    QComboBox QAbstractItemView {{
        background-color: {t['bg_color']}; 
        border: 1px solid {t['glass_border']};
        selection-background-color: {t['accent']};
        selection-color: {t['text_inverse']};
        border-radius: 10px;
        padding: 5px;
        outline: none;
        color: {t['text_primary']};
    }}
    
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {t['accent']};
        min-height: 20px;
        border-radius: 3px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
         height: 0px;
    }}
    
    QScrollArea {{
        background: transparent;
        border: none;
    }}
    """
