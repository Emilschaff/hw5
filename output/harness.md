# Campus Customs Agent Harness

## Global model rule

Every agent in this assignment must use `gpt-6-luna` through Portkey. No other model may be configured or called anywhere in the code.

## Database working copy

The original `data/campus_customs.db` is preserved. Work for later problems should use `data/campus_customs_new.db`, which was copied byte-for-byte from the original on 2026-10-13.

## Table and field inventory

### `desk`

Operational desk state used to ground agents in the current business date and shared notes.

| Field | Why it matters to agents |
|---|---|
| `date_today` | Anchors due-date, rent, payment, and ticket reasoning to the shop's current date. |
| `notes` | Carries shared operational context that agents should consider before acting. |

### `tickets`

The work queue for customer, rent, and pricing issues; it links operational requests to inventory, leases, and invoices.

| Field | Why it matters to agents |
|---|---|
| `id` | Stable identifier for tracking and updating a request. |
| `type` | Tells the agent what workflow and controls apply. |
| `requester` | Identifies the customer, organization, landlord, or other party needing attention. |
| `subject` | Short human-readable description for triage and display. |
| `sku` | Connects a ticket to a specific inventory and pricing item. |
| `size` | Identifies the requested product variant. |
| `qty` | Captures requested quantity for availability and pricing checks. |
| `lease_id` | Connects rent-related work to a lease record. |
| `invoice_id` | Connects purchasing or payment work to an invoice. |
| `status` | Shows whether the request still needs action. |
| `notes` | Stores the detailed request and important constraints. |
| `created_at` | Establishes ticket age and ordering. |

### `inventory`

Authoritative size-level stock data used to answer availability questions and evaluate order requests.

| Field | Why it matters to agents |
|---|---|
| `sku` | Identifies the product and joins stock to pricing and tickets. |
| `name` | Gives agents the customer-facing product name. |
| `size` | Distinguishes each stocked variant. |
| `qty` | Provides the real quantity; agents must not invent stock. |
| `location` | Helps staff find or pick the item. |

### `pricing`

Authoritative cost and selling-price data used for quotes, margin checks, and overrides.

| Field | Why it matters to agents |
|---|---|
| `sku` | Joins prices to the correct product. |
| `unit_cost` | Supports margin and purchasing analysis. |
| `list_price` | Gives the standard customer-facing price. |

### `vendors`

Supplier directory used to understand who provides goods or services and how quickly they can respond.

| Field | Why it matters to agents |
|---|---|
| `id` | Stable vendor identifier for invoices and joins. |
| `name` | Identifies the supplier in communications and recommendations. |
| `specialty` | Shows what goods or services the vendor provides. |
| `lead_days` | Helps estimate replenishment timing. |

### `leases`

Store-location obligations used by agents handling rent and occupancy tasks.

| Field | Why it matters to agents |
|---|---|
| `id` | Stable identifier referenced by rent tickets. |
| `space_name` | Identifies the leased shop space. |
| `landlord` | Identifies who should receive rent or correspondence. |
| `monthly_rent` | Shows the recurring financial obligation. |
| `next_due` | Supports deadline and payment reminders. |
| `notes` | Holds lease-specific context. |

### `cash_accounts`

Current cash position by account, used to assess whether proposed payments are fundable.

| Field | Why it matters to agents |
|---|---|
| `name` | Identifies the account a payment uses. |
| `balance` | Shows available funds for safe payment decisions. |
| `date` | Establishes when the balance was recorded. |

### `payments`

The payment ledger used to verify completed disbursements and connect them to an account or reference.

| Field | Why it matters to agents |
|---|---|
| `id` | Stable payment identifier. |
| `kind` | Describes the payment's business purpose. |
| `ref_id` | Links the payment to a related record when applicable. |
| `amount` | States the amount that moved. |
| `account` | Identifies the cash account used. |
| `paid_at` | Establishes when the payment occurred. |
| `approved_by` | Shows authorization responsibility. |

### `invoices`

Vendor bills used for accounts-payable review and payment decisions.

| Field | Why it matters to agents |
|---|---|
| `id` | Stable invoice identifier referenced by tickets. |
| `vendor_id` | Connects the bill to its supplier. |
| `amount` | Shows the amount owed. |
| `due_date` | Supports prioritization and deadline alerts. |
| `status` | Distinguishes open bills from completed work. |
| `description` | Explains what the invoice covers. |

## The three open tickets and their connections

All three tickets have `status = open`.

