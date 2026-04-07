#!/usr/bin/env python3
import pandas as pd
from sqlalchemy import create_engine
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main():
    # 1) Connect to your PostgreSQL
    engine_url = 'postgresql://youruserid:yourpassword@webik.ms.mff.cuni.cz:5432/ndbi046'
    engine = create_engine(engine_url)
    
    # 2) Query the joined fact + dims
    sql = '''
    SELECT
      f.fact_id,
      p.provider_id,
      p.name       AS provider_name,
      r.program_id,
      r.program_name,
      f.participants_count
    FROM "29471679_Fact_CourseAccreditation" AS f
    JOIN "29471679_Dim_Provider" AS p
      ON f.provider_id = p.provider_id
    JOIN "29471679_Dim_Program" AS r
      ON f.program_id  = r.program_id
    '''
    
    logging.info("Running SQL to fetch data…")
    df = pd.read_sql_query(sql, engine)
    
    # 3) Write to CSV
    out_file = 'dataset.csv'
    df.to_csv(out_file, index=False)
    logging.info(f"Wrote joined data to {out_file}")
    
    engine.dispose()

if __name__ == "__main__":
    main()
