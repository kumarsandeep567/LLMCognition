from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.onprem.container import Docker
from diagrams.programming.framework import Fastapi
from diagrams.onprem.database import Mysql
from diagrams.onprem.compute import Server
from diagrams.gcp.storage import GCS
from diagrams.programming.language import Python

with Diagram("LLM Cognition", show=False):
    
    users = Users("End Users")
    
    with Cluster("Data Collection Stage"):
        data_source = Python("Hugging Face API / BS4 Scraper")
    
    with Cluster("Data Processing Stage"):
        data_processing = Python("Data Structuring")
        text_data = Server("Text or Numeric Data")
        files = Server("Files (JPG, PNG, JSON, etc.)")
    
    with Cluster("Data Loading Stage"):
        db_loader = Python("Database Loader")
        db = Mysql("MySQL Database")
    
    with Cluster("Abstraction Layer"):
        api = Fastapi("FastAPI (Core backend service)")
        gcs = GCS("Google Cloud Bucket (File storage)")
        gpt_api = Python("OpenAI GPT-4 API")
    
    streamlit_app = Python("Streamlit Application")
    
    # Connections
    users >> streamlit_app
    streamlit_app >> api
    api >> db
    api >> gcs
    api >> gpt_api
    db_loader >> db
    data_processing >> text_data
    data_processing >> files
    data_source >> data_processing
