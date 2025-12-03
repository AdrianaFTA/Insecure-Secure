import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:5000';

test.describe('Secure Notes App', () => {
    test('User can register', async({page}) =>{
        await page.goto(`${BASE_URL}/register`);

        await page.fill('input[name="username"]', 'secureUser');
        await page.fill('input[name="password"]', 'TestPass123');
        await page.click('button[type="submit"]');

        await expect(page).toHaveURL(/.*login/);
    });

    test('User can log in', async({page}) => {
        await page.goto(`${BASE_URL}/login`);

        await page.fill('input[name="username"]', 'secureUser');
        await page.fill('input[name="password"]', 'TestPass123');
        await page.click('button[type="submit"]');

        await expect(page).toHaveURL(/.*notes/);


    });

    test('User can add a note', async({page}) =>{
        await page.goto(`${BASE_URL}/login`);

        await page.fill('input[name="username"]', 'secureUser');
        await page.fill('input[name="password"]', 'TestPass123');
        await page.click('button[type="submit"]');

        // add note
        await page.fill('textarea[name="note"]', 'this is a secure test note');
        await page.click('button[type="submit"]');

        await expect(page.locator('li')).toContainText('this is a secure test note');

    });

    test('User can edit a note', async ({page}) =>{
        await page.goto(`${BASE_URL}/login`);

        await page.fill('input[name="username"]', 'secureUser');
        await page.fill('input[name="password"]', 'TestPass123');
        await page.click('button[type="submit"]');

        //click the first edit link
        await page.click('text=Edit');

        await expect(page).toHaveURL(/.*edit/);

        await page.fill('textarea[name="note"]', 'updated secure note text');
        await page.click('button:has-text("Save")');

        await expect(page.locator('li')).toContainText('updated secure note text');


    });

    test('User can delete note', async ({page}) =>{
        await page.goto(`${BASE_URL}/login`);

        await page.fill('input[name="username"]', 'secureUser');
        await page.fill('input[name="password"]', 'TestPass123');
        await page.click('button[type="submit"]');

        //delete first note
        await page.click('text=Delete');

        //check undo message
        await expect(page).toHaveURL(/undo_available/);
    });

    test('User can undo a delete',async ({page}) =>{
        await page.goto(`${BASE_URL}/login`);

        await page.fill('input[name="username"]', 'secureUser');
        await page.fill('input[name="password"]', 'TestPass123');
        await page.click('button[type="submit"]');

        //undo delete if available
        if (await page.locator('text=Undo').isVisable()) {
            await page.click('text=Undo');


        }
        await expect(page.locator('li')).toContainText(/secure/i);
    });

    test('User can search for notes', async({page}) =>{
        await page.goto(`${BASE_URL}/login`);

        await page.fill('input[name="username"]', 'secureUser');
        await page.fill('input[name="password"]', 'TestPass123');
        await page.click('button[type="submit"]');

        await page.goto(`${BASE_URL}/search?q=secure`);

        await expect(page.locator('li')).toContainText(/secure/i);
    });

    test('User can logout', async ({page}) =>{
        await page.goto(`${BASE_URL}/login`);

        await page.fill('input[name="username"]', 'secureUser');
        await page.fill('input[name="password"]', 'TestPass123');
        await page.click('button[type="submit"]');

        await page.click('text=Logout');

        await expect(page).toHaveURL(`${BASE_URL}/?logout=1`);
    });

});