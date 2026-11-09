import React, { useEffect, useState } from "react";
import api from "../api/api";

function Inventario() {
  const [inventario, setInventario] = useState([]);
  const [movimientos, setMovimientos] = useState([]);
  const [alertasStock, setAlertasStock] = useState([]);
  const [lotesVencidos, setLotesVencidos] = useState([]);
  const [lotesPorVencer, setLotesPorVencer] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [tab, setTab] = useState("inventario");
  const [mostrarAjuste, setMostrarAjuste] = useState(false);
  const [ajuste, setAjuste] = useState({ id_producto: "", cantidad: 0, descripcion: "" });

  const [stockFisico, setStockFisico] = useState({});
  const [guardandoConteo, setGuardandoConteo] = useState(false);
  const [resultadoConteo, setResultadoConteo] = useState(null);

  const cargar = async () => {
    try {
      const [r1, r2, r3, r4] = await Promise.all([
        api.get("/inventario/"),
        api.get("/inventario/movimientos/"),
        api.get("/inventario/alertas/stock"),
        api.get("/inventario/alertas/vencimiento"),
      ]);
      setInventario(r1.data); setMovimientos(r2.data);
      setAlertasStock(r3.data);
      setLotesVencidos(r4.data.vencidos); setLotesPorVencer(r4.data.por_vencer);

      const valoresIniciales = {};
      r1.data.forEach((inv) => { valoresIniciales[inv.id_producto] = inv.stock_actual; });
      setStockFisico(valoresIniciales);
    } catch { setError("Error al cargar inventario"); }
  };

  useEffect(() => { cargar(); }, []);

  const guardarConteo = async () => {
    setError(""); setGuardandoConteo(true);
    try {
      const detalles = inventario.map((inv) => {
        const valor = stockFisico[inv.id_producto];
        // "" (input vacío mientras el staff retipea el número) no debe
        // enviarse como 0 -- Number("") es 0, no "sin cambio". Con el campo
        // vacío se usa el stock del sistema, igual que el valor por defecto.
        const stockFisicoFinal = valor === "" || valor === undefined || valor === null
          ? inv.stock_actual
          : Number(valor);
        return { id_producto: inv.id_producto, stock_fisico: stockFisicoFinal };
      });
      const res = await api.post("/inventario/conteos", { detalles });
      setResultadoConteo(res.data);
      await cargar();
    } catch (err) {
      setError(err.response?.data?.detail || "Error al guardar el conteo");
    } finally {
      setGuardandoConteo(false);
    }
  };

  const aplicarAjuste = async (e) => {
    e.preventDefault(); setError("");
    if (!ajuste.id_producto) { setError("Seleccione un producto"); return; }
    if (Number(ajuste.cantidad) === 0) { setError("La cantidad no puede ser cero"); return; }
    try {
      await api.post("/inventario/ajustes", {
        id_producto: Number(ajuste.id_producto),
        cantidad: Number(ajuste.cantidad),
        descripcion: ajuste.descripcion || null,
      });
      setMostrarAjuste(false); setAjuste({ id_producto: "", cantidad: 0, descripcion: "" });
      await cargar();
    } catch (err) { setError(err.response?.data?.detail || "Error al ajustar"); }
  };

  const filtrados = inventario.filter((inv) => {
    const t = busqueda.toLowerCase();
    return String(inv.nombre_producto || "").toLowerCase().includes(t);
  });

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">COMERCIO</span>
          <h1>Inventario</h1>
          <p>Control de stock, movimientos, alertas de bajo stock y vencimientos.</p>
        </div>
        <button className="btn-primary" onClick={() => setMostrarAjuste(true)}>+ Ajuste manual</button>
      </section>

      <section className="stats-grid">
        <div className="stat-card"><span>Productos</span><strong>{inventario.length}</strong></div>
        <div className="stat-card"><span>Bajo stock</span><strong style={{ color: alertasStock.length > 0 ? "var(--danger)" : undefined }}>{alertasStock.length}</strong></div>
        <div className="stat-card"><span>Por vencer</span><strong style={{ color: lotesPorVencer.length > 0 ? "var(--warning)" : undefined }}>{lotesPorVencer.length}</strong></div>
        <div className="stat-card"><span>Vencidos</span><strong style={{ color: lotesVencidos.length > 0 ? "var(--danger)" : undefined }}>{lotesVencidos.length}</strong></div>
      </section>

      <div className="tabs-container" style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        {["inventario", "movimientos", "alertas", "conteo"].map((t) => (
          <button key={t} className={tab === t ? "btn-primary" : "btn-secondary"} onClick={() => setTab(t)}>
            {t === "inventario" ? "Inventario" : t === "movimientos" ? "Movimientos" : t === "alertas" ? "Alertas" : "Conteo físico"}
          </button>
        ))}
      </div>

      {error && <p className="error-message">{error}</p>}

      {mostrarAjuste && (
        <form onSubmit={aplicarAjuste} className="form-card">
          <div className="card-header"><div><h2>Ajuste de inventario</h2></div></div>
          <div className="form-grid">
            <div className="form-field field-large">
              <label>Producto</label>
              <select value={ajuste.id_producto} onChange={(e) => setAjuste({ ...ajuste, id_producto: e.target.value })}>
                <option value="">Seleccionar</option>
                {inventario.map((inv) => (
                  <option key={inv.id_producto} value={inv.id_producto}>{inv.nombre_producto} (Stock: {inv.stock_actual})</option>
                ))}
              </select>
            </div>
            <div className="form-field">
              <label>Cantidad (+ o -)</label>
              <input type="number" value={ajuste.cantidad} onChange={(e) => setAjuste({ ...ajuste, cantidad: e.target.value })} />
            </div>
            <div className="form-field field-large">
              <label>Motivo</label>
              <input value={ajuste.descripcion} onChange={(e) => setAjuste({ ...ajuste, descripcion: e.target.value })} placeholder="Motivo del ajuste" />
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn-primary">Aplicar</button>
            <button type="button" className="btn-secondary" onClick={() => setMostrarAjuste(false)}>Cancelar</button>
          </div>
        </form>
      )}

      {tab === "inventario" && (
        <section className="table-card">
          <div className="card-header">
            <div><h2>Stock actual</h2></div>
            <input className="search-input" placeholder="Buscar..." value={busqueda} onChange={(e) => setBusqueda(e.target.value)} />
          </div>
          {filtrados.length === 0 ? <p className="empty-message">Sin datos de inventario.</p> : (
            <div className="cards-grid">
              {filtrados.map((inv) => (
                <div key={inv.id_inventario} className="card item-card">
                  <div className="item-card-top">
                    <span className={inv.stock_actual <= inv.stock_minimo ? "badge badge-danger" : "badge badge-success"}>
                      {inv.stock_actual <= inv.stock_minimo ? "BAJO STOCK" : "OK"}
                    </span>
                  </div>
                  <h3>{inv.nombre_producto}</h3>
                  <div className="mini-stats-grid">
                    <div><strong>{inv.stock_actual}</strong><span>Stock actual</span></div>
                    <div><strong>{inv.stock_minimo}</strong><span>Mínimo</span></div>
                    <div><strong>S/ {inv.ultimo_costo || 0}</strong><span>Último costo</span></div>
                    <div><strong>{inv.unidad_medida}</strong><span>Unidad</span></div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {tab === "movimientos" && (
        <section className="table-card">
          <div className="card-header"><div><h2>Movimientos de stock</h2></div></div>
          {movimientos.length === 0 ? <p className="empty-message">Sin movimientos registrados.</p> : (
            <div className="cards-grid">
              {movimientos.map((m) => (
                <div key={m.id_movimiento} className="card item-card">
                  <div className="item-card-top">
                    <span className="badge">{m.tipo_movimiento}</span>
                    <span className="badge">#{m.id_movimiento}</span>
                  </div>
                  <h3>{m.nombre_producto}</h3>
                  <div className="mini-stats-grid">
                    <div><strong>{m.cantidad}</strong><span>Cantidad</span></div>
                    {m.costo_unitario && <div><strong>S/ {m.costo_unitario}</strong><span>Costo</span></div>}
                  </div>
                  {m.descripcion && <p className="item-description">{m.descripcion}</p>}
                  <p className="item-description">{new Date(m.fecha_movimiento).toLocaleString()}</p>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {tab === "alertas" && (
        <section className="table-card">
          <div className="card-header"><div><h2>Alertas</h2></div></div>
          {alertasStock.length === 0 && lotesVencidos.length === 0 && lotesPorVencer.length === 0 ? <p className="empty-message">No hay alertas activas.</p> : (
            <>
              {alertasStock.length > 0 && (
                <>
                  <h3 style={{ color: "var(--danger)", marginBottom: "0.5rem" }}>Stock bajo</h3>
                  <div className="cards-grid">
                    {alertasStock.map((inv) => (
                      <div key={inv.id_inventario} className="card item-card" style={{ borderLeft: "3px solid var(--danger)" }}>
                        <h3>{inv.nombre_producto}</h3>
                        <div className="mini-stats-grid">
                          <div><strong>{inv.stock_actual}</strong><span>Actual</span></div>
                          <div><strong>{inv.stock_minimo}</strong><span>Mínimo</span></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
              {lotesVencidos.length > 0 && (
                <>
                  <h3 style={{ color: "var(--danger)", margin: "1rem 0 0.5rem" }}>Vencidos</h3>
                  <div className="cards-grid">
                    {lotesVencidos.map((l) => (
                      <div key={l.id_lote} className="card item-card" style={{ borderLeft: "3px solid var(--danger)" }}>
                        <h3>{l.nombre_producto}</h3>
                        <p className="item-description">Lote: {l.numero_lote}</p>
                        <p className="item-description">Vence: {l.fecha_vencimiento}</p>
                        <p className="item-description">Venció hace {Math.abs(l.dias_restantes)} día(s)</p>
                        <p className="item-description">Cantidad: {l.cantidad}</p>
                      </div>
                    ))}
                  </div>
                </>
              )}
              {lotesPorVencer.length > 0 && (
                <>
                  <h3 style={{ color: "var(--warning)", margin: "1rem 0 0.5rem" }}>Próximos a vencer</h3>
                  <div className="cards-grid">
                    {lotesPorVencer.map((l) => (
                      <div key={l.id_lote} className="card item-card" style={{ borderLeft: "3px solid var(--warning)" }}>
                        <h3>{l.nombre_producto}</h3>
                        <p className="item-description">Lote: {l.numero_lote}</p>
                        <p className="item-description">Vence: {l.fecha_vencimiento}</p>
                        <p className="item-description">
                          {l.dias_restantes === 0 ? "Vence hoy" : `Vence en ${l.dias_restantes} día(s)`}
                        </p>
                        <p className="item-description">Cantidad: {l.cantidad}</p>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </>
          )}
        </section>
      )}

      {tab === "conteo" && (
        <section className="table-card">
          <div className="card-header">
            <div>
              <h2>Conteo físico de inventario</h2>
              <p>Ingresa el stock físico contado por producto; el sistema calcula la diferencia y la exactitud (F-16).</p>
            </div>
          </div>

          {inventario.length === 0 ? <p className="empty-message">Sin datos de inventario.</p> : (
            <>
              <table className="table">
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Stock en sistema</th>
                    <th>Stock físico contado</th>
                  </tr>
                </thead>
                <tbody>
                  {inventario.map((inv) => (
                    <tr key={inv.id_producto}>
                      <td>{inv.nombre_producto}</td>
                      <td>{inv.stock_actual}</td>
                      <td>
                        <input
                          type="number"
                          step="0.01"
                          value={stockFisico[inv.id_producto] ?? inv.stock_actual}
                          onChange={(e) => setStockFisico({ ...stockFisico, [inv.id_producto]: e.target.value })}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div className="form-actions">
                <button className="btn-primary" disabled={guardandoConteo} onClick={guardarConteo}>
                  {guardandoConteo ? "Guardando..." : "Guardar conteo"}
                </button>
              </div>
            </>
          )}

          {resultadoConteo && (
            <div className="form-card" style={{ marginTop: "1rem" }}>
              <h3>
                Resultado del conteo #{resultadoConteo.id_conteo} — Exactitud:{" "}
                <strong>{resultadoConteo.exactitud_pct ?? "-"}%</strong>{" "}
                ({resultadoConteo.productos_correctos}/{resultadoConteo.total_productos} productos correctos)
              </h3>
              <table className="table">
                <thead>
                  <tr>
                    <th>Producto</th>
                    <th>Stock sistema</th>
                    <th>Stock físico</th>
                    <th>Diferencia</th>
                  </tr>
                </thead>
                <tbody>
                  {resultadoConteo.detalles.map((d) => (
                    <tr key={d.id_detalle_conteo}>
                      <td>{d.nombre_producto}</td>
                      <td>{d.stock_sistema}</td>
                      <td>{d.stock_fisico}</td>
                      <td style={{ color: d.diferencia !== 0 ? "var(--danger)" : "var(--success)" }}>
                        {d.diferencia}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

export default Inventario;
