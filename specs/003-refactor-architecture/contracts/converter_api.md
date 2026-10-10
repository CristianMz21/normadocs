# Core Converter API Contract

This contract defines the public-facing programmatic API for NormaDocs after the architectural refactor. It isolates the library execution from the Typer CLI.

## `Converter` Class

```python
from normadocs.converter import Converter
from normadocs.models import ConvertOptions
from normadocs.exceptions import NormaDocsError

# 1. Instantiate options
options = ConvertOptions(
    input_file=Path("document.md"),
    output_dir=Path("export"),
    format="all",
    style="apa7",
    language_tool="es",
    lt_docker=True
)

# 2. Execute conversion
try:
    converter = Converter(options)
    converter.convert_document()
except NormaDocsError as e:
    # Handle the error programmatically
    print(f"Conversion failed: {e}")
```

## Methods & Behavior

- `Converter.__init__(self, options: ConvertOptions)`: Initializes the orchestrator state. Validates inputs implicitly (e.g. checks if input file exists) or raises `ValidationError`.
- `Converter.convert_document(self) -> None`: Runs the 9-stage pipeline sequentially. Will block execution until completion. Uses standard Python `logging` for output, not `sys.stdout` directly.

## Guarantees

1. The `Converter` will **never** invoke `sys.exit()` or `raise typer.Exit()`.
2. The `Converter` will **never** call `typer.echo()`.
3. All errors emitted will be subclasses of `NormaDocsError`.
