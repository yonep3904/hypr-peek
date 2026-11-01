"""C++ formatting and analysis of project-owned translation units."""

import json
from pathlib import Path

from _common import CPP_EXTENSIONS, EXCLUDE_DIRS, ROOT, iter_files, run


def format_files(executable: str, fix: bool) -> int:
    if run([executable, "--version"]):
        return 1

    files = list(iter_files(ROOT, EXCLUDE_DIRS, CPP_EXTENSIONS))
    if not files:
        print("C++ formatting: no files; skip")
        return 0

    flags = ["-i"] if fix else ["--dry-run", "--Werror"]

    return run([executable, "--style=file", *flags, *map(str, files)])


def lint_files(executable: str, build: Path) -> int:
    database = build / "compile_commands.json"

    if not database.is_file():
        raise ValueError(
            f"Missing {database}; run cmake --preset dev (CI: $PRESET) first"
        )

    entries = json.loads(database.read_text())
    if not isinstance(entries, list):
        raise ValueError(f"Expected a JSON array in {database}")

    owned = {path.resolve() for path in iter_files(ROOT, EXCLUDE_DIRS, CPP_EXTENSIONS)}
    files: set[Path] = set()
    for entry in entries:
        directory = Path(entry["directory"])
        if not directory.is_absolute():
            directory = database.parent / directory
        path = (directory / entry["file"]).resolve()
        if path in owned:
            files.add(path)

    if not files:
        raise ValueError(f"No project translation units in {database}")

    if run([executable, "--version"]):
        return 1

    failed = 0
    for path in sorted(files):
        failed |= run(
            [
                executable,
                f"-p={database.parent}",
                "--warnings-as-errors=*",
                f"--config-file={ROOT / '.clang-tidy'}",
                str(path),
            ]
        )
    return failed