1. **Ticket 101 — Bulldog tee:** Tauhid Zaman requests 1 `CC-TEE-WHITE` in size S. The ticket's `sku` and `size` join to the inventory row showing **0 in stock** at Aisle B. The same SKU joins to pricing (`unit_cost` $8.00, `list_price` $28.00). Its `invoice_id = 501` joins to invoice 501, an $840 open invoice from vendor 1, Bulldog Print Co., described as a rush reprint for `CC-TEE-WHITE S`. There is no direct vendor ID on the ticket; the vendor is reached through that invoice.

2. **Ticket 102 — Rent due:** Elm City Properties reports rent due in two days. Its `lease_id = 1` joins to the Chapel Street shop lease with Elm City Properties, monthly rent $2,400, due 2026-09-02. There is no invoice or inventory reference. The current desk date is 2026-08-31, which explains the two-day warning. The checking cash account has $3,400 as of the desk date, but no payment has been recorded.

3. **Ticket 103 — Bulk hoodie discount:** Yale AI Club requests 20 `CC-HOOD-NAVY` hoodies in size M. The ticket joins to inventory, which has **8 in stock** in size M at Aisle A, and to pricing, which lists a $22.00 unit cost and $58.00 list price. The requested quantity exceeds current stock by 12. It has no lease, invoice, vendor, or cash-account reference; any discount or replenishment decision therefore needs additional authorization and a separate vendor/payment workflow.

### Relationship summary

`tickets.sku + tickets.size` → `inventory.(sku, size)` and `tickets.sku` → `pricing.sku`.

`tickets.lease_id` → `leases.id`; `tickets.invoice_id` → `invoices.id`; `invoices.vendor_id` → `vendors.id`.

`payments.account` → `cash_accounts.name` by business meaning, although the schema does not declare a foreign-key constraint. The current database has no payment rows.

## MCP tools — Problem 3

The MCP server is in `mcp_server/server.py` and reads `data/campus_customs_new.db`. It is not started in this problem.

| Tool | Tables read | Ticket unlocked | Why this is the right tool |
|---|---|---:|---|
| `get_customer_order_context` | `tickets`, `inventory`, `pricing`, `invoices`, `vendors` | 101 | Ticket 101 needs the real size-S tee availability and price, plus the linked rush-reprint invoice and its vendor. |
| `get_rent_payment_context` | `tickets`, `leases`, `desk`, `cash_accounts`, `payments` | 102 | Ticket 102 is a rent notice, so the agent needs the linked lease, current desk date, available cash, and any recorded payment before discussing next steps. |
| `get_bulk_hoodie_context` | `tickets`, `inventory`, `pricing` | 103 | Ticket 103 asks for 20 size-M hoodies, so the agent needs every hoodie size's real stock and the current price to identify the shortfall and evaluate the request. |
| `list_open_tickets` | `tickets` | 101, 102, 103 | Boss needs the live open queue to triage all three tickets without relying on a copied list. |
| `get_restock_vendor_options` | `pricing`, `vendors` | 101, 103 | Inventory can compare the affected SKU's real economics with recorded vendor specialties and lead times before proposing replenishment. |
| `get_financial_obligations` | `invoices`, `leases`, `cash_accounts`, `payments` | 101, 102, 103 | Accounting needs one authoritative view of open obligations, available cash, and completed payments before recommending action. |
| `get_facilities_context` | `tickets`, `leases`, `desk`, `payments` | 102 | Facilities needs the rent ticket's linked lease, current desk date, and any related payment evidence to assess urgency safely. |

## Five-agent team

Every agent uses the same Portkey-backed `gpt-6-luna` model and the same MCP server. Delegation is fully connected: each agent can delegate to any of the other four through the shared `delegate` tool, subject to a two-hop budget.

| Agent | Primary responsibility | MCP evidence it uses |
|---|---|---|
| Boss | Triage, coordination, approvals, and escalation | `list_open_tickets`, all ticket-context tools, `get_financial_obligations` |
| Inventory | Stock, variants, locations, vendor lead times, and replenishment recommendations | `get_customer_order_context`, `get_bulk_hoodie_context`, `get_restock_vendor_options` |
| Accounting | Invoices, leases, prices, cash, payments, and financial risk | `get_customer_order_context`, `get_rent_payment_context`, `get_bulk_hoodie_context`, `get_financial_obligations` |
| Facilities | Rent, lease, shop date, and occupancy operations | `get_rent_payment_context`, `get_facilities_context`, `get_financial_obligations` |
| Customer Service | Evidence-based customer and organization communication | `get_customer_order_context`, `get_bulk_hoodie_context`, `get_rent_payment_context` |

