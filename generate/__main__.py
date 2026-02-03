import argparse

from .generators import *

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
        fmt="{asctime} - {levelname:8} - {origin:20} - {message}",
        style="{",
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root.handlers.clear()
    root.addHandler(handler)
    return root


def main(**kwargs):
    setup_logging(kwargs.get("logging_level", logging.INFO))

    TexIdentityGenerator("toplevel", subdir="").generate_file("modules/aboutme.tex")
    ContactInfoGenerator().generate_file("modules/contact-info.yaml")
    SkillsGenerator().generate_file("modules/skills.yaml")
    CompactSkillsGenerator().generate_file("modules/skills.yaml")
    LanguagesGenerator().generate_file("modules/languages.yaml")

    (education := EducationItemGenerator()).generate_dir("modules/education-items")
    AllItemsByDateGenerator(education).generate_dir("modules/education-items")
    (work := WorkItemGenerator()).generate_dir("modules/work-items")
    AllItemsByDateGenerator(work).generate_dir("modules/work-items")
    (experience := ExperienceItemGenerator()).generate_dir("modules/experience-items")
    AllItemsByDateGenerator(experience).generate_dir("modules/experience-items")
    (course := CourseItemGenerator()).generate_dir("modules/courses-items")
    AllItemsByDateGenerator(course).generate_dir("modules/courses-items")
    (project := ProjectItemGenerator()).generate_dir("modules/projects-items")
    AllItemsByDateGenerator(project).generate_dir("modules/projects-items")
    (award := AwardItemGenerator()).generate_dir("modules/awards-items")
    AllItemsByDateGenerator(award).generate_dir("modules/awards-items")


def define_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--logging-level", type=logging.getLevelName)
    return parser


if __name__ == "__main__":
    arg_parser = define_cli()
    arg_namespace = arg_parser.parse_args()
    main(**vars(arg_namespace))
