import hashlib
from datetime import datetime


def make_artifact_id(text: str) -> str:
    sha = hashlib.sha1(text.encode()).hexdigest()[:8]
    ts = datetime.utcnow().strftime("%Y.%m.%d_%H-%M-%S")
    return f"{ts}_{sha}"
