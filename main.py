####################
# POSTGRESQL SETUP #
####################

# This file will be used to populate the PostgreSQL database with information found online regarding US legislators and their voting data.
#
# Useful video:
# https://www.youtube.com/watch?v=miEFm1CyjfM

import os
import psycopg2
import time
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


##########
# TABLES #
##########

# Legislators
# Note: We do not include DOB information because that is not public for most state legislators. Additionally, the family name currently also includes all middle names. Bit of a bug. 
cur.execute("""
CREATE TABLE IF NOT EXISTS legislators (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    given_name TEXT,
    family_name TEXT,
    gender CHAR(1)
);
""")

# Parties
# Note: D/R/I
cur.execute("""
CREATE TABLE IF NOT EXISTS parties (
    id SERIAL PRIMARY KEY,
    abbreviation CHAR(1)
);
""")

# Jurisdictions
# Note: What STATE do you represent, and is it at the FEDERAL or STATE level?
cur.execute("""
CREATE TABLE IF NOT EXISTS jurisdictions (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    abbrev CHAR(2),
    type TEXT CHECK (type IN ('state','federal'))
);
""")

# Chambers
# Note: HOUSE or SENATE
cur.execute("""
CREATE TABLE IF NOT EXISTS chambers (
    id SERIAL PRIMARY KEY,
    jurisdiction_id INT REFERENCES jurisdictions(id),
    name TEXT NOT NULL CHECK (name IN ('House','Senate'))
);
""")

# Districts
# Note: 12, At-Large, etc. Might need to mess with the formatting, because the repo we're pulling this data from saves, Wyoming for instance, as WY-AL. Not sure what's preferable.
cur.execute("""
CREATE TABLE IF NOT EXISTS districts (
    id SERIAL PRIMARY KEY,
    chamber_id INT REFERENCES chambers(id),
    district_number TEXT NOT NULL
);
""")

# Terms
# Note: This might be useful for keeping data about terms other than the current one, including retired members, and keeping a rolling database of some kind. Not sure. 
cur.execute("""
CREATE TABLE IF NOT EXISTS terms (
    id SERIAL PRIMARY KEY,
    legislator_id INT NOT NULL REFERENCES legislators(id),
    district_id INT NOT NULL REFERENCES districts(id),
    party_id INT REFERENCES parties(id),
    start_date DATE NOT NULL,
    end_date DATE,
    election_year INT
);
""")


###############
# LEGISLATORS #
###############

STATE_DIR = "data"

def insert_state_legislator(file_path):
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)

    full_name = data.get("name")
    given_name = data.get("given_name")
    family_name = data.get("family_name")

    gender = data.get("gender")
    if gender:
        gender = gender[0].upper()

    cur.execute("""
        INSERT INTO legislators (full_name, given_name, family_name, gender)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """, (full_name, given_name, family_name, gender))


#########
# FILES #
#########

files = []

for state in os.listdir(STATE_DIR):
    state_path = os.path.join(STATE_DIR, state, "legislature")
    if not os.path.isdir(state_path):
        continue

    for file in os.listdir(state_path):
        if file.endswith(".yml"):
            files.append(os.path.join(state_path, file))

total = len(files)
print(f"Found {total} legislators to import.\n")

############
# PROGRESS #
############

start_time = time.perf_counter()

for i, file_path in enumerate(files, start=1):
    insert_state_legislator(file_path)

    percent = (i / total) * 100

    print(f"\rProgress: {i}/{total} ({percent:6.2f}%)", end="", flush=True)


##########
# FINISH #
##########

conn.commit()
cur.close()
conn.close()

elapsed = time.perf_counter() - start_time
minutes = int(elapsed // 60)
seconds = int(elapsed % 60)

print(f"\n\nDONE in {minutes}m {seconds}s")