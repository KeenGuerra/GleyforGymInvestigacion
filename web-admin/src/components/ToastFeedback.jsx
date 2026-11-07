import React from "react";
import PropTypes from "prop-types";

/**
 * Notificación flotante usando las clases de alerta/toast de Bootstrap (ver
 * src/styles/bootstrap-custom.scss) — visibilidad controlada por React
 * (useToast), no por el runtime JS de Bootstrap.
 */
function ToastFeedback({ toast, onClose }) {
  if (!toast) return null;

  return (
    <div
      className="position-fixed top-0 end-0 p-3"
      style={{ zIndex: 1080 }}
      role="alert"
    >
      <div className={`toast show align-items-center text-bg-${toast.tipo} border-0`}>
        <div className="d-flex">
          <div className="toast-body">{toast.mensaje}</div>
          <button
            type="button"
            className="btn-close btn-close-white me-2 m-auto"
            aria-label="Cerrar"
            onClick={onClose}
          ></button>
        </div>
      </div>
    </div>
  );
}

ToastFeedback.propTypes = {
  toast: PropTypes.shape({
    tipo: PropTypes.oneOf(["danger", "success"]).isRequired,
    mensaje: PropTypes.string.isRequired,
  }),
  onClose: PropTypes.func.isRequired,
};

export default ToastFeedback;
