# This file will be used to populate the PostgreSQL database with information found online regarding US legislators and their voting data.
#
# Useful video:
# https://www.youtube.com/watch?v=miEFm1CyjfM

import requests
import os
import psycopg2
from dotenv import load_dotenv

# We don't want to put sensitive information in the code, so we use this to load from the .env file in the root directory of the program.
load_dotenv()

# A repo with some basic information we need about legislators.
url = "https://unitedstates.github.io/congress-legislators/legislators-current.json"

# Fetch :3c and parse.
response = requests.get(url)
legislators_data = response.json()

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
    external_id TEXT UNIQUE,
    full_name TEXT NOT NULL,
    birthday DATE,
    gender CHAR(1)
);
""")

# Get the data we need GAHAHAHAHAHAHAHAH!!!!!!
# Lowkey though, this feels so much cleaner and easy to work with than JSON in Java (ToT)
for person in legislators_data:
    bioguide = person["id"].get("bioguide")
    name = person["name"].get("official_full") or (
        person["name"].get("first", "") + " " + person["name"].get("last", "")
    )
    birthday = person["bio"].get("birthday")
    gender = person["bio"].get("gender")

    cur.execute("""
    INSERT INTO legislators (external_id, full_name, birthday, gender)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (external_id) DO NOTHING;
    """, (bioguide, name, birthday, gender))

conn.commit()
cur.close()
conn.close()
print("Meow! :3c")