## Safety and operating limits

- MCP/database evidence is authoritative. Agents must not invent stock, prices, balances, dates, vendor terms, payment status, or customer promises.
- Payment, refund, discount, invoice settlement, vendor order, lease action, external communication, and ticket mutation require explicit human approval; agents only analyze and recommend.
- Customer-facing replies should expose only appropriate business information and should clearly distinguish confirmed facts, recommendations, and unknowns.
- Agents must flag overdue obligations and size-specific shortages rather than silently substituting variants or assuming replenishment.
- The audit helper appends one timestamped record for each MCP call, delegation, and delegation result to `output/audit_trail.json`; it never resets prior entries.
- Each run starts with a delegation budget of two and decrements it at every handoff. Tool calls are bounded to the records needed for the ticket, and structured replies keep context small. This limits token growth in a fully connected team.
- Each model call has a 1,200-token output cap in `backend/team.py`. PydanticAI translates the internal `max_tokens` setting to Portkey's `max_completion_tokens` field, which is required by `gpt-6-luna`; the two-hop delegation budget remains enforced separately.

## FastAPI dashboard routes — Problem 7

- `GET /api/tickets` — returns tickets 101–103 with their current fields and open/resolved status.
- `POST /api/tickets/{ticket_id}/run` — runs a selected team agent on ticket 101, 102, or 103; the agent may delegate and must use MCP evidence.
- `GET /api/events?limit=50` — returns the most recent append-only agent audit events, including agent actions, delegations, MCP tools, and short results.
- `POST /api/tickets/{ticket_id}/approve` — executes a human-approved payment or purchase, inserts the payment, decrements the selected cash account, and resolves the ticket after safety checks.
- `GET /api/cash/checking` — returns the current `checking` row from `cash_accounts`.
- `POST /api/reset` — restores `data/campus_customs_new.db` byte-for-byte from `data/campus_customs.db`.

## Dashboard — Problem 8

The React/Vite/TypeScript dashboard lives in `frontend/` and calls the FastAPI service at `http://localhost:8000`. It presents the three-ticket queue, a selected-ticket work surface, a five-agent signal row, live audit-event notes, human approval controls, checking balance, and a database reset control. The visual design is documented in `output/design.md`; `npm run dev` serves it at `http://localhost:5173`.

## Problem 9 run record and ticket-103 incident

The Problem 9 run began from a reset checking balance of $3,400. Ticket 101 paid invoice 501 ($840), ticket 102 paid lease 1 rent ($2,400), and ticket 103 ultimately resolved as a 0% discount with no cash movement. The final checking balance is $160 and matches the working database.

During testing, a human entered an arbitrary $50 approval for ticket 103 even though no $50 purchase, discount, or other amount existed in ticket data. The approval route accepted it, reduced checking to $110, and marked the ticket resolved. That payment was then reversed and removed from the working ledger; the audit trail preserves both the historical approval and the reversal, and the corrected resolution has zero cash impact.

This is a real safety gap. The current system now requires an explicit amount for purchases, prevents negative balances, and preserves audit records, but it still permits an operator-supplied amount when the request has no database-grounded purchase amount. Before production use, `/api/tickets/{ticket_id}/approve` should reject arbitrary amounts unless they match an invoice, lease, or an MCP-backed purchase-order record. Price-override tickets should have a separate no-cash approval route that records the approved percentage/price and never inserts a payment. The UI should display the evidence source and block approval when no traceable amount exists.

## Delegation audit correction

The implementation contains a reusable `delegate` tool and registers it on every agent, so full connectivity is available in code. However, the recorded ticket 101–103 runs did not call that delegation tool. `backend/team.py` shows Boss and the other four agents are separately registered, but `boss_agent.py` and the other agent entry files only register agents; they do not create an automatic delegation plan. The audit trail attributes the MCP calls and agent-loop entries to Boss, with no Inventory, Accounting, Facilities, or Customer Service entries. Therefore the original `resolved_tickets.json` specialist-agent credits were inaccurate and have been corrected: those runs were Boss-led direct MCP lookups, not five-agent executions. This is a material gap against the assignment's five-agent/full-delegation requirement and should be addressed by an explicit orchestration plan plus tests that assert delegated agent names appear in the audit trail.
