import os
import io
import pandas as pd
import boto3
from dotenv import load_dotenv
from datetime import datetime

# Carrega variáveis do .env
load_dotenv()

# Variáveis do ambiente
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_PREFIX = os.getenv("S3_PREFIX", "raw")

# Inicializa o cliente S3
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=AWS_REGION
)


def save_parquet_to_s3(
    data: list[dict], 
    bucket: str = S3_BUCKET, 
    prefix: str = S3_PREFIX
):
    """
    Salva uma lista de dicionários como arquivo Parquet (com compressão Snappy)
    em um bucket S3, usando uma partição baseada na data atual.
    """
    if not data:
        print("⚠️ Nenhum dado recebido para salvar.")
        return

    # Converte para DataFrame
    df = pd.DataFrame(data)
    if df.empty:
        print("⚠️ DataFrame convertido está vazio.")
        return

    # Adiciona coluna 'date' se não existir
    now = datetime.utcnow()
    if 'date' not in df.columns:
        df['date'] = now
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')

    # Cria strings para partição e nome do arquivo
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H-%M-%S")

    s3_key = f"{prefix}/date={date_str}/sample-aqi-{time_str}.snappy.parquet"

    # Escreve o arquivo em memória
    buffer = io.BytesIO()
    df.to_parquet(
        buffer,
        index=False,
        engine="pyarrow",
        compression="snappy"
    )
    buffer.seek(0)

    # Envia para o S3
    s3.upload_fileobj(buffer, bucket, s3_key)
    print(f"✅ Arquivo salvo em s3://{bucket}/{s3_key}")
