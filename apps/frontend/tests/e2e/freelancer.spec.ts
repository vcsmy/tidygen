import { test, expect, Page } from '@playwright/test';

test.describe('Freelancer Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to freelancer management page
    await page.goto('/freelancer-management');
  });

  test('should display freelancer list', async ({ page }) => {
    // Check if the page loads correctly
    await expect(page.getByRole('heading', { name: 'Freelancer & Gig Management' })).toBeVisible();
    
    // Check if the tabs are present
    await expect(page.getByRole('tab', { name: 'Find Freelancers' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Job Board' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'My Profile' })).toBeVisible();
  });

  test('should filter freelancers by search', async ({ page }) => {
    // Click on freelancers tab if not already active
    await page.getByRole('tab', { name: 'Find Freelancers' }).click();

    // Check if search input is present
    const searchInput = page.locator('input[placeholder*="Search by name, skills"]');
    await expect(searchInput).toBeVisible();

    // Test search functionality
    await searchInput.fill('John');
    await page.getByRole('button', { name: 'Search' }).click();

    // Verify search results (this would depend on your actual API responses)
    await expect(page.locator('[data-testid="freelancer-card"]')).toBeVisible();
  });

  test('should filter freelancers by city', async ({ page }) => {
    await page.getByRole('tab', { name: 'Find Freelancers' }).click();

    // Test city filter
    const cityInput = page.locator('input[placeholder="Enter city"]');
    await expect(cityInput).toBeVisible();

    await cityInput.fill('New York');
    await page.getByRole('button', { name: 'Search' }).click();

    // Verify filtered results
    await expect(page.locator('[data-testid="freelancer-card"]')).toBeVisible();
  });

  test('should filter freelancers by rating', async ({ page }) => {
    await page.getByRole('tab', { name: 'Find Freelancers' }).click();

    // Test rating filter
    const ratingSelect = page.locator('select[data-testid="rating-filter"]');
    await expect(ratingSelect).toBeVisible();

    await ratingSelect.selectOption({ label: '3+ Stars' });
    await page.getByRole('button', { name: 'Search' }).click();

    // Verify filtered results
    await expect(page.locator('[data-testid="freelancer-card"]')).toBeVisible();
  });

  test('should view freelancer profile details', async ({ page }) => {
    await page.getByRole('tab', { name: 'Find Freelancers' }).click();

    // Wait for freelancer cards to load
    await expect(page.locator('[data-testid="freelancer-card"]').first()).toBeVisible();

    // Click on first freelancer's "View Profile" button
    await page.getByRole('button', { name: 'View Profile' }).first().click();

    // Verify profile details are shown (this would depend on your modal/page navigation)
    await expect(page.getByText('About')).toBeVisible();
  });

  test('should contact freelancer', async ({ page }) => {
    await page.getByRole('tab', { name: 'Find Freelancers' }).click();

    // Wait for freelancer cards to load
    await expect(page.locator('[data-testid="freelancer-card"]').first()).toBeVisible();

    // Click on Contact button
    await page.getByRole('button', { name: 'Contact' }).first().click();

    // Verify contact form/modal opens
    await expect(page.getByText('Send Message')).toBeVisible();
  });
});

test.describe('Job Board', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/freelancer-management');
    await page.getByRole('tab', { name: 'Job Board' }).click();
  });

  test('should display job board', async ({ page }) => {
    // Check if job board loads
    await expect(page.getByRole('heading', { name: 'Job Board' })).toBeVisible();
    
    // Check if "Post Job" button is present
    await expect(page.getByRole('button', { name: 'Post Job' })).toBeVisible();
  });

  test('should search jobs', async ({ page }) => {
    // Test job search
    const searchInput = page.locator('input[placeholder*="Search jobs by title"]');
    await expect(searchInput).toBeVisible();

    await searchInput.fill('cleaning');
    await page.getByRole('button', { name: 'Search' }).click();

    // Verify search results
    await expect(page.locator('[data-testid="job-card"]')).toBeVisible();
  });

  test('should filter jobs by category', async ({ page }) => {
    // Test category filter
    const categorySelect = page.locator('select[data-testid="category-filter"]');
    await expect(categorySelect).toBeVisible();

    await categorySelect.selectOption({ label: 'Residential Cleaning' });
    await page.getByRole('button', { name: 'Search' }).click();

    // Verify filtered results
    await expect(page.locator('[data-testid="job-card"]')).toBeVisible();
  });

  test('should filter jobs by payment method', async ({ page }) => {
    // Test payment method filter
    const paymentSelect = page.locator('select[data-testid="payment-method-filter"]');
    await expect(paymentSelect).toBeVisible();

    await paymentSelect.selectOption({ label: 'Hourly' });
    await page.getByRole('button', { name: 'Search' }).click();

    // Verify filtered results
    await expect(page.locator('[data-testid="job-card"]')).toBeVisible();
  });

  test('should view job details', async ({ page }) => {
    // Wait for job cards to load
    await expect(page.locator('[data-testid="job-card"]').first()).toBeVisible();

    // Click on "View Details" button
    await page.getByRole('button', { name: 'View Details' }).first().click();

    // Verify job details are shown
    await expect(page.getByText('Job Details')).toBeVisible();
  });

  test('should apply to job', async ({ page }) => {
    // Wait for job cards to load
    await expect(page.locator('[data-testid="job-card"]').first()).toBeVisible();

    // Click on "Apply Now" button
    await page.getByRole('button', { name: 'Apply Now' }).first().click();

    // Verify application form opens
    await expect(page.getByText('Job Application')).toBeVisible();
  });
});

