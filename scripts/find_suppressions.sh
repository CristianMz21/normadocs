#!/bin/bash
# Script to find all code suppressions in the project
# Usage: ./scripts/find_suppressions.sh [path]

set -e

SEARCH_PATH="${1:-.}"
NONE_FOUND="  (none found)"

echo "=== Searching for suppressions in: $SEARCH_PATH ==="
echo ""

# Type ignore comments
echo "### # type: ignore comments ###"
rg -n "# type: ignore" "$SEARCH_PATH" --type py 2>/dev/null || echo "${NONE_FOUND}"

echo ""

# nosec comments
echo "### # nosec comments ###"
rg -n "# nosec" "$SEARCH_PATH" --type py 2>/dev/null || echo "${NONE_FOUND}"

echo ""

# noqa comments
echo "### # noqa comments ###"
rg -n "# noqa" "$SEARCH_PATH" --type py 2>/dev/null || echo "${NONE_FOUND}"

echo ""

# Bandit suppressions
echo "### Bandit suppressions (B###) ###"
rg -n "# B[0-9]" "$SEARCH_PATH" --type py 2>/dev/null || echo "${NONE_FOUND}"

echo ""

# Ruff suppressions
echo "### Ruff suppressions (RUF###, S###) ###"
rg -n "# RUF[0-9]|# S[0-9]" "$SEARCH_PATH" --type py 2>/dev/null || echo "${NONE_FOUND}"

echo ""

# mypy comments
echo "### mypy: comments ###"
rg -n "# mypy:" "$SEARCH_PATH" --type py 2>/dev/null || echo "${NONE_FOUND}"

echo ""

# Check pyproject.toml for ignore/skip settings
echo "### Ignore settings in pyproject.toml ###"
if [[ -f "${SEARCH_PATH}/pyproject.toml" ]]; then
    grep -n "ignore = \|skips = " "$SEARCH_PATH/pyproject.toml" 2>/dev/null || echo "${NONE_FOUND}"
else
    echo "  pyproject.toml not found"
fi

echo ""
echo "=== Done ==="
