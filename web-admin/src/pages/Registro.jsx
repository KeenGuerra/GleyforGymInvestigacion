import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import logo from "../assets/logo-gleyforgym.png";

function Registro() {
  const navigate = useNavigate();

  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [listo, setListo] = useState(false);

  const registrarse = async (e) => {
    e.preventDefault();
    setError("");

    if (password.length < 6) {
      setError("La contraseña debe tener al menos 6 caracteres");
      return;
    }
    if (password !== confirmar) {
      setError("Las contraseñas no coinciden");
      return;
    }

    try {
      setEnviando(true);
      const res = await api.post("/usuarios/registro", { correo, password });
      setMensaje(res.data.mensaje);
      setListo(true);
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo crear la cuenta");
    } finally {
      setEnviando(false);
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
            <span className="badge">Tienda GleyforGym</span>
            <h2>Crea tu cuenta para comprar</h2>
            <p>
              Solo necesitas tu correo y una contraseña — puedes comprar en la
              tienda sin ser socio del gimnasio.
            </p>
          </div>
        </div>

        <main className="form-card auth-card">
          <div className="card-header">
            <div>
              <span className="badge">CREAR CUENTA</span>
              <h2>Regístrate para comprar</h2>
              <p>Usa tu correo personal, el mismo con el que luego iniciarás sesión.</p>
            </div>
          </div>

          {error && <p className="error-message">{error}</p>}

          {listo ? (
            <>
              <p className="muted-text">{mensaje}</p>
              <button className="btn-primary auth-submit" onClick={() => navigate("/login")}>
                Ir a iniciar sesión
              </button>
            </>
          ) : (
            <form onSubmit={registrarse}>
              <div className="form-grid auth-form-grid">
                <div className="form-field field-large">
                  <label htmlFor="correo">Correo electrónico</label>
                  <input
                    id="correo"
                    type="email"
                    placeholder="tu.correo@gmail.com"
                    value={correo}
                    onChange={(e) => setCorreo(e.target.value)}
                    required
                  />
                </div>

                <div className="form-field field-large">
                  <label htmlFor="password">Contraseña</label>
                  <input
                    id="password"
                    type="password"
                    placeholder="Mínimo 6 caracteres"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>

                <div className="form-field field-large">
                  <label htmlFor="confirmar">Confirmar contraseña</label>
                  <input
                    id="confirmar"
                    type="password"
                    value={confirmar}
                    onChange={(e) => setConfirmar(e.target.value)}
                    required
                  />
                </div>
              </div>

              <button type="submit" className="btn-primary auth-submit" disabled={enviando}>
                {enviando ? "Creando cuenta..." : "Crear cuenta"}
              </button>

              <p className="muted-text">
                ¿Ya tienes cuenta?{" "}
                <button type="button" className="link-button" onClick={() => navigate("/login")}>
                  Inicia sesión
                </button>
              </p>
            </form>
          )}
        </main>
      </div>
    </section>
  );
}

export default Registro;
