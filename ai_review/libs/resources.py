import importlib.metadata
import importlib.resources
import os
import pathlib
import shutil
import tempfile


def load_resource(package: str, filename: str, fallback: str | None = None) -> pathlib.Path:
    try:
        traversable = importlib.resources.files(package) / filename
        if isinstance(traversable, pathlib.Path):
            return traversable

        tmp_dir = pathlib.Path(tempfile.gettempdir())
        tmp_file = tmp_dir / filename
        with traversable.open("rb") as src, tmp_file.open("wb") as dst:
            shutil.copyfileobj(src, dst)
        return tmp_file
    except importlib.metadata.PackageNotFoundError:
        if fallback:
            return pathlib.Path(os.path.join(os.getcwd(), fallback))

        raise
