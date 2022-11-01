from playwright.async_api import async_playwright


class QuillBot:
    def __init__(self, page) -> None:
        self.page = page

    async def type_text(self, text: str) -> None:
        await self.page.click("div[data-gramm_editor='false']")
        await self.page.keyboard.type(text)

    async def fix_all_errors(self) -> None:
        try:
            await self.page.click("text=Fix All Errors", timeout=3000)
            await self.page.wait_for_selector("text=Fixed all grammar errors.")
        except Exception:
            return None

    async def get_text(self) -> str:
        return await self.page.inner_text("div[data-gramm_editor='false']")

    async def cut_paste(self) -> None:
        await self.page.keyboard.press("Control+A")
        await self.page.keyboard.press("Control+X")
        await self.page.keyboard.press("Control+V")


async def recursive_correcting(
    initial_text: str, quillbot: QuillBot, iteration_count: int = 0
) -> str:
    await quillbot.fix_all_errors()
    text = await quillbot.get_text()
    if text == initial_text:
        return text
    await quillbot.page.wait_for_timeout(50)
    await quillbot.cut_paste()
    return await recursive_correcting(text, quillbot, iteration_count)


async def correcting(text: str) -> str:
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True, timeout=0)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await page.goto("https://quillbot.com/grammar-check", timeout=5000)
        except Exception:
            await page.reload()

        quillbot = QuillBot(page)

        # await quillbot.close_signin()
        await quillbot.type_text(text)
        return await recursive_correcting(text, quillbot)