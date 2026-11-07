import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import api from "../api/api";
import logo from "../assets/logo-gleyforgym.jpeg";

function VerificarCorreo() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";

  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    if (!token) {
      setError("Este enlace no incluye un token válido. Solicita uno nuevo.");
      setCargando(false);
      return;
    }

    const verificar = async () => {
      try {
        const res = await api.post("/usuarios/verificar-correo", { token });
        setMensaje(res.data.mensaje);
      } catch (err) {
        setError(err.response?.data?.detail || "No se pudo verificar el correo");
      } finally {
        setCargando(false);
      }
    };

    verificar();
  }, [token]);

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
            <p>Verificación de correo</p>
          </div>
        </div>

        <main className="form-card auth-card">
          <div className="card-header">
            <div>
              <span className="badge">VERIFICACIÓN</span>
              <h2>Confirmación de correo</h2>
            </div>
          </div>

          {cargando && <p className="muted-text">Verificando tu correo...</p>}

          {!cargando && error && <p className="error-message">{error}</p>}
          {!cargando && mensaje && <p className="muted-text">{mensaje}</p>}

          {!cargando && (
            <button className="btn-primary auth-submit" onClick={() => navigate("/login")}>
              Ir a iniciar sesión
            </button>
          )}
        </main>
      </div>
    </section>
  );
}

export default VerificarCorreo;
