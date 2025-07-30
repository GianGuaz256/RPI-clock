"""
Test suite for Raspberry Pi Digital Dashboard.

This package contains comprehensive tests for all dashboard components:
- Unit tests for individual classes and functions
- Integration tests for component interactions
- Mock tests for external dependencies
- Configuration and error handling tests
"""

import os
import sys

# Add the project root to Python path for testing
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root) 