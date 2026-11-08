import React, { useCallback, useEffect, useState } from "react";
import api from "../api/api";

const FILTROS = [
  { value: "pendiente", label: "Pendientes" },
  { value: "aprobada", label: "Aprobadas" },
  { value: "aprobada_con_cambios", label: "Aprobadas con cambios" },
  { value: "rechazada", label: "Rechazadas" },
  { value: "todas", label: "Todas" },
];

function RevisionIA() {
  const [clientes, setClientes] = useState([]);
  const [items, setItems] = useState([]);
  const [filtro, setFiltro] = useState("pendiente");
  const [error, setError] = useState("");
  const [procesandoId, setProcesandoId] = useState(null);

  const [editando, setEditando] = useState(null); // { tipo, id, lista: [...], observaciones }
  const [catalogoEjercicios, setCatalogoEjercicios] = useState([]);
  const [catalogoComidas, setCatalogoComidas] = useState([]);

  const obtenerNombreCliente = (id_cliente) => {
    const c = clientes.find((c) => c.id_cliente === id_cliente);
    return c ? `${c.nombres} ${c.apellidos}` : "Cliente no encontrado";
  };

  const cargar = useCallback(async (filtroActual) => {
    try {
      setError("");
      const resClientes = await api.get("/clientes/");
      setClientes(resClientes.data);

      let rutinas;
      let planes;

      if (filtroActual === "pendiente") {
        const [r, p] = await Promise.all([
          api.get("/rutinas/pendientes"),
          api.get("/nutricion/pendientes"),
        ]);
        rutinas = r.data;
        planes = p.data;
      } else {
        const [r, p] = await Promise.all([api.get("/rutinas/"), api.get("/nutricion/")]);
        rutinas = filtroActual === "todas" ? r.data : r.data.filter((x) => x.estado_revision === filtroActual);
        planes = filtroActual === "todas" ? p.data : p.data.filter((x) => x.estado_revision === filtroActual);
      }

      const combinados = [
        ...rutinas.map((r) => ({
          tipo: "rutina",
          id: r.id_rutina,
          id_cliente: r.id_cliente,
          titulo: r.nombre,
          objetivo: r.objetivo,
          estado_revision: r.estado_revision,
          fecha_creacion: r.fecha_creacion,
          editado_antes_revision: r.editado_antes_revision,
          observaciones_revision: r.observaciones_revision,
          origen_ia: r.origen_ia,
        })),
        ...planes.map((p) => ({
          tipo: "plan",
          id: p.id_plan,
          id_cliente: p.id_cliente,
          titulo: `Plan nutricional #${p.id_plan}`,
          objetivo: p.objetivo,
          estado_revision: p.estado_revision,
          fecha_creacion: p.fecha_creacion,
          editado_antes_revision: p.editado_antes_revision,
          observaciones_revision: p.observaciones_revision,
          comidas: p.comidas || [],
          origen_ia: p.origen_ia,
        })),
      ].sort((a, b) => new Date(a.fecha_creacion) - new Date(b.fecha_creacion));

      setItems(combinados);
    } catch (err) {
      console.error(err);
      setError("Error al cargar la bandeja de revisión");
    }
  }, []);

  useEffect(() => {
    cargar(filtro);
  }, [filtro, cargar]);

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    return new Date(fecha).toLocaleString("es-PE");
  };

  const badgeEstado = (estado) => {
    if (estado === "aprobada" || estado === "aprobada_con_cambios") return "badge badge-success";
    if (estado === "rechazada") return "badge badge-danger";
    return "badge";
  };

  const badgeOrigen = (origen) => (origen === "claude" ? "badge badge-success" : "badge");
  const etiquetaOrigen = (origen) => (origen === "claude" ? "Claude" : "Reglas");

  const aprobar = async (item) => {
    try {
      setProcesandoId(`${item.tipo}-${item.id}`);
      setError("");
      const url = item.tipo === "rutina" ? `/rutinas/${item.id}/aprobar` : `/nutricion/${item.id}/aprobar`;
      await api.post(url);
      setEditando(null);
      await cargar(filtro);
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo aprobar");
    } finally {
      setProcesandoId(null);
    }
  };

  const rechazar = async (item) => {
    const motivo = globalThis.prompt("Motivo del rechazo:");
    if (!motivo) return;

    try {
      setProcesandoId(`${item.tipo}-${item.id}`);
      setError("");
      const url = item.tipo === "rutina" ? `/rutinas/${item.id}/rechazar` : `/nutricion/${item.id}/rechazar`;
      await api.post(url, { motivo });
      setEditando(null);
      await cargar(filtro);
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo rechazar");
    } finally {
      setProcesandoId(null);
    }
  };

  const abrirEdicion = async (item) => {
    setError("");
    try {
      if (item.tipo === "rutina") {
        const [detalle, catalogo] = await Promise.all([
          api.get(`/rutinas/${item.id}/detalle`),
          catalogoEjercicios.length ? Promise.resolve({ data: catalogoEjercicios }) : api.get("/ejercicios/"),
        ]);
        setCatalogoEjercicios(catalogo.data);
        setEditando({
          tipo: "rutina",
          id: item.id,
          observaciones: "",
          lista: detalle.data.ejercicios.map((e) => ({
            id_ejercicio: e.id_ejercicio,
            nombre_ejercicio: e.nombre,
            grupo_muscular: e.grupo_muscular,
            series: e.series,
            repeticiones: e.repeticiones,
            descanso_segundos: e.descanso_segundos,
            dia_semana: e.dia_semana,
            orden: e.orden,
          })),
        });
      } else {
        const catalogo = catalogoComidas.length ? { data: catalogoComidas } : await api.get("/comidas/");
        setCatalogoComidas(catalogo.data);
        setEditando({
          tipo: "plan",
          id: item.id,
          observaciones: "",
          lista: (item.comidas || []).map((c) => ({
            tipo_comida: c.tipo_comida,
            descripcion: c.descripcion,
            calorias_aprox: c.calorias_aprox,
            hora_recomendada: c.hora_recomendada,
            id_comida_catalogo: c.id_comida_catalogo,
          })),
        });
      }
    } catch (err) {
      console.error(err);
      setError("No se pudo cargar el detalle para editar");
    }
  };

  const cambiarCampoItem = (indice, campo, valor) => {
    setEditando((prev) => {
      const lista = [...prev.lista];
      lista[indice] = { ...lista[indice], [campo]: valor };
      return { ...prev, lista };
    });
  };

  const quitarItem = (indice) => {
    setEditando((prev) => ({ ...prev, lista: prev.lista.filter((_, i) => i !== indice) }));
  };

  const agregarEjercicio = (idEjercicio) => {
    const ejercicio = catalogoEjercicios.find((e) => String(e.id_ejercicio) === String(idEjercicio));
    if (!ejercicio) return;
    setEditando((prev) => ({
      ...prev,
      lista: [
        ...prev.lista,
        {
          id_ejercicio: ejercicio.id_ejercicio,
          nombre_ejercicio: ejercicio.nombre,
          grupo_muscular: ejercicio.grupo_muscular,
          series: 3,
          repeticiones: "10-12",
          descanso_segundos: 60,
          dia_semana: "Día 1",
          orden: prev.lista.length + 1,
        },
      ],
    }));
  };

  const agregarComida = (idComida) => {
    const comida = catalogoComidas.find((c) => String(c.id_comida_catalogo) === String(idComida));
    if (!comida) return;
    setEditando((prev) => ({
      ...prev,
      lista: [
        ...prev.lista,
        {
          tipo_comida: comida.tipo_comida,
          // El plato real del catálogo (comida.nombre), no la etiqueta corta
          // de comida.descripcion -- mismo bug ya corregido en
          // orquestador.py/recomendador_nutricion.py.
          descripcion: comida.nombre || comida.descripcion,
          calorias_aprox: comida.calorias,
          hora_recomendada: "",
          id_comida_catalogo: comida.id_comida_catalogo,
        },
      ],
    }));
  };

  const guardarEdicion = async () => {
    if (!editando) return;
    try {
      setProcesandoId(`${editando.tipo}-${editando.id}`);
      setError("");

      if (editando.tipo === "rutina") {
        await api.put(`/rutinas/${editando.id}/ejercicios`, {
          ejercicios: editando.lista,
          observaciones_revision: editando.observaciones || null,
        });
      } else {
        await api.put(`/nutricion/${editando.id}/comidas`, {
          comidas: editando.lista,
          observaciones_revision: editando.observaciones || null,
        });
      }

      setEditando(null);
      await cargar(filtro);
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudieron guardar los cambios");
    } finally {
      setProcesandoId(null);
    }
  };

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">REVISIÓN</span>
          <h1>Bandeja de revisión de IA</h1>
          <p>Aprueba, edita o rechaza las rutinas y planes nutricionales generados por IA antes de que el cliente los vea.</p>
        </div>
      </section>

      {error && <p className="error-message">{error}</p>}

      <section className="table-card">
        <div className="table-header">
          <h2>Rutinas y planes</h2>
          <select value={filtro} onChange={(e) => setFiltro(e.target.value)}>
            {FILTROS.map((f) => (
              <option key={f.value} value={f.value}>{f.label}</option>
            ))}
          </select>
        </div>

        {items.length === 0 ? (
          <p className="empty-message">No hay rutinas ni planes en este filtro.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Cliente</th>
                <th>Nombre</th>
                <th>Objetivo</th>
                <th>Generado el</th>
                <th>Origen</th>
                <th>Estado</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => {
                const clave = `${item.tipo}-${item.id}`;
                return (
                  <tr key={clave}>
                    <td>{item.tipo === "rutina" ? "Rutina" : "Plan nutricional"}</td>
                    <td>{obtenerNombreCliente(item.id_cliente)}</td>
                    <td>{item.titulo}</td>
                    <td>{item.objetivo || "-"}</td>
                    <td>{formatearFecha(item.fecha_creacion)}</td>
                    <td><span className={badgeOrigen(item.origen_ia)}>{etiquetaOrigen(item.origen_ia)}</span></td>
                    <td><span className={badgeEstado(item.estado_revision)}>{item.estado_revision || "sin revisión"}</span></td>
                    <td className="table-actions">
                      {item.estado_revision === "pendiente" && (
                        <>
                          <button disabled={procesandoId === clave} onClick={() => aprobar(item)}>
                            Aprobar
                          </button>
                          <button onClick={() => abrirEdicion(item)}>Editar</button>
                          <button className="btn-danger" disabled={procesandoId === clave} onClick={() => rechazar(item)}>
                            Rechazar
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </section>

      {editando && (
        <section className="form-card">
          <div className="card-header">
            <div>
              <h2>Editando {editando.tipo === "rutina" ? "rutina" : "plan nutricional"}</h2>
              <p>Modifica, quita o agrega ítems. Al guardar, quedará marcado "aprobada con cambios" cuando apruebes.</p>
            </div>
          </div>

          {editando.tipo === "rutina" ? (
            <table className="table">
              <thead>
                <tr>
                  <th>Ejercicio</th>
                  <th>Día</th>
                  <th>Series</th>
                  <th>Reps</th>
                  <th>Descanso (s)</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {editando.lista.map((e, i) => (
                  <tr key={`${e.id_ejercicio}-${i}`}>
                    <td>{e.nombre_ejercicio}</td>
                    <td>
                      <input value={e.dia_semana || ""} onChange={(ev) => cambiarCampoItem(i, "dia_semana", ev.target.value)} />
                    </td>
                    <td>
                      <input type="number" value={e.series || ""} onChange={(ev) => cambiarCampoItem(i, "series", Number(ev.target.value))} style={{ width: "60px" }} />
                    </td>
                    <td>
                      <input value={e.repeticiones || ""} onChange={(ev) => cambiarCampoItem(i, "repeticiones", ev.target.value)} style={{ width: "70px" }} />
                    </td>
                    <td>
                      <input type="number" value={e.descanso_segundos || ""} onChange={(ev) => cambiarCampoItem(i, "descanso_segundos", Number(ev.target.value))} style={{ width: "70px" }} />
                    </td>
                    <td>
                      <button className="btn-danger" onClick={() => quitarItem(i)}>Quitar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Tipo de comida</th>
                  <th>Descripción</th>
                  <th>Kcal</th>
                  <th>Hora</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {editando.lista.map((c, i) => (
                  <tr key={`${c.descripcion}-${i}`}>
                    <td>{c.tipo_comida}</td>
                    <td>
                      <input value={c.descripcion || ""} onChange={(ev) => cambiarCampoItem(i, "descripcion", ev.target.value)} />
                    </td>
                    <td>
                      <input type="number" value={c.calorias_aprox || ""} onChange={(ev) => cambiarCampoItem(i, "calorias_aprox", Number(ev.target.value))} style={{ width: "70px" }} />
                    </td>
                    <td>
                      <input value={c.hora_recomendada || ""} onChange={(ev) => cambiarCampoItem(i, "hora_recomendada", ev.target.value)} style={{ width: "70px" }} />
                    </td>
                    <td>
                      <button className="btn-danger" onClick={() => quitarItem(i)}>Quitar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <div className="form-grid" style={{ marginTop: "1rem" }}>
            {editando.tipo === "rutina" ? (
              <div className="form-field">
                <label>Agregar ejercicio del catálogo</label>
                <select defaultValue="" onChange={(e) => { if (e.target.value) { agregarEjercicio(e.target.value); e.target.value = ""; } }}>
                  <option value="">Seleccione un ejercicio</option>
                  {catalogoEjercicios.map((ej) => (
                    <option key={ej.id_ejercicio} value={ej.id_ejercicio}>{ej.nombre} ({ej.grupo_muscular})</option>
                  ))}
                </select>
              </div>
            ) : (
              <div className="form-field">
                <label>Agregar comida del catálogo</label>
                <select defaultValue="" onChange={(e) => { if (e.target.value) { agregarComida(e.target.value); e.target.value = ""; } }}>
                  <option value="">Seleccione una comida</option>
                  {catalogoComidas.map((c) => (
                    <option key={c.id_comida_catalogo} value={c.id_comida_catalogo}>{c.nombre} ({c.tipo_comida})</option>
                  ))}
                </select>
              </div>
            )}

            <div className="form-field field-large">
              <label>Observaciones del cambio</label>
              <input
                value={editando.observaciones}
                onChange={(e) => setEditando((prev) => ({ ...prev, observaciones: e.target.value }))}
                placeholder="Ej: cambié repeticiones de pierna, quité banca inclinada"
              />
            </div>
          </div>

          <div className="form-actions">
            <button className="btn-secondary" onClick={() => setEditando(null)}>Cancelar</button>
            <button className="btn-primary" disabled={procesandoId === `${editando.tipo}-${editando.id}`} onClick={guardarEdicion}>
              Guardar cambios
            </button>
          </div>
        </section>
      )}
    </div>
  );
}

export default RevisionIA;
