# Cursor Magnet (Accessibility Tool)

A general-purpose cursor assistance tool that lets users set an on-screen anchor and gently "pull" the mouse cursor towards it, with configurable strength and smoothness. Intended to assist users with motor impairments. Not game-specific.

## Features
- Set/clear a magnet anchor anywhere on screen
- Adjustable **strength** (pull intensity)
- Adjustable **smoothness** (movement dampening)
- Global hotkeys to toggle and adjust settings on-the-fly

## Hotkeys (default)
- Toggle magnet on/off: `Ctrl+Alt+M`
- Set anchor at current cursor: `Ctrl+Alt+S`
- Clear anchor: `Ctrl+Alt+C`
- Increase strength: `Ctrl+Alt+Up`
- Decrease strength: `Ctrl+Alt+Down`
- Increase smoothness: `Ctrl+Alt+Right`
- Decrease smoothness: `Ctrl+Alt+Left`
- Quit: `Ctrl+Alt+Q`

## Usage
```bash
./cursor_magnet --strength 0.5 --smoothness 0.2
```

## Build
```bash
pip install -r requirements.txt
pyinstaller -F magnet.py -n cursor_magnet
```
The binary will be in `dist/cursor_magnet`.

## Notes
- Requires X11/Wayland desktop with permission for global hotkeys and cursor control.
- Not designed for or endorsed for competitive gameplay. This is an accessibility utility.
