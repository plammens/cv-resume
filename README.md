# CV & Resume builder

This repository is what I use to build my CVs and resumes.
An overview of how it works:
1. I have my experiences (work, education, projects, etc.) written as individual YAML modules in the `modules` directory.
2. A Python module converts them to TeX files:

   ```bash
   python -m generate
   ```
4. These are put together in a master cv.tex or resume.tex document, which `\input`s the generated TeX files.
5. These master LaTeX files are compiled as usual.

Each branch of this repository represents a different flavour of CV/resume tailored to a specific
job search, company, or opportunity.
