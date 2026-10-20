# Spec: Siam Bean Mini ERP

Status: ready-for-agent
Part: all (1, 2 and 3; ownership in `docs/plan.md`)

Sources: `docs/scenario.md` (the business brief; always wins), `docs/plan.md` (team decisions), `GLOSSARY.md` (vocabulary).

## Problem Statement

Siam Bean Co. sells 1 kg bags of coffee to about 80 cafés with 5 staff. Orders arrive by LINE and phone and are retyped into a spreadsheet; stock lives in another sheet; invoices are written in Word and numbered by hand. The owner, Khun Somchai, puts it plainly:

1. "Stock in the sheet is always wrong."
2. "Each invoice takes me an hour and the numbers get mixed up."
3. "I never know who still owes me money."
4. "Sales sometimes promise beans we don't have."
5. "Anyone can change anything in the spreadsheet."

## Solution

A small web ERP, deployed at a public URL, where each staff member logs in and sees only what their role allows:

- **Products** and **customers** are kept in one place and are **deactivated**, never deleted.
- **Stock on hand** is never typed: it is the sum of **stock movements**. The warehouse records **stock in**; confirming a **sales order** takes stock out. **Low stock** products are flagged.
- Sales create a **draft** sales order and **confirm** it. Confirming checks stock, takes stock out and issues an **invoice** with 7% VAT, all at once or not at all. Too little stock means a clear error and no change.
- The accountant records **payments** against invoices; an invoice becomes paid when its **outstanding** amount reaches zero. **Open receivables** show who still owes money.
- A dashboard shows **sales today (incl. VAT)**, low-stock count, open invoices count, open receivables and stock value, live.
- The server checks every role on every request; a hidden button is never the only protection.

## User Stories

### Login and roles

1. As any staff member, I want to log in with my email and password, so that the system knows who I am and what I may do.
2. As any staff member, I want to see my name and role after logging in, so that I know I am on the right account.
3. As any staff member, I want the menu to show only the screens my role may use, so that I am not offered things I cannot do.
4. As a Sales user, when I open the Accounting screen directly, I want to see an access-denied page, so that I understand it is not for my role (US-3).
5. As the owner, I want the API to return 403 when a Sales user calls the accounting API, so that a hidden menu is not the only protection (US-3).
6. As the owner, I want the API to return 403 when a Warehouse user calls confirm-order directly, so that only sales staff and I can issue invoices (US-3).
7. As the Admin, I want every screen to load for me, so that I can do everything in the business (US-3).
8. As any user who is not logged in, I want every API call except the health check to return 401, so that no data leaks to strangers.
9. As any staff member, I want to log out, so that the next person on a shared PC cannot act as me.

### Products

10. As any staff member, I want to see the product list with SKU, name, unit, price and stock on hand, so that I know what we sell and what we have.
11. As a Warehouse user, I want low-stock products to show a low-stock badge in the product list, so that I can reorder in time (US-2).
12. As the Admin, I want to create a product with SKU, name, unit, cost, price and reorder level, so that we can sell it.
13. As the Admin, I want a duplicate SKU to be rejected with a message naming the SKU, so that every product is unique.
14. As the Admin, I want a negative price or cost to be rejected, so that prices stay valid.
15. As the Admin, I want to edit a product's price, so that new orders use the new price.
16. As the Admin, I want changing a product's price never to change existing orders or invoices, so that old documents stay correct.
17. As the Admin, I want to deactivate a product, so that it can no longer be sold but old documents still show it.
18. As the Admin, I want deactivated products hidden from the list by default and visible with a "Show inactive" toggle, so that the list stays clean but nothing is lost.
19. As the Admin, I want to reactivate a deactivated product, so that a mistake can be undone.
20. As a Sales, Warehouse or Accountant user, I want to be refused (403) if I try to create, edit or deactivate a product, so that only the owner sets prices.

### Customers

21. As a Sales user, I want to search customers by part of the name, case-insensitive, so that I find a café quickly (US-5).
22. As a Sales user, I want search results within 1 second and at most 20 rows per page with a total count, so that the list stays fast with 200 customers (US-5).
23. As a Sales user, I want to page through customer results, so that I can reach every match.
24. As a Sales user or the Admin, I want to create a customer with name, tax ID and payment terms, so that I can sell to a new café.
25. As a Sales user, I want a missing tax ID to be rejected with a clear message, so that every invoice has a valid buyer.
26. As a Sales user, I want to edit a customer's details and payment terms, so that they stay current.
27. As a Sales user, I want to deactivate a customer, so that no new orders go to a café we no longer serve.
28. As a Sales user, I want to reactivate a deactivated customer, so that a returning café can order again.
29. As an Accountant, I want to view customers but not change them, so that I can check who an invoice is for.
30. As a Warehouse user, I want to be refused (403) on the customer API, so that customer data stays with the people who need it.

