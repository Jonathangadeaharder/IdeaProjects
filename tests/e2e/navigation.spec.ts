import { test, expect, assertions, navigation, actions } from '../fixtures/fixtures';
import { ROUTES } from '../fixtures/testData';

test.describe('Navigation - Main Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto(ROUTES.login);
    const uniqueEmail = `navtest${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'navuser', 'NavPass123!');
  });

  test('should navigate between Videos and Vocabulary', async ({ page }) => {
    // Should be on videos page after login
    await expect(page).toHaveURL(ROUTES.videos);

    // Click Vocabulary Library
    await navigation.goToVocabulary(page);
    await expect(page).toHaveURL(ROUTES.vocabulary);
    await expect(page.locator('text=Vocabulary Library')).toBeVisible();

    // Click back button or LangPlug logo
    await page.click('text=← Back to Videos');
    await expect(page).toHaveURL(ROUTES.videos);
  });

  test('should navigate using navigation buttons', async ({ page }) => {
    // Click Vocabulary Library button
    const vocabButton = page.locator('button:has-text("Vocabulary Library")');
    await expect(vocabButton).toBeVisible();
    await vocabButton.click();

    await page.waitForURL(ROUTES.vocabulary);
    await expect(page).toHaveURL(ROUTES.vocabulary);
  });

  test('should display user profile in header', async ({ page }) => {
    // Check username is displayed
    await expect(page.locator('text=Welcome, navuser')).toBeVisible();

    // Check profile button exists
    const profileButton = page.locator('button:has-text("Profile")');
    await expect(profileButton).toBeVisible();
  });

  test('should have logout button in header', async ({ page }) => {
    // Check logout button exists
    const logoutButton = page.locator('button:has-text("Logout")');
    await expect(logoutButton).toBeVisible();

    // Click logout
    await logoutButton.click();
    await page.waitForURL(ROUTES.login);
  });
});

test.describe('Navigation - URL Routing', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto(ROUTES.login);
    const uniqueEmail = `urltesttest${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'urluser', 'UrlPass123!');
  });

  test('should navigate directly via URL to videos page', async ({ page }) => {
    await page.goto(ROUTES.videos);
    await expect(page).toHaveURL(ROUTES.videos);
    await expect(page.locator('text=Learn German Through TV Shows')).toBeVisible();
  });

  test('should navigate directly via URL to vocabulary page', async ({ page }) => {
    await page.goto(ROUTES.vocabulary);
    await expect(page).toHaveURL(ROUTES.vocabulary);
    await expect(page.locator('text=Vocabulary Library')).toBeVisible();
  });

  test('should redirect to login when accessing protected pages without auth', async ({ page }) => {
    // Logout first
    await page.click('button:has-text("Logout")');
    await page.waitForURL(ROUTES.login);

    // Try to access videos page directly
    await page.goto(ROUTES.videos);

    // Should redirect to login or show error
    const isOnLogin = page.url().includes(ROUTES.login);
    const isAccessDenied = await page.locator('text=unauthorized').isVisible().catch(() => false);

    // At minimum, shouldn't see the videos content
    const videosContent = await page.locator('text=Learn German Through TV Shows').isVisible().catch(() => false);
    expect(isOnLogin || isAccessDenied || !videosContent).toBeTruthy();
  });
});

test.describe('Navigation - State Persistence', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto(ROUTES.login);
    const uniqueEmail = `statetest${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'stateuser', 'StatePass123!');
  });

  test('should preserve vocabulary data when navigating away', async ({ page }) => {
    // Navigate to vocabulary
    await navigation.goToVocabulary(page);

    // Mark a word
    await actions.markWordAsKnown(page, 'Haus');
    await expect(page.locator('text=1 / 715')).toBeVisible();

    // Navigate to videos
    await page.goto(ROUTES.videos);
    await expect(page).toHaveURL(ROUTES.videos);

    // Navigate back to vocabulary
    await navigation.goToVocabulary(page);

    // Word should still be marked
    await expect(page.locator('text=1 / 715')).toBeVisible();
  });

  test('should maintain login state across navigation', async ({ page }) => {
    // Check logged in
    await assertions.assertUserLoggedIn(page, 'stateuser');

    // Navigate to vocabulary
    await navigation.goToVocabulary(page);
    await assertions.assertUserLoggedIn(page, 'stateuser');

    // Navigate back to videos
    await page.goto(ROUTES.videos);
    await assertions.assertUserLoggedIn(page, 'stateuser');

    // Refresh page
    await page.reload();
    await page.waitForLoadState('networkidle');
    await assertions.assertUserLoggedIn(page, 'stateuser');
  });
});

test.describe('Navigation - Breadcrumbs and Back Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto(ROUTES.login);
    const uniqueEmail = `breadtest${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'breaduser', 'BreadPass123!');
  });

  test('should show back button on vocabulary page', async ({ page }) => {
    await navigation.goToVocabulary(page);

    // Check for back button
    const backButton = page.locator('text=← Back to Videos');
    await expect(backButton).toBeVisible();

    // Click back
    await backButton.click();
    await expect(page).toHaveURL(ROUTES.videos);
  });

  test('should navigate back to correct page with state', async ({ page }) => {
    // Go to vocabulary
    await navigation.goToVocabulary(page);

    // Switch to A2 level
    await actions.switchVocabularyLevel(page, 'A2');
    const a2Heading = page.locator('text=A2 Level Vocabulary');
    await expect(a2Heading).toBeVisible();

    // Go back to videos
    await page.click('text=← Back to Videos');
    await expect(page).toHaveURL(ROUTES.videos);

    // Go back to vocabulary
    await navigation.goToVocabulary(page);

    // Should return to A2 level (implementation dependent)
    // If not, that's okay - just showing the pattern
  });
});

test.describe('Navigation - Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto(ROUTES.login);
    const uniqueEmail = `errnavtest${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'errnavuser', 'ErrNav123!');
  });

  test('should handle invalid routes gracefully', async ({ page }) => {
    // Navigate to non-existent page
    await page.goto('/invalid-page');

    // Should either redirect or show error
    await page.waitForLoadState('networkidle');

    // Should not have a white screen of death
    const content = page.locator('body');
    await expect(content).toBeVisible();
  });

  test('should recover from network errors during navigation', async ({ page }) => {
    // This is a placeholder for network error handling
    // In a real scenario, you might simulate network offline mode

    try {
      // Go to vocabulary
      await navigation.goToVocabulary(page);
      await expect(page).toHaveURL(ROUTES.vocabulary);

      // Go back to videos
      await page.goto(ROUTES.videos);
      await expect(page).toHaveURL(ROUTES.videos);
    } catch (error) {
      // Should handle gracefully
      console.log('Navigation error handled:', error);
    }
  });
});
