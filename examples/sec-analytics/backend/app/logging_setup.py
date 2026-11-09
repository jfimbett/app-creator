"""Log redaction for the AI boundary (M5).

The app never logs request headers or bodies, and the key is never put in a log message. This
filter is a second line of defence on the handlers: anything that looks like an `Authorization`
or `X-OpenRouter-Key` value, a `Bearer …` token or an OpenRouter key (`sk-or-…`) is replaced with
`[REDACTED]`. httpx and httpcore, which can log request details at DEBUG, are kept at WARNING.
"""

from __future__ import annotations

import logging
import re

REDACTED = "[REDACTED]"
_SECRETS = re.compile(
    r"(?i)(authorization\s*[:=]\s*)(bearer\s+)?\S+|(x-openrouter-key\s*[:=]\s*)\S+|"
    r"(bearer\s+)\S+|sk-or-[A-Za-z0-9_-]+"
)


def _redact(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        prefix = "".join(group for group in match.groups() if group)
        return f"{prefix}{REDACTED}"

    return _SECRETS.sub(replace, text)


class RedactingFilter(logging.Filter):
    """Rewrites a record's message with secrets replaced. Never drops a record."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:  # a broken format string is left as it is
            return True
        redacted = _redact(message)
        if redacted != message:
            record.msg, record.args = redacted, ()
        return True


def install_log_redaction() -> None:
    """Add the filter to every handler of the root and uvicorn loggers; quiet httpx and httpcore."""
    for name in ("httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)
    for name in ("", "uvicorn", "uvicorn.error", "uvicorn.access", "sec_analytics"):
        logger = logging.getLogger(name)
        if not any(isinstance(f, RedactingFilter) for f in logger.filters):
            logger.addFilter(RedactingFilter())
        for handler in logger.handlers:
            if not any(isinstance(f, RedactingFilter) for f in handler.filters):
                handler.addFilter(RedactingFilter())
