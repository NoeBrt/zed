from pathlib import Path
import os, subprocess, json, sys
base=Path(sys.argv[1] if len(sys.argv)>1 else 'northstar-demo').resolve()
assert not base.exists(), 'Demo already exists; preserve captured state'
base.mkdir(parents=True)
(base/'README.md').write_text('''# Northstar — multi-repository Git demo\n\nA fictional SaaS product with three independent repositories.\n\n- `saas/backend`: invoice API and pagination\n- `saas/frontend`: invoice dashboard\n- `data-pipeline`: nightly invoice ingestion and deduplication\n\nAll repositories, authors, commits and data in this workspace are fictional.\n''')
(base/'.zed').mkdir()
(base/'.zed/settings.json').write_text(json.dumps({'file_scan_depth':0,'git':{'auto_fetch':{'enabled':False}}},indent=2)+'\n')
repos={
'saas/backend':{
 'branch':'feat/invoice-pagination','subject':'Add cursor pagination to invoice API',
 'files':{
  'README.md':'# Northstar Invoice API\n\nFictional demo backend for a SaaS billing product.\n',
  'api/routes/invoices.py':'from api.schemas.invoice import Invoice\n\ndef list_invoices(limit: int = 25):\n    return Invoice.query().limit(limit).all()\n',
  'api/schemas/invoice.py':'from dataclasses import dataclass\n\n@dataclass\nclass Invoice:\n    id: str\n    customer_id: str\n    amount_cents: int\n    status: str = "draft"\n',
  'api/legacy_export.py':'def export_invoices(invoices):\n    return [{"id": invoice.id} for invoice in invoices]\n',
  'tests/test_invoices.py':'def test_invoice_status_defaults_to_draft():\n    assert {"status": "draft"}["status"] == "draft"\n'},
 'changes':{
  'api/routes/invoices.py':'from api.schemas.invoice import Invoice\nfrom api.schemas.pagination import Page\n\ndef list_invoices(limit: int = 50, cursor: str | None = None):\n    invoices = Invoice.query().after(cursor).limit(limit + 1).all()\n    return Page.from_records(invoices, limit=limit)\n',
  'tests/test_invoices.py':'def test_invoice_status_defaults_to_draft():\n    assert {"status": "draft"}["status"] == "draft"\n\ndef test_invoice_page_has_next_cursor():\n    page = {"items": [{"id": "inv_demo_002"}], "next_cursor": "inv_demo_002"}\n    assert page["next_cursor"] == page["items"][-1]["id"]\n',
  'api/schemas/pagination.py':'from dataclasses import dataclass\n\n@dataclass\nclass Page:\n    items: list\n    next_cursor: str | None = None\n'},
 'delete':['api/legacy_export.py'],'stage':['api/routes/invoices.py']},
'saas/frontend':{
 'branch':'feat/billing-dashboard','subject':'Build invoice overview dashboard',
 'files':{
  'README.md':'# Northstar Billing Dashboard\n\nFictional SaaS frontend for the multi-repository demo.\n',
  'src/components/InvoiceTable.tsx':'type Invoice = { id: string; customer: string; total: string };\n\nexport function InvoiceTable({ invoices }: { invoices: Invoice[] }) {\n  return <table><tbody>{invoices.map(invoice => (\n    <tr key={invoice.id}><td>{invoice.customer}</td><td>{invoice.total}</td></tr>\n  ))}</tbody></table>;\n}\n',
  'src/styles/invoices.css':'.invoice-table {\n  width: 100%;\n  border-collapse: collapse;\n}\n',
  'src/lib/api.ts':'export const API_BASE = "/api/v1";\n'},
 'changes':{
  'src/components/InvoiceTable.tsx':'import { Pagination } from "./Pagination";\n\ntype Invoice = { id: string; customer: string; total: string };\n\nexport function InvoiceTable({ invoices }: { invoices: Invoice[] }) {\n  return <section className="invoice-table">\n    <table><tbody>{invoices.map(invoice => (\n      <tr key={invoice.id}><td>{invoice.customer}</td><td>{invoice.total}</td></tr>\n    ))}</tbody></table>\n    <Pagination hasNextPage={invoices.length === 50} />\n  </section>;\n}\n',
  'src/styles/invoices.css':'.invoice-table {\n  width: 100%;\n  border-collapse: collapse;\n  border: 1px solid var(--border-muted);\n  padding: 1rem;\n}\n',
  'src/components/Pagination.tsx':'export function Pagination({ hasNextPage }: { hasNextPage: boolean }) {\n  return <nav aria-label="Invoice pages">\n    <button disabled={!hasNextPage}>Next page</button>\n  </nav>;\n}\n'},
 'delete':[],'stage':['src/components/InvoiceTable.tsx']},
'data-pipeline':{
 'branch':'fix/invoice-deduplication','subject':'Schedule nightly invoice ingestion',
 'files':{
  'README.md':'# Northstar Data Pipeline\n\nFictional nightly invoice ingestion pipeline.\n',
  'pipelines/invoices.py':'def ingest_invoices(frame):\n    return frame.drop_duplicates()\n',
  'config/schedule.yaml':'pipeline: invoice-ingestion\nschedule: "0 2 * * *"\nsource: demo-invoices\n'},
 'changes':{
  'pipelines/invoices.py':'def ingest_invoices(frame):\n    return (frame\n        .sort_values("updated_at")\n        .drop_duplicates(subset=["invoice_id"], keep="last")\n    )\n',
  'tests/test_deduplication.py':'def test_deduplication_keeps_latest_invoice():\n    rows = [{"invoice_id": "inv_demo_001", "version": 1},\n            {"invoice_id": "inv_demo_001", "version": 2}]\n    latest = {row["invoice_id"]: row for row in rows}\n    assert latest["inv_demo_001"]["version"] == 2\n'},
 'delete':[],'stage':['pipelines/invoices.py']}}
