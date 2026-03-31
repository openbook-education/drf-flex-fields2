We use poetry to manage our Python dependencies. So when talking about
Python dependencies, please use the `poetry` command.

We always write strings with double quotes, unless the strings include
double quotes themselves. In that case, we use single quotes.

In all programming languages we use four spaces for indentation.

In Python we never put the quotes of a docstring in the same line as the text.

In Python we often use the `from x import y` syntax. When importing from
the same project, we use a relative import like `from .models import MyModel`.
Imports should be grouped by standard library, third-party libraries, and own.
Within each group, imports should be sorted alphabetically by module name.
The import keywords should be aligned vertically.

Comments use markdown syntax. Programming language keywords, variables
etc. are wrapped in backticks, e.g. `my_variable`.

We always use one empty line to separate logical blocks of code. So please try to
avoid writing long blocks of code without empty lines.

When breaking long method calls into multiple lines, please vertically align the
equal signs with at least one space before and one space after the equal sign.
Also add trailing commas, and use one empty line before the first line of the
method call.

When breaking long dictionary definitions into multiple lines, please vertically
align the values with at least one space after the colon.

Remember: Before you can execute shell commands that need to access python packages,
first execute `poetry shell` to switch into the virtual environment.

When modifying the repo setup or tooling, please update the documentation in the
`doc` directory accordingly.

Unit tests need to be run with `manage.py test` (Django test framework) from within
the `src` directory.