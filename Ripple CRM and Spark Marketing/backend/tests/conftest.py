"""Shared test configuration for Beast tests."""
import os

# Enable test environment — disables rate limiting
os.environ["RIPPLE_TESTING"] = "1"
