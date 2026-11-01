#!/usr/bin/env python3

"""Check C++ and QML formatting; use --fix to apply changes."""

import argparse
from dataclasses import dataclass
from typing import Literal

import _cpp
import _qml
from _common import resolve_tool, run_cli


@dataclass(frozen=True)
class Options:
    language: Literal["all", "cpp", "qml"]
    fix: bool
    cpp_tool: str | None
    qml_tool: str | None


def parse_args() -> Options:
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("--language", choices=("all", "cpp", "qml"), default="all")
    parser.add_argument("--fix", action="store_true", help="Apply formatting changes")
    parser.add_argument(
        "--cpp-tool", "--clang-format", help="clang-format executable (default: PATH)"
    )
    parser.add_argument(
        "--qml-tool", help="Qt 6 qmlformat executable (default: auto-detect)"
    )

    args = parser.parse_args()

    return Options(
        language=args.language,
        fix=args.fix,
        cpp_tool=args.cpp_tool,
        qml_tool=args.qml_tool,
    )


def main() -> int:
    options = parse_args()
    failed = 0

    if options.language in ("all", "cpp"):
        executable = resolve_tool("clang-format", options.cpp_tool)
        failed |= _cpp.format_files(executable, options.fix)

    if options.language in ("all", "qml"):
        executable = _qml.resolve_qt_tool("qmlformat", options.qml_tool)
        failed |= _qml.format_files(executable, options.fix)

    return failed


if __name__ == "__main__":
    run_cli(main)
