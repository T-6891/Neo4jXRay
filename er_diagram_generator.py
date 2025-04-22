import os
import subprocess
from typing import Dict, List, Any

class GraphDiagramGenerator:
    def __init__(self, nodes: List[Dict], relationships: List[Dict]):
        """
        Инициализирует генератор диаграмм для графа Neo4j
        
        Args:
            nodes: Список словарей с информацией о типах узлов
            relationships: Список словарей с информацией о типах отношений
        """
        self.nodes = nodes
        self.relationships = relationships
    
    def generate_node_html(self, node: Dict) -> str:
        """
        Генерирует HTML-представление узла для DOT-диаграммы
        
        Args:
            node: Словарь с информацией о типе узла
            
        Returns:
            HTML-строка для отображения узла в DOT
        """
        label = node['label']
        properties = node['properties']
        
        # Генерируем строки для каждого свойства
        property_rows = []
        for prop in properties:
            pk_marker = '<TD BGCOLOR="#E0FFE0"><B>PK</B></TD>' if prop['is_primary_key'] else '<TD></TD>'
            prop_name = prop['property_name']
            data_type = prop['data_type']
            
            property_rows.append(f'<TR><TD ALIGN="LEFT">{prop_name}</TD><TD ALIGN="LEFT">{data_type}</TD>{pk_marker}</TR>')
        
        property_rows_str = "\n".join(property_rows) if property_rows else '<TR><TD COLSPAN="3">No properties</TD></TR>'
        
        html = f'''<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                <TR>
                    <TD COLSPAN="3" BGCOLOR="#4D7A97"><FONT COLOR="white"><B>{label}</B> (Node)</FONT></TD>
                </TR>
                <TR>
                    <TD BGCOLOR="#EEEEFF"><B>Property</B></TD>
                    <TD BGCOLOR="#EEEEFF"><B>Type</B></TD>
                    <TD BGCOLOR="#EEEEFF"><B>PK</B></TD>
                </TR>
                {property_rows_str}
            </TABLE>
        >'''
        
        return html
    
    def generate_graph_dot(self, dot_path: str):
        """
        Генерирует DOT-файл для графовой диаграммы
        
        Args:
            dot_path: Путь для сохранения DOT-файла
        """
        with open(dot_path, 'w', encoding='utf-8') as f:
            f.write('digraph Neo4jGraph {\n')
            f.write('  graph [rankdir=LR, fontname="Helvetica", fontsize=12, pad="0.5", nodesep="0.5", ranksep="1.5"];\n')
            f.write('  node [shape=plain, fontname="Helvetica", fontsize=10];\n')
            f.write('  edge [fontname="Helvetica", fontsize=9, penwidth=1.0];\n\n')
            
            # Добавляем узлы
            for node in self.nodes:
                label = node['label']
                node_html = self.generate_node_html(node)
                f.write(f'  "{label}" [label={node_html}];\n')
            
            f.write('\n')
            
            # Добавляем отношения
            for relationship in self.relationships:
                rel_type = relationship['type']
                
                # Для каждого типа отношений может быть несколько комбинаций начальных и конечных меток
                for start_label in relationship['start_labels']:
                    for end_label in relationship['end_labels']:
                        # Формируем метку для отношения
                        rel_label = f"{rel_type}"
                        
                        # Если у отношения есть свойства, добавляем их в метку
                        if relationship['properties']:
                            props_str = ", ".join([f"{k}: {type(v).__name__}" for k, v in relationship['properties'].items()])
                            rel_label += f" ({props_str})"
                        
                        # Добавляем отношение в DOT
                        f.write(f'  "{start_label}" -> "{end_label}" [label="{rel_label}", fontname="Helvetica", ')
                        f.write('fontsize=8, color="#5D8AA8", style="solid"];\n')
            
            f.write('}\n')
        
        print(f"[+] DOT graph diagram generated: {dot_path}")
    
    def render_png(self, dot_path: str, png_path: str):
        """
        Конвертирует DOT-файл в PNG-изображение
        
        Args:
            dot_path: Путь к DOT-файлу
            png_path: Путь для сохранения PNG-файла
        """
        try:
            subprocess.check_call(['dot', '-Tpng', '-Gdpi=300', dot_path, '-o', png_path])
            print(f"[+] PNG graph diagram generated: {png_path}")
        except FileNotFoundError:
            print("Error: Graphviz 'dot' not found. Install with: sudo apt install graphviz", file=os.sys.stderr)
        except subprocess.CalledProcessError as e:
            print(f"PNG generation error: {e}", file=os.sys.stderr)
