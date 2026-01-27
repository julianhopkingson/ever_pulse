# Ever Pulse

[中文文档](README_cn.md)

**v2.2 (EverPulse - Tech Navy Edition)**

A modernized, premium utility designed to keep your Windows session active. Rebuilt with **PySide6** and "Crystal Navy" aesthetics.

![UI Preview](assets/v2.0_ui_preview.png)

*(Note: v2.2 UI updated with Ever Pulse branding)*

## Features

- **Premium UI**: "Crystal Green" aesthetic with Glassmorphism, real-time Dark/Light mode, and smooth animations.
- **Smart Idle Detection**: Only moves mouse when you are idle (Idle Threshold setting).
- **Scheduled Operation**: Auto-start and auto-stop at defined working hours.
- **Invisible 'Jiggle'**: Micro-movements are practically invisible but keep status 'Online'.
- **Bilingual Support**: Instant switching between **English** and **Chinese**.
- **Portable & Persistent**: Single EXE file, saves settings permanently to `config/config.ini`.
- **High Stability**: Robust `QPainter` rendering (ARGB Hex) prevents black screens and glitches.

## Usage

1.  **Run directly**: Double-click `dist/ever_pulse.exe`.
    *(Note: If updating, run `taskkill /F /IM ever_pulse.exe` first)*

2.  **Build from Source**:
    ```bash
    # Install dependencies
    pip install -r requirements.txt
    
    # Build executable (clean build)
    pyinstaller main.spec --clean --noconfirm
    ```
3.  Set your desired **Start Time** and **End Time**.
4.  Click **Start**.

## Configuration

> **Note**: The configuration file is automatically generated at `config/config.ini`.

- **Interval**: How often the mouse moves (in seconds).
- **Idle Time**: How long you must be inactive before the tool starts moving the mouse.
- **Direction & Pixels**: Customize the movement direction and distance.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
