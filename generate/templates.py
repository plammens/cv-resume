from abc import ABCMeta, abstractmethod
from typing import Dict, Optional

from .config import ITEMS_FIELD
from .utils import FormattedFields


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
    def __init__(
        self,
        global_template: str,
        item_template: str,
        item_sep: str = "\n",
        max_items: Optional[int] = None,
    ):
        self.global_template = global_template
        self.item_template = item_template
        self.item_sep = item_sep
        self.max_items = max_items

    def fill(self, fields: FormattedFields) -> str:
        items_fmt = self.item_sep.join(
            self.item_template.format(**item)
            for item in fields[ITEMS_FIELD][: self.max_items]
        )
        return self.global_template.format(items=items_fmt)


# fmt: off
TEX_TEMPLATES: Dict[str, Dict[str, Template]] = {
    "education": {
        "cv": SimpleTemplate(
r"""
\cvchronoitem
{{\textsc{{{degree}}} {title} }}
{{ {institution} }}
{{ {start-date} }}
{{ {end-date} }}
{{{comment}}}
{{ {description} {grade} }}
"""
        ),
        "resume": SimpleTemplate(
r"""
\twentyitem
{{ \noindent {start-date} - \\ {end-date} \\{comment} }}
{{ {degree} {title} }}
{{ {institution} }}
{{ {description} {grade} }}
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
    "experience": {
        "cv": SimpleTemplate(
r"""
\cvchronoitem
{{{title}}}
{{{institution}}}
{{{start-date}}}
{{{end-date}}}
{{{comment}}}
{{{description}}}
"""
        ),
        "resume": SimpleTemplate(
r"""
\twentyitem
{{\noindent {start-date} - \\ {end-date} }}
{{{title}}}
{{{institution}}}
{{{description}}}
"""
        ),
    },
    "course": {
        "cv": SimpleTemplate(
r"""
\cvchronoitem
{{ {title} }}
{{ {institution} }}
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
{{ {title} }}
{{ {institution} }}
{{ {short-description} }}
"""
        ),
    },
    "project": {
        "cv": SimpleTemplate(
r"""
\cvchronoitem
{{ {title} }}
{{}}
{{ {start-date} }}
{{ {end-date} }}
{{{comment}}}
{{ {description} {link} }}
"""
        ),
        "resume": SimpleTemplate(
r"""
\twentyitem
{{\noindent {start-date} - \\ {end-date} }}
{{ {title} }}
{{{link}}}
{{ {short-description} }}
"""
        ),
    },
    "award": {
        "cv": SimpleTemplate(
r"""
\cvchronoitem
{{ {title} }}
{{ {awarded-by} }}
{{ {date} }}
{{}}
{{}}
{{ {description} }}
"""
        ),
        "resume": SimpleTemplate(
r"""
\twentyitem
{{\noindent {date} }}
{{ {title} }}
{{}}
{{ {short-description} }}
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
"""
        ),
    },
    "skill": {
        "cv": MultiItemTemplate(
            global_template=
r"""
\vspace{{-5mm}}
\begin{{itemize}}
{items}
\end{{itemize}}
\vspace{{-5mm}}
""",
            item_template=r"\item \textbf{{ {name} }} -- {level} -- "
                          r"{{ \small {description} }}",
        ),
        "resume": MultiItemTemplate(
            global_template="{items}",
            item_template=r"\item \textbf{{ {name} }} -- {level} -- "
                          r"{{ \small {short-description} }}",
            max_items=4,
        )
    },
    "language": {
        "cv": MultiItemTemplate(
            global_template="{items}",
            item_template=r"\addcvlanguage{{{language}}}{{{level}}}"
        ),
        "resume": MultiItemTemplate(
            global_template="{items}",
            item_template=r"{language} & \textcolor{{lgray}}{{ {level} }} \\"
        ),
    }
}
# fmt: on
