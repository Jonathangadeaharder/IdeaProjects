import { test, expect, assertions, navigation, actions } from '../fixtures/fixtures';
import { TEST_USERS, ROUTES } from '../fixtures/testData';

test.describe('Authentication - User Registration', () => {
  test('should register with valid credentials', async ({ page, freshPage }) => {
    await navigation.goToRegister(page);

    // Register new user
    const uniqueEmail = `test${Date.now()}@example.com`;
    await actions.register(page, uniqueEmail, 'newuser', 'NewPass123!');

    // Verify successful registration
    await expect(page).toHaveURL(ROUTES.videos);
    await assertions.assertUserLoggedIn(page, 'newuser');
  });

  test('should reject password without special character', async ({ page, freshPage }) => {
    await navigation.goToRegister(page);

    const uniqueEmail = `test${Date.now()}@example.com`;
    await page.fill('input[type="email"]', uniqueEmail);
    await page.fill('input[placeholder*="Username"]', 'testuser');

    const passwordFields = page.locator('[type="password"]');
    await passwordFields.nth(0).fill('NoSpecialChar123456');
    await passwordFields.nth(1).fill('NoSpecialChar123456');

    await page.click('button:has-text("Sign Up")');

    // Expect to stay on registration page with error
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(ROUTES.register);

    // Check for error message (currently generic, but should be specific)
    const errorMessage = page.locator('text=Failed to create account');
    await expect(errorMessage).toBeVisible();
  });

  test('should reject password shorter than 12 characters', async ({ page, freshPage }) => {
    await navigation.goToRegister(page);

    const uniqueEmail = `test${Date.now()}@example.com`;
    await page.fill('input[type="email"]', uniqueEmail);
    await page.fill('input[placeholder*="Username"]', 'shortpass');

    const passwordFields = page.locator('[type="password"]');
    await passwordFields.nth(0).fill('Short1!');
    await passwordFields.nth(1).fill('Short1!');

    await page.click('button:has-text("Sign Up")');

    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(ROUTES.register);
  });

  test('should show form validation for empty fields', async ({ page, freshPage }) => {
    await navigation.goToRegister(page);

    // Try to submit without filling anything
    const signUpButton = page.locator('button:has-text("Sign Up")');
    await signUpButton.click();

    // Should not proceed with submission
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(ROUTES.register);
  });
});

test.describe('Authentication - User Login', () => {
  test('should login with valid credentials', async ({ page, freshPage }) => {
    await navigation.goToLogin(page);

    // First register a user
    const uniqueEmail = `testlogin${Date.now()}@example.com`;
    const password = 'LoginPass123!';

    // Go to register and create account
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'loginuser', password);

    // Now logout and test login
    await actions.logout(page);
    await assertions.assertUserLoggedOut(page);

    // Login
    await actions.login(page, uniqueEmail, password);
    await assertions.assertUserLoggedIn(page, 'loginuser');
  });

  test('should reject login with wrong password', async ({ page, freshPage }) => {
    await navigation.goToLogin(page);

    await page.fill('input[type="email"]', TEST_USERS.valid.email);
    await page.fill('input[type="password"]', 'WrongPassword123!');

    await page.click('button:has-text("Sign In")');

    // Should stay on login page or show error
    await page.waitForLoadState('networkidle');
    // Depending on error handling, might see error message
    const isOnLoginPage = page.url().includes('/login');
    const hasErrorMessage = await page.locator('text=Invalid').isVisible().catch(() => false);

    if (!isOnLoginPage && !hasErrorMessage) {
      throw new Error('Expected login to fail with wrong password');
    }
  });

  test('should reject login with non-existent email', async ({ page, freshPage }) => {
    await navigation.goToLogin(page);

    await page.fill('input[type="email"]', 'nonexistent@example.com');
    await page.fill('input[type="password"]', TEST_USERS.valid.password);

    await page.click('button:has-text("Sign In")');

    await page.waitForLoadState('networkidle');
    // Should show error or stay on login page
    const isOnLoginPage = page.url().includes('/login');
    expect(isOnLoginPage).toBeTruthy();
  });

  test('should persist login session across navigation', async ({ page, freshPage }) => {
    // This test will use the authenticatedPage fixture implicitly
    await page.goto(ROUTES.login);
    await navigation.goToLogin(page);

    // Register and login
    const uniqueEmail = `testsession${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'sessionuser', 'SessionPass123!');

    // Navigate to different pages
    await page.goto(ROUTES.vocabulary);
    await expect(page).toHaveURL(ROUTES.vocabulary);

    // User should still be logged in
    await assertions.assertUserLoggedIn(page, 'sessionuser');

    // Navigate back to videos
    await page.goto(ROUTES.videos);
    await expect(page).toHaveURL(ROUTES.videos);

    // Still logged in
    await assertions.assertUserLoggedIn(page, 'sessionuser');
  });
});

test.describe('Authentication - User Logout', () => {
  test('should logout and clear session', async ({ page }) => {
    // First login
    await page.goto(ROUTES.login);
    const uniqueEmail = `testlogout${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'logoutuser', 'LogoutPass123!');

    // Verify logged in
    await assertions.assertUserLoggedIn(page, 'logoutuser');

    // Logout
    await actions.logout(page);

    // Verify logged out
    await assertions.assertUserLoggedOut(page);

    // Verify can't access protected pages without login
    await page.goto(ROUTES.videos);
    // Should redirect to login
    await page.waitForURL(ROUTES.login);
  });

  test('should show success message on logout', async ({ page }) => {
    // Login first
    await page.goto(ROUTES.login);
    const uniqueEmail = `testlogoutmsg${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'logoutmsguser', 'LogoutMsg123!');

    // Logout
    await page.click('button:has-text("Logout")');

    // Wait for logout to complete
    await page.waitForURL(ROUTES.login);

    // Check for success message
    const successMessage = page.locator('text=Logged out successfully');
    await expect(successMessage).toBeVisible();
  });
});

test.describe('Authentication - Session Management', () => {
  test('should preserve user info after page refresh', async ({ page }) => {
    // Login
    await page.goto(ROUTES.login);
    const uniqueEmail = `testrefresh${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'refreshuser', 'RefreshPass123!');

    // Refresh page
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Should still be logged in
    await assertions.assertUserLoggedIn(page, 'refreshuser');
  });
});
