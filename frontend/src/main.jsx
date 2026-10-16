import { StrictMode, useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { AlertTriangle, ArrowDownRight, ArrowUpRight, Box, FlaskConical, LayoutGrid, MapPin, Package, Pencil, Plus, RefreshCw, Search, Trash2, X } from 'lucide-react';
import { request } from './api';
import './styles.css';

const emptyForm = { name: '', category: '', quantity: 1, low_stock_threshold: 2, location: '' };

function EquipmentForm({ record, onClose, onSaved }) {
  const dialog = useRef(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => { dialog.current.showModal(); }, []);

  async function save(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const payload = Object.fromEntries(form);
    payload.quantity = Number(payload.quantity);
    payload.low_stock_threshold = Number(payload.low_stock_threshold);
    setSaving(true);
    setError('');
    try {
      await request(record.id ? `/api/equipment/${record.id}` : '/api/equipment', {
        method: record.id ? 'PUT' : 'POST', body: JSON.stringify(payload),
      });
      onSaved(record.id ? 'Equipment updated.' : 'Equipment added to inventory.');
      onClose();
    } catch (err) { setError(err.message); }
    finally { setSaving(false); }
  }

  return <dialog ref={dialog} onCancel={(event) => { if (saving) event.preventDefault(); else onClose(); }} aria-labelledby="form-title">
    <form onSubmit={save}>
      <div className="dialog-heading"><div><p className="eyebrow">INVENTORY RECORD</p><h2 id="form-title">{record.id ? 'Edit equipment' : 'Add equipment'}</h2></div><button type="button" className="icon-button" aria-label="Close form" onClick={onClose} disabled={saving}><X size={20} /></button></div>
      <label>Equipment name<input name="name" autoFocus required maxLength={120} defaultValue={record.name} placeholder="e.g. Digital microscope" /></label>
      <label>Category<input name="category" required list="categories" maxLength={60} defaultValue={record.category} placeholder="Choose or enter a category" /><datalist id="categories">{['Microscopy', 'Glassware', 'Measurement', 'Safety', 'Consumables'].map(value => <option key={value} value={value} />)}</datalist></label>
      <div className="form-row"><label>Quantity<input name="quantity" required type="number" min="0" max="1000000" step="1" defaultValue={record.quantity} /></label><label>Low-stock threshold<input name="low_stock_threshold" required type="number" min="0" max="1000000" step="1" defaultValue={record.low_stock_threshold} /></label></div>
      <label>Storage location<input name="location" required maxLength={120} defaultValue={record.location} placeholder="e.g. Lab A / Shelf 3" /></label>
      {error && <p className="form-error" role="alert">{error}</p>}
      <div className="dialog-actions"><button type="button" className="secondary" onClick={onClose} disabled={saving}>Cancel</button><button className="primary" disabled={saving}>{saving ? 'Saving…' : record.id ? 'Save changes' : 'Add equipment'}</button></div>
    </form>
  </dialog>;
}

function DeleteDialog({ record, onClose, onDeleted }) {
  const dialog = useRef(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => { dialog.current.showModal(); }, []);
  async function remove() {
    setBusy(true);
    try { await request(`/api/equipment/${record.id}`, { method: 'DELETE' }); onDeleted('Equipment removed.'); onClose(); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  return <dialog ref={dialog} onCancel={(event) => { if (busy) event.preventDefault(); else onClose(); }} aria-labelledby="delete-title"><div className="delete-content"><h2 id="delete-title">Remove equipment?</h2><p>This removes <strong>{record.name}</strong> from the inventory. You cannot undo this action.</p>{error && <p role="alert" className="form-error">{error}</p>}<div className="dialog-actions"><button className="secondary" onClick={onClose} disabled={busy}>Keep record</button><button className="danger" onClick={remove} disabled={busy}>{busy ? 'Removing…' : 'Remove equipment'}</button></div></div></dialog>;
}

function App() {
  const [items, setItems] = useState([]);
  const [summary, setSummary] = useState({ records: 0, units: 0, low_stock: 0, categories: [] });
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [lowStock, setLowStock] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [editing, setEditing] = useState(null);
  const [deleting, setDeleting] = useState(null);
  const [revision, setRevision] = useState(0);
  const [version, setVersion] = useState('');
  const [updated, setUpdated] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      setLoading(true);
      setError('');
      try {
        const params = new URLSearchParams({ q: search, category, low_stock: String(lowStock) });
        const [records, totals] = await Promise.all([
          request(`/api/equipment?${params}`, { signal: controller.signal }),
          request('/api/summary', { signal: controller.signal }),
        ]);
        setItems(records); setSummary(totals); setUpdated(new Date());
      } catch (err) { if (err.name !== 'AbortError') setError(err.message); }
      finally { if (!controller.signal.aborted) setLoading(false); }
    }, 200);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [search, category, lowStock, revision]);

  useEffect(() => { request('/health').then(data => setVersion(data.version)).catch(() => {}); }, []);
  function saved(message) { setNotice(message); setRevision(value => value + 1); }
  function resetFilters() { setSearch(''); setCategory(''); setLowStock(false); }

  return <div className="app-shell">
    <aside className="sidebar">
      <a className="brand" href="/" aria-label="LabShelf home"><span className="brand-icon"><FlaskConical size={25} /></span><span>LabShelf<small>LABORATORY INVENTORY</small></span></a>
      <p className="nav-caption">WORKSPACE</p>
      <button className={`nav-item ${!lowStock ? 'active' : ''}`} onClick={() => { resetFilters(); }}><LayoutGrid size={18} />Equipment<span>{summary.records}</span></button>
      <button className={`nav-item ${lowStock ? 'active' : ''}`} onClick={() => setLowStock(true)}><AlertTriangle size={18} />Low stock<span>{summary.low_stock}</span></button>
      <div className="sidebar-note"><span className="small-icon"><FlaskConical size={20} /></span><h3>A place for every piece.</h3><p>Keep the lab organised, one shelf at a time.</p></div>
      <div className="sidebar-footer"><span className="avatar">LS</span><div>Laboratory workspace<small>DevOps capstone</small></div></div>
    </aside>
    <main>
      <div className="topbar"><span>Workspace <span className="slash">/</span> <strong>Equipment</strong></span><span className="workspace-tag">LAB OPERATIONS</span></div>
      <div className="page-content">
        <header className="page-header"><div><p className="eyebrow">YOUR LAB, IN ORDER</p><h1>Equipment inventory<span>.</span></h1><p>Know what you have. Find what you need.</p></div><button className="primary" onClick={() => { setNotice(''); setEditing(emptyForm); }}><Plus size={18} />Add equipment</button></header>
        <section className="stats" aria-label="Inventory overview">
          <Stat label="Equipment records" value={summary.records} Icon={Box} description="Distinct inventory entries" />
          <Stat label="Total units" value={summary.units} Icon={Package} description="Across all storage locations" />
          <Stat label="Low-stock records" value={summary.low_stock} Icon={ArrowDownRight} description="At or below their threshold" warning />
          <Stat label="Categories" value={summary.categories.length} Icon={LayoutGrid} description="Equipment groups in your lab" />
        </section>
        <section className="inventory-panel" aria-labelledby="inventory-title">
          <div className="panel-title"><div><h2 id="inventory-title">{lowStock ? 'Low-stock equipment' : 'All equipment'}<span className="count">{items.length}</span></h2><p>A clear view of everything on your shelves.</p></div><button className="icon-button refresh" aria-label="Refresh inventory" onClick={() => setRevision(value => value + 1)} disabled={loading}><RefreshCw size={17} /></button></div>
          <div className="toolbar"><div className="search-field"><Search size={18} /><input aria-label="Search equipment or location" placeholder="Search equipment or location…" value={search} onChange={event => setSearch(event.target.value)} /></div><select aria-label="Filter category" value={category} onChange={event => setCategory(event.target.value)}><option value="">All categories</option>{summary.categories.map(value => <option key={value}>{value}</option>)}</select><button className={`filter-button ${lowStock ? 'selected' : ''}`} aria-pressed={lowStock} onClick={() => setLowStock(value => !value)}><AlertTriangle size={15} />Low stock</button></div>
          {notice && <div className="notice" role="status">{notice}<button aria-label="Dismiss notification" onClick={() => setNotice('')}><X size={15} /></button></div>}
          {error ? <div className="empty-state" role="alert"><AlertTriangle size={30} /><h3>We couldn’t load the inventory</h3><p>{error}</p><button className="secondary" onClick={() => setRevision(value => value + 1)}>Try again</button></div> : loading ? <div className="empty-state" role="status"><RefreshCw size={26} className="spin" /><p>Loading your inventory…</p></div> : items.length === 0 ? <div className="empty-state"><FlaskConical size={36} /><h3>{summary.records ? 'No matching equipment' : 'Your shelves are ready'}</h3><p>{summary.records ? 'Try a different search or clear your filters.' : 'Add your first piece of equipment to get started.'}</p><button className="secondary" onClick={summary.records ? resetFilters : () => setEditing(emptyForm)}>{summary.records ? 'Clear filters' : 'Add equipment'}</button></div> : <div className="table-scroll"><table><thead><tr><th>EQUIPMENT</th><th>CATEGORY</th><th>QUANTITY</th><th>LOCATION</th><th>STOCK STATUS</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>{items.map(item => {
            const low = item.quantity <= item.low_stock_threshold;
            return <tr key={item.id}><td><div className="equipment-cell"><span className="equipment-icon"><FlaskConical size={21} /></span><div><strong>{item.name}</strong><small>EQ-{String(item.id).padStart(4, '0')}</small></div></div></td><td><span className="category-tag">{item.category}</span></td><td><strong className="quantity">{item.quantity}</strong><span className="unit-label"> units</span></td><td><span className="location"><MapPin size={14} />{item.location}</span></td><td><span className={`stock-badge ${low ? 'low' : ''}`}><i />{item.quantity === 0 ? 'Out of stock' : low ? 'Low stock' : 'In stock'}</span></td><td><div className="row-actions"><button className="icon-button" aria-label={`Edit ${item.name}`} onClick={() => { setNotice(''); setEditing(item); }}><Pencil size={15} /></button><button className="icon-button remove" aria-label={`Remove ${item.name}`} onClick={() => { setNotice(''); setDeleting(item); }}><Trash2 size={15} /></button></div></td></tr>;
          })}</tbody></table></div>}
          <div className="table-footer"><span>{loading ? 'Updating inventory' : `${items.length} record${items.length === 1 ? '' : 's'} shown`}</span><span>{updated ? `Updated ${updated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : 'Waiting for inventory'}</span></div>
        </section>
        <div className="inventory-tip"><span><FlaskConical size={18} /><strong>A little organisation goes a long way.</strong> Set a threshold to spot supplies running low.</span><ArrowUpRight size={17} /></div>
        <footer className="page-footer"><span>LabShelf <span className="footer-dot">·</span> Laboratory equipment inventory</span><span>{version ? `Build ${version === 'dev' ? 'development' : version.slice(0, 7)}` : 'Lab workspace'}</span></footer>
      </div>
    </main>
    {editing && <EquipmentForm record={editing} onClose={() => setEditing(null)} onSaved={saved} />}
    {deleting && <DeleteDialog record={deleting} onClose={() => setDeleting(null)} onDeleted={saved} />}
  </div>;
}

function Stat({ label, value, Icon, description, warning }) {
  return <div className={`stat ${warning ? 'warning' : ''}`}><div className="stat-label">{label}<Icon size={18} /></div><strong>{value.toLocaleString()}</strong><p>{description}</p></div>;
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>);
