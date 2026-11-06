"""Versioned numerical admission policy, including resource limits."""

PROFILE = "nfc-jcs-decimal-checked-sha256-v2"
MAX_BYTES = 8 * 1024 * 1024
MAX_DEPTH = 128
MAX_NUMBER_CHARS = 4096
MAX_ABS_EXPONENT = 10000
UNSUPPORTED_REASONS = frozenset({
    "NUMBER_OUT_OF_RANGE", "NUMBER_PRECISION_LOSS", "RESOURCE_LIMIT",
})
