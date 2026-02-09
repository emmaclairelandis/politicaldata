####################
# POSTGRESQL SETUP #
####################

# This file will be used to populate the PostgreSQL database with information found online regarding US legislators and their voting data.
#
# Useful video:
# https://www.youtube.com/watch?v=miEFm1CyjfM

import requests
import os
import psycopg2
import yaml
from dotenv import load_dotenv

# We don't want to put sensitive information in the code, so we use this to load from the .env file in the root directory of the program.
load_dotenv()

# PostgreSQL asks that you connect to it like a server for writing and what have you.
# It isn't a single file or anything. It's a bunch of files. 
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

# Let's make a variable called cur to run SQL commands.
# Would this be better higher up for cleanliness?
# https://www.sqlines.com/postgresql/datatypes/serial
# https://www.w3schools.com/sql/sql_syntax.asp
cur = conn.cursor()

# We execute the command that is...
cur.execute("""
CREATE TABLE IF NOT EXISTS legislators (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    gender CHAR(1)
);
""")


###############
# LEGISLATORS #
###############

# We'll be more careful with the state legislators.
STATE_DIR = "data"

def insert_state_legislator(file_path):
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    
    #external_id = data.get("id")
    full_name = data.get("name")
    gender = data.get("gender")
    if gender:
        gender = gender[0].upper()  # F/M
    
    cur.execute("""
    INSERT INTO legislators (full_name, gender)
    VALUES (%s, %s)
    """, (full_name, gender))

# Walk through all states
for state in os.listdir(STATE_DIR):
    state_path = os.path.join(STATE_DIR, state, "legislature")
    if not os.path.isdir(state_path):
        continue
    for file in os.listdir(state_path):
        if file.endswith(".yml"):
            file_path = os.path.join(state_path, file)
            insert_state_legislator(file_path)


######################
# *GIVES YOU TREATS* #
######################

conn.commit()
cur.close()
conn.close()
print("Meow! :3c")