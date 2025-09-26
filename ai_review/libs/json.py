import re

CONTROL_CHARS_RE = re.compile(r"[\x00-\x1F]")
REPLACEMENTS = {
    "\n": "\\n",
    "\r": "\\r",
    "\t": "\\t",
}


def sanitize_json_string(raw: str) -> str:
    def replace(match: re.Match) -> str:
        char = match.group()
        return REPLACEMENTS.get(char, f"\\u{ord(char):04x}")

    return CONTROL_CHARS_RE.sub(replace, raw)
