
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
        "input_border": "#0D000000",    # 5% black

        # Dropdown Specific (Light)
        "dropdown_hover_bg": "#F0FFF4", # Light Green Bg
        "dropdown_hover_text": "#2F855A" # Dark Green Text
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
        "input_border": "#12FFFFFF",    # 7% white (Subtle, non-intrusive)

        # Dropdown Specific (Dark)
        "dropdown_hover_bg": "#102F25", # Very Dark Green
        "dropdown_hover_text": "#48BB78" # Light Green Text
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
    
    /* QComboBox Main Input Area */
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
    QComboBox::down-arrow {{
        image: none; /* Can add custom arrow if needed, but keeping simple for now */
        border: none;
    }}

    /* Dropdown List Container (Floating Card Effect) */
    /* Dropdown List Container (Floating Card Effect) */
    QComboBox QAbstractItemView {{
        background-color: {t['bg_color']}; 
        border: 2px solid {t['glass_border']};
        /* border-radius: 12px;  <-- REMOVED per User Request (Fig 2) to avoid white corner artifacts */
        padding: 4px;
        min-width: 100px;
        outline: none;
        color: {t['text_primary']};
    }}
    
    QListView {{
        background-color: {t['bg_color']};
        border: none;
        outline: none;
        color: {t['text_primary']};
    }}

    /* Individual Items (Capsule Look) */
    QComboBox QAbstractItemView::item {{
        height: 32px;
        border-radius: 8px;
        padding-left: 10px;
        margin: 2px 4px;
        color: {t['text_primary']};
        background: transparent;
    }}

    /* Hover Interaction */
    QComboBox QAbstractItemView::item:hover {{
        background-color: {t['dropdown_hover_bg']};
        color: {t['dropdown_hover_text']};
        padding-left: 15px; /* Motion Shift */
        font-weight: bold;
    }}

    /* Selected Item interaction */
    QComboBox QAbstractItemView::item:selected {{
        background-color: {t['dropdown_hover_bg']};
        color: {t['dropdown_hover_text']};
        font-weight: bold;
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
        margin-right: 2px; /* Pull away from edge */
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
         height: 0px;
    }}
    
    QScrollArea {{
        background: transparent;
        border: none;
    }}
    """
