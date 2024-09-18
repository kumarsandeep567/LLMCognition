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