from loggerConfig import logger
from datetime import datetime
import requests
import pandas as pd
import json
import csv
import re


def clean_string(value):
    """Remove extra spaces and characters from a string."""
    if isinstance(value, str):
        # Remove extra spaces at the beginning and end
        value = value.strip()
        # Replace multiple spaces with a single space
        value = re.sub(r'[\x00\s\n]', ' ', value)
        # Mark empty strings as None (null)
        return f'"{value}"' if value else '""'
    return f'"{str(value)}"'


def clean_data(data):
    """Recursively clean each value in the dictionary."""
    for key, value in data.items():
        if value is None:
            # Replace None with an empty string
            data[key] = '""'
        if isinstance(value, dict):
            # Clean and convert nested dictionaries to JSON strings
            data[key] = json.dumps(clean_data(value))
        elif isinstance(value, list):
            # Convert list to string
            data[key] = json.dumps([clean_string(v) if isinstance(v, str) else str(v) for v in value])
        else:
            # Clean and convert everything else to a string
            data[key] = clean_string(str(value) if value else "")
    return data

def process_json_file(file_path):
    processed_data = []
    # Loads the entire jsonl metadata file
    with open(file_path, 'r') as file:
        for line in file:
            try:
                # Parse each line as JSON
                json_data = json.loads(line)
                # Clean the data
                cleaned_data = clean_data(json_data)
                
                processed_data.append(cleaned_data)
            except json.JSONDecodeError as e:
                print(f"Error parsing line: {line}")
                print(f"Error message: {e}")
    return processed_data

def load_into_csv(data, csv_file_path):
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def jsonData():
    json_file_path = r"C:\Documents\BigData\Assignment_1\Data\GAIA\2023\validation\metadata.jsonl"
    csv_file_path = 'parsed_data.csv'
    processed_data = process_json_file(json_file_path)
    load_into_csv(processed_data, csv_file_path)


def main():
    curr_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Remove colons
    # log = logger(f"dataExtractor_Logger_{curr_time}", f"dataExtractor_{curr_time}_log.log")
    print("Inside main function")
    data = jsonData()

    # #Converting csv to pandas
    processed_csv_file_path = r"C:\Documents\BigData\Assignment_1\database\parsed_data.csv"
    df = pd.read_csv(processed_csv_file_path)
    print(df["file_name"].head(20))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error while executing main function: {e}")
        raise(e)