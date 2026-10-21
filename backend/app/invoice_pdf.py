from fpdf import FPDF

# Owner: Part 2. Lays out GET /invoices/{id} as a one-page tax invoice; it never recalculates money.

# (heading, width in mm, align) for the line table; the widths add up to the 180 mm text width.
COLUMNS = [("SKU", 25, "L"), ("Product", 65, "L"), ("Quantity", 25, "R"), ("Unit price", 32, "R"), ("Line total", 33, "R")]


def thb(amount: float) -> str:
    """9630 -> "9,630.00 THB", the same as formatTHB in the frontend."""
    return f"{amount:,.2f} THB"


def text(value) -> str:
    # The built-in Helvetica font only has Latin-1 characters (é is fine); anything else becomes "?".
    return str(value).encode("latin-1", "replace").decode("latin-1")


def invoice_pdf(invoice: dict, company: dict) -> bytes:
    """invoice is the GET /invoices/{id} response; company has name and tax_id."""
    pdf = FPDF(format="A4")
    pdf.set_margins(15, 15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 8, text(company["name"]), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, text(f"Tax ID {company['tax_id']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Tax Invoice", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    for label, value in [
        ("Invoice", invoice["number"]),
        ("Sales order", invoice["order_number"]),
        ("Issued", invoice["issue_date"]),
        ("Due", invoice["due_date"]),
        ("Customer", invoice["customer_name"]),
        ("Customer tax ID", invoice["customer_tax_id"]),
    ]:
        pdf.cell(35, 6, label)
        pdf.cell(0, 6, text(value), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 10)
    for heading, width, align in COLUMNS:
        pdf.cell(width, 7, heading, border="B", align=align)
    pdf.ln()
    pdf.set_font("Helvetica", size=10)
    for line in invoice["lines"]:
        values = [
            line["sku"],
            line["name"],
            f"{line['quantity']} {line['unit']}",
            thb(line["unit_price"]),
            thb(line["line_total"]),
        ]
        for value, (_, width, align) in zip(values, COLUMNS):
            pdf.cell(width, 7, text(value), align=align)
        pdf.ln()

    pdf.ln(2)
    label_width = sum(width for _, width, _ in COLUMNS[:-1])
    for label, amount, style in [
        ("Subtotal", invoice["subtotal"], ""),
        ("VAT 7%", invoice["vat"], ""),
        ("Total", invoice["total"], "B"),
    ]:
        pdf.set_font("Helvetica", style, 10)
        pdf.cell(label_width, 7, label, align="R")
        pdf.cell(COLUMNS[-1][1], 7, thb(amount), align="R", new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())
