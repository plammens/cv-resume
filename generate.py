import argparse
import calendar
import logging
import os
from abc import ABCMeta, abstractmethod
from collections import defaultdict, namedtuple
from typing import *
from typing import IO

import yaml


ROOT_OUTPUT_PATH = os.path.abspath("generated")
FORMATS = ["cv", "resume"]
# fmt: off
TEX_TEMPLATES = {
    "education": {
        "cv": \
r"""
\cvchronoitem
{{ {degree} {title} }}
{{ {institution} }}
{{ {start-date} }}
{{ {end-date} }}
{{ {comment} }}
{{ {description} \textit{{ {grade[type]}: {grade[value]} }} }}
""",
        "resume": \
r"""
\twentyitem
{{ \noindent {start-date} - \\ {end-date} \\({comment}) }}
{{ {degree} {title} }}
{{ {institution} }}
{{ {description} \textit{{ GPA: 19 (out of 22) }} }}
""",
    },
    "work": {
        "cv": \
r"""
\cvchronoitem
{{ {job-title} }}
{{ {company} }}
{{ {start-date} }}
{{ {end-date} }}
{{ {comment} }}
{{ {description} }}
""",
        "resume": None,
    },
}
# fmt: on
DATE_FIELDS = ["start-date", "end-date"]

logger = logging.getLogger()

# utility types
MonthDate = namedtuple("Date", ["year", "month"])

# type aliases
Data = Dict[str, Any]
FormattedFields = Dict[str, str]
Parser = Callable[[Data], Data]
Formatter = Callable[[Data], FormattedFields]


class AbstractTexModuleGenerator(metaclass=ABCMeta):
    def __init__(self, module_type: str, formatters: Dict[str, Formatter]):
        self.module_type = module_type
        self.formatters = formatters

    @abstractmethod
    def read(self, source: IO) -> Data:
        pass

    @abstractmethod
    def parse(self, data: Data) -> Data:
        pass

    @abstractmethod
    def generate(self, parsed_data: Data, fmt: str) -> str:
        pass

    @abstractmethod
    def save(self, generated_tex: str, *, name: str, fmt: str):
        pass


class FileToFileGenerator(AbstractTexModuleGenerator, metaclass=ABCMeta):
    def __init__(
        self,
        module_type: str,
        formatters: Dict[str, Formatter],
        subdir: Optional[str] = None,
    ):
        super().__init__(module_type, formatters)
        self.subdir = subdir or self.module_type

    def save(self, generated_tex: str, *, name: str, fmt: str):
        save_tex(
            generated_tex,
            type_name=f"{fmt} TeX",
            name=name,
            output_dir=os.path.join(ROOT_OUTPUT_PATH, fmt, self.subdir),
        )

    def generate_all(self, source_dir: str) -> None:
        for file_name in os.listdir(source_dir):
            path = os.path.join(source_dir, file_name)
            name = file_name.rsplit(".")[0]
            if not os.path.isfile(path):
                continue

            logger.debug("Processing %s (%s)", name, path)
            with open(path) as f:
                data = self.parse(self.read(f))

            for fmt in self.formatters:
                tex = self.generate(data, fmt)
                self.save(tex, name=name, fmt=fmt)


class YamlTexModuleGenerator(FileToFileGenerator, metaclass=ABCMeta):
    def __init__(
        self,
        module_type: str,
        formatters: Dict[str, Formatter],
        root_output_dir: str = ROOT_OUTPUT_PATH,
    ):
        super().__init__(module_type, formatters)
        self.root_output_path = root_output_dir

    def read(self, source):
        return yaml.full_load(source)

    def generate(self, parsed_data: Data, fmt: str) -> str:
        formatter = self.formatters[fmt]
        template = TEX_TEMPLATES[self.module_type][fmt]
        tex = template.format(**formatter(parsed_data))
        return tex


class EducationItemGenerator(YamlTexModuleGenerator):
    def __init__(self):
        item_type = "education"
        formatters = {"cv": self.format_fields_cv, "resume": self.format_fields_resume}
        super().__init__(item_type, formatters)

    def parse(self, data: Data) -> Data:
        parsed = data.copy()
        for date_field in DATE_FIELDS:
            parsed[date_field] = parse_date(data[date_field])
        return parsed

    @staticmethod
    def format_fields_cv(data: Data) -> FormattedFields:
        formatted = data.copy()

        formatted["degree"] = format_optional(data["degree"])

        comment = data["comment"]
        formatted["comment"] = (
            f"Expected graduation: {comment['expected-end-date']}"
            if comment["expected-end-date"]
            else f"{comment['other']}"
        )

        for date_field in DATE_FIELDS:
            formatted[date_field] = format_date_long(data[date_field])

        return formatted

    @staticmethod
    def format_fields_resume(data: Data) -> FormattedFields:
        formatted = data.copy()

        formatted["degree"] = format_optional(data["degree"])

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

        for date_field in DATE_FIELDS:
            formatted[date_field] = format_date_short(data[date_field])

        return formatted


class WorkItemGenerator(YamlTexModuleGenerator):
    def __init__(self):
        item_type = "work"
        formatters = {"cv": self.format_fields_cv, "resume": self.format_fields_resume}
        super().__init__(item_type, formatters)

    def parse(self, data: Data) -> Data:
        parsed = data.copy()
        for date_field in DATE_FIELDS:
            parsed[date_field] = parse_date(data[date_field])
        return parsed

    @staticmethod
    def format_fields_cv(data: Data) -> FormattedFields:
        formatted = data.copy()

        formatted["comment"] = format_optional(data["comment"])

        for date_field in DATE_FIELDS:
            formatted[date_field] = format_date_long(data[date_field])

        return formatted

    @staticmethod
    def format_fields_resume(data: Data) -> FormattedFields:
        formatted = data.copy()

        formatted["optional"] = format_optional(data["comment"])

        for date_field in DATE_FIELDS:
            formatted[date_field] = format_date_short(data[date_field])

        return formatted


class TexIdentityGenerator(FileToFileGenerator):
    def __init__(
        self, module_type: str, subdir: Optional[str] = None,
    ):
        formatters = {key: lambda x: x for key in FORMATS}
        super().__init__(module_type, formatters, subdir)

    def read(self, source: IO) -> Data:
        return {"tex": source.read()}

    def parse(self, data: Data) -> Data:
        return data

    def generate(self, parsed_data: Data, fmt: str) -> str:
        return parsed_data["tex"]


def parse_date(date: str) -> Union[MonthDate, str]:
    try:
        month, year = date.split()
        month = list(calendar.month_name).index(month.title())
        year = int(year)
        return MonthDate(year, month)
    except ValueError:
        return date


def format_date_long(date):
    return (
        f"{calendar.month_name[date.month]} {date.year}"
        if isinstance(date, MonthDate)
        else date
    )


def format_date_short(date):
    return (
        f"{calendar.month_name[date.month][:3]} {date.year}"
        if isinstance(date, MonthDate)
        else date
    )


def format_optional(optional):
    return optional if optional else ""


def ensure_output_dir(path=ROOT_OUTPUT_PATH):
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
        with open(path, "w") as f:
            f.write(tex)

    save_output(
        save_func,
        output_dir=output_dir,
        output_name=type_name,
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

    EducationItemGenerator().generate_all("modules/education-items")
    TexIdentityGenerator("toplevel", subdir="").generate_all("modules")


def define_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--logging-level", type=logging.getLevelName)
    return parser


if __name__ == "__main__":
    arg_parser = define_cli()
    arg_namespace = arg_parser.parse_args()
    main(**vars(arg_namespace))
