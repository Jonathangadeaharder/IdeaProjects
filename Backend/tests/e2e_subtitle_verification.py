#!/usr/bin/env python3
"""
E2E Test: Verify subtitle display (German top, Spanish bottom)
Tests the complete workflow: Login → Superstore → Episode 1 → Skip Game → Video with Subtitles
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

# Check if playwright is installed
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("[ERROR] Playwright not installed. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    from playwright.async_api import async_playwright


REPO_ROOT = Path(__file__).parent.parent.parent
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
SCREENSHOT_PATH = REPO_ROOT / "tests" / "e2e_subtitle_screenshot.png"


def start_servers():
    """Start backend and frontend servers using start-all.bat"""
    print("[INFO] Starting servers via start-all.bat...")
    start_script = REPO_ROOT / "scripts" / "start-all.bat"

    # Run the batch file (it will start servers in separate windows)
    subprocess.Popen([str(start_script)], shell=True, cwd=str(REPO_ROOT))

    print("[INFO] Waiting 30 seconds for servers to fully initialize...")
    time.sleep(30)


def check_server_health(url: str, max_retries: int = 10) -> bool:
    """Check if server is responding"""
    import requests

    for i in range(max_retries):
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"[OK] Server at {url} is healthy")
                return True
        except Exception as e:
            print(f"[RETRY {i+1}/{max_retries}] Waiting for {url}... ({e})")
            time.sleep(3)

    return False


async def run_e2e_test():
    """Run the E2E test"""
    print("\n" + "=" * 60)
    print("E2E Test: Subtitle Verification")
    print("=" * 60 + "\n")

    # Check if servers are running
    print("[CHECK] Verifying backend health...")
    if not check_server_health(BACKEND_URL):
        print("[ERROR] Backend not responding. Please check logs.")
        return False

    print("[CHECK] Waiting for frontend...")
    time.sleep(5)  # Frontend takes a bit longer

    # Register test user via API first
    print("[SETUP] Registering test user via API...")
    import requests

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json={"username": "e2etest", "email": "e2etest@example.com", "password": "E2eTest123!"},
            timeout=10,
        )
        if response.status_code == 201:
            print("[OK] Test user registered successfully")
        elif response.status_code == 400 and "already exists" in response.text.lower():
            print("[INFO] Test user already exists, continuing...")
        else:
            print(f"[WARN] User registration returned {response.status_code}: {response.text[:100]}")
    except Exception as e:
        print(f"[WARN] Could not register user via API: {e}")
        print("[INFO] Continuing anyway, might already exist...")

    async with async_playwright() as p:
        # Launch browser
        print("[BROWSER] Launching Chromium...")
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}, record_video_dir=str(REPO_ROOT / "tests")
        )
        page = await context.new_page()

        try:
            # Step 1: Navigate to frontend
            print(f"[STEP 1] Navigating to {FRONTEND_URL}...")
            await page.goto(FRONTEND_URL, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            # Step 2: Login (user pre-registered via API)
            print("[STEP 2] Logging in...")

            # Fill login form
            email_input = page.locator('input[type="email"], input[placeholder*="email" i]').first
            password_input = page.locator('input[type="password"]').first

            await email_input.fill("e2etest@example.com")
            await password_input.fill("E2eTest123!")

            # Click submit
            submit_btn = page.locator('button[type="submit"], button:has-text("Sign In")').first
            await submit_btn.click()

            print("[INFO] Waiting for login to complete...")
            await page.wait_for_timeout(5000)

            # Check if login was successful
            if await page.locator('text="Invalid email or password"').count() > 0:
                print("[ERROR] Login failed - invalid credentials")
                await page.screenshot(path=str(SCREENSHOT_PATH))
                return False

            # Should be redirected to main page/dashboard after successful login
            print("[OK] Login successful")

            # Step 3: Navigate to Superstore
            print("[STEP 3] Navigating to Superstore...")

            # Wait for page to fully load after login
            await page.wait_for_timeout(3000)

            # Take a screenshot to see what's on the page
            after_login_screenshot = REPO_ROOT / "tests" / "after_login.png"
            await page.screenshot(path=str(after_login_screenshot))
            print(f"[DEBUG] Screenshot saved after login: {after_login_screenshot}")

            # Get page HTML for debugging
            page_html = await page.content()
            debug_html_path = REPO_ROOT / "tests" / "after_login.html"
            debug_html_path.write_text(page_html, encoding="utf-8")
            print(f"[DEBUG] Page HTML saved: {debug_html_path}")

            # Wait for series cards to load
            print("[INFO] Waiting for series cards to load...")
            await page.wait_for_selector('[data-testid^="series-card-"]', timeout=15000)

            # Use the proper data-testid selector
            superstore_selector = '[data-testid="series-card-superstore"]'

            # Verify the card exists
            if await page.locator(superstore_selector).count() == 0:
                print("[ERROR] Superstore series card not found using data-testid")

                # Debug: List all series cards
                all_cards = await page.locator('[data-testid^="series-card-"]').all()
                print(f"[DEBUG] Found {len(all_cards)} series cards on page")

                for card in all_cards:
                    try:
                        testid = await card.get_attribute("data-testid")
                        print(f"[DEBUG] - Card: {testid}")
                    except:
                        pass

                await page.screenshot(path=str(SCREENSHOT_PATH))
                return False

            print("[INFO] Clicking Superstore card...")
            superstore_card = page.locator(superstore_selector)
            await superstore_card.click(timeout=5000)
            await page.wait_for_timeout(3000)

            # Step 4: Click Play for Episode 1
            print("[STEP 4] Clicking Play for Episode 1...")

            # Look for the Play button for Episode 1
            play_btn = page.locator('button:has-text("Play")').first

            if await play_btn.count() == 0:
                print("[ERROR] Play button not found")
                await page.screenshot(path=str(SCREENSHOT_PATH))
                return False

            await play_btn.click()
            print("[INFO] Clicked Play button...")
            await page.wait_for_timeout(3000)

            # Handle multi-chunk processing: Each chunk shows game separately
            print("[INFO] Episode has multiple chunks - each shows vocabulary game after processing")
            print("[INFO] Will skip through all games until video player appears...")

            max_iterations = 5  # Max 5 chunks
            for chunk_iteration in range(max_iterations):
                print(f"\n[CHUNK {chunk_iteration + 1}] Waiting for processing/game...")

                # Wait for either game or video to appear
                max_wait = 180  # 3 minutes per chunk
                waited = 0

                while waited < max_wait:
                    await page.wait_for_timeout(5000)
                    waited += 5

                    # Check for game or video
                    has_game = (
                        await page.locator(
                            'button:has-text("Skip"), button:has-text("Start"), button:has-text("Continue")'
                        ).count()
                        > 0
                    )
                    has_video = await page.locator("video").count() > 0

                    if has_video:
                        print(f"[OK] Video player appeared after chunk {chunk_iteration + 1}!")
                        break

                    if has_game:
                        print(f"[OK] Game ready for chunk {chunk_iteration + 1} (waited {waited}s)")
                        break

                    # Show progress
                    if waited % 20 == 0:
                        try:
                            if await page.locator('text*="Processing"').count() > 0:
                                status = await page.locator('text*="Processing"').first.inner_text()
                                status_safe = "".join(char if ord(char) < 128 else "?" for char in status[:50])
                                print(f"[INFO] {status_safe}... ({waited}s)")
                        except:
                            print(f"[INFO] Waiting... ({waited}s)")

                # Check what we got
                has_video = await page.locator("video").count() > 0
                if has_video:
                    print(f"[SUCCESS] Video player found after {chunk_iteration + 1} chunk(s)!")
                    break

                # Skip through the game for this chunk
                print(f"[INFO] Skipping game for chunk {chunk_iteration + 1}...")
                for i in range(10):  # Try to skip up to 10 times
                    skip_btn = page.locator(
                        'button:has-text("Skip"), button:has-text("Continue"), button:has-text("Start"), button:has-text("Next")'
                    ).first

                    if await skip_btn.count() > 0:
                        try:
                            await skip_btn.click(timeout=2000)
                            await page.wait_for_timeout(1000)
                        except:
                            break
                    else:
                        break

                # After skipping, wait a moment before checking for next chunk
                await page.wait_for_timeout(2000)

            # Step 5: Final check for vocabulary game (shouldn't be needed but just in case)
            print("\n[STEP 5] Final game check...")

            # Look for skip/continue/start buttons
            max_attempts = 15
            for i in range(max_attempts):
                # Try multiple button variations
                skip_btn = page.locator(
                    'button:has-text("Skip"), button:has-text("Continue"), button:has-text("Start"), button:has-text("Next")'
                ).first

                if await skip_btn.count() > 0:
                    print(f"[INFO] Found action button (attempt {i+1}), clicking...")
                    try:
                        await skip_btn.click(timeout=2000)
                        await page.wait_for_timeout(1500)
                    except:
                        print("[WARN] Could not click button, might have moved on")
                        break
                else:
                    # Check if we're already on video player
                    if await page.locator("video").count() > 0:
                        print("[INFO] Video player detected, game completed or skipped")
                        break

                    print(f"[INFO] No action buttons found (attempt {i+1})")
                    await page.wait_for_timeout(1000)

            # Step 6: Wait for video player and subtitles
            print("[STEP 6] Waiting for video player...")

            # Wait for video element
            try:
                await page.wait_for_selector("video", timeout=15000)
                print("[OK] Video player found!")
            except:
                print("[ERROR] Video element not found after 15 seconds")
                await page.screenshot(path=str(SCREENSHOT_PATH))
                # List page content for debugging (avoid Unicode issues)
                try:
                    page_text = await page.locator("body").inner_text()
                    # Filter out non-ASCII characters to avoid Windows console encoding issues
                    page_text_safe = "".join(char if ord(char) < 128 else "?" for char in page_text)
                    print(f"[DEBUG] Page content: {page_text_safe[:300]}...")
                except Exception as e:
                    print(f"[WARN] Could not extract page text: {e}")
                return False

            # Play the video
            print("[INFO] Starting video playback...")
            try:
                await page.locator("video").first.click()
                await page.wait_for_timeout(2000)

                # Try to play via JavaScript
                await page.evaluate("document.querySelector('video')?.play()")
            except Exception as e:
                print(f"[WARN] Could not start playback: {e}")

            print("[INFO] Waiting for subtitles to appear (10 seconds)...")
            await page.wait_for_timeout(10000)

            # Step 7: Take screenshot for manual verification
            print("[STEP 7] Taking screenshot of video with subtitles...")
            await page.screenshot(path=str(SCREENSHOT_PATH), full_page=False)
            print(f"[SUCCESS] Screenshot saved: {SCREENSHOT_PATH}")

            # Step 8: Analyze subtitle content
            print("[STEP 8] Analyzing subtitle content...")

            # Get all text on page
            page_content = await page.locator("body").inner_text()

            # Look for common German characters
            has_german_chars = any(char in page_content for char in ["ä", "ö", "ü", "ß", "Ä", "Ö", "Ü"])

            # Look for common Spanish words/characters
            has_spanish_chars = any(char in page_content for char in ["¿", "¡", "ñ", "á", "é", "í", "ó", "ú"])

            print(f"[RESULT] German characters detected: {has_german_chars}")
            print(f"[RESULT] Spanish characters detected: {has_spanish_chars}")

            # Try to extract subtitle elements
            try:
                subtitle_tracks = await page.locator('track, [class*="subtitle"], [class*="caption"]').all()
                print(f"[INFO] Found {len(subtitle_tracks)} subtitle-related elements")
            except:
                print("[WARN] Could not locate subtitle elements via selectors")

            print("\n[SUCCESS] E2E test completed!")
            print(f"[ACTION] Review screenshot at: {SCREENSHOT_PATH}")
            print("[ACTION] Verify manually:")
            print("  1. German subtitle should be on TOP (original audio)")
            print("  2. Spanish subtitle should be on BOTTOM (translation)")

            # Keep browser open for manual inspection
            print("\n[INFO] Keeping browser open for 30 seconds for manual inspection...")
            await page.wait_for_timeout(30000)

            return True

        except Exception as e:
            print(f"[ERROR] Test failed: {e}")
            import traceback

            traceback.print_exc()

            # Take error screenshot
            try:
                await page.screenshot(path=str(SCREENSHOT_PATH))
                print(f"[INFO] Error screenshot saved: {SCREENSHOT_PATH}")
            except:
                pass

            return False

        finally:
            await context.close()
            await browser.close()


def main():
    """Main entry point"""
    # Check if servers need to be started
    import requests

    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if response.status_code != 200:
            print("[INFO] Backend not healthy, starting servers...")
            start_servers()
    except:
        print("[INFO] Backend not responding, starting servers...")
        start_servers()

    # Run the E2E test
    success = asyncio.run(run_e2e_test())

    if success:
        print("\n[SUCCESS] E2E test completed successfully")
        print(f"[SUCCESS] Review screenshot: {SCREENSHOT_PATH}")
        sys.exit(0)
    else:
        print("\n[FAILED] E2E test failed")
        print(f"[FAILED] Check screenshots in: {REPO_ROOT / 'tests'}")
        sys.exit(1)


if __name__ == "__main__":
    main()
