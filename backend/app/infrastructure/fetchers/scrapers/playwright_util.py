from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from playwright.async_api import Browser, Page, async_playwright

BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

_browser_lock = asyncio.Lock()
_playwright = None
_browser: Browser | None = None


async def get_browser() -> Browser:
    global _browser, _playwright
    async with _browser_lock:
        if _browser is None or not _browser.is_connected():
            _playwright = await async_playwright().start()
            _browser = await _playwright.chromium.launch(headless=True)
        return _browser


async def close_browser() -> None:
    global _browser, _playwright
    async with _browser_lock:
        if _browser is not None:
            await _browser.close()
            _browser = None
        if _playwright is not None:
            await _playwright.stop()
            _playwright = None


async def with_page(
    handler: Callable[[Page], Awaitable[Any]],
    *,
    cookies: list[dict] | None = None,
) -> Any:
    browser = await get_browser()
    context = await browser.new_context(user_agent=BROWSER_USER_AGENT)
    if cookies:
        await context.add_cookies(cookies)
    page = await context.new_page()
    try:
        return await handler(page)
    finally:
        await context.close()
