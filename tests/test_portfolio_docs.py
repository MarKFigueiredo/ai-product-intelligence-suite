from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="ignore")


def test_readme_repositions_project_as_portfolio_case_study():
    text = read("README.md")

    required_phrases = [
        "This project is a portfolio case study, not a commercial product.",
        "domain understanding",
        "AI workflow design",
        "human-in-the-loop review",
        "risk-aware communication",
        "evaluation discipline",
        "enterprise readiness judgment",
        "product strategy",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_public_review_documents_are_present():
    public_docs = [
        "HERO_CASE_STUDY.md",
        "WHAT_THIS_DEMONSTRATES.md",
        "PRODUCT_STRATEGY.md",
        "VALIDATION_LIMITATIONS.md",
        "docs/reviewer/DEMO_WALKTHROUGH.md",
        "PORTFOLIO_REVIEW_GUIDE.md",
        "docs/SYSTEM_OVERVIEW.md",
        "docs/CLAIM_HYGIENE_SCANNER.md",
    ]

    for doc in public_docs:
        assert (ROOT / doc).exists(), f"Missing public review document: {doc}"


def test_private_or_personal_prep_files_are_not_public():
    private_files = [
        "ABOUT_ME.md",
        "INTERVIEW_TALKING_POINTS.md",
        "LINKEDIN_POST.md",
        "LANDING_PAGE.md",
        "PUBLICATION_STEP_BY_STEP.md",
        "PUBLISH_TO_GITHUB.md",
        "START_HERE_UBUNTU.md",
    ]

    for private_file in private_files:
        assert not (ROOT / private_file).exists(), (
            f"{private_file} should not be part of the public portfolio repository"
        )


def test_old_internal_version_notes_are_not_public_root_files():
    old_release_files = [
        "RELEASE_1_01.md",
        "RELEASE_1_02.md",
        "RELEASE_1_03.md",
    ]

    for old_file in old_release_files:
        assert not (ROOT / old_file).exists(), (
            f"{old_file} should not be part of the sanitized public release"
        )
