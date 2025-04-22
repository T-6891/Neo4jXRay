# Neo4jXRay - Advanced Neo4j Audit Tool

![Neo4j](https://img.shields.io/badge/Neo4j-4581C3?style=for-the-badge&logo=neo4j&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)
![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)

Neo4jXRay is a powerful tool for comprehensive auditing and documentation of Neo4j graph databases. This project was created to automate the process of auditing graph database structures and generating documentation, including visual graph diagrams.

## 🚀 Features

- **Complete Graph Structure Audit**:
  - Node labels and properties
  - Relationship types and properties
  - Property data types
  
- **Data Analysis**:
  - Sample data from each node label (up to SAMPLE_LIMIT nodes)
  - Node count for each label
  - Relationship count for each type
  
- **Indexes and Constraints Analysis**:
  - Index types and properties
  - Constraint types and properties
  
- **Procedure Examination**:
  - Available procedures (APOC, Algorithms, GDS)
  - Signatures and descriptions
  
- **Visualization**:
  - Graph diagrams in DOT and PNG formats
  - HTML tables in diagram nodes
  - Relationship indicators on edges
  - Clear distinction between different node labels
  
- **Reporting**:
  - Detailed Markdown report
  - Execution process logging

## 📋 Requirements

- Python 3.9+
- neo4j >= 5.8.0
- graphviz >= 0.20
- `dot` utility (part of the Graphviz package)

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/T-6891/Neo4jXRay.git
cd neo4jXRay

# Set up Python virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
# venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Graphviz (Linux)
sudo apt install graphviz

# Install Graphviz (macOS)
brew install graphviz

# Install Graphviz (Windows)
# Download and install from https://graphviz.org/download/
```

## 🔧 Usage

### Basic Audit

```bash
python neo4j_xray.py --uri "neo4j://username:password@host:port" --md "audit_report.md"
```

### Full Parameter Set

```bash
python neo4j_xray.py --uri "neo4j://username:password@host:port" \
                   --md "audit_report.md" \
                   --dot "graph_diagram.dot" \
                   --png "graph_diagram.png"
```

### Command Line Parameters

| Parameter | Description | Default |
|---------|------------|---------|
| `--uri` | Neo4j connection URI | (required) |
| `--user` | Neo4j username (override from URI) | (optional) |
| `--password` | Neo4j password (override from URI) | (optional) |
| `--md` | Path to save the Markdown report | `audit_report.md` |
| `--dot` | Path to save the DOT diagram file | `graph_diagram.dot` |
| `--png` | Path to save the PNG diagram | `graph_diagram.png` |

## 📊 Audit Results

Running the script will generate:

1. **Graph diagram** in DOT and PNG formats visualizing node labels and relationship types
2. **Markdown report** including:
   - General database information (Neo4j version, DB size)
   - Node label structures with properties
   - Sample data from each node label
   - Relationship type definitions and properties
   - Complete index and constraint definitions
   - Available procedures

## 🏗️ Project Architecture

The project follows a modular architecture with the following components:

1. **neo4j_xray.py** - Main entry point, handles command-line arguments and workflow orchestration
2. **db_connector.py** - Manages Neo4j database connections and query execution
3. **data_extractor.py** - Extracts metadata and sample data from the graph database
4. **er_diagram_generator.py** - Generates graph diagrams in DOT and PNG formats
5. **report_generator.py** - Creates comprehensive Markdown reports

## 🛠️ Configuration

Main settings are located at the top of the `neo4j_xray.py` script:

```python
# Configuration
DOT_FILE = 'graph_diagram.dot'     # DOT filename
PNG_FILE = 'graph_diagram.png'     # PNG filename
DEFAULT_MD_REPORT = 'audit_report.md'
```

Sample limit configuration is in `data_extractor.py`:

```python
# Number of nodes to sample from each label
SAMPLE_LIMIT = 10
```

## 🤝 Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).
For more details: [https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/)

## 📌 Roadmap

- [ ] Schema comparison functionality
- [ ] Interactive web-based diagrams
- [ ] Database structure versioning
- [ ] Performance insights and index recommendations
- [ ] Extended security audit capabilities
- [ ] HTML export format
- [ ] Optimization for large graph databases
- [ ] Support for advanced Neo4j features (spatial, temporal)
- [ ] Integration with Neo4j Desktop
