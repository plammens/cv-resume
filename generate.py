import argparse
import calendar
import datetime
import itertools as itt
import logging
import os
from collections import namedtuple
from typing import *

import yaml

ROOT_OUTPUT_PATH = os.path.abspath("generated")

FORMATS = ["cv", "resume"]
TEX_TEMPLATES = {
    "education": {
        "cv": r"""\cvchronoitem
{{ \textbf{{ {degree} {title} }} }}
{{ {institution} }}
{{{start-date} }}
{{ {end-date} }}
{{ {comment} }}
{{ {description} \textit{{ {grade[type]}: {grade[value]} }} }}
""",
        "resume": r"""\twentyitem
{{ \noindent {start-date} - \\ {end-date} \\({comment}) }}
{{ {degree} {title} }}
{{ {institution} }}
{{ {description} \textit{{ GPA: 19 (out of 22) }} }}
""",
    }
}

logger = logging.getLogger()

MonthDate = namedtuple("Date", ["year", "month"])


def generate_education_items(source_dir="modules/education-items"):
    date_fields = ["start-date", "end-date"]

    def parse_fields(data):
        parsed = data.copy()
        for date_field in date_fields:
            parsed[date_field] = parse_date(data[date_field])
        return parsed

    def format_fields_cv(data):
        formatted = data.copy()

        comment = data["comment"]
        formatted["comment"] = (
            f"Expected graduation: {comment['expected-end-date']}"
            if comment["expected-end-date"]
            else f"{comment['other']}"
        )

        for date_field in date_fields:
            date = data[date_field]
            formatted[date_field] = (
                f"{calendar.month_name[date.month]} {date.year}"
                if isinstance(date, MonthDate)
                else date
            )

        return formatted

    def format_fields_resume(data):
        formatted = data.copy()

        comment = data["comment"]
        formatted["comment"] = (
            f"exp. {comment['expected-end-date']}"
            if comment["expected-end-date"]
            else f"{comment['other']}"
        )

        institution = data["institution"]
        formatted["institution"] = (
            rf" \newline {institution}"
            if len(data["degree"]) + len(data["title"]) + len(institution) > 55
            and len(institution) < 30
            else institution
        )

        for date_field in date_fields:
            date = data[date_field]
            formatted[date_field] = (
                f"{calendar.month_name[date.month][:3]} {date.year}"
                if isinstance(date, MonthDate)
                else date
            )

        return formatted

    for file_name in os.listdir(source_dir):
        path = os.path.join(source_dir, file_name)
        name = file_name.rsplit(".")[0]
        logger.debug("Processing %s (%s)", name, path)
        with open(path) as f:
            data = parse_fields(yaml.full_load(f))

        for fmt in FORMATS:
            template = TEX_TEMPLATES["education"][fmt]
            fields = locals()[f"format_fields_{fmt}"](data)
            tex = template.format(**fields)
            save_tex(tex, name, os.path.join(ROOT_OUTPUT_PATH, fmt, "education"))


def parse_date(date: str) -> Union[MonthDate, str]:
    try:
        month, year = date.split()
        month = list(calendar.month_name).index(month.title())
        year = int(year)
        return MonthDate(year, month)
    except ValueError:
        return date


def ensure_output_dir(path=ROOT_OUTPUT_PATH):
    if not os.path.exists(path):
        ensure_output_dir(os.path.dirname(path))
        os.mkdir(path)
    elif not os.path.isdir(path):
        raise IOError("Output path {} already exists and is a file".format(path))
    return path


def save_output(save_func, output_dir, output_name, identifiers, file_extension):
    # type: (Callable[[str], None], str, str, Sequence[str], str) -> None
    """Greatest common denominator for output saving functions"""
    fname = "-".join(
        x.replace(" ", "_") for x in itt.chain([output_name], identifiers) if x
    )
    file_extension = file_extension.lstrip(".")
    full_fname = "{}.{}".format(fname, file_extension)
    path = os.path.join(output_dir, full_fname)

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


def save_tex(tex: str, name: str, output_dir=ROOT_OUTPUT_PATH):
    def save_func(path):
        with open(path, "w") as f:
            f.write(tex)

    save_output(
        save_func,
        output_dir=output_dir,
        output_name="",
        identifiers=(name,),
        file_extension=".tex",
    )


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

    generate_education_items()


def define_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--logging-level", type=logging.getLevelName)
    return parser


if __name__ == "__main__":
    arg_parser = define_cli()
    arg_namespace = arg_parser.parse_args()
    main(**vars(arg_namespace))
