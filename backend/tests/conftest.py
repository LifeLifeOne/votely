import os

# Test-only settings, applied before the application reads its configuration.
os.environ.setdefault("VOTELY_JWT_SECRET", "test-secret-not-used-anywhere-else")
os.environ.setdefault("VOTELY_COOKIE_SECURE", "false")
