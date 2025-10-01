from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional, Union
import requests
import asyncio


class AirQualityScraper:
    """Serviço de scraping de dados de qualidade do ar"""
    
    BASE_URL = "https://aqicn.org/map/world/pt"
    
    @staticmethod
    def _get_value(soup: BeautifulSoup, element_id: str) -> Optional[str]:
        """
        Extrai valor de um elemento <td> pelo ID.
        
        Args:
            soup: Objeto BeautifulSoup
            element_id: ID do elemento
            
        Returns:
            Valor textual ou None
        """
        td = soup.find('td', {"id": element_id})
        if td:
            return td.text.strip()
        return None
    
    def _parse_station_data(self, station_name: str, station_url: str) -> Dict[str, Any]:
        """
        Realiza o scraping de uma estação específica.
        
        Args:
            station_name: Nome da estação
            station_url: URL da página da estação
            
        Returns:
            Dados formatados da estação
        """
        response = requests.get(station_url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extrair localização da URL
        parts = station_url.split('/city/')[-1].split('/')
        country = parts[0] if len(parts) > 0 else "N/A"
        state = parts[1] if len(parts) > 1 else "N/A"
        city = parts[2] if len(parts) > 2 else "N/A"
        
        # Extrair AQI
        aqivalue = soup.find('div', class_='aqivalue')
        aqi = aqivalue.attrs.get('title', "N/A") if aqivalue else "N/A"
        
        return {
            'date': datetime.now().isoformat(),
            'station': station_name,
            'country': country,
            'state': state,
            'city': city,
            'pm25': self._get_value(soup, 'cur_pm25'),
            'pm10': self._get_value(soup, 'cur_pm10'),
            'no2': self._get_value(soup, 'cur_no2'),
            'so2': self._get_value(soup, 'cur_so2'),
            'co': self._get_value(soup, 'cur_co'),
            'temperature': self._get_value(soup, 'cur_t'),
            'pressure': self._get_value(soup, 'cur_p'),
            'humidity': self._get_value(soup, 'cur_h'),
            'wind': self._get_value(soup, 'cur_w'),
            'aqi': aqi
        }
    
    async def scrape_all_stations(self) -> List[Dict[str, Any]]:
        """
        Realiza scraping de todas as estações disponíveis.
        
        Returns:
            Lista com dados de todas as estações
        """
        response = requests.get(self.BASE_URL, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encontrar todos os links de estações
        stations = soup.find_all('a')
        results = []
        
        for station in stations:
            station_name = station.text.strip()
            station_url = station.get('href')
            
            # Filtrar apenas URLs válidas de estações
            if station_url and 'city' in station_url and 'aqicn' in station_url:
                try:
                    data = self._parse_station_data(station_name, station_url)
                    results.append(data)
                except Exception as e:
                    print(f"⚠️ Erro ao processar {station_name}: {str(e)}")
                    continue
        
        return results
    
    async def count_stations(self) -> int:
        """
        Conta o número de estações disponíveis.
        
        Returns:
            Número de estações encontradas
        """
        response = requests.get(self.BASE_URL, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        stations = soup.find_all('a')
        count = sum(
            1 for station in stations
            if station.get('href') and 'city' in station.get('href', '') and 'aqicn' in station.get('href', '')
        )
        
        return count