import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";

function Clientes() {
  const navigate = useNavigate();

  const [clientes, setClientes] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [editandoId, setEditandoId] = useState(null);
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);

  const formInicial = {
    dni: "",
    nombres: "",
    apellidos: "",
    correo: "",
    password: "",
    telefono: "",
    fecha_nacimiento: "",
    sexo: "",
    direccion: "",
    peso: "",
    estatura: "",
    objetivo: "",
    nivel: "",
    restricciones_medicas: "",
  };

  const [form, setForm] = useState(formInicial);

  const calcularEdad = (fechaNacimiento) => {
    if (!fechaNacimiento) return "";

    const nacimiento = new Date(fechaNacimiento);
    const hoy = new Date();

    let edad = hoy.getFullYear() - nacimiento.getFullYear();
    const mes = hoy.getMonth() - nacimiento.getMonth();

    if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) {
      edad--;
    }

    return String(edad);
  };

  const cargarClientes = async () => {
    try {
      const res = await api.get("/clientes/");
      setClientes(res.data);
    } catch (error) {
      console.error(error);
      setError(error.response?.data?.detail || "Error al cargar clientes");
    }
  };

  useEffect(() => {
    cargarClientes();
  }, []);

  const cambiar = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const limpiarFormulario = () => {
    setForm(formInicial);
    setEditandoId(null);
    setError("");
    setMostrarFormulario(false);
  };

  const guardarCliente = async (e) => {
    e.preventDefault();
    setError("");

    if (!form?.dni || form?.dni?.length !== 8) {
      setError("DNI inválido");
      return;
    }

    try {
      const datos = { ...form };
      delete datos.edad;

      if (editandoId) {
        delete datos.password;
        await api.put(`/clientes/${editandoId}`, datos);
      } else {
        await api.post("/clientes/", datos);
      }

      limpiarFormulario();
      cargarClientes();
    } catch (error) {
      console.error(error);
      setError(error.response?.data?.detail || "Error al guardar cliente");
    }
  };

  const editarCliente = (cliente) => {
    setEditandoId(cliente.id_cliente);
    setMostrarFormulario(true);

    setForm({
      dni: cliente.dni || "",
      nombres: cliente.nombres || "",
      apellidos: cliente.apellidos || "",
      correo: cliente.correo || "",
      password: "",
      telefono: cliente.telefono || "",
      fecha_nacimiento: cliente.fecha_nacimiento || "",
      sexo: cliente.sexo || "",
      direccion: cliente.direccion || "",
      peso: cliente.peso || "",
      estatura: cliente.estatura || "",
      objetivo: cliente.objetivo || "",
      nivel: cliente.nivel || "",
      restricciones_medicas: cliente.restricciones_medicas || "",
    });

    globalThis.scrollTo({ top: 0, behavior: "smooth" });
  };

  const cambiarEstadoCliente = async (cliente) => {
    const nuevoEstado = cliente.estado === "ACTIVO" ? "INACTIVO" : "ACTIVO";

    const confirmar = globalThis.confirm(
      `¿Seguro que deseas ${
        nuevoEstado === "ACTIVO" ? "activar" : "desactivar"
      } este cliente?`
    );

    if (!confirmar) return;

    try {
      await api.put(`/clientes/${cliente.id_cliente}`, {
        estado: nuevoEstado,
      });

      cargarClientes();
    } catch (error) {
      console.error(error);
      setError(error.response?.data?.detail || "Error al cambiar estado");
    }
  };

  const clientesFiltrados = clientes.filter((c) =>
    `${c.nombres} ${c.apellidos} ${c.dni} ${c.correo}`
      .toLowerCase()
      .includes(busqueda.toLowerCase())
  );

  const iniciales = (c) =>
    `${c.nombres} ${c.apellidos}`
      .split(" ")
      .map((n) => n[0])
      .join("")
      .substring(0, 2)
      .toUpperCase();

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">CLIENTES</span>
          <h1>Directorio de clientes</h1>
          <p>Administra los socios registrados del gimnasio GleyforGym.</p>
        </div>

        <button
          className="btn-primary"
          onClick={() => {
            setMostrarFormulario(true);
            setEditandoId(null);
            setForm(formInicial);
            setError("");
          }}
        >
          + Registrar cliente
        </button>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span>Total clientes</span>
          <strong>{clientes.length}</strong>
        </div>

        <div className="stat-card">
          <span>Filtrados</span>
          <strong>{clientesFiltrados.length}</strong>
        </div>

        <div className="stat-card">
          <span>Activos</span>
          <strong>{clientes.filter((c) => c.estado === "ACTIVO").length}</strong>
        </div>
      </section>

      {mostrarFormulario && (
        <form onSubmit={guardarCliente} className="form-card">
          <div className="card-header">
            <div>
              <h2>{editandoId ? "Editar cliente" : "Registrar cliente"}</h2>
              <p>
                {editandoId
                  ? "Actualiza la información del socio seleccionado."
                  : "Completa los datos personales y físicos del nuevo socio."}
              </p>
            </div>
          </div>

          {error && <p className="error-message">{error}</p>}

          <div className="form-grid">
            <div className="form-field">
              <label htmlFor="dni">DNI</label>
              <input
                id="dni"
                name="dni"
                placeholder="Ingrese DNI"
                value={form.dni}
                onChange={cambiar}
              />
            </div>

            <div className="form-field">
              <label htmlFor="nombres">Nombres</label>
              <input
                id="nombres"
                name="nombres"
                placeholder="Nombres"
                value={form.nombres}
                onChange={cambiar}
              />
            </div>

            <div className="form-field">
              <label htmlFor="apellidos">Apellidos</label>
              <input
                id="apellidos"
                name="apellidos"
                placeholder="Apellidos"
                value={form.apellidos}
                onChange={cambiar}
              />
            </div>

            <div className="form-field">
              <label htmlFor="correo">Correo</label>
              <input
                id="correo"
                name="correo"
                placeholder="correo@email.com"
                value={form.correo}
                onChange={cambiar}
              />
            </div>

            {!editandoId && (
              <div className="form-field">
                <label htmlFor="password">Contraseña</label>
                <input
                  id="password"
                  type="password"
                  name="password"
                  placeholder="Contraseña"
                  value={form.password}
                  onChange={cambiar}
                />
              </div>
            )}

            <div className="form-field">
              <label htmlFor="telefono">Teléfono</label>
              <input
                id="telefono"
                name="telefono"
                placeholder="Teléfono"
                value={form.telefono}
                onChange={cambiar}
              />
            </div>

            <div className="form-field">
              <label htmlFor="fecha_nacimiento">Fecha nacimiento</label>
              <input
                id="fecha_nacimiento"
                type="date"
                name="fecha_nacimiento"
                value={form.fecha_nacimiento}
                onChange={cambiar}
              />
            </div>

            <div className="form-field">
              <label htmlFor="edad_calculada">Edad calculada</label>
              <input
                id="edad_calculada"
                value={calcularEdad(form.fecha_nacimiento)}
                placeholder="Se calcula automáticamente"
                readOnly
              />
            </div>

            <div className="form-field">
              <label htmlFor="sexo">Sexo</label>
              <select id="sexo" name="sexo" value={form.sexo} onChange={cambiar}>
                <option value="">Seleccione sexo</option>
                <option>Masculino</option>
                <option>Femenino</option>
              </select>
            </div>

            <div className="form-field field-large">
              <label htmlFor="direccion">Dirección</label>
              <input
                id="direccion"
                name="direccion"
                placeholder="Dirección"
                value={form.direccion}
                onChange={cambiar}
              />
            </div>

            <div className="form-field">
              <label htmlFor="peso">Peso</label>
              <input
                id="peso"
                name="peso"
                placeholder="Peso"
                value={form.peso}
                onChange={cambiar}
              />
            </div>

            <div className="form-field">
              <label htmlFor="estatura">Estatura</label>
              <input
                id="estatura"
                name="estatura"
                placeholder="Estatura"
                value={form.estatura}
                onChange={cambiar}
              />
            </div>

            <div className="form-field">
              <label htmlFor="objetivo">Objetivo</label>
              <select id="objetivo" name="objetivo" value={form.objetivo} onChange={cambiar}>
                <option value="">Seleccione objetivo</option>
                <option>Bajar de peso</option>
                <option>Ganar masa muscular</option>
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="nivel">Nivel</label>
              <select id="nivel" name="nivel" value={form.nivel} onChange={cambiar}>
                <option value="">Seleccione nivel</option>
                <option>Principiante</option>
                <option>Intermedio</option>
                <option>Avanzado</option>
              </select>
            </div>

            <div className="form-field field-large">
              <label htmlFor="restricciones_medicas">Restricciones médicas</label>
              <input
                id="restricciones_medicas"
                name="restricciones_medicas"
                placeholder="Ejemplo: lesión de rodilla"
                value={form.restricciones_medicas}
                onChange={cambiar}
              />
            </div>
          </div>

          <div className="form-actions">
            <button className="btn-primary">
              {editandoId ? "Actualizar cliente" : "Registrar cliente"}
            </button>

            <button
              type="button"
              className="btn-secondary"
              onClick={limpiarFormulario}
            >
              Cancelar
            </button>
          </div>
        </form>
      )}

      {error && !mostrarFormulario && <p className="error-message">{error}</p>}

      <section className="table-card">
        <div className="card-header">
          <div>
            <h2>Lista de clientes</h2>
            <p>Consulta, edita o cambia el estado de cada socio.</p>
          </div>

          <input
            className="search-input"
            placeholder="Buscar por nombre, DNI o correo..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Cliente</th>
                <th>DNI</th>
                <th>Correo</th>
                <th>Nivel</th>
                <th>Edad</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {clientesFiltrados.length === 0 ? (
                <tr>
                  <td colSpan="7" className="empty-message">
                    No hay clientes registrados
                  </td>
                </tr>
              ) : (
                clientesFiltrados.map((c) => (
                  <tr key={c.id_cliente}>
                    <td>
                      <div className="user-info">
                        <div className="profile-avatar">{iniciales(c)}</div>
                        <div>
                          <strong>
                            {c.nombres} {c.apellidos}
                          </strong>
                          <span>ID #{c.id_cliente}</span>
                        </div>
                      </div>
                    </td>

                    <td>{c.dni}</td>
                    <td>{c.correo}</td>
                    <td>{c.nivel || "-"}</td>
                    <td>{c.edad || calcularEdad(c.fecha_nacimiento) || "-"}</td>

                    <td>
                      <span className="badge">{c.estado}</span>
                    </td>

                    <td>
                      <div className="table-actions">
                        <button
                          className="btn-secondary"
                          onClick={() =>
                            navigate(`/clientes/${c.id_cliente}/detalle`)
                          }
                        >
                          Ver
                        </button>

                        <button
                          className="btn-secondary"
                          onClick={() => editarCliente(c)}
                        >
                          Editar
                        </button>

                        <button
                          className={
                            c.estado === "ACTIVO" ? "btn-danger" : "btn-primary"
                          }
                          onClick={() => cambiarEstadoCliente(c)}
                        >
                          {c.estado === "ACTIVO" ? "Desactivar" : "Activar"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default Clientes;