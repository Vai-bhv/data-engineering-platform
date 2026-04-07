-- SQL script to create the star schema in the PostgreSQL data warehouse

-- Dimension Table: Provider (from akris_transformed.csv)
CREATE TABLE IF NOT EXISTS "29471679_Dim_Provider" (
    provider_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    accreditation VARCHAR(100)
);

-- Dimension Table: Program (from akris_transformed.csv)
CREATE TABLE IF NOT EXISTS "29471679_Dim_Program" (
    program_id SERIAL PRIMARY KEY,
    program_name VARCHAR(255),
    program_scope VARCHAR(255)
);

-- Dimension Table: Social Service (from social_service_transformed.csv)
CREATE TABLE IF NOT EXISTS "29471679_Dim_SocialService" (
    social_service_id SERIAL PRIMARY KEY,
    idhod VARCHAR(255),
    hodnota NUMERIC,
    stapro_kod VARCHAR(50),
    dsz_cis INTEGER,
    dsz_kod VARCHAR(50),
    rok INTEGER,
    obec_kod VARCHAR(50),
    obec_txt VARCHAR(255),
    okres_kod VARCHAR(50),
    okres_txt VARCHAR(255),
    dsz_txt VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS "29471679_Dim_RPSS" (
    rpss_id SERIAL PRIMARY KEY,
    id TEXT,
    identifikator TEXT,
    datum_od DATE,
    provider_name VARCHAR(255),
    ico VARCHAR(50),
    dic VARCHAR(50),
    psc VARCHAR(50),
    kraj VARCHAR(50),
    okres VARCHAR(50),
    obec VARCHAR(50),
    ulice VARCHAR(255),
    email VARCHAR(255),
    telefon VARCHAR(50),
    web VARCHAR(255),
    zarizeni_count INTEGER,
    facility_name VARCHAR(255),
    form_id VARCHAR(100),
    kapacita INTEGER,
    rpss_surrogate_id INTEGER
);


-- Fact Table: Course Accreditation (sample from akris_transformed.csv)
CREATE TABLE IF NOT EXISTS "29471679_Fact_CourseAccreditation" (
    fact_id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES "29471679_Dim_Provider"(provider_id),
    program_id INTEGER REFERENCES "29471679_Dim_Program"(program_id),
    participants_count INTEGER,
    program_duration VARCHAR(50),
    course_date DATE
);

-- Fact Table: Joined Data (stores the entire joined row as JSONB)
CREATE TABLE IF NOT EXISTS "29471679_fact_joined" (
    fact_joined_id SERIAL PRIMARY KEY,
    joined_data JSONB
);
