```json
{
  "owner": "humanlayer",
  "name": "skills",
  "full_name": "humanlayer/skills",
  "url": "https://github.com/humanlayer/skills",
  "description": "",
  "readme_sha256": "8123e666e2c8a5cb27f7211557f65544383178c7d1ad816b350d08bede2e323e"
}
```

# humanlayer/skills

- URL: https://github.com/humanlayer/skills
- Description: No description
- README SHA256: `8123e666e2c8a5cb27f7211557f65544383178c7d1ad816b350d08bede2e323e`

## README

# skills

Claude Code skills from [HumanLayer](https://humanlayer.dev).

## Installation

```bash
npx skills add humanlayer/skills --skill SKILLNAME
```

## Available Skills

### improve-claude-md

Rewrites your CLAUDE.md using `<important if>` blocks to improve instruction adherence.

```bash
npx skills add humanlayer/skills --skill improve-claude-md
```

Then in your project:

```
/improve-claude-md
```

### narrow-react-prop-types

Narrows React component prop types to match live code paths instead of Storybook, test, or mock-only states.

```bash
npx skills add humanlayer/skills --skill narrow-react-prop-types
```

Then in your project:

```
/narrow-react-prop-types
```

### build-iterated-agentic-loop

Builds a repo-local skill plus an iterated coding-agent GitHub Actions workflow, prompt, memory file, and reference templates.

```bash
npx skills add humanlayer/skills --skill build-iterated-agentic-loop
```

Then in your project:

```
/build-iterated-agentic-loop
```

### design-control-loop

Interviews you to design an agentic control loop — sensor, controller, actuator, and disturbances — tailored to your codebase, then builds it as locally-runnable components plus a scheduled coding-agent workflow.

```bash
npx skills add humanlayer/skills --skill design-control-loop
```

Then in your project:

```
/design-control-loop
```

### show-me

Explains the current topic with concise diagrams, code-shape sketches, and focused HTML artifacts.

```bash
npx skills add humanlayer/skills --skill show-me
```

Then invoke:

```
/show-me
```
