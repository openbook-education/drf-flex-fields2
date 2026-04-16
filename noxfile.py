"""Nox sessions for Django/DRF compatibility testing."""

from __future__ import annotations

import nox

# NOTE: Update these versions when a new Django or DRF version is released
# as well as the versions in `pyproject.toml`.
# Django = [Most current LTS Release … current release]
# DRF = [Major version from one year ago … current release]
DJANGO_MIN = "5.2"
DJANGO_MAX = "6.0.4"
DRF_MIN = "3.16.0"
DRF_MAX = "3.17.1"


# Full compatibility matrix:
# 1. min Django + min DRF
# 2. max Django + max DRF
# 3. min Django + max DRF
# 4. max Django + min DRF
@nox.session(
    name="tests",
    reuse_venv=True,
    python=False,
)
@nox.parametrize(
    "django_version,drf_version",
    [
        (DJANGO_MIN, DRF_MIN),
        (DJANGO_MAX, DRF_MAX),
        (DJANGO_MIN, DRF_MAX),
        (DJANGO_MAX, DRF_MIN),
    ],
)
def tests(session: nox.Session, django_version: str, drf_version: str) -> None:
    """Run Django tests for one Django/DRF version combination."""

    session.run("poetry", "install", "--no-interaction", external=True)
    session.run(
        "poetry", "run",
        "python", "-m", "pip", "install",
        f"Django=={django_version}",
        f"djangorestframework=={drf_version}",
        external=True,
    )
    session.run(
        "poetry", "run",
        "python", "src/manage.py", "test", "tests",
        env={"PYTHONPATH": "src"},
        external=True,
    )
