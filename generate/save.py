import logging
import os
from typing import Callable, Sequence

from .config import ROOT_OUTPUT_PATH


logger = logging.getLogger(__name__)


def ensure_output_dir(path=ROOT_OUTPUT_PATH):
    path = os.path.normpath(path)  # avoid empty path at the end (foo/bar/)
    if not os.path.exists(path):
        ensure_output_dir(os.path.dirname(path))
        os.mkdir(path)
    elif not os.path.isdir(path):
        raise IOError("Output path {} already exists and is a file".format(path))
    return path


def save_output(
    save_func: Callable[[str], None],
    output_dir: str,
    output_name: str,
    identifiers: Sequence[str],
    file_extension: str,
    include_output_name: bool = False,
) -> None:
    """Greatest common denominator for output saving functions"""
    components = list(identifiers)
    if include_output_name:
        components.insert(0, output_name)
    name = "-".join(x.replace(" ", "_") for x in components if x)
    file_extension = file_extension.lstrip(".")
    filename = "{}.{}".format(name, file_extension)
    path = os.path.join(output_dir, filename)

    message = " ".join(
        [
            "Saving {}".format(output_name),
            "for {}".format(", ".join(identifiers)) if identifiers else "",
            "to {}".format(path),
        ]
    )
    logger.info(message)
    ensure_output_dir(output_dir)
    save_func(path)


def save_tex(tex: str, type_name: str, name: str, output_dir=ROOT_OUTPUT_PATH):
    def save_func(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(tex)

    save_output(
        save_func,
        output_dir=output_dir,
        output_name=type_name,
        identifiers=(name,),
        file_extension=".tex",
    )
