# LLM Cognition
The goal of this project is to evaluate the comprehension capabilities of a Large Language Model (LLM), specifically OpenAI's GPT-4o. 
This project is influenced by the General AI Assistant (GAIA) dataset and benchmark, developed by researchers at Meta AI, Hugging Face, and AutoGPT.

The framework enables users to:
- Extract data from the GAIA dataset
- Prompt the LLM with the dataset’s predefined prompts
- Collect and rank the LLM's responses
- Re-prompt the LLM in cases of incorrect responses
- Analyze response statistics

---

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
   


---

### Contributors take note!
Please avoid commiting to the `main` branch directly. Instead, create your own branch (say `api` branch) and push your changes to your own branch. 

How to create a your own branch?
1. Clone the repository using `git clone <repo_url>` and navigate to the repository via terminal
2. Create a new branch (keeping `main` branch as reference) `git branch <new_branch_name> main`
3. Switch to your branch with `git checkout <new_branch_name>`
4. Learn more at [git - the simple guide (website)](https://rogerdudler.github.io/git-guide/)

**Ready to merge?**
- Please create a pull request before merging your branch with the `main` branch
- Improper merges can break stuff
