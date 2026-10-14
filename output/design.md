# Problem 8 Dashboard Design

The dashboard is designed as an internal operations desk rather than a generic admin table: dark ink, warm brass highlights, and mint status signals create a calm, focused work surface for decisions that may affect customers and cash.

- The left rail is an open queue of the three tickets. Each card shows the requester, issue type, open/resolved state, and a distinct accent color so the operator can scan urgency before selecting a ticket.
- The main panel gives the selected ticket a clear title, note, live run status, and one prominent “Start team run” action. The cash card stays visible at the top so money is never hidden in a secondary screen.
- Five agent cards form a “team signal” row. Agents begin dimmed as standing by, then brighten when their audit event appears. Their short evidence/result text, action label, and timestamp make reading, delegation, and tool use visible without turning the page into a log dump.
- A run-notes stream gives the operator the recent sequence of MCP calls, handoffs, and results. The visual hierarchy moves from what needs attention, to who is working, to the evidence behind the work.
- Resolved tickets change to a mint status and the run action disables. The approval control is mint and deliberately separate from the team run action: agents can prepare a payment, but only the human button executes it.
- The checking balance is a persistent brass-number “instrument” card. After approval, the UI refreshes the balance and confirms the amount and new balance in the run strip, making cash movement legible and auditable.
- The reset control is intentionally small and tucked into the header because it is useful during testing but should not compete with daily operating actions.

The layout collapses into a single-column mobile desk while retaining the queue, selected-ticket context, agent signals, and approval gate.
