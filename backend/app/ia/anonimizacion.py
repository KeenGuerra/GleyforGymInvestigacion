def codigo_cliente(id_cliente: int) -> str:
    """Código anónimo determinístico (C-001, C-002...) — nunca se envía el
    nombre/DNI/teléfono del cliente a servicios externos (reportes para la
    tesis, integración con Claude)."""
    return f"C-{id_cliente:03d}"
