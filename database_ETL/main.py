import logging
import subprocess
import os

# Logger function
logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("Inside main function")

    # Load files from Hugging Face into GCP
    try:
        subprocess.run(['python', 'fileLoader.py'], check = True)
        print("Successfully executed fileLoader.py")
    except Exception as e:
        print(f"Error executing fileLoader.py: {e}")
        raise e
    
    # Process JSON file and load it into CSV
    try:
        subprocess.run(['python', 'jsonParser.py'], check=True)
        print("Successfully executed jsonParser.py")
    except Exception as e:
        print(f"Error executing jsonParser.py: {e}")
        raise e
    
    # Upload data to MySQL
    try:
        subprocess.run(['python', 'connectDB.py'], check=True)
        print("Successfully executed connectDB.py")
    except Exception as e:
        print(f"Error executing connectDB.py: {e}")
        raise e

if __name__ == "__main__":
    main()