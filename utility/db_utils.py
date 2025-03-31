import pymysql, os
import pandas as pd
from dateutil import parser

secrets = {
    "rds_host" : os.getenv("RDS_HOST"),
    "rds_user" : os.getenv("RDS_USER"),
    "rds_password" : os.getenv("RDS_PASSWORD"),
    "rds_db_name" : os.getenv("RDS_DB_NAME")
}

def db_connection_test():
    try:
        conn = pymysql.connect(
            host=secrets["rds_host"],
            port=3306,
            user=secrets["rds_user"],
            password=secrets["rds_password"],
            db=secrets["rds_db_name"]
        )
        cursor = conn.cursor()
        print("DATABASE CONNECTION SUCCESSFULL", cursor)
    except Exception as e:
        print("UNABLE TO CONNECT TO THE DATABASE", e)

db_connection_test()

def read_data_from_db_as_df(query):
    conn = pymysql.connect(
        host=secrets["rds_host"],
        port=3306,
        user=secrets["rds_user"],
        password=secrets["rds_password"],
        db=secrets["rds_db_name"]
    )
    cursor = conn.cursor()

    # Execute a query to retrieve data from the database
    cursor.execute(query)
    # Fetch the results of the query
    rows = cursor.fetchall()
    # Load the results into a Pandas DataFrame
    df = pd.DataFrame(rows, columns=[i[0] for i in cursor.description])
    cursor.close()
    conn.close()
    return df

def insert_data_into_db_save_game_log(datestamp, timestamp, user_id, scores):
    conn = pymysql.connect(
        host=secrets["rds_host"],
        port=3306,
        user=secrets["rds_user"],
        password=secrets["rds_password"],
        db=secrets["rds_db_name"]
    )
    cursor = conn.cursor()

    ## Part 1
    query_1 = "SELECT * FROM game_reports WHERE user_id = %s"
    cursor.execute(query_1, (user_id,))
    rows = cursor.fetchall()

    ## Part 2
    query_2 = "INSERT INTO game_reports (date, time, user_id, number_of_successive_correct_score, attempt) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query_2, (datestamp, timestamp, user_id, scores, (len(rows) + 1) ))
    conn.commit()

    cursor.close()
    conn.close()

def insert_data_into_db_user_cache_logs(lofitems):
    conn = pymysql.connect(
        host=secrets["rds_host"],
        port=3306,
        user=secrets["rds_user"],
        password=secrets["rds_password"],
        db=secrets["rds_db_name"]
    )
    cursor = conn.cursor()
    timestamp, datestamp, userId, question = lofitems
    ## Part 2
    query = "INSERT INTO user_cache_logs (date, time, user_id, question) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (timestamp, datestamp, userId, question))
    conn.commit()

    cursor.close()
    conn.close()

def read_data_from_db(query, argument):
    conn = pymysql.connect(
        host=secrets["rds_host"],
        port=3306,
        user=secrets["rds_user"],
        password=secrets["rds_password"],
        db=secrets["rds_db_name"]
    )
    cursor = conn.cursor()
    cursor.execute(query, argument)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

def insert_data_to_db(query, argument):
    conn = pymysql.connect(
        host=secrets["rds_host"],
        port=3306,
        user=secrets["rds_user"],
        password=secrets["rds_password"],
        db=secrets["rds_db_name"]
    )
    cursor = conn.cursor()
    cursor.execute(query, argument)
    conn.commit()

    cursor.close()
    conn.close()
    
 
def convert_to_date(row):
  return str(parser.parse(row).date())

# df = pd.read_excel("/content/user_not_satisfied.xlsx")
# df['Date'] = df['Date'].apply(convert_to_date)
# df = df.where((pd.notnull(df)), None)

# for i, row in tqdm(df.iterrows()):
#   query = "INSERT INTO quiz_data (question, option_1 , option_2, option_3, option_4, answer) VALUES (%s, %s, %s, %s, %s, %s)"
#   cursor.execute(query, (row['Question'], row['Option 1'], row['Option 2'], row['Option 3'], row['Option 4'], row['Answer']))

#   query = "INSERT INTO game_reports (date, time, user_id, number_of_successive_correct_score, attempt) VALUES (%s, %s, %s, %s, %s)"
#   cursor.execute(query, (row['Datestamp'], row['Timestamp'], row['number_of_successive_correct_score'], row['attempt']))
  
#   query = "INSERT INTO user_cache_logs (date, time, user_id, question) VALUES (%s, %s, %s, %s)"
#   cursor.execute(query, (row['Date'], row['Time'], row['UserId'], row['question']))

#   query = "INSERT INTO user_comments (date, user_id, rating, comments) VALUES (%s, %s, %s, %s)"
#   cursor.execute(query, (row['Date'], row['Unique User_Id'], row['Rating'], row['Comment']))

#   query = "INSERT INTO user_escalations (date, user_id) VALUES (%s, %s)"
#   cursor.execute(query, (row['Date'], row['Sender']))

#   query = "INSERT INTO user_not_satisfied (date, user_id, message_content) VALUES (%s, %s, %s)"
#   cursor.execute(query, (row['Date'], row['Unique User_Id'], row['Message Content']))
  
#   conn.commit()
# cursor.close()
# conn.close()
