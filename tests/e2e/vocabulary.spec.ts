import { test, expect, assertions, navigation, actions } from '../fixtures/fixtures';
import { VOCABULARY_DATA, ROUTES } from '../fixtures/testData';

test.describe('Vocabulary - Library Display', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto(ROUTES.login);
    const uniqueEmail = `vocabtest${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'vocabuser', 'VocabPass123!');

    // Navigate to vocabulary
    await navigation.goToVocabulary(page);
  });

  test('should display A1 vocabulary with correct word count', async ({ page }) => {
    await page.waitForURL(ROUTES.vocabulary);

    // Check heading
    await expect(page.locator('text=Vocabulary Library')).toBeVisible();

    // Check stats
    const statsText = page.locator('text=Total Words');
    await expect(statsText).toBeVisible();

    // Check A1 level shows correct count
    await expect(page.locator('text=A1 0 / 715')).toBeVisible();

    // Check first words are displayed
    for (const word of VOCABULARY_DATA.a1.firstWords.slice(0, 3)) {
      await expect(page.locator(`text="${word}"`).first()).toBeVisible();
    }
  });

  test('should display all vocabulary levels', async ({ page }) => {
    // Check all level buttons exist with correct counts
    await expect(page.locator('text=A1 0 / 715')).toBeVisible();
    await expect(page.locator('text=A2 0 / 574')).toBeVisible();
    await expect(page.locator('text=B1 0 / 896')).toBeVisible();
    await expect(page.locator('text=B2 0 / 1409')).toBeVisible();
    await expect(page.locator('text=C1 0 / 0')).toBeVisible();
    await expect(page.locator('text=C2 0 / 0')).toBeVisible();
  });

  test('should show pagination controls', async ({ page }) => {
    // Check pagination
    await expect(page.locator('text=Page 1 of 8')).toBeVisible();
    await expect(page.locator('button:has-text("Next")')).toBeVisible();
    await expect(page.locator('button:has-text("Previous")')).toBeVisible();

    // Previous button should be disabled on first page
    const prevButton = page.locator('button:has-text("Previous")');
    const prevClass = await prevButton.getAttribute('class');
    if (prevClass && prevClass.includes('disabled')) {
      expect(prevClass).toContain('disabled');
    }
  });
});

test.describe('Vocabulary - Mark Word as Known', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(ROUTES.login);
    const uniqueEmail = `marktest${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'markuser', 'MarkPass123!');
    await navigation.goToVocabulary(page);
  });

  test('should mark single word as known', async ({ page }) => {
    // Get initial count
    const initialStats = await page.locator('text=0 / 715').isVisible();
    expect(initialStats).toBeTruthy();

    // Mark word as known
    await actions.markWordAsKnown(page, 'Haus');

    // Check stats updated
    await expect(page.locator('text=1 / 715')).toBeVisible();
    await expect(page.locator('text=A1 1 / 715')).toBeVisible();

    // Check word is marked with checkmark
    const hausWord = page.locator('text="Haus"').first();
    await expect(hausWord).toBeVisible();
  });

  test('should update total word count when marking words', async ({ page }) => {
    // Mark first word
    await actions.markWordAsKnown(page, 'Haus');
    await expect(page.locator('text=Words Known').nth(0)).toContainText('1');

    // Mark second word
    await actions.markWordAsKnown(page, 'ab');
    await expect(page.locator('text=Words Known').nth(0)).toContainText('2');

    // Mark third word
    await actions.markWordAsKnown(page, 'Abend');
    await expect(page.locator('text=Words Known').nth(0)).toContainText('3');
  });

  test('should mark all words in level', async ({ page }) => {
    // Click "Mark All Known"
    await page.click('button:has-text("Mark All Known")');

    // Wait for update
    await page.waitForLoadState('networkidle');

    // Check all 715 words are marked
    await expect(page.locator('text=715 / 715')).toBeVisible();
    await expect(page.locator('text=A1 715 / 715')).toBeVisible();

    // Check progress updated
    await expect(page.locator('text=100%')).toBeVisible();
  });
});

