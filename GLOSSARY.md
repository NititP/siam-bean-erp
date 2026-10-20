# Siam Bean Mini ERP

The business language of Siam Bean Co., a Bangkok coffee-bean distributor selling to cafés: products, stock, sales orders, invoices and payments.

## Master data

**Product**:
A bean or drip-bag item the company sells, identified by its SKU, with a cost, a price (without VAT) and a reorder level.
_Avoid_: Item, article

**Customer**:
A café that buys from Siam Bean, identified by its tax ID, with payment terms in days (0 = cash).
_Avoid_: Client, account, buyer

**Deactivated**:
A product or customer that can no longer be used on new documents but is kept because old documents refer to it. Never deleted.
_Avoid_: Deleted, archived

## Stock

**Stock movement**:
One signed change to a product's stock (+ in, − out), tagged with the document or reason that caused it.
_Avoid_: Stock transaction, stock entry

**Stock on hand**:
The sum of a product's stock movements. Always calculated, never typed in.
_Avoid_: Inventory count, balance, quantity

**Stock in**:
A warehouse receipt of goods that adds stock, recorded as a positive stock movement.
_Avoid_: Goods receipt (that is the bonus purchasing flow), restock

**Low stock**:
A product whose stock on hand is below its reorder level.
_Avoid_: Out of stock (that means zero)

## Sales

**Sales order**:
A café's request for products, numbered `SO-0001`. It is a **draft** until confirmed.
_Avoid_: Order request, quotation, sale

**Draft**:
A sales order not yet confirmed. It holds no stock and has no invoice, and it is the only kind of order that can be cancelled.

**Confirm**:
Turning a draft into a confirmed sales order: stock goes out and an invoice is issued, all at once or not at all. When US-1 says "stock is reserved", it means this: there is no separate reservation step.
_Avoid_: Approve, submit

**Cancelled order**:
A draft that was abandoned. Confirmed orders are never cancelled.

**Order line**:
One product and quantity on a sales order, carrying the price and cost copied from the product at the time.
_Avoid_: Order item, row

## Billing

**Invoice**:
The bill issued when a sales order is confirmed, numbered `INV-0001`, with a subtotal, 7% VAT and a total. It is **open** until fully paid, then **paid**.
_Avoid_: Bill, receipt, tax invoice

**Payment**:
Money received from a customer against one invoice. Partial payments are allowed; overpayment is not.
_Avoid_: Receipt, settlement

**Outstanding**:
An open invoice's total minus its payments.
_Avoid_: Balance, remaining, due

**Open receivables**:
The sum of outstanding amounts across all open invoices: what customers still owe.
_Avoid_: Debtors, AR balance, unpaid total

**Sales today**:
The total, including VAT, of invoices issued today (Bangkok time).
_Avoid_: Revenue, turnover, daily income
