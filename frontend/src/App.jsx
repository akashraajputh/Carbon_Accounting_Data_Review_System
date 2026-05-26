import { useEffect, useState } from "react";

// Default to the deployed Render backend if VITE_API_BASE is not set at build time
const API_BASE = import.meta.env.VITE_API_BASE || "https://carbon-accounting-data-review-system-9.onrender.com/api";
const SOURCES = [
  { slug: "sap", label: "SAP fuel & procurement" },
  { slug: "utility", label: "Utility electricity" },
  { slug: "travel", label: "Corporate travel" },
];

function App() {
  const [tenantSlug, setTenantSlug] = useState("acme-corp");
  const [tenants, setTenants] = useState([]);
  const [records, setRecords] = useState([]);
  const [uploadStatus, setUploadStatus] = useState("");
  const [statusFilter, setStatusFilter] = useState("pending");
  const [flaggedOnly, setFlaggedOnly] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/tenants/`)
      .then((resp) => resp.json())
      .then((data) => {
        const tenantList = Array.isArray(data) ? data : data.results || [];
        setTenants(tenantList);
        if (tenantList.length && !tenantList.some((t) => t.slug === tenantSlug)) {
          setTenantSlug(tenantList[0].slug);
        }
      })
      .catch(() => setTenants([]));
  }, []);

  useEffect(() => {
    loadRecords();
  }, [tenantSlug, statusFilter, flaggedOnly]);

  function loadRecords() {
    setLoading(true);
    const params = new URLSearchParams({ tenant_slug: tenantSlug });
    if (statusFilter) params.set("status", statusFilter);
    if (flaggedOnly) params.set("flagged", "true");
    fetch(`${API_BASE}/records/?${params.toString()}`)
      .then((resp) => resp.json())
      .then((data) => {
        setRecords(data.results || data);
      })
      .finally(() => setLoading(false));
  }

  function handleUpload(e, sourceType) {
    e.preventDefault();
    const fileInput = e.target.querySelector("input[type=file]");
    if (!fileInput.files.length) {
      return setUploadStatus("Select a file before uploading.");
    }
    const form = new FormData();
    form.append("tenant_slug", tenantSlug);
    form.append("source_type", sourceType);
    form.append("file", fileInput.files[0]);
    setUploadStatus("Uploading...");
    fetch(`${API_BASE}/import/`, {
      method: "POST",
      body: form,
    })
      .then(async (resp) => {
        const text = await resp.text();
        let json = null;
        try {
          json = JSON.parse(text);
        } catch (parseError) {
          const message = text || "Upload failed";
          throw new Error(message);
        }
        if (!resp.ok) throw new Error(json.detail || text || "Upload failed");
        setUploadStatus(`Imported ${json.inserted} rows from ${sourceType}.`);
        loadRecords();
      })
      .catch((err) => setUploadStatus(err.message));
  }

  function updateRecord(recordId, action) {
    fetch(`${API_BASE}/records/${recordId}/action/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action }),
    })
      .then((resp) => resp.json())
      .then(() => loadRecords())
      .catch(() => {});
  }

  return (
    <div className="app-shell">
      <header>
        <h1>Carbon Intake Review</h1>
        <p>Upload realistic SAP, utility, and travel exports, then approve records for audit.</p>
      </header>

      <section className="controls">
        <label>
          Tenant
          <select value={tenantSlug} onChange={(e) => setTenantSlug(e.target.value)}>
            {tenants.map((tenant) => (
              <option key={tenant.slug} value={tenant.slug}>
                {tenant.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Status
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="">All</option>
          </select>
        </label>
        <label className="checkbox-label">
          <input type="checkbox" checked={flaggedOnly} onChange={(e) => setFlaggedOnly(e.target.checked)} />
          Only suspicious
        </label>
      </section>

      <section className="upload-panel">
        <h2>Upload source data</h2>
        {SOURCES.map((source) => (
          <form key={source.slug} onSubmit={(e) => handleUpload(e, source.slug)}>
            <strong>{source.label}</strong>
            <input type="file" accept=".csv" />
            <button type="submit">Upload</button>
          </form>
        ))}
        <div className="upload-status">{uploadStatus}</div>
      </section>

      <section className="review-panel">
        <h2>Review queue</h2>
        {loading ? (
          <p>Loading records…</p>
        ) : (
          <>
            <div className="summary">
              <span>{records.length} records</span>
              <span>{records.filter((r) => r.flagged_reasons.length).length} suspicious</span>
            </div>
            <div className="records-table">
              <div className="table-header">
                <div>Source</div>
                <div>Date</div>
                <div>Category</div>
                <div>Qty</div>
                <div>Emissions</div>
                <div>Status</div>
                <div>Actions</div>
              </div>
              {records.map((record) => (
                <div key={record.id} className={`table-row ${record.flagged_reasons.length ? "flagged" : ""}`}>
                  <div>{record.source_name}</div>
                  <div>{record.observation_date || "—"}</div>
                  <div>{record.category}</div>
                  <div>{record.normalized_quantity || record.quantity_value || "—"} {record.normalized_unit || record.quantity_unit}</div>
                  <div>{record.emission_kg_co2e?.toFixed(1) || "—"} kg</div>
                  <div>{record.status}</div>
                  <div className="actions">
                    <button type="button" onClick={() => updateRecord(record.id, "approve")}>Approve</button>
                    <button type="button" onClick={() => updateRecord(record.id, "reject")}>Reject</button>
                  </div>
                  {record.flagged_reasons.length ? <div className="flagged-note">{record.flagged_reasons.join(", ")}</div> : null}
                </div>
              ))}
            </div>
          </>
        )}
      </section>
    </div>
  );
}

export default App;