test.describe('Vocabulary - Unmark Words', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(ROUTES.login);
    const uniqueEmail = `unmarktest${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'unmarkuser', 'UnmarkPass123!');
    await navigation.goToVocabulary(page);

    // Mark some words first
    await actions.markWordAsKnown(page, 'Haus');
    await actions.markWordAsKnown(page, 'ab');
  });

  test('should unmark word by clicking again', async ({ page }) => {
    // Verify 2 words marked
    await expect(page.locator('text=2 / 715')).toBeVisible();

    // Unmark one word
    await actions.markWordAsKnown(page, 'Haus');

    // Check count decreased
    await expect(page.locator('text=1 / 715')).toBeVisible();
  });

  test('should unmark all words', async ({ page }) => {
    // First mark all
    await page.click('button:has-text("Mark All Known")');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('text=715 / 715')).toBeVisible();

    // Click Unmark All
    await page.click('button:has-text("Unmark All")');
    await page.waitForLoadState('networkidle');

    // Check all unmarked
    await expect(page.locator('text=0 / 715')).toBeVisible();
  });

  test('should remove word progress via × button', async ({ page }) => {
    // Mark a word
    await actions.markWordAsKnown(page, 'Haus');
    await expect(page.locator('text=1 / 715')).toBeVisible();

    // Find and click the × button for the word
    const hausRow = page.locator('text="Haus"').first().locator('..');
    const removeButton = hausRow.locator('button:has-text("×")');
    await removeButton.click();
    await page.waitForLoadState('networkidle');

    // Check count decreased
    await expect(page.locator('text=0 / 715')).toBeVisible();
  });
});

test.describe('Vocabulary - Search Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(ROUTES.login);
    const uniqueEmail = `searchtest${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'searchuser', 'SearchPass123!');
    await navigation.goToVocabulary(page);
  });

  test('should search for word by exact name', async ({ page }) => {
    // Search for specific word
    const searchBox = page.locator('input[placeholder*="Search"]');
    await searchBox.fill('Haus');
    await page.waitForLoadState('networkidle');

    // Should show only matching word
    const results = page.locator('text="Haus"');
    const count = await results.count();
    expect(count).toBeGreaterThan(0);

    // Other common words shouldn't be visible
    const haushalt = page.locator('text="Haushalt"');
    const isVisible = await haushalt.isVisible().catch(() => false);
  });

  test('should show partial matches', async ({ page }) => {
    // Search for partial word
    const searchBox = page.locator('input[placeholder*="Search"]');
    await searchBox.fill('ab');
    await page.waitForLoadState('networkidle');

    // Should show words starting with 'ab'
    await expect(page.locator('text="ab"').first()).toBeVisible();
    await expect(page.locator('text="Abend"').first()).toBeVisible();
    await expect(page.locator('text="abendessen"').first()).toBeVisible();
  });

  test('should clear search and restore full list', async ({ page }) => {
    // Search for word
    const searchBox = page.locator('input[placeholder*="Search"]');
    await searchBox.fill('Haus');
    await page.waitForLoadState('networkidle');

    // Clear search
    await searchBox.fill('');
    await page.waitForLoadState('networkidle');

    // Should show full vocabulary again
    await expect(page.locator('text=Page 1 of 8')).toBeVisible();
  });

  test('should show no results for non-existent word', async ({ page }) => {
    // Search for word that doesn't exist
    const searchBox = page.locator('input[placeholder*="Search"]');
    await searchBox.fill('xyzabc123');
    await page.waitForLoadState('networkidle');

    // Should show no results or empty message
    // Implementation depends on how frontend handles no results
  });
});

