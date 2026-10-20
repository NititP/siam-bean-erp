# 07: Part 1: Customer list with search and paging

Part: 1
Status: ready-for-agent

**What to build:** Sales, the Accountant and the Admin see the customer list and search it by part of the name, 20 rows per page with a total count. Warehouse is refused.

**Blocked by:** 02 (Part 3: Login, current user and roles)

Spec: `.scratch/mini-erp/spec.md`. Plan: `docs/plan.md`.

- [ ] `GET /customers?q=&page=` matches names containing `q`, ignoring case
- [ ] Given 200 customers, a search returns at most 20 rows and the full `total` (US-5)
- [ ] Search responds within 1 second with 200 customers (US-5)
- [ ] Inactive customers are hidden unless `?include_inactive=true`
- [ ] Warehouse gets 403
- [ ] Customers page has a search box that filters as you type and page controls; an empty result shows a message
