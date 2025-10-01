from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from api.routes import air_quality_router
from pathlib import Path

app = FastAPI(
    title="Air Quality Classifier",
    description="Sistema de monitoramento e classificação de qualidade do ar",
    version="2.0.0"
)

# Configurar diretórios
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Montar arquivos estáticos (CSS, JS, imagens)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Incluir rotas da API
app.include_router(air_quality_router, prefix="/api", tags=["Air Quality"])


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    """Página inicial da aplicação"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/config", response_class=HTMLResponse, include_in_schema=False)
async def config_page(request: Request):
    """Página de configuração AWS"""
    return templates.TemplateResponse("aws_form.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)