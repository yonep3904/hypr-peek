"""Qt 6 tool discovery and QML checks."""

import difflib
import re
import shutil
import subprocess
import sys
from pathlib import Path

from _common import EXCLUDE_DIRS, QML_EXTENSIONS, ROOT, iter_files, run


def resolve_qt_tool(name: str, override: str | None = None) -> str:
    candidates = (
        [override]
        if override
        else [
            f"/usr/lib/qt6/bin/{name}",
            f"/usr/lib64/qt6/bin/{name}",
            f"/usr/lib/qt6/libexec/{name}",
            f"{name}6",
            f"{name}-qt6",
            name,
        ]
    )
    if override is None:
        for query_tool in ("qtpaths6", "qtpaths-qt6", "qmake6", "qmake-qt6"):
            query = shutil.which(query_tool)
            if query:
                flag = "--query" if query_tool.startswith("qtpaths") else "-query"
                result = subprocess.run(
                    [query, flag, "QT_HOST_BINS"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    candidates.insert(0, str(Path(result.stdout.strip()) / name))
    rejected = []
    for candidate in candidates:
        executable = shutil.which(candidate)
        if executable is None:
            continue
        result = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        version = (result.stdout + result.stderr).strip()
        if result.returncode == 0 and re.search(r"\b6\.\d+(?:\.\d+)?\b", version):
            print(f"{executable}: {version}", flush=True)
            return str(Path(executable).absolute())
        rejected.append(f"{executable}: {version or 'version check failed'}")
    detail = "; ".join(rejected) or "no executable found"
    raise ValueError(
        f"Qt 6 {name} is required ({detail}); specify --qml-tool /path/to/qt6/{name}"
    )


def format_files(executable: str, fix: bool) -> int:
    files = list(iter_files(ROOT, EXCLUDE_DIRS, QML_EXTENSIONS))
    if not files:
        print("QML formatting: no files; skip")
        return 0

    failed = 0
    for path in files:
        if fix:
            failed |= run([executable, "--inplace", str(path)])
            continue
        result = subprocess.run(
            [executable, str(path)], cwd=ROOT, capture_output=True, check=False
        )
        if result.stderr:
            sys.stderr.buffer.write(result.stderr)
        if result.returncode:
            failed = 1
        elif result.stdout != path.read_bytes():
            failed = 1
            relative = str(path.relative_to(ROOT))
            print(
                "".join(
                    difflib.unified_diff(
                        path.read_text().splitlines(keepends=True),
                        result.stdout.decode().splitlines(keepends=True),
                        fromfile=relative,
                        tofile=f"{relative} (formatted)",
                    )
                ),
                end="",
            )
    return failed


def lint_files(cmake: str, build: Path) -> int:
    cache = build / "CMakeCache.txt"
    if not cache.is_file():
        raise ValueError(f"Missing {cache}; configure the CMake build first")
    # Qt's generated target uses the absolute Qt6::qmllint executable rather
    # than PATH, and supplies the module's generated type/import information.
    if not re.search(
        r"^Qt6QmlTools_DIR:PATH=(?![^\n]*-NOTFOUND)[^\n]+", cache.read_text(), re.M
    ):
        raise ValueError(
            f"{build} is not configured with Qt 6 QML tools; reconfigure it"
        )
    return run([cmake, "--build", str(build), "--target", "all_qmllint"])
