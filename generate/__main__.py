import argparse
import logging

from .generators import (
    ContactInfoGenerator,
    EducationItemGenerator,
    TexIdentityGenerator,
)

logger = logging.getLogger()


def setup_logging(level):
    class CustomLogRecord(logging.LogRecord):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.origin = f"{self.name} ({self.threadName})"

    logging.setLogRecordFactory(CustomLogRecord)
    # noinspection SpellCheckingInspection,PyArgumentList

    root = logging.getLogger()
    root.setLevel(level)
    # noinspection PyArgumentList
    formatter = logging.Formatter(
        fmt="{asctime} - {levelname:8} - {origin:20} - {message}", style="{",
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root.handlers.clear()
    root.addHandler(handler)
    return root


def main(**kwargs):
    setup_logging(kwargs.get("logging_level", logging.INFO))

    EducationItemGenerator().generate_dir("modules/education-items")
    TexIdentityGenerator("toplevel", subdir="").generate_dir("modules")
    ContactInfoGenerator().generate_file("modules/contact-info.yaml")


def define_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--logging-level", type=logging.getLevelName)
    return parser


if __name__ == "__main__":
    arg_parser = define_cli()
    arg_namespace = arg_parser.parse_args()
    main(**vars(arg_namespace))
