from fastapi import APIRouter, HTTPException
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from aws.s3_data import save_parquet_to_s3

import requests

from web.utils import get_value

router = APIRouter()


def parse_station_data(station_name: str, station_url: str) -> Dict[str, Any]:
    """
    Realiza o scraping de dados de uma estação específica de qualidade do ar.

    Args:
        station_name (str): Nome da estação.
        station_url (str): URL da página da estação.

    Returns:
        dict: Dados da estação formatados em padrão AQI (Air Quality Index).
    """
    station_response = requests.get(station_url)
    station_soup = BeautifulSoup(station_response.content, 'html.parser')

    # Extrai país, estado e cidade a partir da URL
    parts = station_url.split('/city/')[-1].split('/')
    country = parts[0] if len(parts) > 0 else "N/A"
    state = parts[1] if len(parts) > 1 else "N/A"
    city = parts[2] if len(parts) > 2 else "N/A"

    # Extrai valor do AQI, se disponível
    aqivalue = station_soup.find('div', class_='aqivalue')
    aqi = aqivalue.attrs['title'] if aqivalue and aqivalue.has_attr('title') else "N/A"

    current_date = datetime.now()

    return {
        'date': current_date,
        'station': station_name,
        'country': country,
        'state': state,
        'city': city,
        'pm25': get_value(station_soup, 'cur_pm25'),
        'pm10': get_value(station_soup, 'cur_pm10'),
        'no2': get_value(station_soup, 'cur_no2'),
        'so2': get_value(station_soup, 'cur_so2'),
        'co': get_value(station_soup, 'cur_co'),
        'temperature': get_value(station_soup, 'cur_t'),
        'pressure': get_value(station_soup, 'cur_p'),
        'humidity': get_value(station_soup, 'cur_h'),
        'wind': get_value(station_soup, 'cur_w'),
        'aqi': aqi
    }


@router.get(
    "/realtime",
    response_model=List[Dict[str, Any]],
    summary="Obter dados em tempo real de todas as estações",
    description="""
Retorna os dados em tempo real de qualidade do ar de todas as estações visíveis no mapa do site [aqicn.org](https://aqicn.org).

O scraping é feito diretamente da página do mapa e os dados incluem:

- Nome da estação
- País, estado e cidade
- Indicadores de poluentes (PM2.5, PM10, NO2, SO2, CO)
- Condições meteorológicas (temperatura, pressão, umidade, vento)
- AQI (Air Quality Index)

⚠️ Algumas estações podem ser ignoradas se os dados estiverem incompletos ou com erro de leitura.
"""
)
def get_all_stations() -> List[Dict[str, Any]]:
    """
    Realiza scraping de todas as estações visíveis no mapa mundial do AQICN e retorna seus dados formatados.

    Returns:
        List[Dict[str, Any]]: Lista de dicionários com dados de cada estação.
    
    Raises:
        HTTPException: Se não houver estações válidas ou se ocorrer erro durante o scraping.
    """
    try:
        url = 'https://aqicn.org/map/world/pt'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontra todos os links (a) que podem ser estações
        stations = soup.find_all('a')
        results = []

        for station in stations:
            station_name = station.text.strip()
            station_url = station.get('href')

            # Filtra apenas estações com URL válida
            if station_url and 'city' in station_url and 'aqicn' in station_url:
                try:
                    data = parse_station_data(station_name, station_url)
                    results.append(data)
                except Exception:
                    # Ignora estações com erros durante o scraping
                    continue

        if not results:
            raise HTTPException(status_code=404, detail="Nenhuma estação válida encontrada")

        save_parquet_to_s3(results)
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estações: {e}")
