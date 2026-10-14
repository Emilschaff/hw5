# Campus Customs MCP Server

This FastMCP server provides database-backed operations tools for every agent in HW 5. It reads only from the working copy at `../data/campus_customs_new.db` relative to this directory; the original database is not used by the server.

The server is intentionally not started for Problem 3. Later problems can run `server.py` through the chosen MCP transport.

## Tools

- `get_customer_order_context` — ticket 101's customer tee request, size-level stock, price, linked invoice, and vendor.
- `get_rent_payment_context` — ticket 102's rent notice, linked lease, desk date, cash accounts, and recorded payments.
- `get_bulk_hoodie_context` — ticket 103's bulk hoodie request, all size-level stock, and current price.
- `list_open_tickets` — all currently open tickets for triage.
- `get_restock_vendor_options` — SKU pricing plus relevant vendor specialties and lead times for replenishment planning.
- `get_financial_obligations` — open invoices, leases, cash accounts, and recorded payments.
- `get_facilities_context` — ticket 102's rent, lease, desk-date, and related payment context.

All values are read from SQLite. Missing records produce an error rather than invented data.
