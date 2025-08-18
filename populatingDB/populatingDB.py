import psycopg2
import csv
import sys
import io
import os
from dotenv import load_dotenv
# Load environment variables from the .env file
load_dotenv()
# Force UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# This function processes CSV data into an array
def generate_array_for_csv_data(file_path):
    array_of_data = []  # To store data from CSV file

    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # This skips the header row of the file
        
        for row in csv_reader:
            # Access the data from the file and add the data to tempArray
            array_of_data.append(row)  # Append the row directly (not as a nested list)
    
    # Print the array with UTF-8 encoding
    return array_of_data

def write_to_database(arr):
    try: # Add some error handling in case the database connection fails
        conn = psycopg2.connect(host="localhost", dbname="coursework_db", user="postgres", password=os.getenv("POSTGRESQL_PASSWORD"), port=5432) # Setup database connection - password censored for security
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
            """ # This is some weird formatting but it works I guess
            # Execute the SQL statement with parameters
            cur.execute(query, i)

        # Commit the changes to the database
        conn.commit()

        # Close the cursor and connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Use a raw string to avoid invalid escape sequences
    csv_file_path = 'populatingDB/topic1_5.csv'
    data_array = generate_array_for_csv_data(csv_file_path)
    write_to_database(data_array)