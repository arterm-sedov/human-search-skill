# Automated Skill Pack Installer Prompt

You are installing a reusable AI-agent skill pack for web research and browser automation.

Goal:
Install the skill directories and required command-line dependencies into either:
- local project `.agents/skills`
- global `~/.agents/skills`

Use these repositories only as sources. Do not install or copy whole repositories into the agent skills directory unless a repository has no separate skill folder and its documentation explicitly requires a whole-repo install.

Source repositories and install targets:
```text
Source repository                                      Copy from repo         Install to selected root
https://github.com/arterm-sedov/web-search-skill      skills/web-search      <install-root>/web-search
https://github.com/arterm-sedov/human-search-skill    skills/human-search    <install-root>/human-search
https://github.com/arterm-sedov/deep-research         skills/deep-research   <install-root>/deep-research
https://github.com/arterm-sedov/browser-switch-skill  skills/browser-switch  <install-root>/browser-switch
```

Install these browser automation tools as command-line dependencies, then install or copy their packaged skills only if they provide a `skills/<name>` directory or an official skill installer:
```text
https://github.com/vercel-labs/agent-browser          npm package / CLI      agent-browser command, optional skill files
https://github.com/microsoft/playwright-cli           npm package / CLI      playwright-cli command, optional skill files
```

Work in semi-interactive mode:
- First ask whether to install locally or globally.
- If local, use the current repository or workspace root and create `.agents/skills`.
- If global, use `~/.agents/skills`.
- Before overwriting an existing skill directory, ask whether to replace, skip, or back it up.
- Automatically install normal user-space dependencies.
- Ask before running privileged commands such as `sudo`, `apt`, `brew`, system package managers, or Docker daemon repair.
- Prefer official install commands when available.
- Fall back to manual clone-and-copy when an installer command fails.
- Support macOS, Linux, and Windows PowerShell where possible.

Environment checks:
1. Detect OS, shell, CPU architecture, and home directory.
2. Check whether these commands are available:
   - `git`
   - `node`
   - `npm`
   - `npx`
   - `python` or `python3`
3. Confirm Node.js is version 18 or newer. If Node.js is missing or too old, stop and tell the user what to install.
4. Confirm Git is available. If Git is missing, stop and tell the user what to install.
5. Check whether `npx skills --help` works.

Install root:
1. Ask:
   - local install into `<workspace>/.agents/skills`
   - global install into `~/.agents/skills`
2. Create the selected skills directory if it does not exist.
3. Use this selected directory for all manual skill installs.

Install command-line dependencies:
1. Install `agent-browser`:
   ```sh
   npm install -g agent-browser
   agent-browser install
   agent-browser --help
   ```
2. On Linux, if browser dependencies are missing, ask before running:
   ```sh
   agent-browser install --with-deps
   ```
3. Install Playwright CLI:
   ```sh
   npm install -g @playwright/cli@latest
   playwright-cli --help
   playwright-cli install --skills
   ```
4. If global npm installs fail because of permissions, ask the user whether to:
   - retry with the platform's recommended user-level npm prefix
   - use a local install
   - use a privileged command

Preferred skill installation:
Try the skills CLI first when it is available:
```sh
npx skills add arterm-sedov/web-search-skill --skill web-search
npx skills add arterm-sedov/human-search-skill --skill human-search
npx skills add arterm-sedov/deep-research --skill deep-research
npx skills add arterm-sedov/browser-switch-skill --skill browser-switch
```

If the skills CLI supports selecting local/global targets, use the user's selected target. If it does not, or if the target is unclear, use manual clone-and-copy so the files definitely land in the selected install root.

For `agent-browser` and `playwright-cli`, prefer their official npm/CLI installation flows first. Only use `npx skills add` or manual copy for these repositories after confirming an actual skill directory or installer-provided skill exists.

Manual fallback installation:
For any failed CLI install, clone the repository into a temporary directory, copy only the skill directory, and then remove the temporary clone.

Skill directory mapping:
```text
https://github.com/arterm-sedov/web-search-skill      -> skills/web-search       -> <install-root>/web-search
https://github.com/arterm-sedov/human-search-skill    -> skills/human-search     -> <install-root>/human-search
https://github.com/arterm-sedov/deep-research         -> skills/deep-research    -> <install-root>/deep-research
https://github.com/arterm-sedov/browser-switch-skill  -> skills/browser-switch   -> <install-root>/browser-switch
```

Manual copy rules:
- Copy only the actual `skills/<name>` directory, not the whole repository.
- Preserve all nested files and directories, including `references`, `scripts`, `templates`, and README files.
- If `<install-root>/<name>` already exists, ask whether to replace, skip, or back it up.
- If backing up, rename the old directory to `<name>.backup-YYYYMMDD-HHMMSS`.
- Clean up temporary clone directories after successful copy.

Human Search dependency check:
After installing `human-search`, run its dependency checker from the installed skill directory if Python is available:
```sh
python references/test_deps.py
```
On systems where the Python command is `python3`, use:
```sh
python3 references/test_deps.py
```
Allow normal user-space package installs. Ask before privileged actions or Docker repair.

Verification:
Confirm these skill directories exist in the selected install root:
```text
web-search
agent-browser
human-search
deep-research
browser-switch
playwright-cli
```

Confirm these commands work:
```sh
agent-browser --help
playwright-cli --help
```

If a command is unavailable but an `npx` fallback works, report the fallback explicitly:
```sh
npx playwright-cli --help
```

Optional agent discovery notes:
If the workspace has an agent instruction file such as `AGENTS.md`, `.agents/AGENTS.md`, `.cursorrules`, `.cursor/rules/*.md`, or `CLAUDE.md`, ask before adding a short installation note that points agents to the installed skills directory. Do not add usage instructions; each skill owns its own usage documentation.

Final report:
Print a concise installation summary with:
- selected install root
- installed skills
- skipped skills
- replaced or backed-up skill directories
- installed CLIs
- dependency checks run
- failures and manual follow-up steps
- whether the user should restart or reload their coding agent so it discovers the skills

Important constraints:
- Do not delete user files without asking.
- Do not run privileged commands without asking.
- Keep the process idempotent.
- Prefer official installation methods, but verify actual files exist in the selected install root.
- Do not include skill usage guidance in generated notes; this task is installation-only.
