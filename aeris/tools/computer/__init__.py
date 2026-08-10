"""Computer control foundation tools."""

from .mouse import MouseTool
from .keyboard import KeyboardTool
from .app import AppTool
from .window import WindowTool
from .fs import FileSystemTool
from .clipboard import ClipboardTool
from .screen import ScreenTool
from .browser import BrowserTool
from .system import SystemTool
from .command import CommandTool


def get_all_computer_tools():
    return [
        MouseTool(),
        KeyboardTool(),
        AppTool(),
        WindowTool(),
        FileSystemTool(),
        ClipboardTool(),
        ScreenTool(),
        BrowserTool(),
        SystemTool(),
        CommandTool(),
    ]
