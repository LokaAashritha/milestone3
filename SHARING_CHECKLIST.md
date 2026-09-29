# GitHub Sharing Checklist

## Commit

- [ ] `Backend_swipex/app/`
- [ ] `Backend_swipex/alembic/`
- [ ] `Backend_swipex/alembic.ini`
- [ ] `Backend_swipex/requirements.txt`
- [ ] `Backend_swipex/.env.example`
- [ ] `Backend_swipex/README.md`
- [ ] `Swipex-Frontend/src/`
- [ ] `Swipex-Frontend/public/`
- [ ] `Swipex-Frontend/package.json`
- [ ] `Swipex-Frontend/package-lock.json`
- [ ] `Swipex-Frontend/vite.config.js`
- [ ] `Swipex-Frontend/tailwind.config.js`
- [ ] `Swipex-Frontend/postcss.config.js`
- [ ] `Swipex-Frontend/index.html`
- [ ] `SwipeX-AIML-/` if the AIML intern work is part of the handoff
- [ ] `SwipeX_Job_Data_Service/` if the data intern work is part of the handoff
- [ ] Root `README.md`
- [ ] Root `.gitignore`

## Never Commit

- [ ] Any `.env` file
- [ ] `integ/`
- [ ] `.venv/` or `venv/`
- [ ] `node_modules/`
- [ ] `dist/`
- [ ] `*.db`, `*.sqlite`, or `*.sqlite3`
- [ ] Uploaded resumes or runtime storage
- [ ] Passwords, JWT secrets, API keys, or tokens

## Before Push

```cmd
git status
git diff --cached --name-only
```

Search staged files for secrets before pushing:

```cmd
git grep -n -I -E "(password|secret|token|DATABASE_URL)=" -- ':!*.example' ':!README.md'
```
