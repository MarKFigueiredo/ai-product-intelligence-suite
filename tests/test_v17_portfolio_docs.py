from pathlib import Path


def test_readme_repositions_project_as_portfolio_case_study():
    text = Path("README.md").read_text(encoding="utf-8")
    assert "This project is a portfolio case study, not a commercial product." in text
    for phrase in [
        "domain understanding",
        "AI workflow design",
        "human-in-the-loop review",
        "risk-aware communication",
        "evaluation discipline",
        "enterprise readiness judgment",
        "product strategy",
    ]:
        assert phrase in text


def test_portfolio_review_guide_has_review_paths_and_skill_map():
    text = Path("PORTFOLIO_REVIEW_GUIDE.md").read_text(encoding="utf-8")
    for phrase in [
        "Read this in 5 minutes",
        "Review this in 15 minutes",
        "Deep dive in 45 minutes",
        "What this project demonstrates about my skills",
        "Recommended reviewer path by persona",
    ]:
        assert phrase in text


def test_error_taxonomy_includes_failure_cases_and_tradeoffs():
    text = Path("docs/ERROR_TAXONOMY_FAILURE_MODES.md").read_text(encoding="utf-8")
    for phrase in [
        "Formal error taxonomy",
        "Failure cases intentionally shown",
        "Trade-off analysis",
        "Speed vs precision",
        "Automation vs human review",
        "Coverage vs noise",
        "Unsupported claim",
        "Missing obligation",
    ]:
        assert phrase in text


def test_interview_talking_points_are_present():
    text = Path("INTERVIEW_TALKING_POINTS.md").read_text(encoding="utf-8")
    for phrase in [
        "30-second version",
        "Why I built this",
        "What I intentionally did not build",
        "How I would measure success with real users",
    ]:
        assert phrase in text
