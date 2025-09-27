#!/usr/bin/env python3
"""
End-to-end test script for LangPlug application
Tests all major user workflows
"""

import requests
import json
import time
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123!"
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

def print_test(message, status="info"):
    if status == "pass":
        print(f"{Colors.GREEN}[PASS]{Colors.ENDC} {message}")
    elif status == "fail":
        print(f"{Colors.RED}[FAIL]{Colors.ENDC} {message}")
    elif status == "info":
        print(f"{Colors.BLUE}[INFO]{Colors.ENDC} {message}")
    elif status == "test":
        print(f"{Colors.YELLOW}[TEST]{Colors.ENDC} {message}")

def test_health_check():
    """Test if the backend is running"""
    print_test("Testing health check...", "test")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_test("Backend is healthy", "pass")
            return True
        else:
            print_test(f"Health check failed: {response.status_code}", "fail")
            return False
    except Exception as e:
        print_test(f"Cannot connect to backend: {e}", "fail")
        return False

def test_register():
    """Test user registration"""
    print_test("Testing user registration...", "test")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": TEST_USER["email"],
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
        )

        if response.status_code == 200 or response.status_code == 201:
            print_test(f"User registered successfully", "pass")
            return True
        elif response.status_code == 400 and "already exists" in response.text.lower():
            print_test("User already exists (OK for repeated tests)", "info")
            return True
        else:
            print_test(f"Registration failed: {response.status_code} - {response.text}", "fail")
            return False
    except Exception as e:
        print_test(f"Registration error: {e}", "fail")
        return False

def test_login():
    """Test user login"""
    print_test("Testing user login...", "test")
    try:
        # Login uses form data, not JSON
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            data={
                "username": TEST_USER["email"],  # API expects email as username
                "password": TEST_USER["password"]
            }
        )

        if response.status_code == 200:
            token_data = response.json()
            if "access_token" in token_data:
                print_test("Login successful", "pass")
                return token_data["access_token"]
            else:
                print_test("Login response missing access_token", "fail")
                return None
        else:
            print_test(f"Login failed: {response.status_code} - {response.text}", "fail")
            return None
    except Exception as e:
        print_test(f"Login error: {e}", "fail")
        return None

def test_authenticated_endpoints(token):
    """Test endpoints that require authentication"""
    headers = {"Authorization": f"Bearer {token}"}

    # Test getting current user
    print_test("Testing get current user...", "test")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print_test(f"Got user data: {user_data.get('email', 'unknown')}", "pass")
        else:
            print_test(f"Get user failed: {response.status_code}", "fail")
    except Exception as e:
        print_test(f"Get user error: {e}", "fail")

    # Test vocabulary endpoints
    print_test("Testing vocabulary languages...", "test")
    try:
        response = requests.get(f"{BASE_URL}/api/vocabulary/languages", headers=headers)
        if response.status_code == 200:
            languages = response.json()
            print_test(f"Got vocabulary languages: {languages}", "pass")
        else:
            print_test(f"Get languages failed: {response.status_code}", "fail")
    except Exception as e:
        print_test(f"Vocabulary error: {e}", "fail")

    # Test getting vocabulary stats
    print_test("Testing vocabulary stats...", "test")
    try:
        response = requests.get(
            f"{BASE_URL}/api/vocabulary/stats",
            headers=headers
        )
        if response.status_code == 200:
            stats = response.json()
            print_test(f"Got vocabulary stats", "pass")
        else:
            print_test(f"Get stats failed: {response.status_code}", "fail")
    except Exception as e:
        print_test(f"Get stats error: {e}", "fail")

    # Test getting vocabulary library
    print_test("Testing vocabulary library...", "test")
    try:
        response = requests.get(
            f"{BASE_URL}/api/vocabulary/library/A1",
            headers=headers
        )
        if response.status_code == 200:
            library = response.json()
            word_count = len(library) if isinstance(library, list) else len(library.get("words", []))
            print_test(f"Got {word_count} vocabulary words", "pass")
        else:
            print_test(f"Get library failed: {response.status_code}", "fail")
    except Exception as e:
        print_test(f"Get library error: {e}", "fail")

def test_logout(token):
    """Test user logout"""
    print_test("Testing logout...", "test")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
        if response.status_code in [200, 204]:  # 204 No Content is also success
            print_test("Logout successful", "pass")
            return True
        else:
            print_test(f"Logout failed: {response.status_code}", "fail")
            return False
    except Exception as e:
        print_test(f"Logout error: {e}", "fail")
        return False

def run_all_tests():
    """Run all end-to-end tests"""
    print("\n" + "="*50)
    print("LangPlug End-to-End Testing")
    print("="*50 + "\n")

    # Check if backend is running
    if not test_health_check():
        print_test("Backend is not running. Please start it first.", "fail")
        return False

    print()

    # Test registration
    test_register()
    print()

    # Test login and get token
    token = test_login()
    if not token:
        print_test("Cannot proceed without authentication", "fail")
        return False

    print()

    # Test authenticated endpoints
    test_authenticated_endpoints(token)
    print()

    # Test logout
    test_logout(token)

    print("\n" + "="*50)
    print("Testing Complete!")
    print("="*50 + "\n")

    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)