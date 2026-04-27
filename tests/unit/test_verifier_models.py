"""Unit tests for the verifier models (VerificationIssue, VerificationResult)."""

import unittest

from normadocs.verifier import CheckCategory, VerificationIssue, VerificationResult


class TestVerificationIssue(unittest.TestCase):
    """Tests for VerificationIssue dataclass."""

    def test_creation_with_required_fields(self) -> None:
        """Test creating an issue with only required fields."""
        issue = VerificationIssue(
            check="margins.top",
            severity="error",
            expected="1.0 inches",
            actual="0.5 inches",
        )
        assert issue.check == "margins.top"
        assert issue.severity == "error"
        assert issue.expected == "1.0 inches"
        assert issue.actual == "0.5 inches"
        assert issue.page is None
        assert issue.coordinates is None
        assert issue.evidence is None

    def test_creation_with_all_fields(self) -> None:
        """Test creating an issue with all fields."""
        issue = VerificationIssue(
            check="fonts.body_font",
            severity="warning",
            expected="Times New Roman",
            actual="Arial",
            page=1,
            coordinates=(100, 200, 300, 400),
            evidence="Font 'Arial' found in paragraph 5",
        )
        assert issue.check == "fonts.body_font"
        assert issue.severity == "warning"
        assert issue.expected == "Times New Roman"
        assert issue.actual == "Arial"
        assert issue.page == 1
        assert issue.coordinates == (100, 200, 300, 400)
        assert issue.evidence == "Font 'Arial' found in paragraph 5"

    def test_severity_values(self) -> None:
        """Test that severity accepts valid values."""
        error_issue = VerificationIssue(check="t", severity="error", expected="", actual="")
        assert error_issue.severity == "error"

        warning_issue = VerificationIssue(check="t", severity="warning", expected="", actual="")
        assert warning_issue.severity == "warning"

        info_issue = VerificationIssue(check="t", severity="info", expected="", actual="")
        assert info_issue.severity == "info"


class TestVerificationResult(unittest.TestCase):
    """Tests for VerificationResult dataclass."""

    def test_passed_with_no_issues(self) -> None:
        """Test that passed is True when there are no issues."""
        result = VerificationResult(passed=True, score=100.0)
        assert result.passed is True
        assert result.score == 100.0
        assert len(result.issues) == 0
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert len(result.infos) == 0

    def test_failed_with_errors(self) -> None:
        """Test that passed is False when there are errors."""
        error = VerificationIssue(check="t", severity="error", expected="", actual="")
        result = VerificationResult(passed=False, score=40.0, errors=[error])
        assert result.passed is False
        assert result.score == 40.0
        assert len(result.errors) == 1

    def test_all_issues_property(self) -> None:
        """Test that all_issues combines errors, warnings, and infos."""
        error = VerificationIssue(check="e", severity="error", expected="", actual="")
        warning = VerificationIssue(check="w", severity="warning", expected="", actual="")
        info = VerificationIssue(check="i", severity="info", expected="", actual="")

        result = VerificationResult(
            passed=False,
            score=50.0,
            errors=[error],
            warnings=[warning],
            infos=[info],
        )

        all_issues = result.all_issues
        assert len(all_issues) == 3
        assert error in all_issues
        assert warning in all_issues
        assert info in all_issues

    def test_score_calculation_with_errors(self) -> None:
        """Test score reflects error count."""
        errors = [
            VerificationIssue(check=f"e{i}", severity="error", expected="", actual="")
            for i in range(3)
        ]
        result = VerificationResult(
            passed=False,
            score=100.0 - (3 / 11) * 60,
            errors=errors,
        )
        assert len(result.errors) == 3
        assert result.score < 100.0

    def test_score_calculation_with_warnings(self) -> None:
        """Test score reflects warning count."""
        warnings = [
            VerificationIssue(check=f"w{i}", severity="warning", expected="", actual="")
            for i in range(5)
        ]
        result = VerificationResult(
            passed=True,
            score=100.0 - (5 / 11) * 30,
            warnings=warnings,
        )
        assert len(result.warnings) == 5
        assert result.score < 100.0
        assert result.score > 50.0


class TestCheckCategory(unittest.TestCase):
    """Tests for CheckCategory constants."""

    def test_all_categories_defined(self) -> None:
        """Test that all expected categories are defined."""
        assert CheckCategory.MARGINS == "margins"
        assert CheckCategory.FONTS == "fonts"
        assert CheckCategory.RUNNING_HEAD == "running_head"
        assert CheckCategory.SPACING == "spacing"
        assert CheckCategory.PARAGRAPHS == "paragraphs"
        assert CheckCategory.HEADINGS == "headings"
        assert CheckCategory.TABLES == "tables"
        assert CheckCategory.FIGURES == "figures"
        assert CheckCategory.REFERENCES == "references"
        assert CheckCategory.COVER_PAGE == "cover_page"
        assert CheckCategory.PAGE_SETUP == "page_setup"


if __name__ == "__main__":
    unittest.main()
