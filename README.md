# Campus Customs HW 5

Campus Customs is a FastMCP-backed, five-agent operations desk for tickets, inventory, accounting, facilities, and customer service. Every model call uses `gpt-6-luna` through Portkey.

## Setup

1. Create a local environment file from the placeholder and add your key:

   ```powershell
   Copy-Item .env.example .env
   # edit .env and set PORTKEY_API_KEY
   ```

   Never commit `.env`; `.env.example` contains placeholders only.

2. Install backend dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. The repository includes both database files. To create a clean working run, copy the original seed over the working copy:

   ```powershell
   Copy-Item data/campus_customs.db data/campus_customs_new.db -Force
   ```

## Run the services

Start the MCP server from the project root:

```powershell
py -3.14 mcp_server/server.py
```

The project MCP configuration is in `.mcp.json`; the server reads `data/campus_customs_new.db`.

In a second terminal, start FastAPI from `backend/`:

```powershell
cd backend
uvicorn main:app --reload --port 8000
```

In a third terminal, start the React board:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The backend is at `http://localhost:8000`.

## Clean three-ticket run

Before a full run, reset the working database to the original values:

```powershell
Copy-Item data/campus_customs.db data/campus_customs_new.db -Force
```

Then use the board to run tickets 101, 102, and 103. Agents prepare recommendations; human approval is required for payments. The API reset route is `POST /api/reset`.

## Project map

- `mcp_server/` — FastMCP database tools
- `backend/` — PydanticAI team and FastAPI routes
- `frontend/` — React/Vite/TypeScript operations board
- `output/` — harness, audit, smoke evidence, design, and resolved-board reports
- `data/` — original and working SQLite databases, intentionally included for graders
