#!/usr/bin/env python3
import time
import threading
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
import pyautogui
from pynput import keyboard
from pydantic import BaseModel, Field, confloat
import mss


pyautogui.FAILSAFE = False


@dataclass
class Anchor:
    position: Tuple[int, int]


class Settings(BaseModel):
    strength: confloat(ge=0.0, le=1.0) = Field(0.5, description="Pull intensity 0..1")
    smoothness: confloat(ge=0.0, le=1.0) = Field(0.2, description="Movement damping 0..1; higher is smoother")
    enabled: bool = Field(True, description="Magnet on/off")


class CursorMagnet:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._anchor: Optional[Anchor] = None
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def set_anchor_to_current(self) -> None:
        x, y = pyautogui.position()
        with self._lock:
            self._anchor = Anchor((int(x), int(y)))

    def clear_anchor(self) -> None:
        with self._lock:
            self._anchor = None

    def toggle_enabled(self) -> None:
        with self._lock:
            self.settings.enabled = not self.settings.enabled

    def adjust_strength(self, delta: float) -> None:
        with self._lock:
            new_value = float(np.clip(self.settings.strength + delta, 0.0, 1.0))
            self.settings.strength = new_value

    def adjust_smoothness(self, delta: float) -> None:
        with self._lock:
            new_value = float(np.clip(self.settings.smoothness + delta, 0.0, 1.0))
            self.settings.smoothness = new_value

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run_loop, name="cursor-magnet", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _run_loop(self) -> None:
        last_pos = None
        with mss.mss():
            pass  # Initialize display access once for Wayland environments
        while not self._stop_event.is_set():
            with self._lock:
                anchor = self._anchor
                enabled = self.settings.enabled
                strength = self.settings.strength
                smoothness = self.settings.smoothness
            if not enabled or anchor is None:
                time.sleep(0.01)
                continue

            cx, cy = pyautogui.position()
            ax, ay = anchor.position
            dx = ax - cx
            dy = ay - cy

            distance = (dx * dx + dy * dy) ** 0.5
            if distance < 1.0:
                time.sleep(0.005)
                continue

            raw_step_x = dx * strength
            raw_step_y = dy * strength

            damp = max(0.01, 1.0 - smoothness)
            step_x = raw_step_x * damp
            step_y = raw_step_y * damp

            step_x = float(np.clip(step_x, -50, 50))
            step_y = float(np.clip(step_y, -50, 50))

            target_x = int(round(cx + step_x))
            target_y = int(round(cy + step_y))

            try:
                pyautogui.moveTo(target_x, target_y, duration=0)
            except Exception:
                time.sleep(0.02)

            time.sleep(0.005)


def run_with_hotkeys(initial_strength: float, initial_smoothness: float) -> None:
    settings = Settings(strength=initial_strength, smoothness=initial_smoothness, enabled=True)
    magnet = CursorMagnet(settings)
    magnet.start()

    print("Cursor Magnet running. Hotkeys:")
    print("  Toggle magnet: Ctrl+Alt+M")
    print("  Set anchor:    Ctrl+Alt+S")
    print("  Clear anchor:  Ctrl+Alt+C")
    print("  Strength +/-:  Ctrl+Alt+Up / Ctrl+Alt+Down")
    print("  Smooth +/-:    Ctrl+Alt+Right / Ctrl+Alt+Left")
    print("  Quit:          Ctrl+Alt+Q")

    hotkey = keyboard.GlobalHotKeys({
        '<ctrl>+<alt>+m': magnet.toggle_enabled,
        '<ctrl>+<alt>+s': magnet.set_anchor_to_current,
        '<ctrl>+<alt>+c': magnet.clear_anchor,
        '<ctrl>+<alt>+up': lambda: magnet.adjust_strength(+0.05),
        '<ctrl>+<alt>+down': lambda: magnet.adjust_strength(-0.05),
        '<ctrl>+<alt>+right': lambda: magnet.adjust_smoothness(+0.05),
        '<ctrl>+<alt>+left': lambda: magnet.adjust_smoothness(-0.05),
        '<ctrl>+<alt>+q': lambda: (_stop_listener.set()),
    })

    global _stop_listener
    _stop_listener = threading.Event()

    with hotkey as hk:
        _stop_listener.wait()

    magnet.stop()


def parse_args() -> Tuple[float, float]:
    import argparse
    parser = argparse.ArgumentParser(description='Cursor Magnet - accessibility cursor helper')
    parser.add_argument('--strength', type=float, default=0.5, help='Pull intensity 0..1 (default 0.5)')
    parser.add_argument('--smoothness', type=float, default=0.2, help='Movement damping 0..1 (default 0.2)')
    args = parser.parse_args()

    s = float(np.clip(args.strength, 0.0, 1.0))
    sm = float(np.clip(args.smoothness, 0.0, 1.0))
    return s, sm


if __name__ == '__main__':
    s, sm = parse_args()
    run_with_hotkeys(s, sm)
