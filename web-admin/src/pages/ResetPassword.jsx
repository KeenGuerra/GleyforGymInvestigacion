import React, { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import api from "../api/api";
import logo from "../assets/logo-gleyforgym.jpeg";

function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";

  const [passwordNueva, setPasswordNueva] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [listo, setListo] = useState(false);

  const enviar = async (e) => {
    e.preventDefault();
    setError("");
    setMensaje("");

    if (passwordNueva.length < 6) {
      setError("La contraseña debe tener al menos 6 caracteres");
      return;
    }
    if (passwordNueva !== confirmar) {
      setError("Las contraseñas no coinciden");
      return;
    }

    try {
      const res = await api.post("/usuarios/reset-password", {
        token,
        password_nueva: passwordNueva,
      });
      setMensaje(res.data.mensaje);
      setListo(true);
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo restablecer la contraseña");
    }
  };

  return (
    <section className="auth-page">
      <button className="btn-secondary auth-back" onClick={() => navigate("/login")}>
        Volver al login
      </button>

      <div className="auth-panel">
        <div className="auth-left card">
          <div className="auth-brand">
            <div className="auth-logo">
              <img src={logo} alt="Logo GLEYFORGYM" />
            </div>
            <h1>GleyforGym</h1>
            <p>Recuperación de acceso</p>
          </div>
        </div>

        <main className="form-card auth-card">
          <div className="card-header">
            <div>
              <span className="badge">RECUPERAR ACCESO</span>
              <h2>Elige tu nueva contraseña</h2>
              <p>El enlace que recibiste te trajo hasta aquí con un token de un solo uso.</p>
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
            <form onSubmit={enviar}>
              {!token && (
                <p className="error-message">
                  Este enlace no incluye un token válido. Solicita uno nuevo desde la pantalla de login.
                </p>
              )}

              <div className="form-grid auth-form-grid">
                <div className="form-field field-large">
                  <label htmlFor="password-nueva">Nueva contraseña</label>
                  <input
                    id="password-nueva"
                    type="password"
                    value={passwordNueva}
                    onChange={(e) => setPasswordNueva(e.target.value)}
                    required
                  />
                </div>

                <div className="form-field field-large">
                  <label htmlFor="password-confirmar">Confirmar contraseña</label>
                  <input
                    id="password-confirmar"
                    type="password"
                    value={confirmar}
                    onChange={(e) => setConfirmar(e.target.value)}
                    required
                  />
                </div>
              </div>

              <button type="submit" className="btn-primary auth-submit" disabled={!token}>
                Restablecer contraseña
              </button>
            </form>
          )}
        </main>
      </div>
    </section>
  );
}

export default ResetPassword;
