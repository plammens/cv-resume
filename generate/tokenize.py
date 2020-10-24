import re
from abc import ABCMeta, abstractmethod
from typing import Callable, ClassVar, Dict, Sequence

URL_SEARCH_PATTERN = re.compile(r"((?:http[s]://|mailto:)\S+)")
URL_PATTERN = re.compile(r"(?P<protocol>http[s]://|mailto:)(?P<address>\S+)")


class Token(metaclass=ABCMeta):
    formatters: ClassVar[Dict[str, Callable[["Token"], str]]]

    def __init__(self, text: str, *args):
        self._init_args = (text,) + args
        self.text = text

    @abstractmethod
    def __format__(self, format_spec):
        """Format for inclusion in LaTeX code."""
        return self.formatters[format_spec](self)

    def __str__(self):
        return self.text

    def __repr__(self):
        args_fmt = ", ".join(repr(arg) for arg in self._init_args)
        return f"{self.__class__.__name__}({args_fmt})"


class PlainTextToken(Token):
    def __init__(self, text: str):
        super().__init__(text)

    def __format__(self, format_spec):
        return self.text


class URLToken(Token):
    def __init__(self, url: str):
        super().__init__(url)
        groups = re.fullmatch(URL_PATTERN, url).groupdict()
        for key, value in groups.items():
            setattr(self, key, value)

    def __format__(self, format_spec):
        return rf"\href{{{self.protocol}{self.address}}}{{{self.address}}}"


class TokenizedText:
    def __init__(self, token_list: Sequence[Token]):
        self.token_list = token_list

    def __format__(self, format_spec):
        s = "".join(format(token, format_spec) for token in self.token_list)
        return format(s, format_spec)

    def __repr__(self):
        return f"TokenizedText({repr(self.token_list)})"


def tokenize(text: str) -> TokenizedText:
    def select_token_class(token_text: str):
        return (
            URLToken if re.fullmatch(URL_SEARCH_PATTERN, token_text) else PlainTextToken
        )

    split_list = re.split(URL_SEARCH_PATTERN, text)
    tokens = [select_token_class(txt)(txt) for txt in split_list]
    return TokenizedText(tokens)