manifest=[]
for ix,(relative,spec) in enumerate(repos.items()):
 path=base/relative;path.mkdir(parents=True)
 def write(files):
  for name,content in files.items():
   p=path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
 def git(*args):
  return subprocess.check_output(['git','-c','core.hooksPath=/dev/null','-C',str(path),*args],text=True).strip()
 def commit(message,step):
  env=os.environ.copy();env.update(GIT_AUTHOR_NAME='Alex Morgan' if step%2 else 'Sam Rivera',GIT_AUTHOR_EMAIL='alex@example.test' if step%2 else 'sam@example.test',GIT_COMMITTER_NAME='Northstar Demo',GIT_COMMITTER_EMAIL='demo@example.test',GIT_AUTHOR_DATE=f'2026-11-0{step+1}T10:{ix}0:00+01:00',GIT_COMMITTER_DATE=f'2026-11-0{step+1}T10:{ix}0:00+01:00')
  subprocess.run(['git','-c','core.hooksPath=/dev/null','-c','commit.gpgSign=false','-C',str(path),'commit','-m',message],env=env,check=True,stdout=subprocess.DEVNULL)
 git('init','-b','main');write({'README.md':spec['files']['README.md']});git('add','.');commit('Initialize fictional Northstar '+path.name,0)
 write(spec['files']);git('add','.');commit('Add '+('invoice API and schemas' if ix==0 else 'billing UI components' if ix==1 else 'invoice ingestion pipeline'),1)
 git('switch','-c',spec['branch'])
 marker=path/'CHANGELOG.md';marker.write_text('# Demo changelog\n\n- '+spec['subject']+'\n');git('add','CHANGELOG.md');commit(spec['subject'],2)
 remote=base.parent/(base.name+'-remotes')/(path.name+'.git');remote.parent.mkdir(exist_ok=True)
 subprocess.run(['git','clone','--bare',str(path),str(remote)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 git('remote','add','origin',str(remote));git('fetch','origin');git('branch','--set-upstream-to','origin/'+spec['branch'])
 write(spec['changes'])
 for name in spec['delete']:(path/name).unlink()
 git('add',*spec['stage'])
 status=git('status','--porcelain');assert len(status.splitlines())==[4,3,2][ix],status
 manifest.append({'path':str(path),'branch':spec['branch'],'changes':len(status.splitlines()),'commits':int(git('rev-list','--count','HEAD'))})
assert sum(row['changes'] for row in manifest)==9
(base.parent/(base.name+'-manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n')
print(base);print(json.dumps(manifest,indent=2))
