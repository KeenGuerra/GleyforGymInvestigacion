import React from "react";
import PropTypes from "prop-types";

/**
 * Modal de confirmación usando la estructura/clases de Bootstrap (modal,
 * ver src/styles/bootstrap-custom.scss) para el fondo/posición, y los
 * botones propios de la app (.btn-primary/.btn-secondary) para que se vea
 * igual que el resto de la UI -- visibilidad controlada por React
 * (useConfirmacion), no por el runtime JS de Bootstrap.
 */
function ConfirmModal({ pregunta, onResponder }) {
  if (!pregunta) return null;

  return (
    <>
      <div className="modal-backdrop show" style={{ zIndex: 1090 }}></div>
      <div
        className="modal d-block"
        tabIndex="-1"
        role="dialog"
        aria-modal="true"
        style={{ zIndex: 1091 }}
      >
        <div className="modal-dialog modal-dialog-centered">
          <div className="modal-content">
            <div className="modal-body">
              <p className="mb-0">{pregunta}</p>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn-secondary" onClick={() => onResponder(false)}>
                Cancelar
              </button>
              <button type="button" className="btn-primary" onClick={() => onResponder(true)}>
                Confirmar
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

ConfirmModal.propTypes = {
  pregunta: PropTypes.string,
  onResponder: PropTypes.func.isRequired,
};

export default ConfirmModal;