### Stock

31. As a Warehouse user, I want a stock-in form with product, quantity and an optional note, so that arriving goods are recorded.
32. As a Warehouse user, I want a quantity of zero or below to be rejected, so that stock in only adds stock.
33. As a Warehouse user, I want my note saved with the movement (for example the supplier's delivery reference), so that we can trace where stock came from.
34. As any staff member, I want stock on hand to update immediately after a stock in, so that the number is always right.
35. As the owner, I want stock on hand always calculated from stock movements, so that nobody can type a wrong number (pain point 1).
36. As a Sales or Accountant user, I want to be refused (403) on stock in, so that only the warehouse and I change stock.

### Sales orders

37. As a Sales user, I want to create a draft sales order for a customer with one or more order lines, so that I can capture what the café wants.
38. As a Sales user, I want each draft to get the next number (`SO-0001`, `SO-0002`, …), so that orders are easy to refer to.
39. As a Sales user, I want each order line to copy the product's current price and cost, so that the order is fixed at today's price.
40. As a Sales user, I want creating an order to be all or nothing, so that a failure never leaves an empty or half-made order.
41. As a Sales user, I want new orders to refuse inactive customers or products with a message naming them, so that we don't sell to or sell things we have stopped.
42. As a Sales user, I want the product picker on the New order page to show stock on hand and the low-stock badge, so that I don't promise beans we don't have (pain point 4).
43. As a Sales user, I want a warning on a line whose quantity is more than stock on hand, while still being able to save the draft, so that I can take an order the café will wait for.
44. As a Sales user, I want the order detail of a draft to show stock on hand for each line, so that I see a shortage before I press Confirm.
45. As a Sales user, I want to confirm a draft, so that stock goes out and an invoice is issued in one step.
46. As a Sales user, given 170 kg of `ARB-1KG` on hand, when I confirm an order for Café Lune of 20 kg at 450 THB, I want stock on hand to show 150 kg and `INV-0001` to show 9,000 + 630 VAT = 9,630 THB (US-1).
47. As a Sales user, given a line quantity greater than stock on hand, when I confirm, I want to see "Not enough stock for ARB-1KG" and nothing to change (US-1).
48. As a Sales user, I want confirming an already-confirmed or cancelled order to be refused with a clear message, so that an order is never invoiced twice.
49. As a Sales user, I want confirming an order with no lines to be refused, so that empty invoices are never issued.
50. As a Sales user, I want two people confirming orders for the same beans at the same moment never to push stock below zero, so that the stock rule always holds.
51. As a Sales user, I want to cancel a draft I made by mistake, so that the order list stays clean.
52. As a Sales user, I want cancelling a confirmed order to be refused, so that issued invoices and stock movements are never silently undone.
53. As a Sales user, I want to see the list of sales orders with number, customer, date, status and total, so that I can follow my work.
54. As a Sales user, I want drafts made before a customer or product was deactivated to still be confirmable, so that work in progress is not lost.

### Invoices

55. As a Sales, Accountant or Admin user, I want to see the invoice list with number, order number, customer, dates, total, status, paid and outstanding, so that I know each invoice's state.
56. As a Sales, Accountant or Admin user, I want the invoice detail to show order lines, subtotal, VAT, total, the payments made, paid and outstanding, so that the numbers are complete and clear.
57. As the owner, I want invoice numbers (`INV-0001`, …) to be sequential and never reused, even when a confirm fails, so that the books are trustworthy (pain point 2).
58. As the owner, I want VAT to be exactly 7% of the subtotal, rounded to the satang, so that invoices are always right.
59. As the owner, I want each invoice's due date to be the issue date plus the customer's payment terms, so that I know when money is due.
60. As a Warehouse user, I want to be refused (403) on invoices, so that billing stays with sales and accounting.

### Accounting and payments

61. As an Accountant, I want an Accounting screen listing open invoices with their outstanding amount, so that I know who still owes money (pain point 3).
62. As an Accountant, I want to record a payment against an open invoice, so that what is owed stays up to date.
63. As an Accountant, given open invoice `INV-0001` of 9,630 THB, when I record a full payment, I want its status to become Paid and open receivables on the dashboard to drop by 9,630 THB (US-4).
64. As an Accountant, I want to record a partial payment and see the outstanding amount go down while the invoice stays open, so that I can handle instalments.
65. As an Accountant, I want a payment above the outstanding amount, or zero or below, to be rejected with the allowed range in the message, so that invoices are never overpaid.
66. As an Accountant, I want a payment on a paid invoice to be refused with a clear message, so that nothing is paid twice.
67. As a Sales user, I want to view invoices but have no way to record payments, so that money handling stays with accounting.

### Dashboard

68. As any staff member, I want a dashboard with live numbers, so that the owner sees the state of the business without asking anyone.
69. As the owner, I want to see sales today (incl. VAT), the total of invoices issued today in Bangkok time, so that I know how the day is going.
70. As the owner, I want to see the low-stock count, including every active product below its reorder level, so that I know what to reorder (US-2).
71. As the owner, I want to see the open invoices count and open receivables, so that I know how much is still owed.
72. As the owner, I want to see stock value (stock on hand × cost for active products), so that I know what the warehouse holds.
73. As the owner, I want the numbers to agree on every screen (invoice, accounting, dashboard), so that I can trust the system.

### Everyday use

74. As any staff member, I want money shown as `9,630.00 THB` everywhere, so that amounts are easy to read and compare.
75. As any staff member, I want every empty list to say so, so that I know it is empty and not broken.
76. As any staff member, I want every error to show the server's message saying what to fix, so that I can correct my input.
77. As any staff member, I want the app to work on a phone (single column under 640 px), so that I can use it away from the desk.
78. As the owner, I want Café Lune's 20 kg order to go from order to stock to invoice to payment to dashboard on the live URL with numbers that agree on every screen, so that I know the system works end to end.

## Implementation Decisions

### Architecture

- Supabase (Postgres + Auth), one project for both the deployed app and the tests. FastAPI backend talks to it with the secret key; the React + TypeScript frontend uses Supabase only to log in, then calls FastAPI with the user's access token. Backend on Render, frontend on Cloudflare Pages.
- The browser never reads tables directly: row-level security is on with no policies, and functions are revoked from public roles.
- The schema is already created. It may only grow: new functions are appended and run once in the SQL Editor; existing tables, views and functions are never changed.

### Authentication and roles

- The auth module checks the bearer token with Supabase Auth, loads the user's role and company from the users table, and exposes a role-requirement dependency that returns 403 for any other role. Every endpoint except the health check uses it.
- Role matrix (admin / sales / warehouse / accountant): view products and stock on hand: all; edit products: admin; view customers: admin, sales, accountant; edit customers: admin, sales; stock in: admin, warehouse; sales orders: admin, sales; view invoices: admin, sales, accountant; accounting and payments: admin, accountant; dashboard: all.
- Users and roles are set in Supabase, not in the app.

### Database functions (all-or-nothing logic)

- **create_order(company, customer, user, lines)** (new, Part 2): checks the customer and every product exist and are active, takes the next SO number, inserts the draft and its order lines with price and cost copied from the product, in one transaction. Raises the not-found or bad-input code.
- **confirm_order(order, user)** (existing): locks the order and its products, checks stock, writes negative stock movements tagged with the SO number, takes the next INV number, writes the invoice (subtotal, 7% VAT, total, due date from payment terms), and marks the order confirmed. Error codes: not found, not enough stock ("Not enough stock for <SKU>"), wrong state.
- **record_payment(invoice, amount, user)** (existing): rejects non-open invoices and amounts outside 0.01 to the outstanding amount; marks the invoice paid when payments reach the total.
- **dashboard_numbers(company)** (existing): sales today, low-stock count, open invoices count, open receivables, stock value.
- **next_doc_number** runs inside the caller's transaction, so a failed confirm uses no number.
- **reset_demo_data('yes-reset')** puts the data back to the scenario starting point.
- FastAPI maps the database error codes to HTTP: not found → 404, not enough stock → 409, wrong state or bad input → 422, always with a `detail` message.

### API contract

All JSON, all need the bearer token except the health check. Errors are `{"detail": "<message that says what to fix>"}`; 401 not logged in, 403 wrong role, 404 not found, 409 not enough stock, 422 bad input.

- Health check (no login); current user (email, full name, role).
- Products: list (includes stock on hand and low-stock flag, active only unless include-inactive is asked for), create, edit, deactivate. Reactivate by editing `active` back to true.
- Customers: list with name search (contains, case-insensitive), 20 per page, total count, include-inactive flag; create, edit, deactivate; tax ID required.
- Stock in: product, quantity > 0, optional note. Saved as one positive stock movement whose reference is `STOCK-IN`, or `STOCK-IN: <note>` when a note is given.
- Sales orders: list, detail, create (customer and lines of product and quantity, via create_order), confirm (via confirm_order), cancel (drafts only; "Only draft orders can be cancelled" otherwise). No editing drafts: cancel and create a new one.
- Invoices: list and detail. The same invoice shape is used by the invoice list, the invoice detail and the accounting receivables list: number, order number, customer name, issue date, due date, subtotal, VAT, total, status, paid (sum of payments), outstanding (total − paid). The detail also has lines and payments (amount, paid at).
- Accounting: receivables (open invoices in the invoice shape) and record payment against an invoice (via record_payment). The payment route is owned by Part 3 even though it sits under invoices.
- Dashboard: the five numbers from dashboard_numbers.
- Money in JSON is a number with 2 decimals. The frontend only formats it and never recalculates VAT or totals.

### Deactivation rules

- Inactive products and customers are hidden from lists unless include-inactive is asked for; admin screens have a "Show inactive" toggle.
- They cannot go on new orders (create_order rejects them by name).
- Drafts made before deactivation can still be confirmed.
- Inactive products are not counted in the low-stock count or stock value.

### Frontend

- Pages: Login, layout and role-filtered menu, access denied, Accounting (Part 3); Products, Customers, Stock in, Dashboard (Part 1); Orders, New order, Order detail, Invoices, Invoice detail (Part 2).
- Shared pieces from Part 3: route table, role-filtered menu, API client (adds the token, surfaces `detail`), the THB money formatter, empty-list and error components.
- Opening a page the role may not use shows the access-denied page.
- New order: product picker shows stock on hand and the low-stock badge; a line over stock on hand shows a warning but can be saved. Order detail of a draft shows stock on hand per line. Confirm is the only real check.
- Invoice detail shows status, paid and outstanding and has no "Record payment" button; payments are recorded only on the Accounting screen.
- The dashboard tile is labelled "Sales today (incl. VAT)".
- Single column under 640 px.

### Build order and ownership

- Part 3 builds the skeleton first and pushes it: backend app with every router registered as an empty stub in its owner's file, auth, database client, test fixtures with the file lock and the role login fixture, passing health and current-user tests; frontend routes pointing at placeholder pages, menu, API client, money formatter, shared components.
- Parts 1 and 2 then edit only their own routers, pages and test files. Shared files belong to Part 3.
- Everyone commits to `main`; tests pass, then pull with rebase, then push. `main` deploys.

## Testing Decisions

- **One seam: the HTTP API.** Tests use FastAPI's test client against the real Supabase project. They call endpoints and check status codes and JSON; they never call database functions directly, never read tables to check internals, and never mock Supabase. Only the token check is overridden: a fixture logs the request in as the demo user with the given role.
- **A good test** describes behaviour a user or the owner would recognise: "a Warehouse user gets 403 on confirm", "confirming 20 kg leaves 150 kg on hand and a 9,630.00 invoice". It survives any rewrite of the code behind the endpoint.
- **Fresh data for every test**: reset the demo data before each test. Tests that need more data (for example 200 customers for US-5) create it through the API or the fixture, and the next reset removes it.
- **One test run at a time** across the three repo copies: the test fixtures hold a file lock outside the repos for the whole run.
- **Test first**: write the failing test, run it and see red, then implement. Never edit a test to make it pass.
- **Each user story US-1 to US-5 gets at least one API test using the scenario's exact numbers**: 170 → 150 kg and `INV-0001` = 9,000 + 630 = 9,630.00; "Not enough stock for ARB-1KG" with nothing changed; ROB-1KG low-stock badge and counted on the dashboard; Sales 403 on accounting, Warehouse 403 on confirm, Admin 200 on both; full payment makes `INV-0001` paid and open receivables drop by 9,630.00; search over 200 customers returns at most 20 rows with a total.
- **Role tests**: for each endpoint, one allowed role succeeds and one forbidden role gets 403; no token gets 401.
- **Modules tested**: auth and current user; products; customers; stock; orders (create, confirm, cancel); invoices; accounting and payments; dashboard. Purchasing and the PDF invoice are tested only if the bonus is built.
- **Each Part owns its test files**; nobody shares a test file. Test fixtures belong to Part 3.
- **Frontend has no automated tests.** It must pass the production build (which type-checks). It is checked by hand on the live URL against the success criteria: Café Lune order to dashboard with agreeing numbers, Warehouse cannot confirm, and the owner's dashboard.
- **Prior art**: none yet; the repo has no code. Part 3's health and current-user tests become the pattern the other Parts copy.

## Out of Scope

- Quotations and delivery notes.
- Purchasing (purchase orders, receiving) and the PDF invoice: bonus only.
- Stock adjustments or manual stock out: possible bonus.
- Cancelling confirmed orders or invoices (would need stock reversal and credit notes). An invoice is never set to cancelled.
- Editing draft orders (cancel and create a new one instead).
- A user management screen: users and roles are set in Supabase.
- More than one company, HR and payroll, withholding tax, more than one warehouse, LINE integration.
- Overriding a line's price on an order.

## Further Notes

- The tests reset the only Supabase project, so they wipe the app's data. Reset the demo data once right before the demo and never run tests during it.
- Render's free tier sleeps when idle; the first request can take about 50 seconds. Open the live app a minute before the demo so US-5's 1-second search holds.
- "Stock is reserved" in US-1 means stock goes out at confirm; there is no separate reservation step (see `GLOSSARY.md`).
- Document numbers may have gaps (for example a cancelled draft keeps its SO number), but a number is never reused.
