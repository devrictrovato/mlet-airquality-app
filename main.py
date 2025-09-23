from fastapi import FastAPI
from web.scrapping import router as air_qualiy_routes

app = FastAPI(title="Air Quality Classifier")

# Incluir rotas
app.include_router(air_qualiy_routes)
