from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from pathlib import Path
import sqlite3, json
from datetime import datetime

HERE=Path(__file__).parent
DB=HERE/"transfers.db"
JOBS=HERE/"job_orders.json"
PLANTS=["Plant 1","Plant 2","Plant 3"]
def connect(): return sqlite3.connect(DB)
def setup():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS transfers (id INTEGER PRIMARY KEY AUTOINCREMENT, job_order TEXT, sfg TEXT, qty INTEGER, source TEXT, destination TEXT, sender TEXT, sent_at TEXT, receiver TEXT, received_at TEXT)""")
    if not JOBS.exists(): JOBS.write_text(json.dumps([{"job_order":"JO-1001","product":"Pump Assembly"},{"job_order":"JO-1002","product":"Valve Assembly"}],indent=2))
def jobs(): return json.loads(JOBS.read_text())
def esc(v): return str(v or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")
def page():
    job_options="".join(f'<option value="{esc(j["job_order"])}">{esc(j["job_order"])} — {esc(j["product"])}</option>' for j in jobs())
    plant_options="".join(f'<option>{p}</option>' for p in PLANTS)
    with connect() as db:
        rows=db.execute("SELECT * FROM transfers ORDER BY id DESC").fetchall()
        total=db.execute("SELECT COUNT(*) FROM transfers").fetchone()[0]
        transit=db.execute("SELECT COUNT(*) FROM transfers WHERE receiver=''").fetchone()[0]
        received=db.execute("SELECT COUNT(*) FROM transfers WHERE receiver IS NOT NULL").fetchone()[0]
        qty=db.execute("SELECT COALESCE(SUM(qty),0) FROM transfers").fetchone()[0]
        plant_counts=dict(db.execute("SELECT source,COUNT(*) FROM transfers GROUP BY source").fetchall())
    plant_cards="".join(f'<div class="plant"><span>{p}</span><strong>{plant_counts.get(p,0)}</strong><small>dispatches</small></div>' for p in PLANTS)
    table=""
    for r in rows:
        if r[8] is None:
            action=f'<form class="receive-form" method="post" action="/receive"><input type="hidden" name="id" value="{r[0]}"><input name="receiver" placeholder="Receiver name" required><button class="small-button">Confirm receipt</button></form>'
            status='<span class="status transit">In transit</span>'
        else:
            action=f'<span>{esc(r[8])}</span><small>{esc(r[9])}</small>'
            status='<span class="status received">Received</span>'
        table+=f'<tr><td>TR-{r[0]:04d}</td><td>{esc(r[1])}</td><td>{esc(r[2])}</td><td>{r[3]}</td><td>{esc(r[4])} → {esc(r[5])}</td><td>{esc(r[6])}</td><td>{esc(r[7])}</td><td>{status}</td><td>{action}</td></tr>'
    if not table: table='<tr><td colspan="9" class="empty">No transfers yet. Record a dispatch to get started.</td></tr>'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SFG Transfer Register</title>
<style>*{{box-sizing:border-box}}body{{font:14px Arial,sans-serif;background:#f5f6f8;color:#202733;margin:0}}header{{background:#172b4d;color:white;padding:19px 30px}}header .brand{{font-size:19px;font-weight:700}}header small{{display:block;color:#c8d4e5;margin-top:5px}}main{{max-width:1250px;margin:28px auto;padding:0 22px}}h1{{font-size:23px;margin:0 0 5px}}.sub{{color:#687386;margin-bottom:22px}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px}}.card,.panel{{background:white;border:1px solid #e2e6ec;border-radius:8px}}.card{{padding:17px 18px}}.card label{{display:block;color:#687386;font-size:12px;margin-bottom:10px}}.card strong{{font-size:27px}}.card small{{display:block;color:#687386;margin-top:5px}}.panel{{padding:20px;margin-bottom:20px}}h2{{font-size:17px;margin:0 0 16px}}.grid-form{{display:grid;grid-template-columns:repeat(4,minmax(130px,1fr));gap:12px;align-items:end}}.field label{{display:block;font-size:12px;color:#596579;margin:0 0 6px}}input,select{{width:100%;padding:9px;border:1px solid #ccd3dd;border-radius:5px;background:white;font:13px Arial}}button{{background:#2459a6;color:white;border:0;border-radius:5px;padding:10px 15px;cursor:pointer;font-weight:600}}button:hover{{background:#194781}}.plant-row{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}.plant{{border:1px solid #e5e8ed;border-radius:6px;padding:12px 14px}}.plant span{{color:#596579}}.plant strong{{float:right;font-size:19px}}.plant small{{display:block;color:#8992a0;margin-top:8px}}.table-wrap{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;min-width:1000px}}th{{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:#6d7787;background:#f7f8fa}}th,td{{padding:11px 9px;border-bottom:1px solid #e8ebef;text-align:left;vertical-align:middle}}td{{font-size:12px}}.status{{padding:4px 7px;border-radius:12px;font-size:11px;white-space:nowrap}}.transit{{background:#fff2d9;color:#805500}}.received{{background:#e5f5eb;color:#17683a}}.receive-form{{display:flex;gap:6px;min-width:210px}}.receive-form input{{min-width:100px;padding:7px}}.small-button{{font-size:11px;padding:7px 8px;white-space:nowrap}}td small{{display:block;color:#87909e;margin-top:4px}}.empty{{text-align:center;color:#788394;padding:28px}}footer{{color:#8a93a0;font-size:11px;padding:4px 0 25px}}@media(max-width:850px){{.cards{{grid-template-columns:repeat(2,1fr)}}.grid-form{{grid-template-columns:repeat(2,1fr)}}}}@media(max-width:520px){{main{{padding:0 12px}}header{{padding:17px}}.grid-form{{grid-template-columns:1fr}}}}</style></head><body>
<header><div class="brand">SFG Transfer Register</div><small>Inter-plant movement tracking</small></header><main><h1>Dashboard</h1><div class="sub">Overview of semi-finished goods moving between plants.</div>
<section class="cards"><div class="card"><label>Total transfers</label><strong>{total}</strong><small>All dispatch records</small></div><div class="card"><label>In transit</label><strong>{transit}</strong><small>Awaiting receipt confirmation</small></div><div class="card"><label>Received</label><strong>{received}</strong><small>Receipt recorded</small></div><div class="card"><label>Units dispatched</label><strong>{qty}</strong><small>Total quantity across transfers</small></div></section>
<section class="panel"><h2>Dispatches by sending plant</h2><div class="plant-row">{plant_cards}</div></section>
<section class="panel"><h2>Log a new dispatch</h2><form method="post" action="/send" class="grid-form"><div class="field"><label>Parent job order</label><select name="job_order" required>{job_options}</select></div><div class="field"><label>SFG / part name</label><input name="sfg" placeholder="e.g. Header assembly" required></div><div class="field"><label>Quantity</label><input type="number" name="qty" min="1" value="1" required></div><div class="field"><label>Sending plant</label><select name="source" required>{plant_options}</select></div><div class="field"><label>Receiving plant</label><select name="destination" required>{plant_options}</select></div><div class="field"><label>Sent by</label><input name="sender" placeholder="Employee name" required></div><div><button type="submit">Save dispatch</button></div></form></section>
<section class="panel"><h2>Transfer register</h2><div class="table-wrap"><table><thead><tr><th>Transfer ID</th><th>Job order</th><th>SFG</th><th>Qty</th><th>Plant movement</th><th>Sent by</th><th>Sent at</th><th>Status</th><th>Receipt details</th></tr></thead><tbody>{table}</tbody></table></div></section><footer>Prototype application · Records are stored locally in transfers.db · Sample job orders are loaded from job_orders.json</footer></main></body></html>'''
class App(BaseHTTPRequestHandler):
    def send_page(self,status=200):
        body=page().encode("utf-8"); self.send_response(status); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def form(self):
        size=int(self.headers.get("Content-Length","0")); return {k:v[0] for k,v in parse_qs(self.rfile.read(size).decode()).items()}
    def do_GET(self): self.send_page()
    def do_POST(self):
        data=self.form(); now=datetime.now().isoformat(timespec="seconds")
        if self.path=="/send":
            try:
                q=int(data["qty"])
                if q<1 or data["job_order"] not in {j["job_order"] for j in jobs()}: self.send_page(400); return
                with connect() as db: db.execute("INSERT INTO transfers (job_order,sfg,qty,source,destination,sender,sent_at) VALUES (?,?,?,?,?,?,?)",(data["job_order"],data["sfg"],q,data["source"],data["destination"],data["sender"],now))
            except (KeyError,ValueError): self.send_page(400); return
        elif self.path=="/receive":
            with connect() as db: db.execute("UPDATE transfers SET receiver=?,received_at=? WHERE id=? AND receiver IS NOT NULL",(data.get("receiver","").strip(),now,data.get("id","")))
        self.send_response(303); self.send_header("Location","/"); self.end_headers()
if __name__=="__main__":
    setup(); print("Open http://127.0.0.1:8000"); HTTPServer(("127.0.0.1",8000),App).serve_forever()
