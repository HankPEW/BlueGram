from fastapi import FastAPI
from src.api.routes import main_router


app = FastAPI(title = "BlueGram API")


app.include_router(main_router)
