from bs4 import BeautifulSoup
from typing import Optional, Union

def get_value(soup: BeautifulSoup, element_id: str) -> Optional[Union[int, float]]:
    """
    Tenta extrair um valor numérico (int ou float) de um elemento <td> com ID específico em uma página HTML.

    Args:
        soup (BeautifulSoup): Objeto BeautifulSoup já carregado com o HTML.
        element_id (str): ID do elemento <td> a ser procurado.

    Returns:
        Optional[Union[int, float]]: Valor textual extraído, ou None se não encontrado ou inválido.
    """
    td = soup.find('td', {"id": element_id})
    if td:
        text = td.text.strip()
        return text
    return None
