from abc import ABCMeta, abstractmethod
from typing import Dict

from .config import ITEMS_FIELD
from .utils import Data, FormattedFields


class Template(metaclass=ABCMeta):
    @abstractmethod
    def fill(self, fields: FormattedFields) -> str:
        pass


class SimpleTemplate(Template):
    def __init__(self, template: str):
        self.template = template

    def fill(self, fields: FormattedFields) -> str:
        return self.template.format(**fields)


class MultiItemTemplate(Template):
    def __init__(self, global_template: str, item_template: str, item_sep: str = "\n"):
        self.global_template = global_template
        self.item_template = item_template
        self.item_sep = item_sep

    def fill(self, fields: FormattedFields) -> str:
        items_fmt = self.item_sep.join(
            self.item_template.format(item) for item in fields[ITEMS_FIELD]
        )
        return self.global_template.format(items=items_fmt)


# fmt:
TEX_TEMPLATES: Dict[str, Dict[str, Template]] = {
    "education": {
        "cv": SimpleTemplate(
r"""
\cvchronoitem
{{ {degree} {title} }}
{{ {institution} }}
{{ {start-date} }}
{{ {end-date} }}
{{ {comment} }}
{{ {description} \textit{{ {grade[type]}: {grade[value]} }} }}
"""
        ),
        "resume": SimpleTemplate(
r"""
\twentyitem
{{ \noindent {start-date} - \\ {end-date} \\({comment}) }}
{{ {degree} {title} }}
{{ {institution} }}
{{ {description} \textit{{ GPA: 19 (out of 22) }} }}
""",
        )
    },
    "work": {
        "cv": SimpleTemplate(
r"""
\cvchronoitem
{{ {job-title} }}
{{ {company} }}
{{ {start-date} }}
{{ {end-date} }}
{{{comment}}}
{{ {description} }}
"""
        ),
        "resume": SimpleTemplate(
r"""
\twentyitem
{{\noindent {start-date} - \\ {end-date} }}
{{ {job-title} }}
{{ {company} }}
{{ {description} }}
"""
        ),
    },
    "contact-info": {
        "cv": SimpleTemplate(
r"""
\newcommand{{\cvemail}}{{{email}}}
\newcommand{{\cvphone}}{{{phone}}}
\newcommand{{\cvlinkedin}}{{{linkedin}}}
\newcommand{{\cvgithub}}{{{github}}}
\newcommand{{\cvstackoverflow}}{{{stack-overflow}}}
"""
        ),
        "resume": SimpleTemplate(
r"""
\cvname{{{name}}}
\cvjobtitle{{{job-title}}}
\cvnumberphone{{{phone}}}
\cvmail{{{email}}}
\cvgithub{{github.com/{github}}}
\cvlinkedin{{linkedin.com/in/{linkedin}}}
\cvstackoverflow{{stackoverflow.com/story/{stack-overflow}}}
"""
        ),
    },
    "skill": {
        "cv": MultiItemTemplate(
            global_template="{items}",
            item_template=r"\addcvsoftwareskill{{ {name} }}{{ {level} }}",
        ),
        "resume": MultiItemTemplate(
            global_template=r"\skills{{{items}}}",
            item_template=r"{{{name}/{score}}}",
            item_sep=",",
        )
    },
}
# fmt: on
