# Claude Code for SWE Teams

Companion plugin for **Claude Code for SWE Teams** talk on Mar 24, 2026. A reference implementation showing how engineering teams can create shared skills and hooks as a Claude Code plugin.

Resources:
- [Event page](https://luma.com/1bkn2r3d)
- [Event recording]

## What's Inside

### Skills (shared domain knowledge)

| Skill | Purpose |
|-------|---------|
| **fasthtml** | FastHTML framework expertise — routing, HTMX, components, styling (Tailwind+DaisyUI). Includes 7 reference docs. |
| **frontend-design** | Production-grade UI design guidance — bold aesthetics, avoids generic AI look. |
| **mux** | Mux video integration — signed playback, JWT tokens, lesson frontmatter, `<mux-player>` pipeline. |
| **lesson-helper** | Course lesson toolkit — transcription (AssemblyAI), content generation, frontmatter management. |
| **playwright-mcp-guidance** | Enforces Playwright MCP usage rules — screenshot output directory, browser cleanup, session management. |

### Hooks (shared automation)

| Hook | Event | What it does |
|------|-------|-------------|
| Playwright dir setup | `PreToolUse` on `browser_navigate` | Creates `.playwright-mcp/` directory before navigation |
| Screenshot cleanup | `PostToolUse` on `browser_close` | Removes `.playwright-mcp/*.png` after browser session ends |

## Prerequisites

Install these plugins from the **official Anthropic marketplace**:

```
/plugin install playwright@claude-plugins-official
/plugin install Notion@claude-plugins-official
/plugin install pyright-lsp@claude-plugins-official
```

## Installation

Add the marketplace and install:

```
/plugin marketplace add ShawhinT/claude-for-swe-teams
/plugin install claude-for-swe-teams@claude-for-swe-teams
```

## Why MCP Servers Aren't Bundled

Plugins that define an MCP server register tools under a namespace like `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`. If this plugin bundled its own Playwright server *and* you already had the marketplace Playwright plugin installed, you'd end up with two sets of identical tools under different prefixes, confusing for both you and Claude.

Instead, this plugin depends on the canonical marketplace plugins for MCP servers and layers **skills** (domain knowledge) and **hooks** (automation) on top. This avoids duplicate tool registrations and keeps a single source of truth for each MCP server.

## Team vs. Individual Primitives

Not everything belongs in a shared plugin. Here's a way to think about it:

#### **Share at the team level** when the primitive provides:
- Instructions or context for working with **shared tools** (e.g., "how our Jira setup works")
- **Shared coding standards** the agent should follow (e.g. PR guidelines)
- **Domain-specific business context** that's consistent across developers (e.g., "how our video pipeline works")

#### **Keep at the individual level** when the primitive reflects:
- **Workflow preferences** and ergonomic choices
- **Personal tool configurations**
- Developer-specific shortcuts or habits

This is similar to how developers on the same team share a CI pipeline and linting config, but pick their own IDE, shell, and keybindings. The same logic applies to skills, hooks, and MCP servers.

## Creating Your Own Team Plugin

The **exact contents of this repo will likely not be helpful** to you or your team. Instead, it is meant to serve as an example to help you imagine what this might look like for your work.

To create your own, you can give the link to Claude as a reference and have it adapt it to your toolkit. An example prompt is shown below. Claude will scaffold the plugin, write the skills, and set up the marketplace config. You fill in the domain knowledge.


```
Create a Claude Code plugin for our team. Use https://github.com/ShawhinT/claude-for-swe-teams
as a reference for the structure. Include skills for [your framework], hooks for [your automation],
and list [your MCP servers] as marketplace prerequisites.
```

---

## Skill-specific Configuration

**Lesson helper** (for video transcription):

```bash
cd skills/lesson-helper
cp .env.example .env    # add your AssemblyAI API key
uv sync                 # install Python dependencies
```

**Mux video** (for signed playback):

Set these environment variables in your project's `.env`:

```
MUX_TOKEN_ID=...
MUX_TOKEN_SECRET=...
MUX_SIGNING_KEY_ID=...
MUX_SIGNING_SECRET_KEY=...
```
