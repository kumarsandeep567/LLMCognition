# Assignment 1
Development of an interactive tool using Streamlit that enables Model Evaluation team to evaluate the performance of OpenAI models against the test cases

## Problem Statement
The project aims to evaluate the comprehension capabilities of a Large Language Model (LLM), specifically OpenAI's GPT-4o. This evaluation framework is inspired by the General AI Assistant (GAIA) dataset and benchmark, developed by researchers at Meta AI, Hugging Face, and AutoGPT. The Streamlit application facilitates a user-friendly experience, allowing users to assess model responses, modify metadata steps if necessary, and provide feedback on the model’s performance.

## Project Goals
### 1. Database - ETL 
- Objective: Extract data from Hugging Face GAIA benchmark dataset, formatting the textual data, loading it into the database, and loading all files into a bucket
- Tools: For extraction of data from hugging face - huggingface_hub downloader, for storage - MySQL database, for file storage - Google Cloud Storage bucket
- Output: Structured database in MySQL with all gaia_features, and gaia_annotations columns, formatted files stored in the google cloud storage bucket

### 2. Fast API
- Objective: 
- Tools: 
- Output:

### 3. Streamlit
- Objective: 
- Tools: 
- Output:

## Technologies
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FD6A2B?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/)
[![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![GCS](https://img.shields.io/badge/Google%20Cloud%20Storage-FBCC30?style=for-the-badge&logo=googlecloud&logoColor=black)](https://cloud.google.com/storage)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-000000?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/)

## Data Source
1. GAIA benchmark dataset: https://huggingface.co/datasets/gaia-benchmark/GAIA

## Prerequisites

## Project Structure


## Architecture Diagram

![Architecture Diagram](https://github.com/BigDataIA-Fall2024-TeamB6/Assignment1/raw/main/diagram/llm_cognition.png)

## Steps to run application


## Team Information and Contribution
Utilizing GitHub Issues is essential for tracking modifications, feature requests, and bugs within the project. It serves as a centralized platform for documenting all project-related concerns, allowing for transparent collaboration, prioritization, and assignment of tasks to team members. This practice ensures that the project's progress is cohesive, organized, and accessible to all stakeholders, fostering an environment of open communication and continuous improvement.

Name           | Contribution %| 
---------------|---------------| 
Anirudh Joshi  | 34%           | 
Nitant Jatale  | 33%           | 
Rutuja More    | 33%           |  


## Problem Statement
The goal of this project is to evaluate the comprehension capabilities of a Large Language Model (LLM), specifically OpenAI's GPT-4o. 
This project is influenced by the General AI Assistant (GAIA) dataset and benchmark, developed by researchers at Meta AI, Hugging Face, and AutoGPT.

The framework enables users to:
- Extract data from the GAIA dataset
- Prompt the LLM with the dataset’s predefined prompts
- Collect and rank the LLM's responses
- Re-prompt the LLM in cases of incorrect responses
- Analyze response statistics


## Database - ETL
### Overview
Automated the process of downloading validation files from the Hugging Face hub, uploading the data into MySQL database, uploading files into Google Cloud Storage bucket, and processing the metadata JSON file into formatted CSV file. The processes are streamlined while ensuring data integrity and accessibility.

### File Structure
In Google Cloud Storage, a bucket is created named ```gaia_benchmark``` where all the validation set files are being stored.
- All the files inside validation split of GAIA benchmark dataset are stored in path: \
```https://storage.cloud.google.com/gaia_benchmark/files/file_name``` \
- All the formatted CSV files created by parsing JSON's are stored in path: \
```https://storage.cloud.google.com/gaia_benchmark/csv_files/file_name``` 

### Installing Dependencies
To install the dependencies run the following command on terminal: \
```pip install -r requirements.txt```

### Execution
To complete the database-ETL process,
1. Ensure that you have set all the necessary environment variables in your .env file.
2. Load data from hugging face into MySQL database and Google Cloud Storage by running the following command: \
```python main.py``` \
- This command will load data from Hugging Face GAIA benchmark dataset
- Download all the files into Google Cloud Storage bucket
- Parse JSON file and format it into CSV file, upload the CSV into Google Cloud Storage bucket
- Insert the gaia_features and gaia_annotations data into MySQL database
   



