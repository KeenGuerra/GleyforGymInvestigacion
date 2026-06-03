import React, { useEffect, useState } from "react";
import api from "../api/api";

function Comidas() {
  const [comidas, setComidas] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [busqueda, setBusqueda] = useState("");
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);

  const formInicial = {
    nombre: "",
    tipo_comida: "",
    descripcion: "",
    calorias: "",
    proteinas: "",
    carbohidratos: "",
    grasas: "",
    objetivo: "",
    estado: "ACTIVO",
  };

  const [form, setForm] = useState(formInicial);

  const cargarComidas = async () => {
    try {
      setError("");
      const res = await api.get("/comidas/");
      setComidas(res.data);
    } catch (error) {
      console.error(error);
      setError("Error al cargar comidas");
    }
  };

  useEffect(() => {
    cargarComidas();
  }, []);

  const cambiar = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const limpiar = () => {
    setForm(formInicial);
    setError("");
    setMostrarFormulario(false);
  };

  const validar = () => {
    if (!form.nombre.trim()) return "Ingrese el nombre de la comida";
    if (!form.tipo_comida) return "Seleccione el tipo de comida";

    if (form.calorias && Number(form.calorias) < 0) return "Calorías inválidas";
    if (form.proteinas && Number(form.proteinas) < 0) return "Proteínas inválidas";
    if (form.carbohidratos && Number(form.carbohidratos) < 0)
      return "Carbohidratos inválidos";
    if (form.grasas && Number(form.grasas) < 0) return "Grasas inválidas";

    return "";
  };

  const guardar = async (e) => {
    e.preventDefault();
    setError("");

    const mensaje = validar();

    if (mensaje) {
      setError(mensaje);
      return;
    }

    try {
      setCargando(true);

      const data = {
        nombre: form.nombre,
        tipo_comida: form.tipo_comida,
        descripcion: form.descripcion || null,
        calorias: form.calorias ? Number(form.calorias) : null,
        proteinas: form.proteinas ? Number(form.proteinas) : null,
        carbohidratos: form.carbohidratos ? Number(form.carbohidratos) : null,
        grasas: form.grasas ? Number(form.grasas) : null,
        objetivo: form.objetivo || null,
        estado: form.estado,
      };

      await api.post("/comidas/", data);

      limpiar();
      await cargarComidas();
    } catch (error) {
      console.error(error);
      setError(error.response?.data?.detail || "Error al registrar comida");
    } finally {
      setCargando(false);
    }
  };

  const desactivar = async (id) => {
    const confirmar = globalThis.confirm("¿Seguro que deseas desactivar esta comida?");
    if (!confirmar) return;

    try {
      await api.delete(`/comidas/${id}`);
      await cargarComidas();
    } catch (error) {
      console.error(error);
      setError("Error al desactivar comida");
    }
  };

  const comidasFiltradas = comidas.filter((c) => {
    const texto = busqueda.toLowerCase();

    return (
      String(c.nombre || "").toLowerCase().includes(texto) ||
      String(c.tipo_comida || "").toLowerCase().includes(texto) ||
      String(c.objetivo || "").toLowerCase().includes(texto) ||
      String(c.estado || "").toLowerCase().includes(texto)
    );
  });

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">NUTRICIÓN IA</span>
          <h1>Catálogo de comidas</h1>
          <p>Registra comidas que la IA usará para crear planes nutricionales.</p>
        </div>

        <button
          className="btn-primary"
          onClick={() => {
            setMostrarFormulario(true);
            setForm(formInicial);
            setError("");
          }}
        >
          + Registrar comida
        </button>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Total comidas</span>
          <strong>{comidas.length}</strong>
        </div>

        <div className="stat-card">
          <span>Filtradas</span>
          <strong>{comidasFiltradas.length}</strong>
        </div>

        <div className="stat-card">
          <span>Activas</span>
          <strong>{comidas.filter((c) => c.estado === "ACTIVO").length}</strong>
        </div>
      </section>

      {mostrarFormulario && (
        <form onSubmit={guardar} className="form-card">
          <div className="card-header">
            <div>
              <h2>Registrar comida</h2>
              <p>Agrega alimentos con sus macros, objetivo y tipo de comida.</p>
            </div>
          </div>

          {error && <p className="error-message">{error}</p>}

          <div className="form-grid">
            <div className="form-field field-large">
              <label htmlFor="nombre">Nombre</label>
              <input
                id="nombre"
                name="nombre"
                placeholder="Nombre de la comida"
                value={form.nombre}
                onChange={cambiar}
              />
            </div>

            <div className="form-field">
              <label htmlFor="tipo_comida">Tipo de comida</label>
              <select id="tipo_comida" name="tipo_comida" value={form.tipo_comida} onChange={cambiar}>
                <option value="">Seleccionar tipo</option>
                <option value="DESAYUNO">DESAYUNO</option>
                <option value="MEDIA MAÑANA">MEDIA MAÑANA</option>
                <option value="ALMUERZO">ALMUERZO</option>
                <option value="MERIENDA">MERIENDA</option>
                <option value="CENA">CENA</option>
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="objetivo">Objetivo</label>
              <select id="objetivo" name="objetivo" value={form.objetivo} onChange={cambiar}>
                <option value="">Seleccionar objetivo</option>
                <option value="GENERAL">GENERAL</option>
                <option value="BAJAR PESO">BAJAR PESO</option>
                <option value="GANAR MASA MUSCULAR">GANAR MASA MUSCULAR</option>
                <option value="MANTENER PESO">MANTENER PESO</option>
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="calorias">Calorías</label>
              <input
                id="calorias"
                name="calorias"
                type="number"
                placeholder="0"
                value={form.calorias}
                onChange={cambiar}
              />
            </div>

            <div className="form-field">
              <label htmlFor="proteinas">Proteínas</label>
              <input
                id="proteinas"
                name="proteinas"
                type="number"
                placeholder="g"
                value={form.proteinas}
                onChange={cambiar}
              />
            </div>

            <div className="form-field">
              <label htmlFor="carbohidratos">Carbohidratos</label>
              <input
                id="carbohidratos"
                name="carbohidratos"
                type="number"
                placeholder="g"
                value={form.carbohidratos}
                onChange={cambiar}
              />
            </div>

            <div className="form-field">
              <label htmlFor="grasas">Grasas</label>
              <input
                id="grasas"
                name="grasas"
                type="number"
                placeholder="g"
                value={form.grasas}
                onChange={cambiar}
              />
            </div>

            <div className="form-field">
              <label htmlFor="estado">Estado</label>
              <select id="estado" name="estado" value={form.estado} onChange={cambiar}>
                <option value="ACTIVO">ACTIVO</option>
                <option value="INACTIVO">INACTIVO</option>
              </select>
            </div>

            <div className="form-field field-large">
              <label htmlFor="descripcion">Descripción</label>
              <textarea
                id="descripcion"
                name="descripcion"
                placeholder="Descripción de la comida"
                value={form.descripcion}
                onChange={cambiar}
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary" disabled={cargando}>
              {cargando ? "Guardando..." : "Guardar comida"}
            </button>

            <button type="button" className="btn-secondary" onClick={limpiar}>
              Cancelar
            </button>
          </div>
        </form>
      )}

      {error && !mostrarFormulario && <p className="error-message">{error}</p>}

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Lista de comidas</h2>
            <p>Consulta los alimentos registrados para nutrición IA.</p>
          </div>

          <input
            className="search-input"
            type="text"
            placeholder="Buscar por nombre, tipo, objetivo o estado..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        {comidasFiltradas.length === 0 ? (
          <p className="empty-message">No hay comidas registradas.</p>
        ) : (
          <div className="cards-grid">
            {comidasFiltradas.map((c) => (
              <div key={c.id_comida_catalogo} className="card item-card">
                <div className="item-card-top">
                  <span className="badge">{c.tipo_comida || "GENERAL"}</span>
                  <span className="badge">{c.estado || "ACTIVO"}</span>
                </div>

                <h3>{c.nombre}</h3>
                <p>{c.objetivo || "GENERAL"}</p>

                <div className="mini-stats-grid">
                  <div>
                    <strong>{c.calorias || 0}</strong>
                    <span>kcal</span>
                  </div>

                  <div>
                    <strong>{c.proteinas || 0}g</strong>
                    <span>Proteínas</span>
                  </div>

                  <div>
                    <strong>{c.carbohidratos || 0}g</strong>
                    <span>Carbos</span>
                  </div>

                  <div>
                    <strong>{c.grasas || 0}g</strong>
                    <span>Grasas</span>
                  </div>
                </div>

                {c.descripcion && <p className="item-description">{c.descripcion}</p>}

                <button
                  className="btn-danger"
                  onClick={() => desactivar(c.id_comida_catalogo)}
                >
                  Desactivar
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Comidas;