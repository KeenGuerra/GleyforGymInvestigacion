# Guía de Despliegue

# SistemaGimnasioGleyforGym

## 1. Introducción

Este documento describe el proceso de despliegue del SistemaGimnasioGleyforGym en ambientes de producción.

Incluye:

- Backend FastAPI
- Frontend React
- PostgreSQL
- Cloudinary
- Flutter
- Docker (futuro)

---

# 2. Arquitectura de Producción

```text
Internet
    │
    ▼
Dominio
    │
    ▼
Nginx
    │
    ├───────────────┐
    │               │
    ▼               ▼
Frontend       Backend
React          FastAPI
    │               │
    └───────┬───────┘
            │
            ▼
      PostgreSQL
            │
            ▼
       Cloudinary
```

---

# 3. Opciones de Despliegue

## Opción 1

Servidor VPS

Ejemplos:

- Contabo
- Hostinger VPS
- Digital Ocean
- Vultr

---

## Opción 2

Cloud

Ejemplos:

- AWS
- Azure
- Google Cloud

---

## Opción 3

PaaS

Ejemplos:

- Railway
- Render
- Fly.io

---

# 4. Requisitos del Servidor

## Mínimos

| Recurso | Valor |
|----------|----------|
| CPU | 2 vCPU |
| RAM | 4 GB |
| Disco | 50 GB SSD |

---

## Recomendados

| Recurso | Valor |
|----------|----------|
| CPU | 4 vCPU |
| RAM | 8 GB |
| Disco | 100 GB SSD |

---

# 5. Sistema Operativo

Recomendado:

```text
Ubuntu 24.04 LTS
```

---

# 6. Instalación de Dependencias

Actualizar servidor:

```bash
sudo apt update
sudo apt upgrade -y
```

---

Instalar Git:

```bash
sudo apt install git -y
```

---

Instalar Python:

```bash
sudo apt install python3 python3-pip python3-venv -y
```

---

Instalar Node.js:

```bash
sudo apt install nodejs npm -y
```

---

# 7. Despliegue Backend

## Clonar Proyecto

```bash
git clone REPOSITORIO

cd backend
```

---

## Crear Entorno Virtual

```bash
python3 -m venv venv
```

---

## Activar

```bash
source venv/bin/activate
```

---

## Instalar Dependencias

```bash
pip install -r requirements.txt
```

---

## Configurar .env

```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/gleyforgym

SECRET_KEY=clave_produccion

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60

CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

---

## Ejecutar Backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

# 8. Configurar Servicio Linux

Crear:

```bash
sudo nano /etc/systemd/system/gleyforgym.service
```

Contenido:

```ini
[Unit]
Description=GLEYFORGYM API

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/gleyforgym/backend
ExecStart=/home/ubuntu/gleyforgym/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

---

Activar:

```bash
sudo systemctl daemon-reload

sudo systemctl enable gleyforgym

sudo systemctl start gleyforgym
```

---

Verificar:

```bash
sudo systemctl status gleyforgym
```

---

# 9. Despliegue Frontend

Entrar:

```bash
cd web-admin
```

---

Instalar:

```bash
npm install
```

---

Compilar:

```bash
npm run build
```

---

Se genera:

```text
dist/
```

---

# 10. Instalar Nginx

```bash
sudo apt install nginx -y
```

---

Copiar frontend:

```bash
sudo cp -r dist/* /var/www/html/
```

---

Reiniciar:

```bash
sudo systemctl restart nginx
```

---

# 11. Configuración PostgreSQL

Instalar:

```bash
sudo apt install postgresql postgresql-contrib -y
```

---

Ingresar:

```bash
sudo -u postgres psql
```

---

Crear base:

```sql
CREATE DATABASE gleyforgym;
```

---

Crear usuario:

```sql
CREATE USER gleyforgym_user
WITH PASSWORD 'password_seguro';
```

---

Permisos:

```sql
GRANT ALL PRIVILEGES
ON DATABASE gleyforgym
TO gleyforgym_user;
```

---

# 12. Configuración Cloudinary

Crear cuenta:

```text
https://cloudinary.com
```

---

Obtener:

```text
Cloud Name
API Key
API Secret
```

---

Agregar:

```env
CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

---

# 13. Configuración HTTPS

Instalar Certbot:

```bash
sudo apt install certbot python3-certbot-nginx -y
```

---

Generar certificado:

```bash
sudo certbot --nginx
```

---

Resultado:

```text
HTTPS habilitado
```

---

# 14. Dominio

Ejemplo:

```text
www.gleyforgym.com
```

DNS:

```text
A Record
→ IP del servidor
```

---

# 15. Docker (Futuro)

Estructura recomendada:

```text
docker-compose.yml

backend
frontend
postgres
nginx
```

---

Arquitectura:

```text
Docker
│
├── FastAPI
├── React
├── PostgreSQL
└── Nginx
```

---

# 16. Backup de Base de Datos

Crear respaldo:

```bash
pg_dump gleyforgym > backup.sql
```

---

Restaurar:

```bash
psql gleyforgym < backup.sql
```

---

# 17. Monitoreo

Herramientas sugeridas:

- Grafana
- Prometheus
- Uptime Kuma

---

# 18. Seguridad

## Recomendaciones

### No exponer

```text
SECRET_KEY
API_SECRET
DATABASE_PASSWORD
```

---

### Utilizar

```text
HTTPS
JWT
Firewall
```

---

### Configurar

```bash
sudo ufw allow 80

sudo ufw allow 443

sudo ufw allow 22
```

---

# 19. Checklist de Producción

Verificar:

- Backend funcionando.
- Frontend funcionando.
- PostgreSQL funcionando.
- Cloudinary funcionando.
- HTTPS activo.
- Dominio configurado.
- Backup configurado.
- Logs funcionando.

---

# 20. Estado Actual

## Implementado

✅ FastAPI

✅ PostgreSQL

✅ React

✅ Flutter

✅ JWT

✅ Cloudinary

✅ IA

---

## Próximo Objetivo

```text
Dockerizar el sistema completo
```

---

## Futuro

```text
SaaS Multi Gimnasio
AWS
Escalado Horizontal
Microservicios
```

---