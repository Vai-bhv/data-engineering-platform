import os
import pandas as pd
import json
import unicodedata

# Define directories for data
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
TRANSFORMED_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'transformed')
os.makedirs(TRANSFORMED_DIR, exist_ok=True)

def transform_akris():
    # Load the provided akris.csv file
    file_path = os.path.join(RAW_DATA_DIR, "akris.csv")
    df = pd.read_csv(file_path, encoding='utf-8', delimiter=',', quotechar='"', engine='python', on_bad_lines='skip')
    
    # 1. Remove duplicates
    df.drop_duplicates(inplace=True)
    
    # 2. Rename columns to a consistent naming convention (lowercase, underscores; fix diacritics)
    df.columns = [unicodedata.normalize("NFKD", col)
                  .encode("ascii", "ignore")
                  .decode("utf-8")
                  .strip()
                  .lower()
                  .replace(" ", "_")
                  for col in df.columns]
    
    # 3. Filter rows to maximum 2000 rows
    df = df.head(2000)
    
    # 4. Standardize text fields (trim whitespace)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # 5. Add surrogate key
    df['akris_surrogate_id'] = range(1, len(df) + 1)
    
    # 6. Convert accreditation number to string (if column exists under diacritic name)
    if 'eíslo_akreditace' in df.columns:
        df['eíslo_akreditace'] = df['eíslo_akreditace'].astype(str)
    
    # 7. Normalize program scope (if present)
    if 'rozsah_programu' in df.columns:
        df['rozsah_programu'] = df['rozsah_programu'].str.lower()
    
    # Save transformed CSV
    transformed_file = os.path.join(TRANSFORMED_DIR, "akris_transformed.csv")
    df.to_csv(transformed_file, index=False)
    print("Transformed akris.csv saved.")
    return df

def transform_social_service():
    # Load the social_service.csv file
    file_path = os.path.join(RAW_DATA_DIR, "social_service.csv")
    df = pd.read_csv(file_path, encoding='utf-8', delimiter=',', quotechar='"', engine='python', on_bad_lines='skip')
    
    # 1. Remove duplicates
    df.drop_duplicates(inplace=True)
    
    # 2. Rename columns based on the provided schema
    df.columns = [col.strip().lower() for col in df.columns]
    
    # 3. Filter rows to maximum 2000 rows
    df = df.head(2000)
    
    # 4. Trim whitespace in text fields
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # 5. Convert numeric columns as necessary
    if 'hodnota' in df.columns:
        df['hodnota'] = pd.to_numeric(df['hodnota'], errors='coerce')
    if 'rok' in df.columns:
        df['rok'] = pd.to_numeric(df['rok'], errors='coerce', downcast='integer')
    
    # 6. Add surrogate key
    df['social_service_surrogate_id'] = range(1, len(df) + 1)
    
    # 7. Standardize region names (convert 'obec_txt' and 'okres_txt' to title case)
    if 'obec_txt' in df.columns:
        df['obec_txt'] = df['obec_txt'].str.title()
    if 'okres_txt' in df.columns:
        df['okres_txt'] = df['okres_txt'].str.title()
    
    # Save transformed CSV
    transformed_file = os.path.join(TRANSFORMED_DIR, "social_service_transformed.csv")
    df.to_csv(transformed_file, index=False)
    print("Transformed social_service.csv saved.")
    return df

