# Air Quality Predictor 🌍

Sistema Inteligente de Predição de Qualidade do Ar usando Machine Learning

## 📋 Visão Geral

Sistema web completo para predição de qualidade do ar que integra:
- **Machine Learning**: Modelo treinado armazenado em S3
- **Data Collection**: Scraping em tempo real de estações globais
- **Cloud Integration**: AWS S3 para storage de modelos e dados
- **Interface Moderna**: Design responsivo com foco em UX

## 🎯 Funcionalidades Principais

### 1. Configuração AWS ⚙️
- Interface intuitiva para configuração de credenciais
- Validação em tempo real da conexão
- Suporte para AWS Academy Labs (session tokens)
- Feedback visual de status

### 2. Predição de Qualidade do Ar 🎯
- Input de 9 parâmetros atmosféricos
- Predição instantânea usando modelo ML
- Cenários pré-definidos para testes rápidos
- Classificação em 3 níveis:
  - **0: Saudável** - Ar de boa qualidade
  - **1: Atenção** - Moderado, cuidado com grupos sensíveis
  - **2: Perigoso** - Nocivo para todos

### 3. Coleta de Dados 📡
- Scraping de estações ao redor do mundo
- Salvamento automático em S3 (formato Parquet)
- Particionamento por data
- Progress tracking em tempo real

## 🏗️ Arquitetura

```
air-quality-predictor/
├── api/
│   └── routes.py              # Endpoints da API
├── services/
│   ├── aws_service.py         # Gerenciamento S3
│   ├── model_service.py       # ML Model Service (NOVO)
│   └── scraper.py             # Web scraping
├── templates/
│   ├── index.html             # Dashboard principal (NOVO)
│   ├── predict.html           # Interface de predição (NOVO)
│   ├── collect.html           # Coleta de dados (NOVO)
│   └── aws_form.html          # Config AWS (ATUALIZADO)
├── main.py                    # App FastAPI (ATUALIZADO)
├── .env                       # Variáveis de ambiente
└── requirements.txt           # Dependências
```

## 🚀 Instalação

### Pré-requisitos
- Python 3.8+
- Conta AWS com S3
- Modelo treinado no formato `.joblib`

### Dependências

```bash
pip install fastapi uvicorn boto3 pandas pyarrow \
    beautifulsoup4 requests python-dotenv pydantic \
    joblib scikit-learn numpy
```

### Arquivo .env (Opcional)

```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_SESSION_TOKEN=your_token
AWS_REGION=us-east-1
S3_BUCKET=your-bucket
S3_PREFIX=raw
```

## 📦 Modelo ML

O modelo deve estar no S3 no caminho:
```
s3://your-bucket/models/air_quality_model.joblib
```

### Features Esperadas (ordem)
1. `pm25` - Material particulado 2.5 (µg/m³)
2. `pm10` - Material particulado 10 (µg/m³)
3. `no2` - Dióxido de nitrogênio (ppb)
4. `so2` - Dióxido de enxofre (ppb)
5. `co` - Monóxido de carbono (ppm)
6. `temperature` - Temperatura (°C)
7. `pressure` - Pressão atmosférica (hPa)
8. `humidity` - Umidade relativa (%)
9. `wind` - Velocidade do vento (m/s)

### Classes de Saída
- `0`: Saudável
- `1`: Atenção
- `2`: Perigoso

## 🎮 Como Usar

### 1. Iniciar a Aplicação

```bash
python main.py
```

Acesse: `http://localhost:8000`

### 2. Configurar AWS

1. Clique em "Configurar AWS"
2. Insira as credenciais do AWS Lab
3. Teste a conexão
4. Salve

### 3. Fazer Predições

1. Clique em "Fazer Predição"
2. Insira os valores dos parâmetros
   - Use os presets para testes rápidos
3. Clique em "Fazer Predição"
4. Analise o resultado e recomendações

### 4. Coletar Dados (Opcional)

1. Configure o AWS primeiro
2. Clique em "Coletar Dados"
3. Clique em "Iniciar Coleta"
4. Aguarde o processamento
5. Dados salvos automaticamente no S3

## 🔌 API Endpoints

### Configuração
- `POST /api/aws/configure` - Configurar credenciais
- `GET /api/aws/status` - Verificar status AWS

### Predição
- `POST /api/predict` - Fazer predição
- `GET /api/model/status` - Status do modelo

### Coleta de Dados
- `POST /api/stations/collect` - Coletar dados

## 🎨 Design Principles

### UX/UI Focado em:
1. **Clareza**: Informações organizadas hierarquicamente
2. **Feedback**: Status em tempo real de todas operações
3. **Acessibilidade**: Design responsivo e intuitivo
4. **Confiança**: Validações e mensagens claras
5. **Eficiência**: Presets e atalhos para ações comuns

### Paleta de Cores
- **Primary**: #667eea (Azul-roxo)
- **Secondary**: #764ba2 (Roxo)
- **Success**: #10b981 (Verde)
- **Warning**: #f59e0b (Amarelo)
- **Danger**: #ef4444 (Vermelho)

## 📊 Estrutura de Dados

### Formato dos Dados Coletados

```json
{
  "date": "2025-10-05T12:00:00",
  "station": "São Paulo - Pinheiros",
  "country": "brazil",
  "state": "sao-paulo",
  "city": "sao-paulo",
  "pm25": 45.2,
  "pm10": 78.5,
  "no2": 32.1,
  "so2": 12.3,
  "co": 1.8,
  "temperature": 24.5,
  "pressure": 1013.2,
  "humidity": 65.0,
  "wind": 3.2,
  "aqi": "Moderate"
}
```

### Particionamento S3

```
s3://bucket/raw/
  └── date=2025-10-05/
      ├── aqi-data-10-30-00.snappy.parquet
      ├── aqi-data-11-00-00.snappy.parquet
      └── aqi-data-12-00-00.snappy.parquet
```

## 🔧 Troubleshooting

### Modelo não carrega
- Verifique o caminho no S3
- Confirme que o bucket está acessível
- Verifique as permissões IAM

### Erro de credenciais AWS
- Session tokens do AWS Lab expiram
- Gere novas credenciais no Lab
- Reconfigure na interface

### Predição falha
- Verifique se todos os 9 campos estão preenchidos
- Confirme que os valores são numéricos
- Teste com os presets primeiro

## 📈 Melhorias Futuras

- [ ] Histórico de predições
- [ ] Gráficos e visualizações
- [ ] API de batch prediction
- [ ] Export de resultados
- [ ] Autenticação de usuários
- [ ] Dashboard de métricas do modelo

## 👨‍💻 Desenvolvimento

### Executar em modo dev

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Estrutura dos Services

**aws_service.py**: Singleton para gerenciar S3
**model_service.py**: Singleton para carregar e usar o modelo
**scraper.py**: Coleta de dados de estações

## 📝 Licença

Este projeto foi desenvolvido para fins educacionais.

## 🤝 Contribuições

Contribuições são bem-vindas! Areas de interesse:
- Melhorias de UI/UX
- Otimizações de performance
- Novos features
- Testes automatizados

---

**Versão**: 3.0.0  
**Última atualização**: Outubro 2025  
**Stack**: FastAPI + Python + AWS S3 + Scikit-learn