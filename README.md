# 🌍 Air Quality Predictor

> Sistema inteligente de predição de qualidade do ar usando Machine Learning

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![AWS S3](https://img.shields.io/badge/AWS-S3-orange.svg)](https://aws.amazon.com/s3/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema web completo para predição de qualidade do ar que integra coleta de dados em tempo real, Machine Learning e armazenamento em nuvem com uma interface moderna e intuitiva.

![Dashboard Preview](https://via.placeholder.com/800x400/667eea/ffffff?text=Air+Quality+Dashboard)

## 📋 Índice

- [Características](#-características)
- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [Instalação](#-instalação)
- [Configuração](#%EF%B8%8F-configuração)
- [Uso](#-uso)
- [API](#-api)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Coleta de Dados](#-coleta-de-dados)
- [Modelo de Predição](#-modelo-de-predição)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

## ✨ Características

### 🤖 Machine Learning
- Modelo treinado com scikit-learn
- Armazenamento e carregamento dinâmico do S3
- Predição em tempo real
- Classificação em 3 níveis de qualidade

### 📊 Coleta de Dados
- Web scraping de estações globais
- Salvamento automático em S3 (formato Parquet)
- Particionamento por data
- Progress tracking em tempo real

### ☁️ Integração Cloud
- AWS S3 para storage de modelos e dados
- Suporte para AWS Academy Labs (session tokens)
- Validação de credenciais em tempo real
- Gerenciamento automático de conexão

### 🎨 Interface Moderna
- Design responsivo e intuitivo
- Feedback visual de status
- Cenários pré-definidos para testes
- Dashboard centralizado

## 🛠 Tecnologias

- **Backend**: FastAPI, Python 3.8+
- **Machine Learning**: Scikit-learn, Joblib
- **Cloud**: AWS S3, Boto3
- **Data Processing**: Pandas, PyArrow
- **Web Scraping**: BeautifulSoup4, Requests
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## 🏗 Arquitetura

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Browser   │ ───> │  FastAPI App │ ───> │   AWS S3    │
│  Interface  │ <─── │   (Python)   │ <─── │   Storage   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├── Model Service (ML)
                            ├── Scraper Service
                            └── AWS Service
```

## 📥 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Conta AWS com acesso ao S3
- Modelo treinado no formato `.joblib`

### Passo a passo

1. **Clone o repositório**

```bash
git clone https://github.com/devrictrovato/mlet-airquality-app.git
cd mlet-airquality-app
```

2. **Crie um ambiente virtual**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

Ou instale manualmente:

```bash
pip install fastapi uvicorn boto3 pandas pyarrow \
    beautifulsoup4 requests python-dotenv pydantic \
    joblib scikit-learn numpy
```

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_SESSION_TOKEN=your_session_token  # Opcional, para AWS Lab
AWS_REGION=us-east-1
S3_BUCKET=your-bucket-name
S3_PREFIX=raw
```

### 2. Modelo ML no S3

Faça upload do modelo treinado para o S3:

```
s3://your-bucket/models/air_quality_model.joblib
```

### 3. Estrutura no S3

```
s3://your-bucket/
├── models/
│   └── air_quality_model.joblib
└── raw/
    └── date=YYYY-MM-DD/
        └── *.snappy.parquet
```

## 🚀 Uso

### Iniciando o servidor

```bash
python main.py
```

Ou com reload automático para desenvolvimento:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Acesse: **http://localhost:8000**

### Fluxo de Uso

#### 1️⃣ Configurar AWS

1. Clique em **"Configurar AWS"** no dashboard
2. Insira suas credenciais do AWS (ou do AWS Academy Lab)
3. Clique em **"Testar Conexão"**
4. Se OK, clique em **"Salvar Configuração"**

#### 2️⃣ Fazer Predição

1. Clique em **"Fazer Predição"**
2. Insira os valores dos 9 parâmetros atmosféricos:
   - PM2.5, PM10, NO₂, SO₂, CO
   - Temperatura, Pressão, Umidade, Vento
3. Ou use um dos **presets** para teste rápido
4. Clique em **"Fazer Predição"**
5. Analise o resultado e as recomendações

#### 3️⃣ Coletar Dados

1. Certifique-se de que o AWS está configurado
2. Clique em **"Coletar Dados"**
3. Clique em **"Iniciar Coleta"**
4. Acompanhe o progresso em tempo real
5. Dados serão salvos automaticamente no S3

## 🔌 API

### Endpoints Disponíveis

#### AWS Configuration

**POST** `/api/aws/configure`
```json
{
  "aws_access_key": "string",
  "aws_secret_key": "string",
  "aws_session_token": "string",  // opcional
  "aws_region": "string",
  "s3_bucket": "string"
}
```

**GET** `/api/aws/status`
```json
{
  "configured": true,
  "bucket": "my-bucket",
  "region": "us-east-1"
}
```

#### Prediction

**POST** `/api/predict`
```json
{
  "pm25": 35.5,
  "pm10": 68.2,
  "no2": 28.4,
  "so2": 10.1,
  "co": 1.5,
  "temperature": 22.0,
  "pressure": 1013.0,
  "humidity": 60.0,
  "wind": 3.5
}
```

**Response:**
```json
{
  "prediction": 1,
  "quality_level": "Atenção",
  "description": "Moderado, cuidado com grupos sensíveis",
  "confidence": 0.87
}
```

#### Model Status

**GET** `/api/model/status`
```json
{
  "loaded": true,
  "source": "s3://bucket/models/air_quality_model.joblib",
  "last_loaded": "2025-10-07T10:30:00"
}
```

#### Data Collection

**POST** `/api/stations/collect`
```json
{
  "status": "success",
  "stations_collected": 150,
  "saved_to": "s3://bucket/raw/date=2025-10-07/"
}
```

## 📁 Estrutura do Projeto

```
air-quality-predictor/
├── api/
│   └── routes.py              # Endpoints da API
├── services/
│   ├── aws_service.py         # Gerenciamento S3
│   ├── model_service.py       # ML Model Service
│   └── scraper.py             # Web scraping
├── templates/
│   ├── index.html             # Dashboard principal
│   ├── predict.html           # Interface de predição
│   ├── collect.html           # Coleta de dados
│   └── aws_form.html          # Configuração AWS
├── static/
│   ├── css/
│   └── js/
├── main.py                    # Aplicação FastAPI
├── .env                       # Variáveis de ambiente
├── requirements.txt           # Dependências Python
└── README.md                  # Este arquivo
```

## 📡 Coleta de Dados

### Formato dos Dados Coletados

```json
{
  "date": "2025-10-07T12:00:00",
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

### Particionamento no S3

```
s3://bucket/raw/
└── date=2025-10-07/
    ├── aqi-data-10-30-00.snappy.parquet
    ├── aqi-data-11-00-00.snappy.parquet
    └── aqi-data-12-00-00.snappy.parquet
```

## 🎯 Modelo de Predição

### Parâmetros de Entrada

| Parâmetro | Descrição | Unidade |
|-----------|-----------|---------|
| `pm25` | Material particulado 2.5 | µg/m³ |
| `pm10` | Material particulado 10 | µg/m³ |
| `no2` | Dióxido de nitrogênio | ppb |
| `so2` | Dióxido de enxofre | ppb |
| `co` | Monóxido de carbono | ppm |
| `temperature` | Temperatura | °C |
| `pressure` | Pressão atmosférica | hPa |
| `humidity` | Umidade relativa | % |
| `wind` | Velocidade do vento | m/s |

### Classes de Predição

| Classe | Nível | Descrição |
|--------|-------|-----------|
| **0** | 🟢 Saudável | Ar de boa qualidade |
| **1** | 🟡 Atenção | Moderado, cuidado com grupos sensíveis |
| **2** | 🔴 Perigoso | Nocivo para todos |

### Presets Disponíveis

- **Ar Saudável**: Condições ideais
- **Moderado**: Valores médios de poluição
- **Perigoso**: Alta concentração de poluentes

## 🔧 Troubleshooting

### Modelo não carrega

**Problema**: Erro ao carregar modelo do S3

**Solução**:
- Verifique o caminho: `s3://bucket/models/air_quality_model.joblib`
- Confirme que o bucket está acessível
- Verifique as permissões IAM

### Credenciais AWS expiradas

**Problema**: Erro 403 ao acessar S3

**Solução**:
- Session tokens do AWS Lab expiram após algumas horas
- Gere novas credenciais no AWS Academy Lab
- Reconfigure na interface

### Erro na predição

**Problema**: Predição falha ou retorna erro

**Solução**:
- Verifique se todos os 9 campos estão preenchidos
- Confirme que os valores são numéricos válidos
- Teste com os presets primeiro

### Coleta de dados falha

**Problema**: Scraper não coleta dados

**Solução**:
- Verifique sua conexão com internet
- Confirme que o AWS está configurado
- Verifique os logs do servidor

## 🗺 Roadmap

### Versão 3.1
- [ ] Histórico de predições
- [ ] Gráficos e visualizações
- [ ] Export de resultados (CSV, JSON)

### Versão 3.2
- [ ] API de batch prediction
- [ ] Autenticação de usuários
- [ ] Dashboard de métricas do modelo

### Versão 4.0
- [ ] Retreinamento automático
- [ ] Múltiplos modelos (A/B testing)
- [ ] Alertas por email/SMS
- [ ] App mobile (React Native)

## 🤝 Contribuindo

Contribuições são bem-vindas! Áreas de interesse:

- ✨ Melhorias de UI/UX
- ⚡ Otimizações de performance
- 🆕 Novos features
- 🧪 Testes automatizados
- 📚 Documentação

### Como Contribuir

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

Desenvolvido por **devrictrovato**

[![GitHub](https://img.shields.io/badge/GitHub-devrictrovato-black?logo=github)](https://github.com/devrictrovato)

---

## 🙏 Agradecimentos

- Dados de qualidade do ar: [World Air Quality Index](https://waqi.info/)
- AWS Academy por fornecer recursos educacionais
- Comunidade FastAPI e Scikit-learn

---

**Versão**: 3.0.0  
**Última atualização**: Outubro 2025  
**Stack**: FastAPI + Python + AWS S3 + Scikit-learn

⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!
