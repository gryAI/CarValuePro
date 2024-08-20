### Introduction
> Insert introduction here

### Project Setup
1. Create a virtual environment <br>
```
pip install pyenv
pip install virtualenv
```
2. Add `PYTHONPATH` in the `venv/Scripts/activate` file
```
echo 'export PYTHONPATH="/path/to/your/src"' >> path/to/your/venv/Scripts/activate
```
3. Activate the virtual environment <br>
```
source venv/Scripts/activate
```
4. Install dependencies
```
pip install -r requirements.txt
```

### Run the Application
- Run specific modules from `src`
```
# Run from project root directory
python -m src.data_pipeline.full_pipeline.extract

# Run from src directory
cd src
python -m data_pipeline.full_pipeline.extract
```
- Run orchestrators from `scripts`
```
python scripts/run_full_pipeline.py
```

### Project Structure

```plaintext
CarValueProRepo/
│
├── 📂 src/                                                            # Main source code for the web app, model, and data pipeline
│   ├── 📂 app/                                                        # Web application code
│   │   ├── 📄 __init__.py
│   │   ├── 📄 routes.py
│   │   ├── 📄 views.py
│   │   ├── 📂 static/                                                 # Static files (e.g., CSS, JS)
│   │   ├── 📂 templates/                                              # HTML templates
│   │   └── 📄 config.py                                               # Configuration settings
│   ├── 📂 model/                                                      # Machine learning model code
│   │   ├── 📄 __init__.py
│   │   ├── 📄 train.py
│   │   ├── 📄 evaluate.py
│   │   ├── 📄 predict.py
│   │   └── 📄 utils.py
│   ├── 📂 data_pipeline/                                               # Data processing and pipeline code
│   │   ├── 📄 __init__.py
│   │   ├── 📄 extract.py
│   │   ├── 📄 transform.py
│   │   ├── 📄 load.py
│   │   ├── 📂 airflow/                                                 # Airflow DAGs and configuration
│   │   │   ├── 📂 dags/                                                # DAG definitions
│   │   │   │   ├── 📄 example_dag.py
│   │   │   │   └── 📄 data_pipeline_dag.py
│   │   │   ├── 📂 plugins/                                             # Custom Airflow plugins
│   │   │   │   └── 📄 custom_plugin.py
│   │   │   ├── 📂 config/                                              # Airflow configuration files
│   │   │   │   └── 📄 airflow.cfg
│   │   │   └── 📄 Dockerfile                                           # Dockerfile for Airflow setup (if applicable)
│
├── 📂 deployment/                                                      # Deployment-related files and configurations
│   ├── 📂 docker/                                                      # Docker-related files
│   │   ├── 📄 Dockerfile                                               # Dockerfile for the web app or other services
│   │   └── 📄 docker-compose.yml                                       # Docker Compose file for local development
│   ├── 📂 k8s/                                                         # Kubernetes configurations (if applicable)
│   │   ├── 📄 deployment.yaml                                          # Kubernetes deployment configuration
│   │   ├── 📄 service.yaml                                             # Kubernetes service configuration
│   │   └── 📄 ingress.yaml                                             # Kubernetes ingress configuration (if applicable)
│   ├── 📂 scripts/                                                     # Deployment scripts (e.g., shell scripts)
│   │   └── 📄 deploy.sh
│   └── 📂 configs/                                                     # Environment-specific configuration files
│       └── 📄 production.env  
│
├── 📂 tests/                                                           # Test scripts
│   ├── 📄 __init__.py
│   ├── 📄 test_app.py
│   ├── 📄 test_model.py
│   ├── 📄 test_pipeline.py
│   └── 📄 test_airflow.py                                              # Tests for Airflow DAGs
│
├── 📂 data/                                                            # Data files or databases
│   ├── 📂 raw/                                                         # Raw data files
│   ├── 📂 processed/                                                   # Processed data files
│   └── 📂 models/                                                      # Saved model files
│
├── 📂 reports/                                                         # Reports and visualizations
│   ├── 📂 visualizations/                                              # Data visualizations and charts
│   │   ├── 📄 dashboard.png
│   │   ├── 📄 performance_metrics.png
│   │   └── 📄 trends_analysis.png
│   ├── 📂 notebooks/                                                   # Jupyter notebooks with analysis
│   │   ├── 📄 data_exploration.ipynb
│   │   ├── 📄 model_evaluation.ipynb
│   │   └── 📄 final_report.ipynb
│   └── 📂 summaries/                                                   # Summary reports and insights
│       ├── 📄 executive_summary.md
│       ├── 📄 weekly_update.md
│       └── 📄 project_review.md
│
├── 📂 docs/                                                            # Documentation
│   ├── 📄 model_description.md
│   ├── 📄 api_documentation.md  
│   ├── 📄 airflow_setup.md
│   ├── 📄 architecture_diagram.png                                     # Documentation for setting up and using Airflow
│   └── 📄 architecture_diagram.jpg
│
├── 📄 requirements.txt                                                 # Python dependencies
├── 📄 README.md                                                        # Project overview
└── 📄 .gitignore                                                       # Git ignore file

