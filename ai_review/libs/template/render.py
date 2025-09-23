import re
from typing import Mapping


def render_template(text: str, values: Mapping[str, str], placeholder: str = "<<{value}>>") -> str:
    regex_pattern = re.escape(placeholder).replace(r"\{value\}", r"([\w\.-]+)")
    regex = re.compile(regex_pattern)

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        return values.get(key, match.group(0))

    return regex.sub(replacer, text)
