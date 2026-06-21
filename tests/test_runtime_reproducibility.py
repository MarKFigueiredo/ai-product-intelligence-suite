from pathlib import Path


def test_python_runtime_files_are_declared():
    assert Path("runtime.txt").read_text(encoding="utf-8").strip() == "python-3.12"
    assert Path(".python-version").read_text(encoding="utf-8").strip() == "3.12"


def test_requirements_use_compatible_release_pins():
    requirements = Path("requirements.txt").read_text(encoding="utf-8").splitlines()

    package_lines = [
        line.strip()
        for line in requirements
        if line.strip() and not line.strip().startswith("#")
    ]

    assert package_lines
    assert all("~=" in line for line in package_lines)


def test_readme_documents_runtime_and_reproducibility():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "## Runtime and reproducibility" in readme
    assert "Python 3.12" in readme
    assert "requirements.txt" in readme
