# Problem 1 — Title not yet provided

Ok today we are going to work in the HW 5 folder, create a new AI_prompts.md to log our chats in, the same way as before

**Change note:** Created `AI_prompts.md` in the HW 5 folder and logged the initial session instructions under Problem 1. The problem title and task details were not included in the prompt.

# Problem 2 — Database Schema and Ticket Relationships

One rule for the whole assignment: every agent must use gpt-6-luna through Portkey, no other model, anywhere in the code. Keep that in mind for every problem going forward.

Open data/campus_customs.db and look through every table and field: desk, tickets, inventory, pricing, vendors, leases, cash_accounts, payments, invoices. Copy the original file to data/campus_customs_new.db, this is the working copy later problems will update, leave the original untouched so it can be reset later.

Study the three open tickets and how they link to the other tables, trace what each ticket references (inventory items, vendors, cash accounts, etc.).

Start output/harness.md. For each table, list its fields and one short line on why that table matters for the agents. I'll keep growing this file in later problems.

Finish without stopping to ask me. When you're done, confirm the copy was made correctly and show me the table breakdown plus how the three tickets connect to other tables.

**Change note:** Inspected every requested table and field, copied the untouched source database to `data/campus_customs_new.db`, traced the three open tickets through their linked records, and created `output/harness.md` with table-level agent rationale. Corrected this entry from Problem 1 to Problem 2 at the start of Problem 3.

# Problem 3 — MCP Ticket Tools

Ok that was problem 2, make sure it is tracked as such. NOw moving on to problem 3:

Build an MCP server in mcp_server/ using FastMCP, talking to data/campus_customs_new.db. Don't connect or run it yet, this problem is just building it.

Every agent in this homework will use the tools in this server, more get added later. For now, write three tools, based on what the three open tickets (101, 102, 103) in the database actually need, pull from what you found studying those tickets in Problem 2. Keep tool names clear, and never invent data, only use what's actually in the database.

In output/harness.md, list each of the three tools: which table it reads, which ticket (101, 102, or 103) it helps unlock, and one sentence on why that tool is the right one for that ticket, tie it to the specific ticket, not a vague description like "reads inventory."

Add a short mcp_server/README.md explaining what the server is for, which database file it uses, and the three tools.

Finish without stopping to ask me. When you're done, show me the three tools and which ticket each one unlocks.

**Change note:** Built an unstarted FastMCP server with three database-backed ticket tools, documented their exact table and ticket relationships in `output/harness.md`, and added `mcp_server/README.md`.

# Problem 4 — Connect and Smoke-Test the MCP Server

Connect the MCP server you built in mcp_server/ to this project so you can call its tools directly. Save the connection JSON in .mcp.json at the project root, or wherever Codex normally stores local MCP server configs.

Once connected, test all three tools for real, actually call each one, don't just describe what they'd do. Save evidence in output/mcp_smoke.json. For each tool, record: the prompt you used to call it, the tool name, and the tool's actual output.

The output values must match what's really in data/campus_customs_new.db, not fabricated or estimated numbers, go verify against the database directly if needed.

Finish without stopping to ask me. When you're done, show me the three test results and confirm they match the database.

**Change note:** Added project-local `.mcp.json`, installed the FastMCP runtime, called all three MCP tools through stdio, and saved their actual outputs in `output/mcp_smoke.json`.

# Problem 5 — Five-Agent PydanticAI Team

Build a five-agent Campus Customs team using PydanticAI: Boss, Inventory, Accounting, Facilities, Customer Service. Every agent may delegate to any other agent, full connectivity, not a fixed hierarchy. All five use PORTKEY_API_KEY and gpt-6-luna only, no other model anywhere.

Put one prompt file per agent in backend/prompts/, data types in backend/models.py, agent files under backend/. Write each agent's prompt yourself, in your own words, covering the shop rules that specific agent needs (which rules those are depends on the role, Boss needs the overdue/approval rules, Inventory needs the vendor/restock rules, Accounting needs the cash/payment rules, etc.). A detailed prompt covering the full scope of that agent's job scores higher than a short generic one.

Add whatever new tools the agents need to the existing MCP server so they can actually work the three open tickets. All shop facts must come through the MCP server over data/campus_customs_new.db, don't build a second tool layer that bypasses it.

Wire every agent to append to output/audit_trail.json as it runs, one entry per agent-loop step with enough detail to audit later (timestamp, agent, tool/delegation call, short result). Append only, never wipe the file between runs.

