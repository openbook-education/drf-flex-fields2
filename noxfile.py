"""Nox sessions for Django/DRF compatibility testing."""

import nox

# NOTE: Update minimum versions in pyproject.toml, too
# NOTE: Set maximum version according to latest-versions.txt (updated by Renovate bot)
@nox.session
@nox.parametrize("django", [
    nox.param("5.2", "lts"),
    nox.param("6.0.6", "latest")
])
@nox.parametrize("drf", [
    nox.param("3.16.0", id="one-year-old"),
    nox.param("3.17.1", id="latest")
])
def tests(session: nox.Session, django: str, drf: str) -> None:
    """Run Django tests for one Django/DRF version combination."""
    # Install matrix versions
    session.install(f"django=={django}")
    session.install(f"djangorestframework=={drf}")

    # Install remaining packages
    pyproject = nox.project.load_toml("pyproject.toml")

    for (package, version) in pyproject["tool"]["poetry"]["dependencies"].items():
        if package in ["python", "django", "djangorestframework"]:
            continue

        session.install(f"{package}{version}")

    # Run test suite
    session.cd("src")
    session.run("python", "manage.py", "test")
