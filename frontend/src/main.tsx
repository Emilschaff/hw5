import { useCallback, useEffect, useMemo, useState } from 'react';
import { Activity, ArrowRight, CheckCircle2, CircleDollarSign, Clock3, RotateCcw, ShieldCheck, Sparkles, WalletCards } from 'lucide-react';
import './styles.css';

const API = 'http://localhost:8000';
const AGENTS = ['Boss', 'Inventory', 'Accounting', 'Facilities', 'Customer Service'] as const;
type Agent = typeof AGENTS[number];
type Ticket = { id:number; type:string; requester:string; subject:string; status:string; notes:string; sku?:string|null; size?:string|null; qty?:number|null };
type Event = { timestamp:string; agent:Agent; action:string; target?:string; result:string };

const ticketAccent: Record<number,string> = { 101:'coral', 102:'gold', 103:'mint' };

function App() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const initialTicket = Number(window.location.hash.replace('#ticket-', ''));
  const [selected, setSelected] = useState(initialTicket === 102 || initialTicket === 103 ? initialTicket : 101);
  const [events, setEvents] = useState<Event[]>([]);
  const [balance, setBalance] = useState<number | null>(null);
  const [running, setRunning] = useState(false);
  const [message, setMessage] = useState('Desk online. Waiting for a ticket.');
  const [approval, setApproval] = useState(false);

  const refresh = useCallback(async () => {
    const [t, e, c] = await Promise.all([fetch(`${API}/api/tickets`), fetch(`${API}/api/events?limit=100`), fetch(`${API}/api/cash/checking`)]);
    if (t.ok) setTickets((await t.json()).tickets);
    if (e.ok) setEvents((await e.json()).events);
    if (c.ok) setBalance((await c.json()).balance);
  }, []);
  useEffect(() => { refresh().catch(() => setMessage('Backend is offline — start FastAPI on port 8000.')); }, [refresh]);
  useEffect(() => { if (!running) return; const timer = window.setInterval(() => refresh(), 1200); return () => window.clearInterval(timer); }, [running, refresh]);

  const current = tickets.find(t => t.id === selected);
  const ticketEvents = events.filter(e => e.target === String(selected) || e.action === 'mcp_tool' || e.action === 'delegation');
  const latestByAgent = useMemo(() => AGENTS.map(agent => ({ agent, event: [...ticketEvents].reverse().find(e => e.agent === agent) })), [ticketEvents]);

  async function runTicket() {
    setRunning(true); setMessage(`Boss is opening ticket ${selected}…`); setApproval(false);
    try {
      const response = await fetch(`${API}/api/tickets/${selected}/run`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ agent:'Boss', delegation_budget:2 }) });
      if (!response.ok) throw new Error((await response.json()).detail || 'Agent run failed');
      const data = await response.json(); setMessage(data.result?.answer || `Ticket ${selected} review complete.`); setApproval(Boolean(data.result?.needs_approval));
      await refresh();
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Agent run failed.'); } finally { setRunning(false); }
  }
  async function approve() {
    const response = await fetch(`${API}/api/tickets/${selected}/approve`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ approved_by:'Human desk operator' }) });
    if (!response.ok) { setMessage((await response.json()).detail || 'Approval failed.'); return; }
    const data = await response.json(); setApproval(false); setMessage(`Approved: $${Number(data.payment_amount).toFixed(2)} paid. Checking is now $${Number(data.new_balance).toFixed(2)}.`); await refresh();
  }
  async function reset() { await fetch(`${API}/api/reset`, { method:'POST' }); setMessage('Working database restored to the seed snapshot.'); await refresh(); }

  return <div className="app-shell">
    <header className="topbar"><div className="brand"><div className="brand-mark">CC</div><div><p className="eyebrow">CAMPUS CUSTOMS / OPERATIONS</p><h1>the desk</h1></div></div><div className="status"><span className="pulse" /> Live workspace <span className="divider" /> <button className="icon-button" onClick={reset} title="Reset working database"><RotateCcw size={15} /></button></div></header>
    <main className="workspace">
      <section className="intro"><div><p className="eyebrow">MONDAY / AUGUST 31, 2026</p><h2>Good morning, operator.</h2><p className="subhead">Three open threads, five specialists, one clear next move.</p></div><div className="cash-card"><div className="cash-label"><WalletCards size={16}/> CHECKING BALANCE</div><strong>${balance === null ? '—' : balance.toLocaleString('en-US',{minimumFractionDigits:2})}</strong><span>live from cash_accounts</span></div></section>
      <div className="grid">
        <aside className="ticket-rail"><div className="rail-heading"><span>OPEN QUEUE</span><b>{tickets.filter(t=>t.status==='open').length.toString().padStart(2,'0')}</b></div>{tickets.map(ticket => <button className={`ticket-card ${selected===ticket.id?'selected':''} ${ticketAccent[ticket.id]}`} key={ticket.id} onClick={()=>{setSelected(ticket.id);setApproval(false)}}><div className="ticket-top"><span>#{ticket.id}</span><span className={`state ${ticket.status}`}>{ticket.status==='resolved'?'resolved':'open'}</span></div><h3>{ticket.subject}</h3><p>{ticket.requester}</p><div className="ticket-meta"><span>{ticket.type.replace('_',' ')}</span><ArrowRight size={14}/></div></button>)}</aside>
        <section className="desk-panel"><div className="panel-head"><div><p className="eyebrow">ACTIVE TICKET / #{selected}</p><h2>{current?.subject || 'Loading ticket…'}</h2><p className="subhead">{current?.notes}</p></div><button className="run-button" onClick={runTicket} disabled={running || !current || current.status==='resolved'}>{running?<><Activity className="spin" size={17}/> Team is working</>:<><Sparkles size={17}/> Start team run</>}</button></div>
          <div className="run-strip"><div className="strip-icon"><ShieldCheck size={17}/></div><div><strong>{message}</strong><span>Agents can prepare actions. A human always approves money movement.</span></div>{approval && <button className="approve-button" onClick={approve}>Approve payment <CheckCircle2 size={15}/></button>}</div>
          <div className="agents-heading"><span>TEAM SIGNAL</span><span className="live-caption"><span className="tiny-pulse"/> {running?'reading the room':'ready to work'}</span></div>
          <div className="agent-grid">{latestByAgent.map(({agent,event})=><article className={`agent-card ${event?'has-event':''}`} key={agent}><div className="agent-avatar">{agent.split(' ').map(x=>x[0]).join('')}</div><div className="agent-copy"><div className="agent-name"><strong>{agent}</strong>{event?<CheckCircle2 size={15}/>:<Clock3 size={15}/>}</div><p>{event ? event.result : 'Standing by for a handoff.'}</p>{event && <small>{event.action.replace('_',' ')} · {new Date(event.timestamp).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</small>}</div></article>)}</div>
          <div className="summary"><div className="agents-heading"><span>RUN NOTES</span><span>{ticketEvents.length} events</span></div>{ticketEvents.length===0?<p className="empty">Start a team run to see evidence, handoffs, and decisions appear here.</p>:ticketEvents.slice(-8).reverse().map((event,i)=><div className="event-row" key={`${event.timestamp}-${i}`}><span className="event-dot"/><div><strong>{event.agent}</strong><span>{event.result}</span></div><small>{event.action}</small></div>)}</div>
        </section>
      </div>
    </main>
    <footer><span><CircleDollarSign size={14}/> Human approval gate active</span><span>Campus Customs / internal desk</span></footer>
  </div>;
}
export default App;
