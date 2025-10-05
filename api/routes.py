from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from services.scraper import AirQualityScraper
from services.aws_service import AWSService
from services.model_service import ModelService

air_quality_router = APIRouter()


class PredictionInput(BaseModel):
    pm25: float
    pm10: float
    no2: float
    so2: float
    co: float
    temperature: float
    pressure: float
    humidity: float
    wind: float


@air_quality_router.post("/aws/configure", summary="Configurar credenciais AWS")
async def configure_aws(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_session_token: str = None,
    aws_region: str = "us-east-1",
    s3_bucket: str = None,
    s3_prefix: str = "raw"
):
    """
    Configura e valida credenciais AWS para acesso ao S3.
    """
    try:
        if not aws_access_key_id or not aws_secret_access_key:
            raise HTTPException(
                status_code=400, 
                detail="Access Key e Secret Key são obrigatórios"
            )
        
        if not s3_bucket:
            raise HTTPException(
                status_code=400, 
                detail="Nome do bucket S3 é obrigatório"
            )
        
        aws_service = AWSService()
        aws_service.configure(
            access_key=aws_access_key_id,
            secret_key=aws_secret_access_key,
            session_token=aws_session_token,
            region=aws_region,
            bucket=s3_bucket,
            prefix=s3_prefix
        )
        
        return {
            "status": "success",
            "message": "Credenciais AWS configuradas com sucesso",
            "region": aws_region,
            "bucket": s3_bucket,
            "prefix": s3_prefix
        }
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        
        if "InvalidAccessKeyId" in error_message:
            detail = "Access Key ID inválido"
        elif "SignatureDoesNotMatch" in error_message:
            detail = "Secret Access Key incorreto"
        elif "ExpiredToken" in error_message:
            detail = "Session Token expirado"
        elif "NoSuchBucket" in error_message:
            detail = f"Bucket '{s3_bucket}' não encontrado"
        elif "AccessDenied" in error_message or "Forbidden" in error_message:
            detail = "Acesso negado ao bucket"
        else:
            detail = f"Erro ao configurar AWS: {error_message}"
        
        raise HTTPException(status_code=400, detail=detail)


@air_quality_router.get("/aws/status", summary="Verificar status AWS")
async def check_aws_status():
    """
    Verifica se as credenciais AWS estão configuradas.
    """
    try:
        aws_service = AWSService()
        
        if not aws_service.is_configured():
            return {
                "configured": False,
                "status": "not_configured",
                "message": "Credenciais AWS não configuradas"
            }
        
        return {
            "configured": True,
            "status": "connected",
            "message": "AWS configurado",
            "bucket": aws_service.bucket,
            "prefix": aws_service.prefix
        }
    except Exception as e:
        return {
            "configured": False,
            "status": "error",
            "message": f"Erro: {str(e)}"
        }


@air_quality_router.post("/stations/collect", summary="Coletar dados de estações")
async def collect_station_data() -> Dict[str, Any]:
    """
    Coleta dados de todas as estações e salva no S3.
    """
    try:
        scraper = AirQualityScraper()
        results = await scraper.scrape_all_stations()
        
        if not results:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma estação encontrada"
            )
        
        # Salvar no S3
        try:
            aws_service = AWSService()
            s3_key = aws_service.save_to_s3(results)
            return {
                "status": "success",
                "message": "Dados coletados e salvos com sucesso",
                "total_stations": len(results),
                "s3_key": s3_key
            }
        except Exception as e:
            return {
                "status": "partial_success",
                "message": "Dados coletados mas não salvos no S3",
                "total_stations": len(results),
                "s3_error": str(e)
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao coletar dados: {str(e)}"
        )


@air_quality_router.post("/predict", summary="Prever qualidade do ar")
async def predict_air_quality(input_data: PredictionInput):
    """
    Prediz a qualidade do ar baseado nos parâmetros fornecidos.
    
    Retorna:
    - 0: Saudável (ar de boa qualidade)
    - 1: Atenção (requer cuidados para grupos sensíveis)
    - 2: Perigoso (nocivo para todos)
    """
    try:
        model_service = ModelService()
        
        # Preparar dados para predição
        features = [
            input_data.pm25,
            input_data.pm10,
            input_data.no2,
            input_data.so2,
            input_data.co,
            input_data.temperature,
            input_data.pressure,
            input_data.humidity,
            input_data.wind
        ]
        
        prediction = await model_service.predict(features)
        
        # Mapear predição para categoria
        categories = {
            0: {
                "label": "Saudável",
                "description": "Ar de boa qualidade. Seguro para atividades ao ar livre.",
                "color": "success",
                "recommendation": "Aproveite atividades ao ar livre normalmente."
            },
            1: {
                "label": "Atenção",
                "description": "Qualidade moderada. Grupos sensíveis devem limitar exposição prolongada.",
                "color": "warning",
                "recommendation": "Pessoas sensíveis devem considerar reduzir atividades intensas ao ar livre."
            },
            2: {
                "label": "Perigoso",
                "description": "Ar de qualidade ruim. Nocivo para todos.",
                "color": "danger",
                "recommendation": "Evite atividades ao ar livre. Mantenha janelas fechadas."
            }
        }
        
        result = categories.get(prediction, categories[1])
        
        return {
            "prediction": int(prediction),
            "category": result["label"],
            "description": result["description"],
            "color": result["color"],
            "recommendation": result["recommendation"],
            "input_values": {
                "pm25": input_data.pm25,
                "pm10": input_data.pm10,
                "no2": input_data.no2,
                "so2": input_data.so2,
                "co": input_data.co,
                "temperature": input_data.temperature,
                "pressure": input_data.pressure,
                "humidity": input_data.humidity,
                "wind": input_data.wind
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao fazer predição: {str(e)}"
        )


@air_quality_router.get("/model/status", summary="Verificar status do modelo")
async def check_model_status():
    """
    Verifica se o modelo está carregado e pronto para predições.
    """
    try:
        model_service = ModelService()
        status = await model_service.get_status()
        return status
    except Exception as e:
        return {
            "loaded": False,
            "status": "error",
            "message": str(e)
        }