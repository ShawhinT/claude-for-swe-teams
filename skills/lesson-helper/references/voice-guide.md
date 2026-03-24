# Voice & Style Guide — Lesson Copy

When generating or editing lesson `.md` body content, follow these rules. Derived from Shaw's teaching voice across course transcripts and written lesson notes.

## Core Principles

Every rule in this guide traces back to one of three principles:

1. **Reduce reader friction.** The reader should never have to work to parse a sentence. Use the lightest punctuation that preserves clarity. Keep heading hierarchy flat. Make openings scannable by bolding both the concept name and its definition.

2. **Stay concrete.** Never describe something abstractly when a concrete example exists. Analogies should reference experiences the reader already has ("a folder you share with a teammate"), not abstract labels ("a knowledge pack"). When explaining how something works, explain the actual mechanism ("only loaded if Claude thinks it's relevant"), not a vague label ("loaded on demand").

3. **End when the content ends.** If the lesson body proved the point, stop. Don't restate, don't summarize, don't sell after the sale. Close with a single punchy element or nothing at all.

---

## Structure

- One `#` heading for the lesson title, never more than one `#` per file
- Default to `###` for all sub-headings under the `#` lesson title
- Only use `##` in two cases: (1) when the `#` heading is a broad category and each sub-section is an independent topic (e.g. "The Basics" → `## Installing`, `## The Terminal`), or (2) for cross-cutting sections that compare concepts across multiple lessons (e.g. `## Skills vs. MCP`). Both are rare.
- Keep sections short, typically 1–3 paragraphs
- No blank lines between list items (keep them tight)
- Merge closely related sentences into one paragraph when they share a single idea, but never exceed 2–3 sentences per paragraph
- Progressive disclosure: introduce concepts simply first, layer on complexity later. Use forward references: "which we'll cover later"

## Formatting Patterns

- **Bold-label lists**: Use `**Label:** description` for list items that name a concept and explain it:
  ```
  - **Building full web apps:** products with databases, auth, and real users
  - **Context management:** how to keep Claude focused as conversations grow
  ```
- **Code blocks**: Always fenced with a language tag (e.g. `bash`). Introduce with a sentence fragment + colon: "Just run:"
- **Inline links**: Use descriptive link text, never bare URLs
- **External links for exhaustive lists**: When a concept has many options (triggers, servers, etc.), mention the 2-3 most common, then link to the canonical source rather than listing everything inline.

## Emphasis & Definitions

- **Bold key claims and definitions** inline within paragraphs
- **Bold the concept name in opening definitions.** When a lesson introduces its core concept, bold both the concept name and its definition in the first sentence:
  ```
  **Hooks** let you **automate actions before and after Claude's tool calls**.
  **MCP** (Model Context Protocol) is **a universal way to connect Claude to external tools and data sources**.
  ```
- Name important concepts and immediately define them in plain language:
  `"Context Rot" i.e. when your conversation grows so long that Claude starts losing track`
- Use `(i.e. ...)` parentheticals for inline clarification

## Tone & Voice

- Conversational, second person ("you" / "we"), contractions ("it's", "you'll", "don't")
- Direct and builder-first: lead with what something IS, not background context
- Grounded in real examples, not hypotheticals: use concrete scenarios from actual projects
- Reassuring: remind readers they don't need to know everything upfront
- Anti-jargon: when a technical term comes up, explain it immediately in plain language

## Conciseness

- Ultra-concise: 1–2 sentence paragraphs, sentence fragments OK ("Just run:")
- Prefer clarity over compression: two short sentences are better than one dense compound sentence
- Colons to introduce lists, examples, and code blocks, not full sentences
- Avoid em dashes (`—`). Use commas, parentheticals, or `i.e` for mid-sentence asides and clarifications.
- No filler transitions, no padding, no passive voice

## Closings

- Don't restate what the lesson body already established. If the content proved the point, a summary sentence is redundant.
- End with a single punchy element: a **Pro tip**, a bold call to action, or a short forward-looking sentence. Never a restating paragraph.
- Bold the action phrase in closing CTAs: `The best way to internalize all of this is to **start using it**.`
- Exclamation marks are OK for high-energy closing calls to action (`just ask Claude!`) but only at the very end, and sparingly.

## What to Avoid

- Generic AI prose (stiff, formal, hedging)
- Filler transitions ("So,", "Basically,", "Just to..."): verbal tics from spoken transcripts, not written style
- Over-explaining or padding sentences for length

## Before / After Examples

**Too dense:**
> Claude Code ships with built-in slash commands, including /init which bootstraps a CLAUDE.md, that let you trigger common workflows without typing full prompts.

**Better (reduce friction):**
> Claude Code ships with built-in slash commands. These let you trigger common workflows without typing full prompts. `/init` bootstraps a CLAUDE.md for your project.

**Abstract analogy:**
> Think of it as a specialized knowledge pack that Claude can load when needed.

**Better (stay concrete):**
> Think of it as a folder you share with a fellow team member that tells them exactly how you get things done.

**Vague mechanism:**
> Skill descriptions are loaded by default, the full body is read on demand.

**Better (stay concrete):**
> Skill descriptions are loaded by default, the full body is read only if Claude thinks it's relevant.

**Redundant closing:**
> With hundreds of MCP servers available, there's really no limit to what you can connect Claude to. **Claude Code isn't just a coding agent, it's a general-purpose agent that happens to be great at coding.**

**Better (end when the content ends):**
> With hundreds of MCP servers available, there's really no limit to what you can connect Claude to.
