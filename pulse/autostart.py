import sys
from pathlib import Path

from .config import BASE_DIR
from .constants import APP_NAME

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def supported() -> bool:
    return sys.platform == "win32"


def _command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    exe = Path(sys.executable)
    windowless = exe.with_name("pythonw.exe")
    interpreter = windowless if windowless.exists() else exe
    return f'"{interpreter}" "{BASE_DIR / "main.py"}"'


def set_enabled(enabled: bool) -> None:
    if not supported():
        return
    import winreg

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _command())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