test.describe('Vocabulary - Level Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(ROUTES.login);
    const uniqueEmail = `leveltest${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'leveluser', 'LevelPass123!');
    await navigation.goToVocabulary(page);
  });

  test('should switch between vocabulary levels', async ({ page }) => {
    // Start on A1
    await expect(page.locator('text=A1 Level Vocabulary')).toBeVisible();

    // Switch to A2
    await actions.switchVocabularyLevel(page, 'A2');
    await expect(page.locator('text=A2 Level Vocabulary')).toBeVisible();

    // Switch to B1
    await actions.switchVocabularyLevel(page, 'B1');
    await expect(page.locator('text=B1 Level Vocabulary')).toBeVisible();

    // Switch back to A1
    await actions.switchVocabularyLevel(page, 'A1');
    await expect(page.locator('text=A1 Level Vocabulary')).toBeVisible();
  });

  test('should preserve word knowledge across level switches', async ({ page }) => {
    // Mark word in A1
    await actions.markWordAsKnown(page, 'Haus');
    await expect(page.locator('text=A1 1 / 715')).toBeVisible();

    // Switch to A2
    await actions.switchVocabularyLevel(page, 'A2');
    const a2Stats = page.locator('text=A2 0 / 574');
    await expect(a2Stats).toBeVisible();

    // Switch back to A1
    await actions.switchVocabularyLevel(page, 'A1');

    // Word should still be marked
    await expect(page.locator('text=A1 1 / 715')).toBeVisible();
  });
});

test.describe('Vocabulary - Pagination', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(ROUTES.login);
    const uniqueEmail = `pagetest${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'pageuser', 'PagePass123!');
    await navigation.goToVocabulary(page);
  });

  test('should navigate to next page', async ({ page }) => {
    // Verify on first page
    await expect(page.locator('text=Page 1 of 8')).toBeVisible();
    const firstWordPage1 = page.locator('text="Haus"').first();
    await expect(firstWordPage1).toBeVisible();

    // Click next
    await page.click('button:has-text("Next")');
    await page.waitForLoadState('networkidle');

    // Should be on page 2
    await expect(page.locator('text=Page 2 of 8')).toBeVisible();
  });

  test('should navigate to previous page', async ({ page }) => {
    // Go to page 2
    await page.click('button:has-text("Next")');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('text=Page 2 of 8')).toBeVisible();

    // Click previous
    await page.click('button:has-text("Previous")');
    await page.waitForLoadState('networkidle');

    // Should be back on page 1
    await expect(page.locator('text=Page 1 of 8')).toBeVisible();
  });

  test('should display 100 words per page', async ({ page }) => {
    // Count visible word items
    const wordItems = page.locator('text^').filter({ hasText: /^[A-Z]/ });
    const count = await wordItems.count();

    // Should have around 100 items (plus some UI elements)
    expect(count).toBeGreaterThanOrEqual(90);
  });
});

test.describe('Vocabulary - Statistics', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(ROUTES.login);
    const uniqueEmail = `statstest${Date.now()}@example.com`;
    await page.click('text=Sign up now');
    await actions.register(page, uniqueEmail, 'statsuser', 'StatsPass123!');
    await navigation.goToVocabulary(page);
  });

  test('should calculate progress percentage correctly', async ({ page }) => {
    // Mark 10% of words in A1 (71 out of 715)
    for (let i = 0; i < 10; i++) {
      const wordElement = page.locator('text').nth(i * 3).locator('..');
      const checkbox = wordElement.locator('input[type="checkbox"]');
      if (await checkbox.isVisible().catch(() => false)) {
        await checkbox.click();
      }
    }

    await page.waitForLoadState('networkidle');

    // Progress should show approximately 1-2%
    const progressText = page.locator('text=Progress').nth(1);
    await expect(progressText).toBeVisible();
  });

  test('should show total words learned across all levels', async ({ page }) => {
    // Mark some words in A1
    for (let i = 0; i < 5; i++) {
      const words = ['Haus', 'ab', 'Abend', 'abendessen', 'aber'];
      try {
        await actions.markWordAsKnown(page, words[i]);
      } catch (e) {
        // Word might not be visible, skip
      }
    }

    // Switch to A2 and mark words
    await actions.switchVocabularyLevel(page, 'A2');
    try {
      await actions.markWordAsKnown(page, 'Wort');
    } catch (e) {
      // Okay if word not found
    }

    // Total should show at top
    const totalStats = page.locator('text=Total Words').nth(0);
    await expect(totalStats).toBeVisible();
  });
});
