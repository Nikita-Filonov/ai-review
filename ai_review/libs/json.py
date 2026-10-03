import re
from json import JSONDecodeError, JSONDecoder

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


def extract_json_objects(raw: str) -> list[str]:
    decoder = JSONDecoder()
    objects: list[str] = []
    position = 0

    while (start := raw.find("{", position)) >= 0:
        try:
            value, end = decoder.raw_decode(raw, start)
        except JSONDecodeError:
            position = start + 1
            continue

        if isinstance(value, dict):
            objects.append(raw[start:end])

        position = end

    return objects
