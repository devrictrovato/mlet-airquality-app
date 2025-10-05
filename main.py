from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from api.routes import air_quality_router
from pathlib import Path

app = FastAPI(
    title="Air Quality Predictor",
    description="Sistema Inteligente de Predição de Qualidade do Ar usando Machine Learning",
    version="3.0.0"
)

# Configurar diretórios
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Montar arquivos estáticos (se houver CSS, JS, imagens)
try:
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
except:
    pass  # Diretório static é opcional

# Incluir rotas da API
app.include_router(air_quality_router, prefix="/api", tags=["Air Quality"])


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    """
    Página inicial - Dashboard principal com navegação
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/config", response_class=HTMLResponse, include_in_schema=False)
async def config_page(request: Request):
    """
    Página de configuração de credenciais AWS
    """
    return templates.TemplateResponse("aws_form.html", {"request": request})


@app.get("/predict", response_class=HTMLResponse, include_in_schema=False)
async def predict_page(request: Request):
    """
    Página de predição de qualidade do ar
    """
    return templates.TemplateResponse("predict.html", {"request": request})


@app.get("/collect", response_class=HTMLResponse, include_in_schema=False)
async def collect_page(request: Request):
    """
    Página de coleta de dados de estações
    """
    return templates.TemplateResponse("collect.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)