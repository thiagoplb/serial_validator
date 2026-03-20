# Serial Validator

REST API para validação de seriais de software vinculados a máquinas específicas.

## Stack

- **Runtime**: Python 3.11+, gerenciado com `uv`
- **Framework**: FastAPI
- **ORM**: SQLAlchemy + SQLite
- **Migrations**: Alembic
- **Config**: python-dotenv

## Comandos essenciais

```bash
# Rodar a API em desenvolvimento
python -m uv run uvicorn app.main:app --reload

# Aplicar migrations
python -m uv run alembic upgrade head

# Gerar nova migration após alterar models.py
python -m uv run alembic revision --autogenerate -m "descrição"

# Adicionar dependência
python -m uv add <pacote>
```

## Estrutura

```
app/
  config.py          # Lê ADMIN_API_KEY e DATABASE_URL do .env
  database.py        # Engine, SessionLocal, Base, get_db()
  models.py          # Modelo Serial (tabela serials)
  schemas.py         # Pydantic schemas (request/response)
  main.py            # FastAPI app, inclui os routers
  routers/
    admin.py         # Endpoints admin (protegidos por X-Admin-Key)
    validate.py      # POST /validate (público)
  services/
    serial_service.py  # Lógica de validação do serial
client/
  fingerprint.py     # Módulo standalone: get_fingerprint() -> str
alembic/             # Migrations
```

## Variáveis de ambiente (`.env`)

```
ADMIN_API_KEY=<chave-forte>
DATABASE_URL=sqlite:///./serials.db
```

O arquivo `.env` é ignorado pelo git. Nunca comitar.

## Autenticação admin

Todos os endpoints `/admin/*` exigem o header `X-Admin-Key` com o valor de `ADMIN_API_KEY`.

## Endpoints

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| POST | `/admin/serials` | Admin | Criar serial |
| GET | `/admin/serials` | Admin | Listar seriais |
| GET | `/admin/serials/{id}` | Admin | Detalhe do serial |
| PATCH | `/admin/serials/{id}/revoke` | Admin | Revogar serial |
| POST | `/validate` | Nenhuma | Validar serial + fingerprint |

## Lógica de validação (`POST /validate`)

1. Serial não encontrado → `401 { valid: false, message: "Serial inválido" }`
2. `is_active = false` → `403 { valid: false, message: "Serial revogado" }`
3. `expires_at` expirado → `403 { valid: false, message: "Serial expirado" }`
4. `pre_bound_fingerprint` definido e não bate → `403 { valid: false, message: "Máquina não autorizada" }`
5. `fingerprint` nulo → vincula agora → `200 { valid: true }`
6. `fingerprint` bate → `200 { valid: true }`
7. `fingerprint` não bate → `403 { valid: false, message: "Serial já ativado em outra máquina" }`

## Modelo de dados (`serials`)

| Campo | Tipo | Observação |
|---|---|---|
| `id` | String PK | UUID gerado automaticamente |
| `serial_key` | String unique | Chave que o usuário digita |
| `fingerprint` | String nullable | SHA-256 do hardware — nulo até ativação |
| `pre_bound_fingerprint` | String nullable | Pré-vinculado pelo admin (seriais de reposição) |
| `expires_at` | DateTime nullable | Expiração opcional |
| `is_active` | Boolean | Padrão `true`; admin pode revogar |
| `created_at` | DateTime | Definido automaticamente |

## Fingerprint do cliente

O módulo `client/fingerprint.py` é autônomo (sem dependências externas além da stdlib).
Coleta: endereço MAC + serial do disco + identificador de CPU → SHA-256 hexadecimal.
Compatível com Windows (wmic) e Linux (blkid).
