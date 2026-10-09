***
## Introduction <br>

The CarValuePro project focuses on developing a Machine Learning model to predict the market value of pre-owned vehicles in the Philippines. It aims to offer sellers a suggested price for their vehicles and provide buyers with a benchmark to help them compare the prices of vehicles they are considering. 
<br><br>
To ensure the model's relevance and accuracy, the data used in this project is sourced from real-world, updated information reflecting current market trends in the Philippines. The dataset encompasses a wide range of variables, including vehicle make, model, year, mileage, and condition, enabling the model to capture the nuances of the automotive market effectively.
<br> <br>
![image](https://github.com/user-attachments/assets/31ee6e2b-d70c-4e87-90cd-0da0804a045e)


To accomplish this, the following project components are involved:
- Data Pipeline Development and Deployment
  - Extraction (Web Scraping)
  - Transformation
  - Loading (Initial Full Load and Daily Incremental Load)
- Model Development
  - Linear Regression
  - XGBoost
  - RandomForest
  - Neural Networks   
- Web App Development
- Model Deployment
- Model Monitoring

***

## Project Details

To replicate this project, you can follow the steps outlined below. <br> For a more detailed documentation, please check this Project's Wiki Page _(still in development)_.

### Environment Setup
1. Clone this repository
```
git clone https://github.com/gryAI/CarValuePro
```
   
2. Create a virtual environment <br>
```
pip install pyenv
pip install virtualenv
```
3. Add `PYTHONPATH` in the `venv/Scripts/activate` file
```
echo 'export PYTHONPATH="/path/to/your/src"' >> path/to/your/venv/Scripts/activate
```
4. Activate the virtual environment <br>
```
source venv/Scripts/activate
```
5. Install dependencies
```
pip install -r requirements.txt
```

### Local Module Execution
You can choose to run the project locally by following these steps. This approach is suitable if you only intend to extract data from the website once and are not concerned with subsequent postings.
- Run orchestrators from `scripts`
```
python scripts/run_full_pipeline.py
```

- Notes on how to run specific modules from `src`
```
# Run from project root directory
python -m src.data_pipeline.full_pipeline.extract

# Run from src directory
cd src
python -m data_pipeline.full_pipeline.extract
```


### Dockerization and Deployment
If you wish to extract subsequent postings on a daily basis, I recommend following these steps to deploy the pipeline, ensuring that the scheduled tasks run continuously.
- Dockerize the pipeline <br>
- Deploy the pipeline as a Background Worker in Render

***

## Project Structure

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

