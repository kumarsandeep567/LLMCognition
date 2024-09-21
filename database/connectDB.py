from mysql.connector import Error
import os
import mysql.connector
import pandas as pd

def execute_select_query(conn):
    query = 'SELECT * FROM gaia_features;'
    conn.execute(query)
    res = conn.fetchall()
    print(f"The query execution results are:")
    for row in res:
        print(row)

def execute_insert_query(conn, formatted_data):
    insert_query = """
    INSERT INTO gaia_features (task_id, question, level, final_answer, file_name, file_path)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    for item in formatted_data:
        conn.execute(insert_query, (item['task_id'], item['question'], item['level'], item['final_answer'], item['file_name'], item['file_path']))

    print("Insert statement executed successfully")

def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host = 'localhost',
            database = 'gaia_benchmark',
            user = 'team6',
            password = 'root@team6'
        )

        if connection.is_connected():
            print("Connected to MySQL database successfully")
            cursor = connection.cursor()
            return cursor, connection
    except Error as e:
        print(f"Error as {e}")
        raise e

def main():
    cursor, connection = connect_to_mysql()
    try:
        execute_select_query(cursor)
        df = pd.read_csv('C:\Documents\BigData\Assignment_1\database\parsed_data.csv')

        formatted_data = []

        for index, row in df.iterrows():
            formatted_row = {
                'task_id': row["task_id"].strip('"'),
                'question': row["Question"].strip('"'),
                'level': int(row["Level"].strip('"')),
                'final_answer': row['Final answer'].strip('"'),
                'file_name': None if ((pd.isna(row['file_name'])) or (row['file_name'] == '')) else row['file_name'].strip('"'),
                'file_path': None
            }
            formatted_data.append(formatted_row)


        execute_insert_query(cursor, formatted_data)
        execute_select_query(cursor)
        connection.commit()
    except Exception as e:
        print(f"Error = {e}")
        raise e
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error while executing main function: {e}")
        raise(e)