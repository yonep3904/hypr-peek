#!/usr/bin/env python3

"""Run clang-tidy and Qt's all_qmllint target on a configured CMake build."""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import _cpp
import _qml
from _common import build_dir, resolve_tool, run_cli


@dataclass(frozen=True)
class Options:
    language: Literal["all", "cpp", "qml"]
    build: Path | None
    cpp_tool: str | None
    cmake: str | None


def parse_args() -> Options:
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("--language", choices=("all", "cpp", "qml"), default="all")
    parser.add_argument(
        "--build-dir",
        type=Path,
        help="Configured build (default: build/$PRESET or build/dev)",
    )
    parser.add_argument(
        "--cpp-tool", "--clang-tidy", help="clang-tidy executable (default: PATH)"
    )
    parser.add_argument("--cmake", help="CMake executable (default: PATH)")

    args = parser.parse_args()

    return Options(
        language=args.language,
        build=args.build_dir,
        cpp_tool=args.cpp_tool,
        cmake=args.cmake,
    )


def main() -> int:
    options = parse_args()
    failed = 0

    resolved_build = build_dir(options.build)

    if options.language in ("all", "cpp"):
        executable = resolve_tool("clang-tidy", options.cpp_tool)
        failed |= _cpp.lint_files(executable, resolved_build)

    if options.language in ("all", "qml"):
        executable = resolve_tool("cmake", options.cmake)
        failed |= _qml.lint_files(executable, resolved_build)

    return failed


if __name__ == "__main__":
    run_cli(main)
