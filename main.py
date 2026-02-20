####################
# POSTGRESQL SETUP #
####################

# This file will be used to populate the PostgreSQL database with information found online regarding US legislators and their voting data.
#
# Useful video:
# https://www.youtube.com/watch?v=miEFm1CyjfM

import os # Optional if you're using an external .env file for database login details
import psycopg2 # Our PostgreSQL stuff
import time # The progress meter when running the code
import us # This is a US civic project, thus, you will be referencing the MANY states often
import yaml # OpenStates uses yaml
from dotenv import load_dotenv # Not super necessary other than for security

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
# Note: We do not include DOB information because that is not public for most state legislators.
cur.execute("""
CREATE TABLE IF NOT EXISTS legislators (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    given_name TEXT,
    middle_name TEXT,
    family_name TEXT,
    gender CHAR(1)
);
""")

# Parties
# Note: D/R/I. Legislators from Minnesota such as Erin Murphy who are under the DFL will be categorized as D. Legislators from North Dakota such as Kathy Hogan who are under the NPL will also be categorized as D. Funny thing about this OpenStates database is that the DFL is distinguished, but not the NPL. Have I adequately stressed my disagreements with the inconsistencies present here?
cur.execute("""
CREATE TABLE IF NOT EXISTS parties (
    id SERIAL PRIMARY KEY,
    abbreviation CHAR(1) UNIQUE NOT NULL CHECK (abbreviation IN ('D','R','I'))
);
""")

# Jurisdictions
# Note: What STATE do you represent, and is it at the FEDERAL or STATE level?
cur.execute("""
CREATE TABLE IF NOT EXISTS jurisdictions (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    abbrev CHAR(2) NOT NULL UNIQUE,
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
# Note: 5, 12, AL, etc. Might need to mess with the formatting, because the repo we're pulling this data from saves, Wyoming for instance, as WY-AL. Not sure what's preferable. CHAR(2)?
cur.execute("""
CREATE TABLE IF NOT EXISTS districts (
    id SERIAL PRIMARY KEY,
    chamber_id INT REFERENCES chambers(id),
    district_number TEXT NOT NULL
);
""")

# Terms
# Note: This might be useful for keeping data about terms other than the current one, including retired members, and keeping a rolling database of some kind. Not sure. One critical flaw of the OpenStates database though is that people like Ann Rest who have been around and changed districts for over 25 years have no more than their current term catalogued, whereas congressmembers like Bernard Sanders who have been around just as long or longer have all of the terms catalogued. That is one of the many fundamental flaws of this database, although for my purposes and goals, I only care about incumbents, so it isn't the biggest deal. 
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

    # OpenStates handles names... oddly. Middle names are paired with family names, and suffixes aren't included at all except as an other name.
    # Let's see about handling a separate column for middle names that's entirely optional for all family_name with spaces. 
    # We wholely ignore the Jr. in anyone whose name has it right now, because it's frankly not very important, and OpenStates hides it away in their database. For example, Donald Sternoff Beyer Jr. is catalogued as merely Donald Beyer. I find it a horrible and inconsistent way for them to organize their data, but hey, you work with what you can get. 
    # In Java, we might use a substring, which you should have learned early on in your typical CSC110 class. For Python, on the other hand, we're gonna do some slicing... of sorts!
    # https://stackoverflow.com/questions/27387415/how-would-i-get-everything-before-a-in-a-string-python
    full_name = data.get("name") # Debbie Wasserman Schultz
    given_name = data.get("given_name") # Debbie

    family_raw = data.get("family_name", "") # Wasserman Schultz
    parts = family_raw.split()

    if len(parts) == 0: # Debbie
        middle_name = None # [null]
        family_name = None # [null]
    elif len(parts) == 1: # Debbie Schultz
        middle_name = None # [null]
        family_name = parts[0] # Schultz
    else: # Debbie Wasserman Schultz
        middle_name = " ".join(parts[:-1]) # Wasserman
        family_name = parts[-1] # Schultz

    gender = data.get("gender")
    if gender:
        gender = gender[0].upper()

    cur.execute("""
        INSERT INTO legislators (full_name, given_name, middle_name, family_name, gender)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """, (full_name, given_name, middle_name, family_name, gender))
    # Individuals with two or more words in their last name are not completely covered, such as with:
    # Steve St. Clair, Oscar De Los Santos, Donovan Dela Cruz, Sue Lee Loy, Trish La Chica, Lori Den Hartog, and about a dozen others. 


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