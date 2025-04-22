#!/usr/bin/env python3

"""
neo4jXRay - Advanced Neo4j Audit Tool

Version    : 1.0.0
Author     : Vladimir Smelnitskiy <master@t-brain.ru>
"""

import os
import argparse
import sys
import urllib.parse

from db_connector import Neo4jConnector
from data_extractor import Neo4jDataExtractor, SAMPLE_LIMIT
from er_diagram_generator import GraphDiagramGenerator
from report_generator import ReportGenerator

# Конфигурация по умолчанию
DOT_FILE = 'graph_diagram.dot'
PNG_FILE = 'graph_diagram.png'
DEFAULT_MD_REPORT = 'audit_report.md'

def parse_neo4j_uri(uri_str):
    """
    Разбирает строку URI Neo4j и возвращает компоненты
    
    Args:
        uri_str: Строка URI Neo4j
        
    Returns:
        Кортеж (uri, username, password)
    """
    # Проверяем, содержит ли URI учетные данные
    parts = uri_str.split('@')
    
    if len(parts) == 1:
        # URI без учетных данных
        return uri_str, None, None
    
    # URI с учетными данными
    credentials = parts[0].split('://')[-1].split(':')
    if len(credentials) != 2:
        raise ValueError("Invalid URI format. Expected: 'neo4j://username:password@host:port'")
    
    username = urllib.parse.unquote(credentials[0])
    password = urllib.parse.unquote(credentials[1])
    
    # Восстанавливаем URI без учетных данных
    protocol = uri_str.split('://')[0]
    host_port = parts[1]
    uri = f"{protocol}://{host_port}"
    
    return uri, username, password

def main():
    parser = argparse.ArgumentParser(description="Neo4j Audit + Graph Diagram")
    parser.add_argument("--uri", required=True, help="Neo4j connection URI (neo4j://username:password@host:port)")
    parser.add_argument("--user", help="Neo4j username (override from URI)")
    parser.add_argument("--password", help="Neo4j password (override from URI)")
    parser.add_argument("--md", default=DEFAULT_MD_REPORT, help="Markdown report path")
    parser.add_argument("--dot", default=DOT_FILE, help="DOT file path")
    parser.add_argument("--png", default=PNG_FILE, help="PNG file path")
    args = parser.parse_args()
    
    try:
        # Разбираем URI Neo4j
        uri, username, password = parse_neo4j_uri(args.uri)
        
        # Приоритет аргументов командной строки над учетными данными из URI
        username = args.user if args.user else username
        password = args.password if args.password else password
        
        if not username or not password:
            raise ValueError("Username and password are required. Provide them in the URI or using --user and --password")
        
        # Подключение к базе данных Neo4j
        db = Neo4jConnector(uri, username, password)
        
        print("[*] Connected to Neo4j database")
        
        # Извлечение данных
        print("[*] Extracting data from Neo4j...")
        extractor = Neo4jDataExtractor(db)
        data = extractor.get_all_data()
        
        # Генерация графовой диаграммы
        print("[*] Generating graph diagram...")
        diagram_generator = GraphDiagramGenerator(data['nodes'], data['relationships'])
        diagram_generator.generate_graph_dot(args.dot)
        diagram_generator.render_png(args.dot, args.png)
        
        # Генерация отчета
        print("[*] Generating report...")
        report_generator = ReportGenerator(data)
        report_generator.generate_markdown_report(args.md, args.dot, args.png)
        
        # Закрытие соединения
        db.close()
        
        print(f"[+] All done! Report is available at {args.md}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
