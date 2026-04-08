from typing import Literal, TextIO, List
from time import strftime, localtime
from atexit import register


LEVELS: List[str] = ["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"]
type LevelType = Literal["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"]

class Logger:
    def __init__(
        self,
        path: str = "latest.log",
        level: LevelType = "INFO"
    ):
        self.path: str = path
        self.level: LevelType = level

        with open(self.path, mode="w", encoding="utf-8") as f:
            pass

        self.handle: TextIO = open(self.path, mode="a", encoding="utf-8", buffering=1)
        register(self.exit)

    def log(
        self,
        *texts: object,
        level: LevelType,
        thread: str,
        **kwargs
    ):
        if LEVELS.index(level) < LEVELS.index(self.level):
            return

        for text in texts:
            text: str = f"[{strftime("%H:%M:%S", localtime())}] [{thread}/{level}]: {text}\n"
            self.handle.write(text)
            self.handle.flush()

            print(text, end="", **kwargs)

    def set(self, level: LevelType):
        self.level = level

    def exit(self):
        if hasattr(self, "handle") and self.handle and not self.handle.closed:
            self.handle.close()

    def trace(
        self,
        *texts: object,
        thread: str = "main",
        **kwargs,
    ):
        self.log(level = "TRACE", thread = thread, *texts, **kwargs)

    def debug(
        self,
        *texts: object,
        thread: str = "main",
        **kwargs,
    ):
        self.log(level = "DEBUG", thread = thread, *texts, **kwargs)

    def info(
        self,
        *texts: object,
        thread: str = "main",
        **kwargs,
    ):
        self.log(level = "INFO", thread = thread, *texts, **kwargs)

    def warn(
        self,
        *texts: object,
        thread: str = "main",
        **kwargs,
    ):
        self.log(level = "WARN", thread = thread, *texts, **kwargs)

    def error(
        self,
        *texts: object,
        thread: str = "main",
        **kwargs,
    ):
        self.log(level = "ERROR", thread = thread, *texts, **kwargs)

    def fatal(
        self,
        *texts: object,
        thread: str = "main",
        **kwargs,
    ):
        self.log(level = "FATAL", thread = thread, *texts, **kwargs)