def transform_rpss():
    file_path = os.path.join(RAW_DATA_DIR, "rpss.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading rpss.json: {e}")
        return None

    records = []
    for item in data.get("polozky", []):
        try:
            poskytovatel = item.get("poskytovatel", {})
            adresy = poskytovatel.get("adresa", {})
            zarizeni = item.get("zarizeni", [])
            formy = item.get("formy", [])
            record = {
                "id": item.get("id"),
                "identifikator": item.get("identifikator"),
                "datum_od": item.get("datumPoskytovaniOd"),
                "datum_do": item.get("datumPoskytovaniDo"),
                "provider_name": poskytovatel.get("nazev"),
                "ico": poskytovatel.get("ico"),
                "dic": poskytovatel.get("dic"),
                "psc": adresy.get("psc"),
                "kraj": adresy.get("kraj", {}).get("id") if adresy.get("kraj") else None,
                "okres": adresy.get("okres", {}).get("id") if adresy.get("okres") else None,
                "obec": adresy.get("obec", {}).get("id") if adresy.get("obec") else None,
                "ulice": adresy.get("ulice", {}).get("nazev") if adresy.get("ulice") else None,
                "email": (poskytovatel.get("emaily", [{}])[0].get("email")
                          if poskytovatel.get("emaily") else None),
                "telefon": (poskytovatel.get("telefony", [{}])[0].get("telefon")
                            if poskytovatel.get("telefony") else None),
                "web": (poskytovatel.get("weby", [{}])[0].get("web")
                        if poskytovatel.get("weby") else None),
                "zarizeni_count": len(zarizeni),
                "facility_name": zarizeni[0].get("nazev") if zarizeni else None,
                "form_id": formy[0].get("forma", {}).get("id") if formy else None,
                "kapacita": (formy[0].get("kapacity", [{}])[0].get("pocet")
                             if formy and formy[0].get("kapacity") else None),
            }
            records.append(record)
        except Exception as e:
            print(f"Skipping item due to error: {e}")
            continue

    df = pd.DataFrame(records)
    df = df.head(2000)
    df['rpss_surrogate_id'] = range(1, len(df) + 1)

    # Convert date fields to proper string format or None
    df['datum_od'] = pd.to_datetime(df['datum_od'], errors='coerce')
    df['datum_do'] = pd.to_datetime(df['datum_do'], errors='coerce')
    df['datum_od'] = df['datum_od'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else None)
    df['datum_do'] = df['datum_do'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else None)

    transformed_file = os.path.join(TRANSFORMED_DIR, "rpss_transformed.csv")
    df.to_csv(transformed_file, index=False)
    print("Transformed rpss.json saved as rpss_transformed.csv.")
    return df


def transform_join():
    """
    Join akris and social_service datasets by matching location fields.
    We assume that the AKRIS dataset has a column "misto_konani" (normalized from "místo_konání")
    and that this corresponds to the "obec_txt" column from the social service dataset.
    """
    akris_file = os.path.join(TRANSFORMED_DIR, "akris_transformed.csv")
    social_service_file = os.path.join(TRANSFORMED_DIR, "social_service_transformed.csv")
    
    try:
        df_akris = pd.read_csv(akris_file)
        df_social = pd.read_csv(social_service_file)
    except Exception as e:
        print(f"Error loading files for join: {e}")
        return
    
    # Create a join key in AKRIS: check for 'misto_konani'
    if 'misto_konani' in df_akris.columns:
        df_akris['join_key'] = df_akris['misto_konani'].str.lower().str.strip()
    else:
        print("Warning: 'misto_konani' column not found in akris data; join may be incomplete.")
        df_akris['join_key'] = ""
    
    # Create a join key in Social Service from 'obec_txt'
    if 'obec_txt' in df_social.columns:
        df_social['join_key'] = df_social['obec_txt'].str.lower().str.strip()
    else:
        print("Warning: 'obec_txt' column not found in social service data; join may be incomplete.")
        df_social['join_key'] = ""
    
    # Perform a left join on the join_key column
    df_joined = pd.merge(df_akris, df_social, on='join_key', how='left', suffixes=('_akris', '_social'))
    
    # Save the joined dataset
    joined_file = os.path.join(TRANSFORMED_DIR, "joined_transformed.csv")
    df_joined.to_csv(joined_file, index=False)
    print("Joined dataset saved as joined_transformed.csv.")
    return df_joined

def main():
    print("Starting transformations...")
    transform_akris()
    transform_social_service()
    transform_rpss()
    transform_join()  # Optional join for integration insights
    print("All transformations complete.")

if __name__ == "__main__":
    main()
