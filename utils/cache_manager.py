import json
import os
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Gerenciador de cache para resultados de busca de medicamentos"""
    
    def __init__(self, cache_dir: str = "cache", cache_duration_hours: int = 24):
        """
        Inicializa o gerenciador de cache
        
        Args:
            cache_dir: Diretório onde os arquivos de cache serão salvos
            cache_duration_hours: Duração do cache em horas
        """
        self.cache_dir = cache_dir
        self.cache_duration_hours = cache_duration_hours
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Garante que o diretório de cache existe"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            logger.info(f"Diretório de cache criado: {self.cache_dir}")
    
    def _generate_cache_key(self, search_term: str) -> str:
        """
        Gera uma chave única para o cache baseada no termo de busca
        
        Args:
            search_term: Termo de busca
            
        Returns:
            Chave única para o cache
        """
        # Normalizar o termo de busca (remover espaços extras, converter para minúsculas)
        normalized_term = search_term.strip().lower()
        
        # Gerar hash MD5 do termo normalizado
        hash_object = hashlib.md5(normalized_term.encode('utf-8'))
        return hash_object.hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> str:
        """
        Obtém o caminho do arquivo de cache
        
        Args:
            cache_key: Chave do cache
            
        Returns:
            Caminho completo do arquivo de cache
        """
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _is_cache_valid(self, cache_data: Dict[str, Any]) -> bool:
        """
        Verifica se o cache ainda é válido
        
        Args:
            cache_data: Dados do cache
            
        Returns:
            True se o cache é válido, False caso contrário
        """
        if 'timestamp' not in cache_data:
            return False
        
        cache_time = datetime.fromisoformat(cache_data['timestamp'])
        current_time = datetime.now()
        
        # Verificar se o cache não expirou
        expiration_time = cache_time + timedelta(hours=self.cache_duration_hours)
        return current_time < expiration_time
    
    def get_cached_results(self, search_term: str) -> Optional[Dict[str, Any]]:
        """
        Obtém resultados do cache se disponível e válido
        
        Args:
            search_term: Termo de busca
            
        Returns:
            Dados do cache se válido, None caso contrário
        """
        try:
            cache_key = self._generate_cache_key(search_term)
            cache_file_path = self._get_cache_file_path(cache_key)
            
            if not os.path.exists(cache_file_path):
                logger.debug(f"Cache não encontrado para: {search_term}")
                return None
            
            # Ler dados do cache
            with open(cache_file_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Verificar se o cache é válido
            if not self._is_cache_valid(cache_data):
                logger.info(f"Cache expirado para: {search_term}")
                # Remover arquivo de cache expirado
                os.remove(cache_file_path)
                return None
            
            logger.info(f"Cache encontrado e válido para: {search_term}")
            return cache_data.get('results', {})
            
        except Exception as e:
            logger.error(f"Erro ao ler cache para '{search_term}': {e}")
            return None
    
    def save_cache_results(self, search_term: str, results: Dict[str, Any]):
        """
        Salva resultados no cache
        
        Args:
            search_term: Termo de busca
            results: Resultados das farmácias (sem dados unificados)
        """
        try:
            cache_key = self._generate_cache_key(search_term)
            cache_file_path = self._get_cache_file_path(cache_key)
            
            # Preparar dados para salvar
            cache_data = {
                'search_term': search_term,
                'timestamp': datetime.now().isoformat(),
                'results': results
            }
            
            # Salvar no arquivo
            with open(cache_file_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Cache salvo para: {search_term}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar cache para '{search_term}': {e}")
    
    def clear_expired_cache(self):
        """Remove todos os arquivos de cache expirados"""
        try:
            if not os.path.exists(self.cache_dir):
                return
            
            current_time = datetime.now()
            removed_count = 0
            
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.json'):
                    continue
                
                file_path = os.path.join(self.cache_dir, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    if not self._is_cache_valid(cache_data):
                        os.remove(file_path)
                        removed_count += 1
                        logger.debug(f"Cache expirado removido: {filename}")
                        
                except Exception as e:
                    logger.warning(f"Erro ao verificar cache {filename}: {e}")
                    # Se não conseguir ler o arquivo, removê-lo
                    try:
                        os.remove(file_path)
                        removed_count += 1
                    except:
                        pass
            
            if removed_count > 0:
                logger.info(f"Removidos {removed_count} arquivos de cache expirados")
                
        except Exception as e:
            logger.error(f"Erro ao limpar cache expirado: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do cache
        
        Returns:
            Dicionário com estatísticas do cache
        """
        try:
            if not os.path.exists(self.cache_dir):
                return {
                    'total_files': 0,
                    'valid_files': 0,
                    'expired_files': 0,
                    'cache_size_mb': 0
                }
            
            total_files = 0
            valid_files = 0
            expired_files = 0
            total_size = 0
            
            for filename in os.listdir(self.cache_dir):
                if not filename.endswith('.json'):
                    continue
                
                file_path = os.path.join(self.cache_dir, filename)
                total_files += 1
                total_size += os.path.getsize(file_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    if self._is_cache_valid(cache_data):
                        valid_files += 1
                    else:
                        expired_files += 1
                        
                except:
                    expired_files += 1
            
            return {
                'total_files': total_files,
                'valid_files': valid_files,
                'expired_files': expired_files,
                'cache_size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do cache: {e}")
            return {
                'total_files': 0,
                'valid_files': 0,
                'expired_files': 0,
                'cache_size_mb': 0,
                'error': str(e)
            } 