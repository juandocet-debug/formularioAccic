# Backend - Formulario ASIC

API interna y publica para el formulario de seleccion de grupos.

## Desarrollo local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

La base SQLite local se crea automaticamente en `data/formulario_asic.sqlite3`.

## Variables importantes

- `JWT_SECRET`: obligatorio cambiarlo en produccion.
- `ADMIN_USERNAME` y `ADMIN_PASSWORD`: credenciales fijas del super administrador. En desarrollo, las credenciales de prueba son `superadmin` / `change-this-password`.
- `CORS_ORIGINS`: origenes permitidos separados por coma.
- `DATABASE_PATH`: ruta SQLite local de desarrollo.
- `DATABASE_URL`: URL PostgreSQL para Railway/produccion. Si existe, el backend usa PostgreSQL automaticamente.

## Endpoints

- `GET /api/public/groups`
- `POST /api/public/registrations`
- `POST /api/auth/login`
- `GET /api/admin/registrations`
- `GET /api/admin/capacity`
- `PUT /api/admin/registrations/{id}`
- `DELETE /api/admin/registrations/{id}`
- `GET /api/admin/exports/excel`
- `GET /api/admin/exports/pdf`
