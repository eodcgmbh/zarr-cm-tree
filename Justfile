set windows-shell := ["powershell"]

# Default command lists all available recipes
[default]
_default:
    @just --list

alias c := clean
alias l := lint
alias q := check
alias t := test
alias fmt := format

# display the system/project information
[group("chore")]
info:
    @echo "{{ CYAN }}Arch{{ NORMAL }}: {{ arch() }}"
    @echo "{{ CYAN }}OS{{ NORMAL }}: {{ os_family() }}, {{ os() }}"
    @echo "{{ CYAN }}Num CPU's{{ NORMAL }}: {{ num_cpus() }}"
    @echo "{{ CYAN }}Project{{ NORMAL }}: `uv version`"

# run the linter [arg:<full|concise|...>]
[group("style")]
lint arg="concise":
    uv run ruff check . --fix --output-format={{ arg }}

# run the formatter
[group("style")]
format:
    uv run ruff format .

# run the type checker [arg:<full|concise|...>]
[group("style")]
types arg="concise":
    uv run ty check --output-format={{ arg }}

# lint, format and type-check [arg:<full|concise|...>]
[group("style")]
check arg="concise":
    -@just lint {{ arg }}
    -@just format
    -@just types {{ arg }}

# run the tests
[group("test")]
test *args:
    uv run pytest tests/ {{ args }}

# run the formatter, linter, typechecker and the tests
[group("test")]
ci python="3.12":
    uv run --python={{ python }} ruff format .
    uv run --python={{ python }} ruff check . --fix
    uv run --python={{ python }} ty check .
    uv run --python={{ python }} pytest tests/

# install dependencies in local venv
[group("dev")]
venv:
    uv sync --all-groups

# update dependencies in the lock file
[group("dev")]
update:
    uv lock --upgrade

# build the source distribution and wheel file
[group("dev")]
dist:
    uv build

# clean all build/compilation files and directories
[group("dev")]
clean:
    rm -fr build/ dist/ .eggs/ htmlcov/ .pytest_cache
    rm -f .coverage
    find . -name '__pycache__' -exec rm -fr {} +
    find . -name '*.py[co]' -exec rm -f {} +
