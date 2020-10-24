import os

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
    "contact-info": {
        "cv": \
r"""
\newcommand{{\cvemail}}{{{email}}}
\newcommand{{\cvphone}}{{{phone}}}
\newcommand{{\cvlinkedin}}{{{linkedin}}}
\newcommand{{\cvgithub}}{{{github}}}
\newcommand{{\cvstackoverflow}}{{{stack-overflow}}}
""",
        "resume": \
r"""
\cvname{{{name}}}
\cvjobtitle{{{job-title}}}
\cvnumberphone{{{phone}}}
\cvmail{{{email}}}
\cvgithub{{github.com/{github}}}
\cvlinkedin{{linkedin.com/in/{linkedin}}}
\cvstackoverflow{{stackoverflow.com/story/{stack-overflow}}}
""",
    }
}
# fmt: on

DATE_FIELDS = {"start-date", "end-date"}
TEXT_FIELDS = {"description"}
