---
name: playwright-mcp-guidance
description: "MANDATORY: Invoke this skill BEFORE calling ANY Playwright MCP tool (browser_navigate, browser_take_screenshot, browser_snapshot, browser_click, browser_fill_form, etc.). This skill MUST be triggered first whenever the user asks to take a screenshot, browse a website, automate a browser, interact with a web page, or use any tool starting with 'mcp__plugin_playwright_playwright__'. Do NOT call Playwright tools without loading this skill first."
user-invocable: false
---

# Playwright MCP Output Rules

When using any Playwright MCP tools (`browser_take_screenshot`, `browser_navigate`, `browser_snapshot`, etc.), follow these rules:

## Screenshots

- **Always** save screenshots into the `.playwright-mcp/` directory in the current project root.
- Set the `filename` parameter to `.playwright-mcp/<descriptive-name>.png` (e.g., `.playwright-mcp/homepage.png`, `.playwright-mcp/login-form.png`).
- Create the `.playwright-mcp/` directory first if it does not exist: `mkdir -p .playwright-mcp`

## Browser Session

- **Always** close the browser when you are done with a Playwright workflow by calling `browser_close`.
- Do this at the end of every workflow — after taking screenshots, scraping, testing, or any other browser interaction.
- If multiple pages/tabs were opened, a single `browser_close` call is sufficient to end the session.

## Cleanup

- After you have finished analyzing or using screenshots and they are no longer needed in the conversation, delete them from `.playwright-mcp/`.
- At the end of a Playwright workflow (e.g., after visual comparison, debugging, or testing is complete), remove any screenshot files you created.
- Do **not** delete console logs or other non-screenshot files in `.playwright-mcp/`.
