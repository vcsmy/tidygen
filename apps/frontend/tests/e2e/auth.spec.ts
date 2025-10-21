import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should login successfully', async ({ page }) => {
    // Check if login form is present
    await expect(page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]')).toBeVisible();
    await expect(page.locator('input[type="password"], input[name="password"]')).toBeVisible();
    
    // Fill in login credentials (adjust selectors based on your actual form)
    const emailInput = page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]').first();
    const passwordInput = page.locator('input[type="password"], input[name="password"]').first();
    
    await emailInput.fill('test@example.com');
    await passwordInput.fill('testpassword123');
    
    // Click login button
    const loginButton = page.getByRole('button', { name: /login|sign in/i });
    await loginButton.click();
    
    // Verify redirect to dashboard or success message
    await expect(page).toHaveURL(/dashboard|freelancer-management/);
  });

  test('should handle login errors', async ({ page }) => {
    // Fill in invalid credentials
    const emailInput = page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]').first();
    const passwordInput = page.locator('input[type="password"], input[name="password"]').first();
    
    await emailInput.fill('invalid@example.com');
    await passwordInput.fill('wrongpassword');
    
    // Click login button
    const loginButton = page.getByRole('button', { name: /login|sign in/i });
    await loginButton.click();
    
    // Verify error message is displayed
    await expect(page.getByText(/invalid|error|incorrect/i)).toBeVisible();
  });

  test('should handle Web3 wallet login', async ({ page }) => {
    // Look for Web3 login option
    const web3LoginButton = page.getByRole('button', { name: /connect wallet|web3|wallet/i });
    if (await web3LoginButton.isVisible()) {
      await web3LoginButton.click();
      
      // Verify wallet connection modal appears
      await expect(page.getByText(/connect|wallet/i)).toBeVisible();
    }
  });

  test('should logout successfully', async ({ page }) => {
    // First login (you might want to mock this or use a test account)
    const emailInput = page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]').first();
    const passwordInput = page.locator('input[type="password"], input[name="password"]').first();
    
    await emailInput.fill('test@example.com');
    await passwordInput.fill('testpassword123');
    
    const loginButton = page.getByRole('button', { name: /login|sign in/i });
    await loginButton.click();
    
    // Wait for login to complete
    await expect(page).toHaveURL(/dashboard|freelancer-management/);
    
    // Find and click logout button
    const logoutButton = page.getByRole('button', { name: /logout|sign out|exit/i });
    if (await logoutButton.isVisible()) {
      await logoutButton.click();
      
      // Verify redirect to login page
      await expect(page).toHaveURL(/login/);
    }
  });
});

test.describe('Protected Routes', () => {
  test('should redirect to login when accessing protected route without auth', async ({ page }) => {
    // Try to access freelancer management without login
    await page.goto('/freelancer-management');
    
    // Should redirect to login page
    await expect(page).toHaveURL(/login/);
  });

  test('should allow access to protected route when authenticated', async ({ page }) => {
    // Login first
    await page.goto('/login');
    
    const emailInput = page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]').first();
    const passwordInput = page.locator('input[type="password"], input[name="password"]').first();
    
    await emailInput.fill('test@example.com');
    await passwordInput.fill('testpassword123');
    
    const loginButton = page.getByRole('button', { name: /login|sign in/i });
    await loginButton.click();
    
    // Wait for login to complete
    await expect(page).toHaveURL(/dashboard|freelancer-management/);
    
    // Now try to access freelancer management
    await page.goto('/freelancer-management');
    
    // Should be able to access the page
    await expect(page.getByRole('heading', { name: 'Freelancer & Gig Management' })).toBeVisible();
  });
});
