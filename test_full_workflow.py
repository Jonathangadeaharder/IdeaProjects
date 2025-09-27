#!/usr/bin/env python3
"""
Full end-to-end workflow test for LangPlug application
Tests complete user journey from login to learning
"""

import requests
import json
import time
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

TEST_USER = {
    "email": "test@example.com",
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

def test_workflow():
    """Test complete workflow"""

    print("\n" + "=" * 60)
    print("LangPlug Full Workflow Test")
    print("=" * 60 + "\n")

    all_passed = True

    # Step 1: Check services
    print_test("Step 1: Checking services...", "test")

    try:
        # Check backend
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_test("Backend is healthy", "pass")
        else:
            print_test(f"Backend health check failed: {response.status_code}", "fail")
            all_passed = False
    except Exception as e:
        print_test(f"Backend connection failed: {e}", "fail")
        return False

    try:
        # Check frontend
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            print_test("Frontend is accessible", "pass")
        else:
            print_test(f"Frontend check failed: {response.status_code}", "fail")
            all_passed = False
    except Exception as e:
        print_test(f"Frontend connection failed: {e}", "fail")
        all_passed = False

    print()

    # Step 2: User Authentication
    print_test("Step 2: User authentication...", "test")

    # Login
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )

    if response.status_code == 200:
        token_data = response.json()
        token = token_data.get("access_token")
        print_test("Login successful", "pass")
        headers = {"Authorization": f"Bearer {token}"}
    else:
        print_test(f"Login failed: {response.status_code}", "fail")
        return False

    # Get user info
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    if response.status_code == 200:
        user = response.json()
        print_test(f"User authenticated: {user.get('email')}", "pass")
    else:
        print_test(f"Get user failed: {response.status_code}", "fail")
        all_passed = False

    print()

    # Step 3: Vocabulary Features
    print_test("Step 3: Testing vocabulary features...", "test")

    # Get available languages
    response = requests.get(f"{BASE_URL}/api/vocabulary/languages", headers=headers)
    if response.status_code == 200:
        languages = response.json()
        lang_list = languages.get("languages", [])
        print_test(f"Available languages: {[l['name'] for l in lang_list]}", "pass")
    else:
        print_test(f"Get languages failed: {response.status_code}", "fail")
        all_passed = False

    # Get vocabulary stats
    response = requests.get(f"{BASE_URL}/api/vocabulary/stats", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print_test("Vocabulary stats retrieved", "pass")

        # Display stats
        for level, data in stats.items():
            if isinstance(data, dict):
                known = data.get("known_words", 0)
                total = data.get("total_words", 0)
                print_test(f"  {level}: {known}/{total} words known", "info")
    else:
        print_test(f"Get stats failed: {response.status_code}", "fail")
        all_passed = False

    # Get vocabulary library
    response = requests.get(f"{BASE_URL}/api/vocabulary/library/A1", headers=headers)
    if response.status_code == 200:
        library = response.json()
        word_count = len(library) if isinstance(library, list) else 0
        print_test(f"A1 vocabulary library: {word_count} words", "pass")
    else:
        print_test(f"Get library failed: {response.status_code}", "fail")
        all_passed = False

    print()

    # Step 4: Processing Features Check
    print_test("Step 4: Checking processing capabilities...", "test")

    # Check if processing routes are available
    response = requests.get(f"{BASE_URL}/api/processing/status", headers=headers)
    if response.status_code in [200, 404]:
        if response.status_code == 200:
            print_test("Processing service available", "pass")
        else:
            print_test("Processing routes not yet implemented", "info")
    else:
        print_test(f"Processing check failed: {response.status_code}", "fail")
        all_passed = False

    print()

    # Step 5: Game Features
    print_test("Step 5: Testing game features...", "test")

    # Check game sessions endpoint
    response = requests.get(f"{BASE_URL}/api/game/sessions", headers=headers)
    if response.status_code in [200, 404]:
        if response.status_code == 200:
            sessions = response.json()
            print_test(f"Game sessions available", "pass")
        else:
            print_test("Game routes not yet implemented", "info")
    else:
        print_test(f"Game check failed: {response.status_code}", "fail")
        all_passed = False

    print()

    # Step 6: Cleanup
    print_test("Step 6: Cleanup...", "test")

    # Logout
    response = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
    if response.status_code in [200, 204]:
        print_test("Logout successful", "pass")
    else:
        print_test(f"Logout failed: {response.status_code}", "fail")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print_test("All workflow tests passed!", "pass")
    else:
        print_test("Some workflow tests failed", "fail")
    print("=" * 60 + "\n")

    return all_passed

if __name__ == "__main__":
    success = test_workflow()
    sys.exit(0 if success else 1)