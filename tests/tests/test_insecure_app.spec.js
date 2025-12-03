import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:5000';

test.describe('Insecure Notes App', () =>{

    test('User can register with plaintext', async({page}) =>{
        await page.goto(`${BASE_URL}/register`);

        await page.fill('input[name="username"]', 'insecureUser');
        await page.fill('input[name="password"]', 'badpassword');
        await page.click('button[type="submit"]');

        await expect(page).toHaveURL(/.*login/);
    });

    test('User can log in with paintext password', async ({page}) =>{
        await page.goto(`${BASE_URL}/login`);

        await page.fill('input[name="username"]', 'insecureUser');
        await page.fill('input[name="password"]', 'badpassword');
        await page.click('button[type="submit"]');

        await expect(page).toHaveURL(/.*notes/);
    });

    test('User can add note(vulnerable XSS', async ({page}) =>{
        await page.goto(`${BASE_URL}/login`);

        await page.fill('input[name="username"]', 'insecureUser');
        await page.fill('input[name="password"]', 'badpassword');
        await page.click('button[type="submit"]');

        await page.fill('textarea[name="note"]', '<script>alert("XSS")</script>');
        await page.click('button[type="submit"]');

        //raw script is visible because no sanitisation exits
        await expect(page.locator('li')).toContainText('<script>');

    });

    test('SQL injection works(demonstrating vulnerability', async ({page}) =>{
        await page.goto(`${BASE_URL}/login`);

        //SQLite playload that logs in bypassing password
        await page.fill('input[name="username"]', "insecureUser' OR '1'='1");
        await page.fill('input[name="password"]', "anything");
        await page.click('button[type="submit"]');

        // should succeed even with wrong password
        await expect(page).toHaveURL(/.*notes/);

    });

    test('Reflected XSS works on/search', async ({page}) =>{
        const payload = `<img src=x onerror="alert('Reflected XSS')">`;

        await page.goto(`${BASE_URL}/search?q=${payload}`);

        //the payload should be reflected unsanitised
        await expect(page.locator('h1')).toContainText(payload);

        
    });

    test('DOM XSS script executes on homepage', async ({page}) =>{
        const payload =`<img src=x onerror="alert('DOMXSS')">`;

        await page.goto(`${BASE_URL}/?q=${payload}`);

        //DOM XSS puts user input directly into innner html
        await expect(page.locator('#output')).toContainText(payload);

    });

    test('User can see notes (no id returned)', async({page}) =>{
        await page.goto(`${BASE_URL}/login`);

        await page.fill('input[name="username"]', 'insecureUser');
        await page.fill('input[name="password"]', 'badpassword');
        await page.click('button[type="submit"]');

        //notes should apper as simple text
        const notes = page.locator('li');
        await expect(notes.first()).toBeVisible();
    });

});
