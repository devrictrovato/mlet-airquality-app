import io
import joblib
import numpy as np
from typing import List, Dict, Any
from services.aws_service import AWSService


class ModelService:
    """Serviço para gerenciar predições do modelo de ML"""
    
    _instance = None
    _model = None
    _model_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.model_key = "models/air_quality_model.joblib"
            self.initialized = True
    
    async def load_model(self) -> bool:
        """
        Carrega o modelo do S3.
        
        Returns:
            True se carregado com sucesso, False caso contrário
        """
        if self._model_loaded:
            return True
        
        try:
            aws_service = AWSService()
            
            if not aws_service.is_configured():
                raise ValueError("AWS não configurado")
            
            # Download do modelo do S3
            response = aws_service.s3_client.get_object(
                Bucket=aws_service.bucket,
                Key=self.model_key
            )
            
            model_bytes = response['Body'].read()
            model_buffer = io.BytesIO(model_bytes)
            
            # Carregar modelo
            self._model = joblib.load(model_buffer)
            self._model_loaded = True
            
            print(f"✅ Modelo carregado do S3: {self.model_key}")
            return True
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar modelo: {str(e)}")
            self._model_loaded = False
            return False
    
    async def predict(self, features: List[float]) -> int:
        """
        Realiza predição baseada nas features fornecidas.
        
        Args:
            features: Lista com 9 valores [pm25, pm10, no2, so2, co, temp, pressure, humidity, wind]
        
        Returns:
            Predição: 0 (Saudável), 1 (Atenção), 2 (Perigoso)
        """
        # Tentar carregar modelo se não estiver carregado
        if not self._model_loaded:
            loaded = await self.load_model()
            if not loaded:
                raise ValueError("Modelo não pôde ser carregado")
        
        # Validar número de features
        if len(features) != 9:
            raise ValueError(f"Esperado 9 features, recebido {len(features)}")
        
        # Converter para array numpy e reshape
        X = np.array(features).reshape(1, -1)
        
        # Fazer predição
        prediction = self._model.predict(X)
        
        return int(prediction[0])
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna status do modelo.
        
        Returns:
            Dicionário com informações do status
        """
        if not self._model_loaded:
            await self.load_model()
        
        return {
            "loaded": self._model_loaded,
            "status": "ready" if self._model_loaded else "not_loaded",
            "model_path": self.model_key,
            "features_expected": 9,
            "feature_names": [
                "pm25", "pm10", "no2", "so2", "co", 
                "temperature", "pressure", "humidity", "wind"
            ],
            "output_classes": {
                "0": "Saudável",
                "1": "Atenção",
                "2": "Perigoso"
            }
        }