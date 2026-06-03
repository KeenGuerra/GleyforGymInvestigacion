import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import logo from "../assets/logo-gleyforgym.jpeg";

function Login() {
  const navigate = useNavigate();

  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");
  const [mostrarPassword, setMostrarPassword] = useState(false);
  const [error, setError] = useState("");

  const iniciarSesion = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await api.post("/usuarios/login", {
        correo,
        password,
      });

      localStorage.setItem("token", res.data.token);
      localStorage.setItem("rol", res.data.usuario.rol);
      localStorage.setItem("id_usuario", res.data.usuario.id_usuario);
      localStorage.setItem("correo", res.data.usuario.correo);

      navigate("/dashboard");
    } catch (error) {
      console.error(error);
      setError("Correo o contraseña incorrectos");
    }
  };

  return (
    <section className="auth-page">
      <button className="btn-secondary auth-back" onClick={() => navigate("/")}>
        Volver al inicio
      </button>

      <div className="auth-panel">
        <div className="auth-left card">
          <div className="auth-brand">
            <div className="auth-logo">
              <img src={logo} alt="Logo GLEYFORGYM" />
            </div>

            <h1>GleyforGym</h1>
            <p>Gestión deportiva profesional</p>
          </div>

          <div className="info-card auth-info">
            <span className="badge">SaaS Fitness</span>
            <h2>Controla tu gimnasio desde una sola plataforma</h2>
            <p>
              Accede al panel para gestionar clientes, pagos, asistencias,
              rutinas IA y planes nutricionales.
            </p>
          </div>
        </div>

        <main className="form-card auth-card">
          <div className="card-header">
            <div>
              <span className="badge">ACCESO SEGURO</span>
              <h2>Bienvenido de nuevo</h2>
              <p>Ingresa tus credenciales para acceder al sistema.</p>
            </div>
          </div>

          {error && <p className="error-message">{error}</p>}

          <form onSubmit={iniciarSesion}>
            <div className="form-grid auth-form-grid">
              <div className="form-field field-large">
                <label htmlFor="correo">Correo electrónico</label>
                <input
                  id="correo"
                  type="email"
                  placeholder="admin@gleyforgym.com"
                  value={correo}
                  onChange={(e) => setCorreo(e.target.value)}
                  required
                />
              </div>

              <div className="form-field field-large">
                <div className="label-row">
                  <label htmlFor="password">Contraseña</label>
                  <span>Contacta al administrador</span>
                </div>

                <div className="password-field">
                  <input
                    id="password"
                    type={mostrarPassword ? "text" : "password"}
                    placeholder="Ingrese su contraseña"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />

                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => setMostrarPassword(!mostrarPassword)}
                  >
                    {mostrarPassword ? "Ocultar" : "Ver"}
                  </button>
                </div>
              </div>
            </div>

            <div className="check-row">
              <input type="checkbox" id="recordar" />
              <label htmlFor="recordar">Recordar sesión en este dispositivo</label>
            </div>

            <button type="submit" className="btn-primary auth-submit">
              Acceder al sistema
            </button>

            <p className="muted-text">
              Acceso exclusivo para usuarios registrados por el gimnasio.
            </p>
          </form>

          <div className="tags-row">
            <span className="badge">FastAPI</span>
            <span className="badge">JWT</span>
            <span className="badge">PostgreSQL</span>
          </div>
        </main>
      </div>
    </section>
  );
}

export default Login;