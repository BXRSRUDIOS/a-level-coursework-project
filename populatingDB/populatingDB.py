import psycopg2
import csv
import sys
import io
import os
from dotenv import load_dotenv
# environment variables from the .env file need loading
load_dotenv()
# Force UTF-8 
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# processes CSV data into an array
def generate_array_for_csv_data(file_path):
    array_of_data = []  #  store data from CSV file

    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # skips the header row of the file
        
        for row in csv_reader:
            # add data to array
            array_of_data.append(row) 
    
    # Print the array with UTF-8 encoding
    return array_of_data

def write_to_database(arr):
    try: # Add some error handling in case the database connection fails
        # Setup database connection - password censored for security
        conn = psycopg2.connect(host="localhost", dbname="coursework_db", user="postgres", password=os.getenv("POSTGRESQL_PASSWORD"), port=5432)
        cur = conn.cursor() # The cursor actually does the SQL work

        # Iterate through array and insert each row into entity
        for i in arr:
            # SQL Statement
            query = """
                INSERT INTO question (
                    questionName, correctAnswer, incorrectAnswerA, 
                    incorrectAnswerB, incorrectAnswerC, difficulty, 
                    topicCode, feedback
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """ 
            # execute the sql statement with parameters
            cur.execute(query, i)

        # commit changes
        conn.commit()

        # close cursor and connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"An error occurred: {e}") # error handling stuff

if __name__ == "__main__":
    csv_file_path = 'populatingDB/topic2_5.csv'
    data_array = generate_array_for_csv_data(csv_file_path)
    write_to_database(data_array)