Update output/harness.md: list each agent and every MCP tool (new and old) with which table it uses, plus a safety section covering guardrails a real business would want when agents touch real customers and real money (the shop rules from the assignment are a good starting point), and limits that keep token use in check given multi-agent delegation burns tokens fast.

Update mcp_server/README.md so the tool list matches what you have now.

Finish without stopping to ask me. When you're done, tell me the five agents and their delegation paths, the full current tool list, and confirm only gpt-6-luna shows up anywhere in the code.

**Change note:** Built the five connected PydanticAI agents, detailed role prompts, MCP-backed tools, append-only audit logging, and updated documentation.

# Problem 6 — Desk Tickets, Cash, and Reflection Page

I forgot the cash and reflection tabs, among some other things. Treat this like a prompt redo, because I don't want to just address the little things that were missed, let's redo problem 6 entirely here. If you have to recreat it, fine, here are your instructions:

Build output/desk_tickets.html, a page I can double-click open, with five tabs: Ticket 101, Ticket 102, Ticket 103, Cash, Reflection.

Cash and Reflection tabs: leave empty, just a short "coming later" placeholder note in each, these get filled in a later problem.

Each ticket tab gets two sections: "Expected" and "Actual." Leave "Actual" empty for now, that gets filled in after we run the agents. Fill "Expected" with the following content exactly, lightly formatted but don't rewrite the substance:

Ticket 101: Boss calls Inventory first, to confirm the size-S stock is at 0 and check Bulldog Print Co.'s 5-day lead time. Then Accounting, because the shop rule against shipping while an unpaid invoice is open means invoice 501 has to be resolved before any reprint can proceed. Then Customer Service, to tell the customer there's a delay without promising a ship date yet. Facilities is not involved. Expected MCP tools: inventory lookup, vendor lookup, invoice/payment check.

Ticket 102: Boss calls Facilities first, to confirm the lease terms and the rent due date are accurate. Then Accounting, to confirm the $3,400 checking balance covers the $2,400 rent without going negative. Then Boss escalates to a human for payment approval, since human approval is required for any payment. Inventory and Customer Service are not involved, this is purely internal. Expected MCP tools: lease lookup, cash balance check, payment tool (held for approval).

Ticket 103: Boss calls Inventory first, to confirm the shortfall, 8 medium hoodies in stock against 20 requested, and whether restock is possible in time. Then Accounting, to evaluate whether a bulk discount off the $58 list price is viable given the $22 unit cost. Then Boss, since this is a price_override ticket and no discount can go out without approval. Finally Customer Service drafts a response communicating the shortage without promising a discount or delivery date. Facilities is not involved. Expected MCP tools: inventory lookup, pricing lookup.

When done, confirm all five tabs exist, confirm each ticket tab shows both Expected (filled) and Actual (empty) sections, and confirm Cash and Reflection show their placeholder notes. Show me a summary of what the page contains so I can verify nothing is missing before I move on.

**Change note:** Rebuilt `output/desk_tickets.html` as a five-tab page with Ticket 101–103, Cash, and Reflection; filled the three Expected sections, left all Actual sections empty, and added both requested placeholder notes.

# Problem 10 — Reflection Content

Here is the information to be put into the reflection:

**1. Agent performance per ticket, and why**
Ticket 101 was technically correct, so the right data was gathered and the payment executed properly once approved. But it was done by Boss alone calling one MCP tool, not through delegation to the other specialist agents.

Ticket 102 had the same issue: correct outcome and payment, but again no delegation, Boss called three MCP tools directly itself.

Ticket 103 worked! This one actually matches the prediction, where it called multiple agents and used them successfully.

**2. Expected vs Actual, per ticket**
For tickets 101 and 102, the Boss was expected to call the next agent for accounting, and then customer service if needed. Instead, the Boss called every tool itself, used input from me, and executed everything without using the other agents. This was materially different from the expectation, and usually resulted in incorrect outcomes.

For the third ticket, the Boss did run things through the agents, asking them to check inventory, then relay the non-discount to the customer. This was successful I think.

**3. One agent instead of five, and why**
Though the five agents working together was more successful, it seemed hard to coordinate and the Boss seemed like it could execute with tools on its own in not much extra time. I'm not really sure though because the Boss did get a lot wrong, so maybe it would have been better with the 5 agents.

