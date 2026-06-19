# Formulario ASIC

Aplicacion web con dos capas para la seleccion de grupo de capacitacion de la Escuela Popular de Artes y Oficios.

## Estructura

```text
backend/
  app/
    domain/          Reglas y contratos del negocio
    application/     Casos de uso y DTOs
    infrastructure/  HTTP, seguridad, SQLite y exportadores
frontend/
  src/
    features/        Modulos por funcionalidad
    shared/          Tipos y cliente API compartidos
```

## Ejecutar local

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

## Despliegue

- Vercel: desplegar `frontend`, configurar `VITE_API_BASE_URL=https://tu-backend.railway.app/api`.
- Railway: desplegar `backend`, agregar PostgreSQL en el mismo proyecto y configurar `DATABASE_URL`, `JWT_SECRET`, `ADMIN_USERNAME`, `ADMIN_PASSWORD` y `CORS_ORIGINS`.

## Seguridad aplicada

- Login admin con token firmado HS256 y expiracion.
- CORS configurable por ambiente.
- Rate limit simple para login.
- Consultas SQL parametrizadas.
- Paginacion y limite maximo en listados internos.
- Documento unico por restriccion de base de datos y validacion de caso de uso.
- Cupos validados antes de crear o editar respuestas.
- Validacion de nombres/apellidos solo con letras y documentos/telefonos solo numericos.
