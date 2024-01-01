const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

const url = process.argv[2];
const idx = process.argv[3];
const action = process.argv[4];

(async () => {
    const browser = await puppeteer.launch({ headless: false, });
    const page = await browser.newPage();

    await page.setViewport({
        width: 1120,
        height: 1120,
        deviceScaleFactor: 1,
    });

    await page.goto(url, { waitUntil: 'domcontentloaded' });
    await new Promise(resolve => setTimeout(resolve, 5000));

    if (action != undefined) {
        const parsed_action = JSON.parse(action);
        
        if (parsed_action.action == 'CLICK') {
            const buttonX = parseFloat(parsed_action.position[0]) * 1120;
            const buttonY = parseFloat(parsed_action.position[1]) * 1120;
            await page.mouse.click(Math.round(buttonX), Math.round(buttonY));
            await new Promise(resolve => setTimeout(resolve, 5000));
        } else if (parsed_action.action == 'TYPE') {
            const buttonX = parseFloat(parsed_action.position[0]) * 1120;
            const buttonY = parseFloat(parsed_action.position[1]) * 1120;
            await page.mouse.click(Math.round(buttonX), Math.round(buttonY));
            await new Promise(resolve => setTimeout(resolve, 200));
            // Clear the old input
            async function pressBackspace() {
                await page.keyboard.press('Backspace');
            }
            async function executeBackspace() {
                const numberOfPresses = 2000;
                const promises = [];
            
                for (let i = 0; i < numberOfPresses; i++) {
                promises.push(pressBackspace());
                }
            
                await Promise.all(promises);
            }
            executeBackspace();
            await new Promise(resolve => setTimeout(resolve, 200));
            // Type the input
            await page.keyboard.type(parsed_action.content);
            await new Promise(resolve => setTimeout(resolve, 200));
            await page.keyboard.press('Enter');
            await new Promise(resolve => setTimeout(resolve, 5000));
        }
    }

    const currentURL = await page.url();
    console.log(currentURL);

    await page.screenshot({
        path: `screenshot/screenshot_${idx}.jpg`,
        fullPage: false,
    });

    await browser.close();
})();