**4. Three new solvable problems**
The three new problems I think are obvious. I think the agents should be called, they should run on their own and ask the human less (because I think I confused them a little) and they should each be able to be much faster working in tandem than just the Boss working by itself.

**5. Three new unsolvable problems**
I think that not having all of the information available was difficult for the agents. They needed to know things that weren't given to them, like what normal protocol for discounts is, what to do about customers who continue to go back and forth without coming to an answer, or how to handle things like the customer saying they want an irregular return policy, like making things right by a personal apology or a card or something crazy.

**Change note:** Added the provided five-part reflection to the Reflection tab in `output/desk_tickets.html`.

# Problem 7 — FastAPI Operations Dashboard Routes

Now for problem 7, in backend/main.py, use FastAPI and add routes for:
- Return the three tickets and whether each is open or resolved.
- Take a ticket id and run the agent team on that ticket.
- Return recent agent events, what each agent said and which tools they used, so a dashboard can refresh.
- Approve a payment or purchase after a human clicks approve, agents only prepare the pay, this route is what actually executes it and changes cash.
- Return the current checking balance from cash_accounts.
- Reset the database (data/campus_customs_new.db) back to the original values, data/campus_customs.db, when I want to try a fresh run.

The server runs from backend/ with: uvicorn main:app --reload --port 8000, at http://localhost:8000.

In output/harness.md, list each route in one line, URL and what it does.

Finish without stopping to ask me. When you're done, confirm the server starts and give me the full route list.

**Change note:** Added the FastAPI operations routes for ticket status, agent execution, audit events, human-approved payments, cash balance, and database reset; documented the route contract and verified the app imports.

# Problem 8 — React Agent Desk Dashboard

For problem 8 now, build the frontend dashboard in frontend/ with React + Vite + TypeScript, calling the backend routes from Problem 7. At minimum the board should:
- List all three tickets
- Let me pick one ticket and start the agent team on it
- Show each agent and what they're saying/doing while the ticket runs
- Mark a ticket resolved when the run finishes
- Show a short summary of what each agent did on that ticket
- Let a human approve a pay or purchase when asked
- Show the checking balance, it should drop after an approved pay

Point the front end at http://localhost:8000 for the backend. On the backend side, allow the Vite origin, usually http://localhost:5173, so the browser can actually call those routes, this probably needs a CORS change in backend/main.py.

The board starts with: npm run dev

Be creative with the layout and feel, this is a real desk people would want to sit at, put real thought into how it looks and how agents reading/working is visually communicated, not just a plain list.

Write output/design.md: what you chose for the dashboard look, layout, how agents reading differently is shown, how resolved tickets and cash show up, and why, including the creative choices that make it feel distinct.

Finish without stopping to ask me. When you're done, tell me how to run both pieces together and confirm a full ticket run actually works end to end through the UI.

**Change note:** Built the React/Vite/TypeScript operations desk, connected it to the Problem 7 API, enabled Vite CORS, and documented the dashboard design.

# Problem 9 — Resolve Tickets and Record Actual Results

For problem 9 now, reset data/campus_customs_new.db back to the original values before testing. Note the starting checking balance after the reset.

Run all three tickets (101, 102, 103) on the dashboard, through the actual UI, until each is marked resolved. For ticket 102 and any other payment, wait for the human-approval step rather than auto-approving, I want to actually click approve myself if the flow requires it, so stop and tell me when a payment is ready for approval instead of approving it for me.

Open output/desk_tickets.html from Problem 6. On each ticket tab, fill the Actual section with what really happened in this run: which agents worked, what they delegated, which tools they used. Don't touch the Expected sections, keep them as they are so I can compare.

On the Cash tab, itemize:
- Starting checking balance after the reset
- For each ticket, how cash changed when it resolved and why, which pay or purchase, dollar amount, note if none
- Ending checking balance, it must match cash_accounts in the working database exactly

Also save:
- output/resolved_tickets.json: for each ticket, id, final status, short outcome, what each agent contributed, any human approvals
- output/resolved_board.html, a page I can double-click, with a screenshot of the React board for each resolved ticket (101, 102, 103)

Append the real run data to output/audit_trail.json, don't wipe prior entries.

Finish output/harness.md so it fully covers: tables, MCP tools, the five agents, API routes, the dashboard, and safety rules.

When you're done, show me the final cash numbers and flag anywhere the Actual results differed from what I predicted in Expected.

**Change note:** Reset the working database and began the live ticket-resolution run. The run pauses at the first human-approval gate, preserving the approval decision for the user.
