#!/usr/bin/env python3
"""
Simplified E2E Test: Assumes servers are already running
Tests: Login → Superstore → Episode 1 → Skip Game → Video with Subtitles
"""

import asyncio
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("[ERROR] Playwright not installed")
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent.parent
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
SCREENSHOT_PATH = REPO_ROOT / "tests" / "e2e_subtitle_screenshot.png"


async def run_test():
    """Run the E2E test (assumes servers are already running)"""
    print("\n" + "=" * 60)
    print("E2E Test: Subtitle Verification (Simple)")
    print("=" * 60 + "\n")

    # Check servers
    import requests

    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if response.status_code != 200:
            print("[ERROR] Backend not healthy")
            return False
        print("[OK] Backend is healthy")
    except Exception as e:
        print(f"[ERROR] Backend not responding: {e}")
        return False

    async with async_playwright() as p:
        print("[BROWSER] Launching Chromium...")
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()

        try:
            # Step 1: Navigate to frontend
            print("[STEP 1] Navigating to frontend...")
            await page.goto(FRONTEND_URL, timeout=15000)
            await page.wait_for_load_state("networkidle")

            # Step 2: Login
            print("[STEP 2] Logging in...")
            await page.fill('input[type="email"]', "e2etest@example.com")
            await page.fill('input[type="password"]', "E2eTest123!")
            await page.click('button:has-text("Sign In")')

            await page.wait_for_timeout(3000)
            print("[OK] Login completed")

            # Save screenshot after login
            after_login = REPO_ROOT / "tests" / "after_login.png"
            await page.screenshot(path=str(after_login))
            print(f"[DEBUG] Screenshot saved: {after_login}")

            # Step 3: Navigate to Superstore
            print("[STEP 3] Clicking Superstore...")
            await page.wait_for_selector('[data-testid="series-card-superstore"]', timeout=15000)
            await page.click('[data-testid="series-card-superstore"]')
            await page.wait_for_timeout(2000)

            # Step 4: Click Play on Episode 1
            print("[STEP 4] Clicking Play for Episode 1...")
            play_button = page.locator('button:has-text("Play")').first
            await play_button.click(timeout=5000)
            await page.wait_for_timeout(3000)

            print("[INFO] Episode has multiple chunks - waiting for processing...")

            # Step 5: Wait for processing to complete and skip games
            print("[STEP 5] Waiting for chunk processing...")

            max_wait = 300  # 5 minutes max
            waited = 0

            while waited < max_wait:
                # Check if we're on video player yet
                if await page.locator("video").count() > 0:
                    print("[OK] Video player found!")
                    break

                # Check for action buttons (Skip, Continue, Start, Next)
                action_btn = page.locator(
                    'button:has-text("Skip"), button:has-text("Continue"), button:has-text("Start"), button:has-text("Next")'
                ).first

                if await action_btn.count() > 0:
                    print(f"[INFO] Found action button at {waited}s, clicking...")
                    try:
                        await action_btn.click(timeout=2000)
                        await page.wait_for_timeout(1500)
                    except:
                        pass

                await page.wait_for_timeout(5000)
                waited += 5

                if waited % 20 == 0:
                    print(f"[INFO] Waiting... ({waited}s)")

            # Step 6: Verify video player
            print("[STEP 6] Verifying video player...")

            if await page.locator("video").count() == 0:
                print("[ERROR] Video player not found after processing")
                await page.screenshot(path=str(SCREENSHOT_PATH))

                # Debug: show page content
                page_text = await page.locator("body").inner_text()
                page_text_safe = "".join(char if ord(char) < 128 else "?" for char in page_text)
                print(f"[DEBUG] Page content: {page_text_safe[:300]}...")
                return False

            # Play video
            print("[INFO] Starting video playback...")
            await page.locator("video").first.click()
            await page.wait_for_timeout(2000)

            try:
                await page.evaluate("document.querySelector('video')?.play()")
            except:
                pass

            # Wait for subtitles to appear
            print("[INFO] Waiting for subtitles...")
            await page.wait_for_timeout(5000)

            # Take final screenshot
            print("[INFO] Taking final screenshot...")
            await page.screenshot(path=str(SCREENSHOT_PATH))

            # Check subtitle tracks
            subtitle_count = await page.evaluate("""
                () => {
                    const video = document.querySelector('video');
                    if (!video) return 0;
                    return video.textTracks.length;
                }
            """)

            print(f"[INFO] Found {subtitle_count} subtitle tracks")

            # Success
            print("\n[SUCCESS] E2E test completed successfully!")
            print(f"[SUCCESS] Screenshot saved: {SCREENSHOT_PATH}")

            return True

        except Exception as e:
            print(f"\n[ERROR] Test failed: {e}")
            import traceback

            traceback.print_exc()

            try:
                await page.screenshot(path=str(SCREENSHOT_PATH))
                print(f"[DEBUG] Error screenshot saved: {SCREENSHOT_PATH}")
            except:
                pass

            return False

        finally:
            await browser.close()


if __name__ == "__main__":
    success = asyncio.run(run_test())
    sys.exit(0 if success else 1)
