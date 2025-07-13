# Módulo de scrapers para diferentes farmácias

from .base_scraper import BaseScraper
from .droga_raia import DrogaRaiaScraper
from .sao_joao import SaoJoaoScraper

__all__ = ['BaseScraper', 'DrogaRaiaScraper', 'SaoJoaoScraper'] 