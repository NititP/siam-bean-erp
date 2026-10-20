# 03: Part 3: Deploy live

Part: 3
Status: ready-for-agent

**What to build:** The app is live at a public URL: backend on Render, frontend on Cloudflare Pages, both deploying from `main`. A demo user can log in on the live site and see their name and role.

**Blocked by:** 02 (Part 3: Login, current user and roles)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] Backend live on Render with env vars set (never committed); live `GET /health` returns 200
- [ ] Frontend live on Cloudflare Pages, pointing at the live API
- [ ] CORS allows the Pages URL
- [ ] Each demo user can log in on the live URL and sees the right menu
- [ ] Live URLs written into `docs/plan.md`
