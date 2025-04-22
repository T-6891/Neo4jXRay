from neo4j import GraphDatabase
from typing import Dict, List, Any, Tuple, Optional

class Neo4jConnector:
    def __init__(self, uri: str, user: str, password: str):
        """
        Инициализирует соединение с базой данных Neo4j
        
        Args:
            uri: URI для подключения к Neo4j
            user: Имя пользователя
            password: Пароль пользователя
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def execute_query(self, query: str, params: Dict = None) -> List[Dict]:
        """
        Выполняет Cypher-запрос и возвращает результаты
        
        Args:
            query: Cypher-запрос
            params: Параметры запроса (опционально)
            
        Returns:
            Список словарей с результатами запроса
        """
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]
    
    def execute_single_result(self, query: str, params: Dict = None) -> Optional[Dict]:
        """
        Выполняет Cypher-запрос и возвращает первый результат
        
        Args:
            query: Cypher-запрос
            params: Параметры запроса (опционально)
            
        Returns:
            Словарь с результатом или None, если результат пустой
        """
        with self.driver.session() as session:
            result = session.run(query, params or {})
            record = result.single()
            return record.data() if record else None
    
    def close(self):
        """Закрывает соединение с базой данных"""
        if self.driver:
            self.driver.close()
