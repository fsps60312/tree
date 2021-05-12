from __future__ import annotations


# class AnsiCode(str, Enum):
#     dircolor = '00;38;5;33'
#     bold = '1'
#     dim = '2'
#     italic = '3'
#     underline = '4'
# class Ansi:
#     __prefix: str = ''
#     __suffix: Final[str] = '\x1b[m'
#
#     def set(self, code: Union[str, AnsiCode]) -> Ansi:
#         self.__prefix += '\x1b[' + code + 'm'
#         return self
#
#     def format(self, s: str) -> str:
#         return self.__prefix + s + self.__suffix


class Ansi:
    @staticmethod
    def bold(s: str) -> str:
        return '\x1b[1m' + s + '\x1b[21m'

    @staticmethod
    def faint(s: str) -> str:
        return '\x1b[2m' + s + '\x1b[22m'

    @staticmethod
    def italic(s: str) -> str:
        return '\x1b[3m' + s + '\x1b[23m'

    @staticmethod
    def underline(s: str) -> str:
        return '\x1b[4m' + s + '\x1b[24m'

    @staticmethod
    def blink(s: str) -> str:
        return '\x1b[5m' + s + '\x1b[25m'

    @staticmethod
    def dircolor(s: str) -> str:
        return '\x1b[38;5;33m' + s + '\x1b[39;49m'
