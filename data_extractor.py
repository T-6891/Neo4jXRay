from typing import Dict, List, Any, Optional
import json

SAMPLE_LIMIT = 10

class Neo4jDataExtractor:
    def __init__(self, db):
        """
        Инициализирует экстрактор данных Neo4j
        
        Args:
            db: Экземпляр Neo4jConnector
        """
        self.db = db
    
    def get_database_info(self) -> Dict:
        """
        Получает основную информацию о базе данных Neo4j
        
        Returns:
            Словарь с информацией о базе данных
        """
        data = {}
        
        # Получаем версию Neo4j
        version_query = "CALL dbms.components() YIELD name, versions WHERE name = 'Neo4j Kernel' RETURN versions[0] AS version"
        version_result = self.db.execute_single_result(version_query)
        data['version'] = version_result['version'] if version_result else "Unknown"
        
        # Получаем имя базы данных
        db_name_query = "CALL db.info() YIELD name RETURN name"
        db_name_result = self.db.execute_single_result(db_name_query)
        data['db_name'] = db_name_result['name'] if db_name_result else "neo4j"
        
        # Получаем размер базы данных (приблизительно)
        size_query = """
        CALL dbms.database.size() YIELD database, totalSize 
        WHERE database = $db_name
        RETURN totalSize
        """
        size_result = self.db.execute_single_result(size_query, {"db_name": data['db_name']})
        data['db_size'] = size_result['totalSize'] if size_result else "Unknown"
        
        return data
    
    def get_node_labels(self) -> List[str]:
        """
        Получает список всех меток узлов
        
        Returns:
            Список строк с метками узлов
        """
        query = "CALL db.labels() YIELD label RETURN label ORDER BY label"
        results = self.db.execute_query(query)
        return [result['label'] for result in results]
    
    def get_relationship_types(self) -> List[str]:
        """
        Получает список всех типов отношений
        
        Returns:
            Список строк с типами отношений
        """
        query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType"
        results = self.db.execute_query(query)
        return [result['relationshipType'] for result in results]
    
    def get_node_properties(self, label: str) -> List[Dict]:
        """
        Получает список свойств для узлов с указанной меткой
        
        Args:
            label: Метка узла
            
        Returns:
            Список словарей со свойствами узлов
        """
        # Получаем все свойства для данной метки
        query = f"""
        MATCH (n:`{label}`) 
        RETURN properties(n) AS props
        LIMIT 1
        """
        result = self.db.execute_query(query)
        
        # Если узлы с такой меткой есть
        properties = []
        if result and 'props' in result[0]:
            # Для каждого свойства определяем его тип на основе первого непустого значения
            props = result[0]['props']
            for prop_name, prop_value in props.items():
                # Определяем тип данных свойства
                data_type = type(prop_value).__name__ if prop_value is not None else "unknown"
                
                # Проверяем, является ли свойство идентификатором
                is_primary_key = prop_name == 'id'  # Упрощенное предположение, может потребоваться корректировка
                
                properties.append({
                    'property_name': prop_name,
                    'data_type': data_type,
                    'is_primary_key': is_primary_key
                })
        
        return properties
    
    def get_nodes(self) -> List[Dict]:
        """
        Получает информацию обо всех типах узлов (метках)
        
        Returns:
            Список словарей с информацией о типах узлов
        """
        labels = self.get_node_labels()
        nodes = []
        
        for label in labels:
            # Получаем количество узлов с данной меткой
            count_query = f"MATCH (n:`{label}`) RETURN count(n) as count"
            count_result = self.db.execute_single_result(count_query)
            node_count = count_result['count'] if count_result else 0
            
            # Получаем свойства узлов с данной меткой
            properties = self.get_node_properties(label)
            
            nodes.append({
                'label': label,
                'node_count': node_count,
                'properties': properties
            })
        
        return nodes
    
    def get_relationships(self) -> List[Dict]:
        """
        Получает информацию обо всех типах отношений
        
        Returns:
            Список словарей с информацией о типах отношений
        """
        rel_types = self.get_relationship_types()
        relationships = []
        
        for rel_type in rel_types:
            # Получаем информацию о типах узлов, которые соединяет данное отношение
            query = f"""
            MATCH (start)-[r:`{rel_type}`]->(end)
            RETURN 
                labels(start) AS start_labels, 
                labels(end) AS end_labels, 
                count(r) AS relationship_count
            LIMIT 1
            """
            result = self.db.execute_single_result(query)
            
            if result:
                # Получаем свойства отношения
                props_query = f"""
                MATCH ()-[r:`{rel_type}`]->() 
                RETURN properties(r) AS props
                LIMIT 1
                """
                props_result = self.db.execute_single_result(props_query)
                properties = props_result['props'] if props_result and 'props' in props_result else {}
                
                # Получаем количество отношений данного типа
                count_query = f"MATCH ()-[r:`{rel_type}`]->() RETURN count(r) as count"
                count_result = self.db.execute_single_result(count_query)
                rel_count = count_result['count'] if count_result else 0
                
                # Для каждой пары меток начального и конечного узлов добавляем информацию об отношении
                relationships.append({
                    'type': rel_type,
                    'start_labels': result['start_labels'],
                    'end_labels': result['end_labels'],
                    'relationship_count': rel_count,
                    'properties': properties
                })
        
        return relationships
    
    def get_samples(self, nodes: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Получает образцы данных для каждого типа узлов
        
        Args:
            nodes: Список словарей с информацией о типах узлов
            
        Returns:
            Словарь с образцами данных для каждого типа узлов
        """
        samples = {}
        
        for node in nodes:
            label = node['label']
            query = f"""
            MATCH (n:`{label}`) 
            RETURN n 
            LIMIT {SAMPLE_LIMIT}
            """
            
            try:
                results = self.db.execute_query(query)
                samples[label] = []
                
                for result in results:
                    node_data = result['n']
                    samples[label].append(node_data)
                    
            except Exception as e:
                print(f"Warning: Error sampling node {label}: {e}")
                samples[label] = []
                
        return samples
    
    def get_indexes(self) -> List[Dict]:
        """
        Получает информацию об индексах
        
        Returns:
            Список словарей с информацией об индексах
        """
        query = """
        SHOW INDEXES
        YIELD name, labelsOrTypes, properties, type, uniqueness, entityType
        RETURN * ORDER BY name
        """
        
        try:
            return self.db.execute_query(query)
        except Exception as e:
            print(f"Warning: Error getting indexes: {e}")
            return []
    
    def get_constraints(self) -> List[Dict]:
        """
        Получает информацию об ограничениях
        
        Returns:
            Список словарей с информацией об ограничениях
        """
        query = """
        SHOW CONSTRAINTS
        YIELD name, labelsOrTypes, properties, type, entityType
        RETURN * ORDER BY name
        """
        
        try:
            return self.db.execute_query(query)
        except Exception as e:
            print(f"Warning: Error getting constraints: {e}")
            return []
    
    def get_procedures(self) -> List[Dict]:
        """
        Получает информацию о доступных процедурах
        
        Returns:
            Список словарей с информацией о процедурах
        """
        query = """
        CALL dbms.procedures()
        YIELD name, signature, description
        WHERE name STARTS WITH 'apoc' OR name STARTS WITH 'algo' OR name STARTS WITH 'gds'
        RETURN name, signature, description
        ORDER BY name
        """
        
        try:
            return self.db.execute_query(query)
        except Exception as e:
            print(f"Warning: Error getting procedures: {e}")
            return []
    
    def get_all_data(self) -> Dict:
        """
        Получает все данные о структуре базы данных Neo4j
        
        Returns:
            Словарь со всей информацией
        """
        data = self.get_database_info()
        data['nodes'] = self.get_nodes()
        data['relationships'] = self.get_relationships()
        data['samples'] = self.get_samples(data['nodes'])
        data['indexes'] = self.get_indexes()
        data['constraints'] = self.get_constraints()
        data['procedures'] = self.get_procedures()
        return data
