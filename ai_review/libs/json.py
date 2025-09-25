import re

CONTROL_CHARS_RE = re.compile(r"[\x00-\x1F]")


def sanitize_json_string(raw: str) -> str:
    def replace(match: re.Match) -> str:
        char = match.group()
        match char:
            case "\n":
                return "\\n"
            case "\r":
                return "\\r"
            case "\t":
                return "\\t"
            case _:
                return f"\\u{ord(char):04x}"

    return CONTROL_CHARS_RE.sub(replace, raw)
