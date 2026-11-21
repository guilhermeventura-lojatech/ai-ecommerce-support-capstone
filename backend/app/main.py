from fastapi import FastAPI

from backend.app.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI E-commerce Support Capstone",
        description="Etapa 1: regras deterministicas e escalonamento humano simulado.",
        version="0.1.0",
    )
    app.include_router(router)
    return app


app = create_app()

