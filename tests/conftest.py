import sys
import os

# Add project root to Python path
root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(root)

"""
Test environment bootstrapper.

Pytest does not automatically include the project root directory
(TradeTrack-Backend/) in Python's import search path. As a result,
imports such as:

    from core.vector_utils import normalize_vector

would fail with:
    ModuleNotFoundError: No module named 'core'

This file ensures that tests can import the application's packages
(`core`, `services`, `routers`, etc.) exactly the same way the
application can when running via uvicorn. It works by:

    1. Determining the project root directory based on the location of
       this file (tests/conftest.py lives inside the tests/ folder).

    2. Appending that root path to sys.path so Python treats it as an
       importable module location.

This enables consistent import behavior during tests without requiring
installation of the package via pip or modifying PYTHONPATH externally.
"""
