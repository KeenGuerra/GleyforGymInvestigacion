import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";

function HazteSocio() {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  const [form, setForm] = useState({
    dni: "",
    nombres: "",
    apellidos: "",
    telefono: "",
    fecha_nacimiento: "",
    sexo: "",
  });

  useEffect(() => {
    if (localStorage.getItem("tiene_cliente") === "true") {
      navigate("/mi-membresia");
    }
  }, [navigate]);

  const cambiar = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const enviar = async (e) => {
    e.preventDefault();
    setError("");
    setEnviando(true);

    try {
      await api.post("/clientes/hazte-socio", {
        ...form,
        fecha_nacimiento: form.fecha_nacimiento || null,
        telefono: form.telefono || null,
        sexo: form.sexo || null,
      });

      localStorage.setItem("tiene_cliente", "true");
      navigate("/mi-membresia");
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo completar tu registro como socio");
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">HAZTE SOCIO</span>
          <h1>Completa tus datos para ser socio</h1>
          <p>
            Con estos datos quedas registrado como socio de GleyforGym y
            podrás elegir y pagar un plan de membresía. Luego, desde "Mi
            perfil", puedes completar tu peso, estatura, objetivo y
            restricciones para personalizar tus rutinas y planes con IA.
          </p>
        </div>
      </section>

      {error && <p className="error-message">{error}</p>}

      <form onSubmit={enviar} className="card" style={{ padding: "24px", maxWidth: "640px" }}>
        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="dni">DNI</label>
            <input
              id="dni"
              name="dni"
              value={form.dni}
              onChange={cambiar}
              maxLength={8}
              required
            />
          </div>

          <div className="form-field">
            <label htmlFor="nombres">Nombres</label>
            <input id="nombres" name="nombres" value={form.nombres} onChange={cambiar} required />
          </div>

          <div className="form-field">
            <label htmlFor="apellidos">Apellidos</label>
            <input id="apellidos" name="apellidos" value={form.apellidos} onChange={cambiar} required />
          </div>

          <div className="form-field">
            <label htmlFor="telefono">Teléfono</label>
            <input id="telefono" name="telefono" value={form.telefono} onChange={cambiar} />
          </div>

          <div className="form-field">
            <label htmlFor="fecha_nacimiento">Fecha de nacimiento</label>
            <input
              id="fecha_nacimiento"
              name="fecha_nacimiento"
              type="date"
              value={form.fecha_nacimiento}
              onChange={cambiar}
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
        </div>

        <div className="form-actions">
          <button type="submit" className="btn-primary" disabled={enviando}>
            {enviando ? "Guardando..." : "Hazte socio"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default HazteSocio;
