import React from "react";

function CheckoutModal({ info, onClose }) {
  if (!info) return null;

  return (
    <div className="checkout-modal-overlay" onClick={onClose}>
      <div className="checkout-modal" onClick={(e) => e.stopPropagation()}>
        <h3>Completar pago</h3>
        <p>Elige cómo pagar:</p>

        {info.qr_yape && (
          <div className="checkout-modal-qr">
            <img src={info.qr_yape} alt="Código QR para pagar con Yape" />
            <p>Escanea con la app de Yape</p>
          </div>
        )}

        <a
          className="btn-primary"
          href={info.url_checkout}
          target="_blank"
          rel="noopener noreferrer"
        >
          Pagar con PagoEfectivo
        </a>

        <button className="btn-secondary" onClick={onClose}>
          Cerrar
        </button>
      </div>
    </div>
  );
}

export default CheckoutModal;
