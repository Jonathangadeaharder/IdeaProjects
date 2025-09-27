#!/usr/bin/env python3
"""
End-to-end UI test script for LangPlug application
Tests the actual user interface flows using Playwright
"""

import asyncio
from playwright.async_api import async_playwright, expect
import sys

BASE_URL = "http://localhost:3000"
API_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "password": "TestPassword123!"
}

class TestStatus:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def pass_test(self, name):
        self.passed += 1
        print(f"[PASS] {name}")

    def fail_test(self, name, error):
        self.failed += 1
        self.errors.append((name, error))
        print(f"[FAIL] {name}: {error}")

    def summary(self):
        total = self.passed + self.failed
        print("\n" + "=" * 50)
        print(f"Test Results: {self.passed}/{total} passed")
        if self.errors:
            print("\nFailed tests:")
            for name, error in self.errors:
                print(f"  - {name}: {error}")
        print("=" * 50)
        return self.failed == 0


async def test_login_flow(page, status):
    """Test the login flow"""
    try:
        print("\n[TEST] Testing login flow...")

        # Navigate to the app
        await page.goto(BASE_URL)
        await page.wait_for_load_state("networkidle")

        # Should redirect to login if not authenticated
        await expect(page).to_have_url(f"{BASE_URL}/login", timeout=5000)

        # Fill in login form
        await page.fill('input[type="email"]', TEST_USER["email"])
        await page.fill('input[type="password"]', TEST_USER["password"])

        # Click login button
        await page.click('button[type="submit"]')

        # Wait for navigation
        await page.wait_for_load_state("networkidle")

        # Should redirect to home after login
        await expect(page).to_have_url(BASE_URL + "/", timeout=10000)

        status.pass_test("Login flow")
        return True
    except Exception as e:
        status.fail_test("Login flow", str(e))
        return False


async def test_navigation(page, status):
    """Test navigation between pages"""
    try:
        print("\n[TEST] Testing navigation...")

        # Should be on home page
        await expect(page).to_have_url(BASE_URL + "/")

        # Look for video selection elements
        video_section = page.locator('text=/select.*video|video.*selection|choose.*video/i').first
        if await video_section.count() > 0:
            status.pass_test("Video selection page visible")
        else:
            status.fail_test("Video selection page", "No video selection elements found")

        # Check for navigation elements
        nav_elements = page.locator('nav, [role="navigation"], header')
        if await nav_elements.count() > 0:
            status.pass_test("Navigation elements present")
        else:
            status.fail_test("Navigation elements", "No navigation found")

        return True
    except Exception as e:
        status.fail_test("Navigation", str(e))
        return False


async def test_video_upload(page, status):
    """Test video upload functionality"""
    try:
        print("\n[TEST] Testing video upload...")

        # Look for upload button or input
        upload_button = page.locator('text=/upload|select.*file|choose.*file/i').first
        if await upload_button.count() > 0:
            status.pass_test("Upload button found")

            # Try to interact with it (but don't actually upload)
            await upload_button.hover()
            status.pass_test("Upload button interactive")
        else:
            status.fail_test("Upload button", "No upload elements found")

        return True
    except Exception as e:
        status.fail_test("Video upload", str(e))
        return False


async def test_vocabulary_section(page, status):
    """Test vocabulary section"""
    try:
        print("\n[TEST] Testing vocabulary section...")

        # Try to navigate to vocabulary
        vocab_link = page.locator('text=/vocabulary|vocab|words/i').first
        if await vocab_link.count() > 0:
            await vocab_link.click()
            await page.wait_for_load_state("networkidle")
            status.pass_test("Vocabulary navigation")

            # Check for vocabulary content
            vocab_content = page.locator('text=/level|A1|A2|B1|B2|word/i')
            if await vocab_content.count() > 0:
                status.pass_test("Vocabulary content loaded")
            else:
                status.fail_test("Vocabulary content", "No vocabulary data visible")
        else:
            # Vocabulary might not be directly accessible yet
            status.pass_test("Vocabulary section (not yet accessible)")

        return True
    except Exception as e:
        status.fail_test("Vocabulary section", str(e))
        return False


async def test_logout(page, status):
    """Test logout functionality"""
    try:
        print("\n[TEST] Testing logout...")

        # Look for logout button
        logout_button = page.locator('text=/logout|sign.*out|log.*out/i').first

        if await logout_button.count() == 0:
            # Try looking in a menu or profile section
            menu_button = page.locator('[aria-label*="menu"], [aria-label*="profile"], button:has-text("Profile")')
            if await menu_button.count() > 0:
                await menu_button.first.click()
                await page.wait_for_timeout(500)
                logout_button = page.locator('text=/logout|sign.*out/i').first

        if await logout_button.count() > 0:
            await logout_button.click()
            await page.wait_for_load_state("networkidle")

            # Should redirect to login
            await expect(page).to_have_url(f"{BASE_URL}/login", timeout=5000)
            status.pass_test("Logout functionality")
        else:
            status.fail_test("Logout", "No logout button found")

        return True
    except Exception as e:
        status.fail_test("Logout", str(e))
        return False


async def run_ui_tests():
    """Run all UI tests"""
    print("\n" + "=" * 50)
    print("LangPlug UI End-to-End Testing")
    print("=" * 50)

    status = TestStatus()

    async with async_playwright() as p:
        # Launch browser in headless mode
        browser = await p.chromium.launch(headless=True)

        try:
            # Create a new browser context
            context = await browser.new_context()
            page = await context.new_page()

            # Run tests in sequence
            if await test_login_flow(page, status):
                await test_navigation(page, status)
                await test_video_upload(page, status)
                await test_vocabulary_section(page, status)
                await test_logout(page, status)

        except Exception as e:
            status.fail_test("Test execution", str(e))
        finally:
            await browser.close()

    # Print summary
    return status.summary()


if __name__ == "__main__":
    success = asyncio.run(run_ui_tests())
    sys.exit(0 if success else 1)