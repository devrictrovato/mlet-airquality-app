import io
import os
import pandas as pd
import boto3
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv


class AWSService:
    """Serviço para gerenciar operações com AWS S3"""
    
    _instance = None
    _configured = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            load_dotenv()
            self.s3_client = None
            self.bucket = None
            self.prefix = "raw"
            self.initialized = True
            
            # Tentar carregar do .env
            self._load_from_env()
    
    def _load_from_env(self):
        """Carrega credenciais do arquivo .env se disponível"""
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        session_token = os.getenv("AWS_SESSION_TOKEN")
        region = os.getenv("AWS_REGION", "us-east-1")
        bucket = os.getenv("S3_BUCKET")
        prefix = os.getenv("S3_PREFIX", "raw")
        
        if access_key and secret_key and bucket:
            try:
                self.configure(
                    access_key=access_key,
                    secret_key=secret_key,
                    session_token=session_token,
                    region=region,
                    bucket=bucket,
                    prefix=prefix
                )
            except Exception as e:
                print(f"⚠️ Erro ao carregar credenciais do .env: {str(e)}")
    
    def configure(
        self,
        access_key: str,
        secret_key: str,
        session_token: Optional[str] = None,
        region: str = "us-east-1",
        bucket: str = None,
        prefix: str = "raw"
    ):
        """
        Configura as credenciais AWS.
        
        Args:
            access_key: AWS Access Key ID
            secret_key: AWS Secret Access Key
            session_token: AWS Session Token (opcional)
            region: Região AWS
            bucket: Nome do bucket S3
            prefix: Prefixo para os arquivos
        """
        if not bucket:
            raise ValueError("Bucket S3 é obrigatório")
        
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token,
            region_name=region
        )
        
        self.bucket = bucket
        self.prefix = prefix
        self._configured = True
        
        # Validar credenciais tentando listar buckets
        try:
            self.s3_client.head_bucket(Bucket=bucket)
            print(f"✅ Conectado ao bucket S3: {bucket}")
        except Exception as e:
            raise ValueError(f"Erro ao validar bucket S3: {str(e)}")
    
    def is_configured(self) -> bool:
        """Verifica se o serviço está configurado"""
        return self._configured and self.s3_client is not None
    
    def save_to_s3(self, data: List[Dict[str, Any]]) -> str:
        """
        Salva dados como arquivo Parquet no S3.
        
        Args:
            data: Lista de dicionários com os dados
            
        Returns:
            Chave S3 do arquivo salvo
        """
        if not self.is_configured():
            raise ValueError("Serviço AWS não está configurado. Configure as credenciais primeiro.")
        
        if not data:
            raise ValueError("Nenhum dado recebido para salvar")
        
        # Converter para DataFrame
        df = pd.DataFrame(data)
        
        if df.empty:
            raise ValueError("DataFrame está vazio")
        
        # Garantir coluna de data
        now = datetime.utcnow()
        if 'date' not in df.columns:
            df['date'] = now
        
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Criar chave S3 com particionamento por data
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H-%M-%S")
        s3_key = f"{self.prefix}/date={date_str}/aqi-data-{time_str}.snappy.parquet"
        
        # Escrever Parquet em memória
        buffer = io.BytesIO()
        df.to_parquet(
            buffer,
            index=False,
            engine="pyarrow",
            compression="snappy"
        )
        buffer.seek(0)
        
        # Upload para S3
        self.s3_client.upload_fileobj(buffer, self.bucket, s3_key)
        print(f"✅ Arquivo salvo em s3://{self.bucket}/{s3_key}")
        
        return s3_key
    
    def list_files(self, max_keys: int = 100) -> List[str]:
        """
        Lista os arquivos no bucket S3.
        
        Args:
            max_keys: Número máximo de chaves a retornar
            
        Returns:
            Lista de chaves S3
        """
        if not self.is_configured():
            raise ValueError("Serviço AWS não está configurado")
        
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket,
            Prefix=self.prefix,
            MaxKeys=max_keys
        )
        
        return [obj['Key'] for obj in response.get('Contents', [])]