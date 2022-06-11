from pypinyin import STYLE_FIRST_LETTER
from pypinyin_dict.phrase_pinyin_data import cc_cedict
from pypinyin import pinyin as _pinyin
from functools import partial
from typing import Optional

cc_cedict.load()

pinyin = partial(_pinyin, style=STYLE_FIRST_LETTER, heteronym=True, strict=True, errors="ignore")


class Match:
    __slots__ = ("status", "st", "pn", "start", "end")
    
    def __init__(
            self, status: bool,
            st: str = "",
            pn: Optional[list[list[str]]] = None,
            start: int = 0,
            end: int = 0
    ):
        self.status: bool = status
        self.st: str = st
        self.pn: Optional[list[list[str]]] = pn
        self.start: int = start
        self.end: int = end

    def __bool__(self) -> bool:
        return self.status

    @staticmethod
    def startswith(st: str, pn: list[list[str]]) -> "Match":
        if not pn:
            return Match(status=False, st=st, pn=pn)
        res = Match(status=True, st=st, pn=pn, start=0)
        for i, letter in enumerate(pn):
            try:
                if st[i] not in letter:
                    res.status = False
                    res.end = i - 1
            except IndexError:
                break
        return res


# def matchpinyin(st: str, pn: list[list[str]]) -> bool:
#     if not pn:
#         return False
#     res = True
#     for i, letter in enumerate(pn):
#         try:
#             if st[i] not in letter:
#                 res = False
#         except IndexError:
#             break
#     return res