test.describe('Freelancer Profile', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/freelancer-management');
    await page.getByRole('tab', { name: 'My Profile' }).click();
  });

  test('should display profile information', async ({ page }) => {
    // Check if profile loads
    await expect(page.locator('[data-testid="freelancer-profile"]')).toBeVisible();
  });

  test('should navigate between profile tabs', async ({ page }) => {
    // Test Overview tab
    await page.getByRole('tab', { name: 'Overview' }).click();
    await expect(page.getByText('About')).toBeVisible();

    // Test Skills tab
    await page.getByRole('tab', { name: 'Skills' }).click();
    await expect(page.getByText('Skills & Certifications')).toBeVisible();

    // Test Availability tab
    await page.getByRole('tab', { name: 'Availability' }).click();
    await expect(page.getByText('Availability Schedule')).toBeVisible();

    // Test Reviews tab
    await page.getByRole('tab', { name: 'Reviews' }).click();
    await expect(page.getByText('Client Reviews')).toBeVisible();

    // Test Web3 tab
    await page.getByRole('tab', { name: 'Web3' }).click();
    await expect(page.getByText('Web3 Integration')).toBeVisible();
  });

  test('should update profile information', async ({ page }) => {
    // Click on edit button if available
    const editButton = page.getByRole('button', { name: /edit|update/i });
    if (await editButton.isVisible()) {
      await editButton.click();
      
      // Test updating bio
      const bioInput = page.locator('textarea[data-testid="bio-input"]');
      if (await bioInput.isVisible()) {
        await bioInput.fill('Updated bio information');
        await page.getByRole('button', { name: 'Save' }).click();
        
        // Verify update
        await expect(page.getByText('Updated bio information')).toBeVisible();
      }
    }
  });

  test('should connect Web3 wallet', async ({ page }) => {
    // Navigate to Web3 tab
    await page.getByRole('tab', { name: 'Web3' }).click();

    // Look for wallet connection button
    const connectWalletButton = page.getByRole('button', { name: /connect wallet/i });
    if (await connectWalletButton.isVisible()) {
      await connectWalletButton.click();
      
      // Verify wallet connection modal/form
      await expect(page.getByText(/wallet address/i)).toBeVisible();
    }
  });
});

test.describe('Responsive Design', () => {
  test('should work on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/freelancer-management');
    
    // Check if mobile navigation works
    await expect(page.getByRole('heading', { name: 'Freelancer & Gig Management' })).toBeVisible();
    
    // Test tab switching on mobile
    await page.getByRole('tab', { name: 'Find Freelancers' }).click();
    await expect(page.locator('[data-testid="freelancer-card"]')).toBeVisible();
  });

  test('should work on tablet devices', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    
    await page.goto('/freelancer-management');
    
    // Check if tablet layout works
    await expect(page.getByRole('heading', { name: 'Freelancer & Gig Management' })).toBeVisible();
    
    // Test tab switching
    await page.getByRole('tab', { name: 'Job Board' }).click();
    await expect(page.locator('[data-testid="job-card"]')).toBeVisible();
  });
});

test.describe('Error Handling', () => {
  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API failure
    await page.route('**/api/v1/freelancers/**', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      });
    });

    await page.goto('/freelancer-management');
    
    // Check if error message is displayed
    await expect(page.getByText(/error loading freelancers/i)).toBeVisible();
  });

  test('should handle empty search results', async ({ page }) => {
    await page.goto('/freelancer-management');
    await page.getByRole('tab', { name: 'Find Freelancers' }).click();

    // Search for non-existent freelancer
    const searchInput = page.locator('input[placeholder*="Search by name, skills"]');
    await searchInput.fill('NonExistentFreelancer12345');
    await page.getByRole('button', { name: 'Search' }).click();

    // Check if "no results" message is displayed
    await expect(page.getByText(/no freelancers found/i)).toBeVisible();
  });
});

test.describe('Accessibility', () => {
  test('should have proper ARIA labels and roles', async ({ page }) => {
    await page.goto('/freelancer-management');
    
    // Check tab navigation
    await expect(page.getByRole('tablist')).toBeVisible();
    await expect(page.getByRole('tab', { name: 'Find Freelancers' })).toBeVisible();
    
    // Check form elements have proper labels
    const searchInput = page.locator('input[placeholder*="Search by name, skills"]');
    await expect(searchInput).toBeVisible();
  });

  test('should support keyboard navigation', async ({ page }) => {
    await page.goto('/freelancer-management');
    
    // Test tab navigation with keyboard
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Test that focus is visible and functional
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });
});
