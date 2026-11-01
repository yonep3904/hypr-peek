"""Shared helpers for the project's developer tools."""

import os
import shlex
import shutil
import subprocess
import sys
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT / "build"

EXCLUDE_DIRS = [
    ".git",
    "build",
    "external",
    "refs",
    "vendor",
]
CPP_EXTENSIONS = (
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hh",
    ".hpp",
    ".hxx",
)
QML_EXTENSIONS = (
    ".qml",
    ".js",
)


def iter_files(
    root: Path,
    exclude_dirs: Sequence[str],
    extensions: Sequence[str],
) -> Iterator[Path]:
    """Yield files under root matching the given extensions.

    Directory names in exclude_dirs are excluded only when they are direct
    children of root. Extension matching is case-insensitive.
    """
    if not isinstance(root, Path):
        raise TypeError("root must be a pathlib.Path")

    if not root.is_dir():
        raise ValueError(f"root is not a directory: {root}")

    if any(not isinstance(name, str) or not name for name in exclude_dirs):
        raise ValueError("exclude_dirs must contain non-empty strings")

    if any(not isinstance(ext, str) or not ext for ext in extensions):
        raise ValueError("extensions must contain non-empty strings")

    # ".cpp" and "cpp" are both accepted.
    normalized_extensions = {f".{ext.lstrip('.')}".lower() for ext in extensions}

    excluded = set(exclude_dirs)

    for current, dirs, files in os.walk(root):
        current_path = Path(current)

        # Only directories directly below root can be excluded.
        if current_path == root:
            dirs[:] = [name for name in dirs if name not in excluded]

        # os.walk() follows dirs in this order.
        dirs.sort()
        files.sort()

        for name in files:
            path = current_path / name

            if path.suffix.lower() in normalized_extensions:
                yield path


def resolve_tool(name: str, override: str | None = None) -> str:
    candidate = override or name
    executable = shutil.which(candidate)

    if executable is None:
        raise ValueError(f"Cannot find {candidate}; install {name} or specify its path")

    return str(Path(executable).absolute())


def run(command: Sequence[str]) -> int:
    print(f"+ {shlex.join(command)}", flush=True)

    return_code = subprocess.run(command, cwd=ROOT, check=False).returncode

    return 1 if return_code else 0


def build_dir(override: Path | None = None) -> Path:
    if override is not None:
        return override.resolve()

    # CI already exposes its selected CMake preset as PRESET.
    preset = os.environ.get("PRESET", "dev")

    return BUILD_DIR / preset


def run_cli(main: Callable[[], int]) -> None:
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
