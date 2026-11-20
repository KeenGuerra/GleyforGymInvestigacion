import React, { useEffect, useRef, useState } from "react";
import api from "../api/api";
import logoDefecto from "../assets/logo-gleyforgym.png";

function Configuracion() {
  const [form, setForm] = useState({
    telefono: "",
    email: "",
    direccion: "",
    facebook_url: "",
    instagram_url: "",
    tiktok_url: "",
    whatsapp_numero: "",
    mapa_embed_url: "",
  });
  const [logoActualUrl, setLogoActualUrl] = useState(null);
  const [logo, setLogo] = useState(null);
  const fileRef = useRef(null);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  const cargar = async () => {
    try {
      setError("");
      const res = await api.get("/configuracion/");
      setForm({
        telefono: res.data.telefono || "",
        email: res.data.email || "",
        direccion: res.data.direccion || "",
        facebook_url: res.data.facebook_url || "",
        instagram_url: res.data.instagram_url || "",
        tiktok_url: res.data.tiktok_url || "",
        whatsapp_numero: res.data.whatsapp_numero || "",
        mapa_embed_url: res.data.mapa_embed_url || "",
      });
      setLogoActualUrl(res.data.logo_url || null);
    } catch (err) {
      console.error(err);
      setError("No se pudo cargar la configuración del sitio");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargar();
  }, []);

  const cambiar = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const guardar = async (e) => {
    e.preventDefault();
    setError("");
    setMensaje("");

    try {
      setGuardando(true);
      await api.put("/configuracion/", form);

      if (logo) {
        const mediaData = new FormData();
        mediaData.append("logo", logo);
        await api.put("/configuracion/media", mediaData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        setLogo(null);
        if (fileRef.current) fileRef.current.value = "";
      }

      await cargar();
      setMensaje("Configuración guardada correctamente.");
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Error al guardar la configuración");
    } finally {
      setGuardando(false);
    }
  };

  if (cargando) return <p className="empty-message">Cargando configuración...</p>;

  return (
    <div className="page-container">
      <section className="page-header-pro">
        <div>
          <span className="badge">CONFIGURACIÓN</span>
          <h1>Datos del gimnasio</h1>
          <p>
            Contacto, redes sociales, mapa y logo que se muestran en la página pública
            (inicio, tienda, avisos y pantallas de acceso) -- cambiarlos acá no requiere tocar código.
          </p>
        </div>
      </section>

      {error && <p className="error-message">{error}</p>}
      {mensaje && <p className="success-message">{mensaje}</p>}

      <form onSubmit={guardar} className="form-card">
        <div className="card-header">
          <div>
            <h2>Contacto y redes sociales</h2>
            <p>Se muestran en la sección "¿Listo para entrenar mejor?" de la página de inicio.</p>
          </div>
        </div>

        <div className="form-grid">
          <div className="form-field">
            <label htmlFor="telefono">Teléfono</label>
            <input id="telefono" name="telefono" placeholder="Ej: +51 902321009" value={form.telefono} onChange={cambiar} />
          </div>

          <div className="form-field">
            <label htmlFor="email">Email</label>
            <input id="email" name="email" type="email" placeholder="Ej: contacto@gleyforgym.com" value={form.email} onChange={cambiar} />
          </div>

          <div className="form-field field-large">
            <label htmlFor="direccion">Dirección</label>
            <input id="direccion" name="direccion" placeholder="Ej: Chupaca, Perú" value={form.direccion} onChange={cambiar} />
          </div>

          <div className="form-field">
            <label htmlFor="whatsapp_numero">Número de WhatsApp</label>
            <input
              id="whatsapp_numero"
              name="whatsapp_numero"
              placeholder="Ej: 51902321009 (con código de país, sin + ni espacios)"
              value={form.whatsapp_numero}
              onChange={cambiar}
            />
          </div>

          <div className="form-field">
            <label htmlFor="facebook_url">Facebook (enlace completo)</label>
            <input id="facebook_url" name="facebook_url" placeholder="https://www.facebook.com/..." value={form.facebook_url} onChange={cambiar} />
          </div>

          <div className="form-field">
            <label htmlFor="instagram_url">Instagram (enlace completo)</label>
            <input id="instagram_url" name="instagram_url" placeholder="https://www.instagram.com/..." value={form.instagram_url} onChange={cambiar} />
          </div>

          <div className="form-field">
            <label htmlFor="tiktok_url">TikTok (enlace completo)</label>
            <input id="tiktok_url" name="tiktok_url" placeholder="https://www.tiktok.com/@..." value={form.tiktok_url} onChange={cambiar} />
          </div>

          <div className="form-field field-large">
            <label htmlFor="mapa_embed_url">Enlace para insertar el mapa</label>
            <input
              id="mapa_embed_url"
              name="mapa_embed_url"
              placeholder="Pega acá la URL que da Google Maps en Compartir → Insertar un mapa"
              value={form.mapa_embed_url}
              onChange={cambiar}
            />
            <p className="muted-text" style={{ margin: 0 }}>
              Si lo dejas vacío, la página de inicio no muestra el mapa.
            </p>
          </div>

          <div className="form-field field-large">
            <label htmlFor="logo">Logo del gimnasio</label>
            <input id="logo" ref={fileRef} type="file" accept="image/*" onChange={(e) => setLogo(e.target.files[0] || null)} />
            <div className="image-preview">
              <img src={logo ? URL.createObjectURL(logo) : (logoActualUrl || logoDefecto)} alt="Logo actual" />
            </div>
            <p className="muted-text" style={{ margin: 0 }}>
              Déjalo vacío para conservar el logo actual.
            </p>
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn-primary" disabled={guardando}>
            {guardando ? "Guardando..." : "Guardar configuración"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default Configuracion;
