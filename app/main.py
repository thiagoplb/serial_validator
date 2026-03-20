from fastapi import FastAPI
from app.routers import admin, validate

app = FastAPI(title="Serial Validator")

app.include_router(admin.router)
app.include_router(validate.router)
