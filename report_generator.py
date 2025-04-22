from datetime import datetime
from typing import Dict, List, Any
import json

class ReportGenerator:
    def __init__(self, data: Dict):
        """
        Инициализирует генератор отчетов
        
        Args:
            data: Словарь с данными о структуре базы данных Neo4j
        """
        self.data = data
    
    def escape_markdown(self, text):
        """
        Экранирует специальные символы Markdown
        
        Args:
            text: Текст для экранирования
            
        Returns:
            Экранированная строка
        """
        if text is None:
            return ""
        escape_chars = ['|', '_', '*', '`', '[', ']', '(', ')', '#', '+', '-', '.', '!']
        result = str(text)
        for char in escape_chars:
            result = result.replace(char, '\\' + char)
        return result
    
    def generate_markdown_report(self, md_path: str, dot_path: str, png_path: str):
        """
        Генерирует отчет в формате Markdown
        
        Args:
            md_path: Путь для сохранения Markdown-отчета
            dot_path: Путь к DOT-файлу диаграммы
            png_path: Путь к PNG-файлу диаграммы
        """
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Neo4j Audit Report: `{self.data['db_name']}`\n")
            f.write(f"*Generated: {datetime.now():%Y-%m-%d %H:%M:%S}*\n\n")
            
            # Общая информация
            f.write("## General Info\n")
            f.write(f"- Neo4j version: **{self.data['version']}**\n")
            f.write(f"- DB Size: **{self.data['db_size']}**\n")
            f.write(f"- Node Labels: **{len(self.data['nodes'])}**\n")
            f.write(f"- Relationship Types: **{len(self.data['relationships'])}**\n\n")
            
            # Информация о типах узлов
            f.write("## Node Labels\n")
            for node in self.data['nodes']:
                f.write(f"### {node['label']}\n")
                f.write(f"- Node Count: `{node['node_count']}`\n")
                
                # Свойства узла
                f.write("#### Properties\n\n")
                
                if node['properties']:
                    f.write("| Name | Type | Primary Key |\n")
                    f.write("| ---- | ---- | ----------- |\n")
                    
                    for prop in node['properties']:
                        prop_name = self.escape_markdown(prop['property_name'])
                        data_type = self.escape_markdown(prop['data_type'])
                        is_pk = "Yes" if prop['is_primary_key'] else "No"
                        
                        f.write(f"| {prop_name} | {data_type} | {is_pk} |\n")
                else:
                    f.write("No properties defined.\n")
                
                # Образцы данных
                f.write("\n#### Sample Data\n\n")
                samples = self.data['samples'].get(node['label'], [])
                
                if samples:
                    # Получаем список всех ключей во всех образцах
                    all_keys = set()
                    for sample in samples:
                        all_keys.update(sample.keys())
                    
                    all_keys = sorted(list(all_keys))
                    
                    # Создаем заголовок таблицы
                    header_row = " | ".join([self.escape_markdown(key) for key in all_keys])
                    f.write(f"| {header_row} |\n")
                    
                    # Создаем разделитель
                    separator = " | ".join(["----" for _ in all_keys])
                    f.write(f"| {separator} |\n")
                    
                    # Добавляем данные
                    for sample in samples:
                        row_values = []
                        for key in all_keys:
                            value = sample.get(key, "")
                            row_values.append(self.escape_markdown(value))
                        
                        data_row = " | ".join(row_values)
                        f.write(f"| {data_row} |\n")
                else:
                    f.write("No sample data available.\n")
                
                f.write("\n")
            
            # Информация о типах отношений
            f.write("## Relationship Types\n")
            for rel in self.data['relationships']:
                rel_type = rel['type']
                f.write(f"### {rel_type}\n")
                f.write(f"- Relationship Count: `{rel['relationship_count']}`\n")
                
                # Начальные и конечные метки
                start_labels = ", ".join(rel['start_labels'])
                end_labels = ", ".join(rel['end_labels'])
                f.write(f"- Pattern: `({start_labels})-[:{rel_type}]->({end_labels})`\n")
                
                # Свойства отношения
                f.write("\n#### Properties\n\n")
                
                if rel['properties']:
                    f.write("| Name | Type |\n")
                    f.write("| ---- | ---- |\n")
                    
                    for prop_name, prop_value in rel['properties'].items():
                        prop_type = type(prop_value).__name__ if prop_value is not None else "unknown"
                        f.write(f"| {self.escape_markdown(prop_name)} | {self.escape_markdown(prop_type)} |\n")
                else:
                    f.write("No properties defined.\n")
                
                f.write("\n")
            
            # Информация об индексах
            if self.data.get('indexes'):
                f.write("## Indexes\n")
                f.write("| Name | Type | Node Label/Relationship Type | Properties | Uniqueness |\n")
                f.write("| ---- | ---- | ---------------------------- | ---------- | ---------- |\n")
                
                for idx in self.data['indexes']:
                    name = self.escape_markdown(idx.get('name', ''))
                    idx_type = self.escape_markdown(idx.get('type', ''))
                    labels = self.escape_markdown(", ".join(idx.get('labelsOrTypes', [])))
                    properties = self.escape_markdown(", ".join(idx.get('properties', [])))
                    uniqueness = self.escape_markdown(idx.get('uniqueness', ''))
                    
                    f.write(f"| {name} | {idx_type} | {labels} | {properties} | {uniqueness} |\n")
                
                f.write("\n")
            
            # Информация об ограничениях
            if self.data.get('constraints'):
                f.write("## Constraints\n")
                f.write("| Name | Type | Node Label/Relationship Type | Properties |\n")
                f.write("| ---- | ---- | ---------------------------- | ---------- |\n")
                
                for constraint in self.data['constraints']:
                    name = self.escape_markdown(constraint.get('name', ''))
                    constraint_type = self.escape_markdown(constraint.get('type', ''))
                    labels = self.escape_markdown(", ".join(constraint.get('labelsOrTypes', [])))
                    properties = self.escape_markdown(", ".join(constraint.get('properties', [])))
                    
                    f.write(f"| {name} | {constraint_type} | {labels} | {properties} |\n")
                
                f.write("\n")
            
            # Информация о процедурах
            if self.data.get('procedures'):
                f.write("## Available Procedures\n")
                f.write("| Name | Signature | Description |\n")
                f.write("| ---- | --------- | ----------- |\n")
                
                for proc in self.data['procedures']:
                    name = self.escape_markdown(proc.get('name', ''))
                    signature = self.escape_markdown(proc.get('signature', ''))
                    description = self.escape_markdown(proc.get('description', ''))
                    
                    f.write(f"| {name} | {signature} | {description} |\n")
                
                f.write("\n")
            
            # Информация о диаграмме
            f.write("## Graph Diagram\n")
            f.write(f"- DOT: `{dot_path}`  \n")
            f.write(f"- PNG: `{png_path}`  \n\n")
            
        print(f"[+] Markdown report generated: {md_path}")
