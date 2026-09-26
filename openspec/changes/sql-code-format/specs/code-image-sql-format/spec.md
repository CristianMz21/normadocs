# Delta for code-image-sql-format

## ADDED Requirements

### Requirement: SQL Code Block Detection

The system MUST apply SQL formatting only to `{code}` blocks whose lang satisfies `lang.lower() == "sql"`, before image render.

#### Scenario: SQL marker triggers format

- GIVEN a `{code}` block declaring lang `sql`
- WHEN `process()` handles the block
- THEN `_format_sql_block` runs before filename and hash computation

#### Scenario: Case-insensitive lang match

- GIVEN a `{code}` block declaring lang `SQL` or `Sql`
- WHEN `process()` handles the block
- THEN it is treated as SQL and formatted

### Requirement: SQL Formatting

The system MUST format SQL via sqlparse with `keyword_case="upper"`, `reindent=True`, `strip_comments=False`; empty or whitespace-only input MUST be returned unchanged.

#### Scenario: Lowercase keywords uppercased

- GIVEN the input `select a from t where a > 1`
- WHEN `_format_sql_block` runs
- THEN the output contains `SELECT`, `FROM`, and `WHERE`

#### Scenario: Multiline query reindented

- GIVEN a single-line multi-clause SELECT statement
- WHEN `_format_sql_block` runs
- THEN clauses are split across lines with indentation

#### Scenario: Empty input passthrough

- GIVEN empty or whitespace-only code
- WHEN `_format_sql_block` runs
- THEN the input is returned unchanged

#### Scenario: Comments preserved

- GIVEN SQL containing an inline `-- comment`
- WHEN `_format_sql_block` runs
- THEN the comment text survives in the output

### Requirement: Graceful Degradation

The system MUST return the original code and emit a debug log when sqlparse is missing or formatting raises; image generation MUST still proceed.

#### Scenario: Missing dependency fallback

- GIVEN sqlparse is not installed
- WHEN a SQL `{code}` block is processed
- THEN the original code renders and a debug record is logged

#### Scenario: Malformed SQL fallback

- GIVEN unparsable SQL that raises inside the formatter
- WHEN `_format_sql_block` runs
- THEN the original code is returned unchanged

### Requirement: Cache Correctness

The system MUST compute the image hash and filename from the formatted content, not the raw input.

#### Scenario: Hash reflects formatted output

- GIVEN a lowercase SQL `{code}` block
- WHEN the document is processed
- THEN the cached filename matches the hash of the formatted code

#### Scenario: Idempotent formatting

- GIVEN already-formatted SQL output
- WHEN `_format_sql_block` runs on it again
- THEN the result is byte-identical (stable)

### Requirement: Zero Regression for Other Blocks

The system MUST NOT alter plain SQL fences without `{code}`, non-SQL languages, or documents with no code blocks.

#### Scenario: Plain fence untouched

- GIVEN a ` ```sql ` fence without the `{code}` marker
- WHEN the document is processed
- THEN its content is byte-identical to the input

#### Scenario: Non-SQL language untouched

- GIVEN a `{code}` block declaring lang `python`
- WHEN the document is processed
- THEN its content is byte-identical to the input
