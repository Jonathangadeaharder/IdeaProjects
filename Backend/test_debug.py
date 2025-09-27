"""Simple debug test to check basic test infrastructure."""
import pytest

def test_simple_math():
    """Test basic math operations."""
    assert 1 + 1 == 2

def test_string_operations():
    """Test basic string operations."""
    assert "hello".upper() == "HELLO"
