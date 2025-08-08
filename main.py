import logging
from fastapi import FastAPI
from routers import employee
from core.error_handler import add_exception_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI()

add_exception_handlers(app)

app.include_router(employee.router)
