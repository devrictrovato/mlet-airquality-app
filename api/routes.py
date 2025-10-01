from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from services.scraper import AirQualityScraper
from services.aws_service import AWSService

air_quality_router = APIRouter()


@air_quality_router.post("/aws/configure", summary="Configurar e testar credenciais AWS")
async def configure_aws(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_session_token: str = None,
    aws_region: str = "us-east-1",
    s3_bucket: str = None,
    s3_prefix: str = "raw"
):
    """
    Configura e testa as credenciais AWS para upload dos dados.
    
    - **aws_access_key_id**: Access Key ID da AWS
    - **aws_secret_access_key**: Secret Access Key da AWS
    - **aws_session_token**: Session Token (opcional, para labs temporários)
    - **aws_region**: Região AWS (padrão: us-east-1)
    - **s3_bucket**: Nome do bucket S3
    - **s3_prefix**: Prefixo para os arquivos (padrão: raw)
    
    Este endpoint valida a conexão tentando acessar o bucket S3 especificado.
    """
    try:
        # Validações básicas
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
        
        # Validar formato do Access Key
        # if not aws_access_key_id.startswith('AKIA'):
        #     raise HTTPException(
        #         status_code=400,
        #         detail="Access Key ID inválido. Deve começar com 'AKIA'"
        #     )
        
        # Configurar AWS Service
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
            "message": "Credenciais AWS configuradas e validadas com sucesso",
            "region": aws_region,
            "bucket": s3_bucket,
            "prefix": s3_prefix,
            "connection_test": "passed"
        }
    except HTTPException:
        raise
    except Exception as e:
        error_message = str(e)
        
        # Mensagens de erro mais amigáveis
        if "InvalidAccessKeyId" in error_message:
            detail = "Access Key ID inválido. Verifique suas credenciais."
        elif "SignatureDoesNotMatch" in error_message:
            detail = "Secret Access Key incorreto. Verifique suas credenciais."
        elif "ExpiredToken" in error_message:
            detail = "Session Token expirado. Gere novas credenciais no AWS Lab."
        elif "NoSuchBucket" in error_message:
            detail = f"Bucket '{s3_bucket}' não encontrado. Verifique o nome e a região."
        elif "AccessDenied" in error_message or "Forbidden" in error_message:
            detail = "Acesso negado ao bucket. Verifique as permissões IAM."
        else:
            detail = f"Erro ao configurar AWS: {error_message}"
        
        raise HTTPException(status_code=400, detail=detail)


@air_quality_router.get(
    "/stations/realtime",
    response_model=List[Dict[str, Any]],
    summary="Obter dados em tempo real de todas as estações"
)
async def get_realtime_data() -> List[Dict[str, Any]]:
    """
    Retorna os dados em tempo real de qualidade do ar de todas as estações.
    
    O scraping é feito do site aqicn.org e os dados incluem:
    - Nome da estação
    - País, estado e cidade
    - Poluentes (PM2.5, PM10, NO2, SO2, CO)
    - Condições meteorológicas (temperatura, pressão, umidade, vento)
    - AQI (Air Quality Index)
    
    Os dados são automaticamente salvos no S3 se as credenciais estiverem configuradas.
    """
    try:
        scraper = AirQualityScraper()
        results = await scraper.scrape_all_stations()
        
        if not results:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma estação válida encontrada"
            )
        
        # Tentar salvar no S3
        try:
            aws_service = AWSService()
            aws_service.save_to_s3(results)
        except Exception as e:
            print(f"⚠️ Dados não foram salvos no S3: {str(e)}")
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar estações: {str(e)}"
        )


@air_quality_router.get(
    "/stations/count",
    summary="Contar estações disponíveis"
)
async def count_stations():
    """Retorna o número de estações disponíveis para scraping"""
    try:
        scraper = AirQualityScraper()
        count = await scraper.count_stations()
        return {
            "total_stations": count,
            "status": "available"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao contar estações: {str(e)}"
        )


@air_quality_router.get("/aws/status", summary="Verificar status da configuração AWS")
async def check_aws_status():
    """
    Verifica se as credenciais AWS estão configuradas e válidas.
    
    Retorna informações sobre:
    - Status da configuração
    - Região configurada
    - Bucket configurado
    - Prefixo dos arquivos
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
            "message": "AWS configurado e conectado",
            "bucket": aws_service.bucket,
            "prefix": aws_service.prefix
        }
    except Exception as e:
        return {
            "configured": False,
            "status": "error",
            "message": f"Erro ao verificar status: {str(e)}"
        }