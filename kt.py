from threading import Thread
from typing import Any
from ctypes import Structure, c_wchar, WinDLL, byref
from time import sleep
from sys import platform

# ----------------------------------------------------------------

try:
    if platform == "win32":
        from ctypes import wintypes
        from ctypes import pythonapi, c_long, py_object

        class KEY_EVENT_RECORD(Structure):
            _fields_ = [
                ("bKeyDown", wintypes.BOOL),
                ("wRepeatCount", wintypes.WORD),
                ("wVirtualKeyCode", wintypes.WORD),
                ("wVirtualScanCode", wintypes.WORD),
                ("uChar", c_wchar),
                ("dwControlKeyState", wintypes.DWORD)
            ]

        class INPUT_RECORD(Structure):
            _fields_ = [
                ("EventType", wintypes.WORD),
                ("Event", KEY_EVENT_RECORD)
            ]
    else:
        from os import kill
        from signal import SIGINT
except:
    raise ImportError

# ----------------------------------------------------------------

class KillableThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def WIN_UNBLOCK(self):
        kernel32: WinDLL = WinDLL("kernel32", use_last_error=True)
        h_stdin: Any = kernel32.GetStdHandle(-10)  # STD_INPUT_HANDLE
        event: INPUT_RECORD = INPUT_RECORD()
        event.EventType = 1  # KEY_EVENT
        event.Event.bKeyDown = True
        event.Event.wVirtualKeyCode = 0x0D  # ENTER
        event.Event.uChar = "\r"

        written: wintypes.DWORD = wintypes.DWORD(0)
        kernel32.WriteConsoleInputW(h_stdin, byref(event), 1, byref(written))

    def RAISE_E(self, exc: BaseException):
        self.WIN_UNBLOCK()

        pythonapi.PyThreadState_SetAsyncExc(
            c_long(self.ident),
            py_object(exc)
        )

    def UNIX_KILL(self):
        kill(self.ident, SIGINT)

    def KILLLL(self, exc: BaseException = SystemExit):
        if not self.is_alive():
            return

        if platform == "win32":
            while self.is_alive():
                try:
                    self.RAISE_E(exc)
                    sleep(0.05)
                except:
                    pass
        else:
            while self.is_alive():
                try:
                    self.UNIX_KILL()
                    sleep(0.05)
                except:
                    pass