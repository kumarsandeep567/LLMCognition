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
- Objective: To provide a user-friendly interface for validating GPT model responses by allowing users to compare generated responses with validation inputs, edit annotator steps, and provide feedback.
- Tools: Streamlit (web application framework), Pandas (data manipulation), Matplotlib (visualization), NumPy (numerical computations), Requests (API calls for data fetching and sending).
- Output: The Search Engine Page features a query input and result display; the Validation Page allows users to compare GPT responses and provide feedback; the Analytics Page presents user data with visualizations of cost efficiency and operational metrics.

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
Software Installations required for the project
1. Python Environment
A Python environment allows you to create isolated spaces for your Python projects, managing dependencies and versions separately.

2. Libraries
This assignment requires mutliple python libraries for data manipulation, API interactions, and web development like streamlit, huggingface_hub, pandas, matplotlib, mysql-connector-python.
To download all the the required libraries for the project run the following command:
```bash
pip install -r requirements.txt
```
   
3. Visual Studio Code

4. Docker
 Docker allows you to package applications and their dependencies into containers, ensuring consistent environments across different platforms

5. Google Cloud Platform
Google Cloud Storage is used for efficient storage of files

6. AWS


7. Streamlit
Streamlit is an open-source app framework that allows you to create interactive web applications easily.

8. MySQL Database
Relational database management system that allows you to store and manage data efficiently 

## Project Structure
```
Assignment1/
├── backend/
│   ├── .env.example
│   ├── .gitignore
│   ├── helpers.py
│   ├── main.py
│   ├── requirements.txt
├── database_ETL/
│   │   ├── .env.example
│   │   ├── connectDB.py
│   │   ├── fileLoader.py
│   │   ├── jsonParser.py
│   │   ├── main.py
│   │   └── requirements.txt
├── diagram/
│   ├── diagram.py
│   └── llm_cognition.png
├── streamlit/
│   ├── .streamlit/
│   │   ├── DBconnection.py
│   │   └── config.toml
│   ├── analytics.py
│   ├── app.py
│   ├── loginpage.py
│   ├── searchengine.py
│   └── validation.py
├── LICENSE
└── README.md
```

## Architecture Diagram

![Architecture Diagram](https://github.com/BigDataIA-Fall2024-TeamB6/Assignment1/raw/main/diagram/llm_cognition.png)

## Google Cloud Storage links
1. GCS bucket link: https://console.cloud.google.com/storage/browser/gaia_benchmark
2. GCS File Storage Path: https://storage.cloud.google.com/gaia_benchmark/files/file_name

## Live Application Link
1. Streamlit application link: 

## Steps to run application
1. **Clone the Repository**: Clone the repository to your local desktop

   ```bash
   git clone https://github.com/BigDataIA-Fall2024-TeamB6/Assignment1
   ```


## Attestation and Team Contribution
**WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK**

Name | NUID | Contribution% 
--- | --- | --- |
Sandeep Suresh Kumar | 002841297 | 33% 
Gomathy Selvamuthiah | 002410534 | 33% 
Deepthi Nasika       | 002474582 | 33% 
