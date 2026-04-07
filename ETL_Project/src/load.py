import os
import json
import pandas as pd
import psycopg2
from psycopg2 import sql

# Database connection parameters
DB_HOST = "webik.ms.mff.cuni.cz"
DB_PORT = 5432
DB_NAME = "ndbi046"
DB_USER = "stud_29471679"
DB_PASSWORD = "Gro!Cla#543"

# Define the directory for transformed data
TRANSFORMED_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'transformed')

def load_csv_to_table(csv_file, table_name, conn):
    """Load CSV file data into a PostgreSQL table."""
    df = pd.read_csv(csv_file)
    tuples = [tuple(x) for x in df.to_numpy()]
    cols = ','.join(list(df.columns))
    
    query = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
        sql.Identifier(table_name),
        sql.SQL(cols)
    )
    from psycopg2.extras import execute_values
    cur = conn.cursor()
    try:
        execute_values(cur, query.as_string(conn), tuples)
        conn.commit()
        print(f"Data loaded into {table_name} successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error loading data into {table_name}: {e}")
    finally:
        cur.close()

def load_json_data_to_table(json_data, table_name, conn):
    """
    Load a list of JSON strings into a table that has a single JSONB column called joined_data.
    """
    tuples = [(data_str,) for data_str in json_data]
    cur = conn.cursor()
    query = sql.SQL("INSERT INTO {} (joined_data) VALUES %s").format(sql.Identifier(table_name))
    from psycopg2.extras import execute_values
    try:
        execute_values(cur, query.as_string(conn), tuples)
        conn.commit()
        print(f"Data loaded into {table_name} successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error loading data into {table_name}: {e}")
    finally:
        cur.close()

def main():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("Connected to PostgreSQL database.")
    except Exception as e:
        print(f"Database connection error: {e}")
        return

    try:
        # Load akris_transformed.csv for Provider, Program, and Fact_CourseAccreditation
        akris_csv = os.path.join(TRANSFORMED_DIR, "akris_transformed.csv")
        df_akris = pd.read_csv(akris_csv)
        
        # Insert into Dim_Provider (using provider name and accreditation)
        df_provider = df_akris[['nazev_vzdilavatele', 'eislo_akreditace']].drop_duplicates().rename(
            columns={'nazev_vzdilavatele': 'name', 'eislo_akreditace': 'accreditation'}
        )
        df_provider.to_csv("provider_temp.csv", index=False)
        load_csv_to_table("provider_temp.csv", "29471679_Dim_Provider", conn)
        
        # Insert into Dim_Program (using program name and program scope)
        df_program = df_akris[['nazev_avzpr', 'rozsah_programu']].drop_duplicates().rename(
            columns={'nazev_avzpr': 'program_name', 'rozsah_programu': 'program_scope'}
        )
        df_program.to_csv("program_temp.csv", index=False)
        load_csv_to_table("program_temp.csv", "29471679_Dim_Program", conn)
        
        # Create dummy fact data for Fact_CourseAccreditation
        fact_data = {
            "provider_id": [1] * 100,
            "program_id": [1] * 100,
            "participants_count": [100] * 100,
            "program_duration": ['30 days'] * 100,
            "course_date": ['2024-01-01'] * 100
        }
        df_fact = pd.DataFrame(fact_data)
        df_fact.to_csv("fact_temp.csv", index=False)
        load_csv_to_table("fact_temp.csv", "29471679_Fact_CourseAccreditation", conn)
        
        # Load Social Service data into Dim_SocialService
        social_csv = os.path.join(TRANSFORMED_DIR, "social_service_transformed.csv")
        df_social = pd.read_csv(social_csv)
        if 'social_service_surrogate_id' in df_social.columns:
            df_social.drop(columns=['social_service_surrogate_id'], inplace=True)
        df_social.to_csv("social_temp.csv", index=False)
        load_csv_to_table("social_temp.csv", "29471679_Dim_SocialService", conn)
        
        # Load RPSS data into Dim_RPSS:
        rpss_csv = os.path.join(TRANSFORMED_DIR, "rpss_transformed.csv")
        df_rpss = pd.read_csv(rpss_csv)

        # Option 1: Drop the datum_do column entirely
        if 'datum_do' in df_rpss.columns:
            df_rpss.drop(columns=['datum_do'], inplace=True)

        # Save the CSV without datum_do
        df_rpss.to_csv("rpss_temp.csv", index=False)
        load_csv_to_table("rpss_temp.csv", "29471679_Dim_RPSS", conn)

        
        # Load Joined dataset into fact_joined: convert each row to JSON string
        joined_csv = os.path.join(TRANSFORMED_DIR, "joined_transformed.csv")
        if os.path.exists(joined_csv):
            df_joined = pd.read_csv(joined_csv)
            json_data = df_joined.apply(lambda row: row.to_json(), axis=1).tolist()
            load_json_data_to_table(json_data, "29471679_fact_joined", conn)
        else:
            print("joined_transformed.csv not found. Skipping joined dataset load.")
        
    except Exception as e:
        print(f"Error during loading process: {e}")
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
