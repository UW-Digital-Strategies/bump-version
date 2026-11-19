"""Terminal output: colors and the message printers.

`Color` holds the ANSI codes and decides, per stream, whether to use them;
`_emit` writes one message to one stream, and the `_print_*` helpers pick
the color and the stream (errors to stderr, everything else to stdout).
Color never carries meaning alone. This module imports nothing from the
package, so every other module may import it.
"""

from __future__ import annotations

import io
import os
import sys
from typing import TextIO


class Color:
    """ANSI color codes for terminal output."""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    RESET = "\033[0m"

    @classmethod
    def enabled(cls, stream: TextIO) -> bool:
        """Check if color output should be enabled for `stream`.

        Honours NO_COLOR (https://no-color.org): present and non-empty
        disables color even on a terminal; an empty value does not.
        """
        return not os.environ.get("NO_COLOR") and stream.isatty()

    @classmethod
    def wrap(cls, text: str, color: str, stream: TextIO) -> str:
        """Wrap text in color codes if colors are enabled for `stream`."""
        if cls.enabled(stream):
            return f"{color}{text}{cls.RESET}"
        return text


def _use_utf8_streams() -> None:
    """
    Write stdout and stderr as UTF-8 whatever the host locale says.

    Commit subjects, tag messages and the `•` bullet reach these streams, and
    an inherited non-UTF-8 encoding (a Latin-1 or ASCII locale, or
    `PYTHONIOENCODING`) raises `UnicodeEncodeError` on the first character it
    cannot represent. A stream that is not a `TextIOWrapper` (a test's
    `StringIO`) has no byte encoding to set, so it is left as it is.
    """
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8")


def _emit(message: str, color: str, stream: TextIO) -> None:
    """
    Write a message to one stream, colored only when that stream is a terminal.

    The tty test has to name the stream being written to. Testing stdout while
    writing to stderr puts escape sequences into a redirected error log
    whenever stdout happens to be a terminal, and drops color from errors
    whenever stdout is piped.
    """
    print(Color.wrap(message, color, stream), file=stream)


def _print_info(message: str) -> None:
    """Print an info message in blue."""
    _emit(message, Color.BLUE, sys.stdout)


def _print_success(message: str) -> None:
    """Print a success message in green."""
    _emit(message, Color.GREEN, sys.stdout)


def _print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    _emit(message, Color.YELLOW, sys.stdout)


def _print_error(message: str) -> None:
    """Print an error message in red to stderr."""
    _emit(message, Color.RED, sys.stderr)
