# ETL Project for Czech Social Services & Training Data

## 1. Overview

This project implements a complete ETL (Extract, Transform, Load) workflow that integrates three datasets from Czech sources:
- **Akris Dataset (CSV):** Contains accreditation course data.
- **Social Service Dataset (CSV):** Contains statistics on social service facilities (e.g., number of facilities per municipality). Documentation and schema are provided.
- **RPSS Dataset (JSON):** Retrieved via an API call from [https://data.mpsv.cz/od/soubory/rpss/rpss.json](https://data.mpsv.cz/od/soubory/rpss/rpss.json).

The workflow extracts the data from various sources, applies several meaningful transformations to ensure quality and consistency, loads the processed data into a PostgreSQL data warehouse using a star schema, and finally produces a set of visualizations to illustrate key insights.

---

## 2. System Requirements

- **Operating System:** Linux, macOS, or Windows
- **Python:** Version 3.x
- **Database:** PostgreSQL (access the server at `webik.ms.mff.cuni.cz`)
- **Required Python Libraries:**  
  - `requests`
  - `pandas`
  - `psycopg2`
  - `matplotlib`

---

## 3. Installation Instructions

1. **Clone the Repository:**

   ```bash
   git clone https://gitlab.mff.cuni.cz/teaching/ndbi046/2024-25/vaibhav-gupta/-/tree/main/ETL_Project/
   cd ETL_Project

2. **Create and Activate a Virtual Environment:**
    python3 -m venv venv
    source venv/bin/activate   # On Windows use: venv\Scripts\activate

3. **Install Required Packages:**
    pip install -r requirements.txt

4. **Database Setup:**
    Ensure you have access to the PostgreSQL database at webik.ms.mff.cuni.cz. (psql -h webik.ms.mff.cuni.cz -p 5432 -U [username] -d ndbi046)
    Execute the SQL script in sql/create_tables.sql to create the necessary tables in your database (\i /home/vaibhav/Desktop/intro_to_data_engineering/ETL_Project/sql/create_tables.sql
)

## 4. Repository Structure and Script Descriptions

The repository is organized as follows:

ETL_Project/
├── README.md
├── LICENSE
├── requirements.txt
├── sql/
│   └── create_tables.sql      # DDL for the star schema and required tables
├── data/
│   ├── raw/                   # Raw input datasets
│   │   ├── akris.csv          # Accreditation course data
│   │   ├── social_service.csv # Social service statistics
│   │   └── rpss.json          # RPSS dataset retrieved via API
│   └── transformed/           # Transformed datasets (output of transformation step)
│       ├── akris_transformed.csv
│       ├── social_service_transformed.csv
│       ├── rpss_transformed.csv
│       └── joined_transformed.csv  # (Optional) Joined dataset of akris and social service data
├── src/
│   ├── extract.py             # Extraction script: downloads CSV files and retrieves JSON from API.
│   ├── transform.py           # Transformation script: cleans, standardizes, and enriches datasets.
│   ├── load.py                # Load script: inserts transformed data into PostgreSQL tables.
│   └── visualize.py           # Visualization script: generates plots from the transformed data.
└── visualizations/            # Contains the output visualization files (PNG)

Script Details
    extract.py 
        Input: None (the script downloads or reads raw files from data/raw/).
        Output: Saves downloaded CSV files and JSON file into data/raw/.
        Purpose:
            Downloads akris.csv from a given URL(https://data.mpsv.cz/documents/1749923/7049685/akris.csv)
            Retrieves rpss.json via an API call(https://data.mpsv.cz/od/soubory/rpss/rpss.json)
            social_service.csv is already present.
    
    transform.py
        Input: Raw data files from data/raw/ (CSV and JSON).
        Output: Transformed CSV files in data/transformed/:
            akris_transformed.csv
            social_service_transformed.csv
            rpss_transformed.csv
            joined_transformed.csv (optional integration of akris and social service data)\
        Key Transformations and Reasons:
            Duplicate Removal: Ensures data quality by eliminating duplicate rows.
            Column Renaming: Converts column names to lower case with underscores and removes diacritics (e.g., “místo konání” → misto_konani) for consistency and easier processing.
            Row Limiting: Filters datasets to a maximum of 2000 rows for demonstration and resource management.
            Whitespace Trimming: Standardizes text fields by removing extra spaces.
            Surrogate Key Addition: Adds unique surrogate keys (e.g., akris_surrogate_id, social_service_surrogate_id, rpss_surrogate_id) to simplify later joins and maintain data integrity.
            Data Type Conversion: Converts columns such as accreditation numbers and date fields to the appropriate data types.
            Optional Join: oins the akris and social_service datasets on a normalized location field (e.g., misto_konani vs. obec_txt) to integrate training provider data with social service statistics. This integration provides insights such as matching training capacity with regional social service demands.
        
    load.py
        Input: Transformed CSV files from data/transformed/.
        Output: Inserts data into PostgreSQL tables according to the star schema.
        Purpose:
            Loads dimension data into tables such as Dim_Provider, Dim_Program, Dim_SocialService, and Dim_RPSS.
            Loads fact data (e.g., Fact_CourseAccreditation and optionally a joined fact table) for analysis.
            The script uses the psycopg2 library with fast bulk insertion methods.

    visualize.py
        Input: Transformed CSV files from data/transformed/.
        Output: PNG image files stored in the visualizations/ folder:
            program_distribution.png
            social_service_statistics.png
            rpss_distribution.png
        Purpose:
            Generates a bar chart showing the distribution of accredited programs by location.
            Produces a bar chart of social service facilities grouped by municipality.
            Creates a line plot (or alternative plot) that summarizes RPSS capacity or record counts by region.


## 5. ETL Workflow Diagram and Explanation
Workflow Diagram : Below is a simplified text-based diagram illustrating the ETL process:

               +---------------------+
               |  Raw Data Sources   |
               |---------------------|
               | akris.csv         |<-- File Download
               | social_service.csv|<-- Provided File
               | rpss.json         |<-- API Extraction
               +---------------------+
                         |
                         v
               +---------------------+
               |   Extraction        |
               | (extract.py)        |
               +---------------------+
                         |
                         v
               +---------------------+
               |  Transformation     |
               |  (transform.py)     |
               |---------------------|
               | - Remove duplicates |
               | - Standardize names |
               | - Limit rows        |
               | - Trim whitespace   |
               | - Add surrogate keys|
               | - Data type conversion  |
               | - Join datasets     |
               +---------------------+
                         |
                         v
               +---------------------+
               |      Loading        |
               |   (load.py)         |
               |---------------------|
               | PostgreSQL Data     |
               | Warehouse (Star     |
               | Schema)             |
               +---------------------+
                         |
                         v
               +---------------------+
               |   Visualization     |
               |   (visualize.py)      |
               |---------------------|
               | - Program Distribution |
               | - Social Service Stats |
               | - RPSS Analysis         |
               +---------------------+

Explanation of ETL Steps
1.  Extraction:
        Sources:
            The akris and social service datasets are read as CSV files.
            The RPSS dataset is fetched via an API call and saved as a JSON file.
        Purpose: To gather data from diverse sources (file downloads and web requests) ensuring multi-format input.

2.  Transformation:
        Cleaning: Duplicate removal and whitespace trimming ensure consistent, high-quality data.
        Standardization: Renaming columns to a uniform naming scheme (lower case, underscores) eases future integration and SQL querying.
        Row Limiting: Capping to 2000 rows simplifies development and testing.
        Surrogate Key Generation: Adding unique IDs facilitates table joins and future data warehouse operations.
        Data Type Conversion: Ensuring that dates, numbers, and strings have the correct formats prevents errors during loading.
        Integration (Join): By joining akris and social service data on location keys, we correlate training program availability with regional social service capacity, revealing potential gaps or overlaps.

3.  Loading:
        Data Warehouse Design: The data warehouse uses a star schema with separate dimension tables (e.g., for providers, programs, social services, and RPSS data) and a central fact table for course accreditation data.
        Insertion : The load script uses bulk insert operations (via psycopg2.extras.execute_values) to efficiently insert transformed records into the PostgreSQL tables.

4. Visualization:
        Insights: Visualizations such as the program distribution by location, social service statistics by municipality, and RPSS capacity trends allow for a quick assessment of the integrated data and help identify regional imbalances or training gaps.

        Program Distribution by Location:
            File: program_distribution.png
            Function: plot_program_distribution()

            How it works!
                Reads the transformed Akris dataset (akris_transformed.csv) from the data/transformed/ folder.
                Counts how many accredited programs (misto_konani column) occur in each unique location.
                Creates a bar chart:
                    x-axis: The unique locations (místo konání)
                    y-axis: Number of accredited programs at each location
            Insights / Observations
                as we only see one large bar , it suggests that most of the records in the dataset share the same location value, or that the column might contain something unexpected (e.g., a date instead of an actual place).
            How to Interpret the Chart:
                High bar: The location with the highest number of accredited programs.
                Low or no bar: Indicates fewer or zero programs at that location (or it’s not in the dataset).

         Social Service Facilities by Municipality:
            File: social_service_statistics.png
            Function: plot_social_service_statistics()

            How It works!
                Reads the transformed Social Service dataset (social_service_transformed.csv).
                Groups the data by municipality (obec_txt) and sums the hodnota column, which represents the number of social service facilities.
                Creates a bar chart:
                    x-axis: Municipality name
                    y-axis: Total facilities (summed across each municipality)

            Insights / Observations:
                As seen in your screenshot, the x-axis has many municipalities, creating a “long tail” distribution (a few municipalities with very high facility counts, and many with very low counts).
                Some municipalities might have dozens of facilities, while most have only a few or none.
            
            How to Interpret the Chart:
                Municipalities on the far left with tall bars: They have the highest total number of social service facilities.
                Long tail on the right: Indicates a large number of municipalities with relatively few facilities.

        RPSS Average Capacity by Region (kraj)
            File: rpss_distribution.png
            Function: plot_rpss_distribution()

            How It Works!
                Reads the transformed RPSS dataset (rpss_transformed.csv).
                Groups by the region (kraj column) and calculates the average capacity (kapacita) for each region.
                Creates a line chart:
                    x-axis: The region IDs (e.g., Kraj/19, Kraj/27, etc.)
                    y-axis: Average capacity
            Insights / Observations
                The screenshot shows a descending line from left to right, indicating some regions have significantly higher average capacity than others.
                For instance, if Kraj/19 is near 160 average capacity and Kraj/60 is closer to 20, it implies that Kraj/19 has more capacity in these RPSS records.

            How to Interpret the Chart:
                Higher average capacity means that, on average, facilities or services in that region can serve more clients or have more resources available.
                Lower average capacity might suggest limited resources or smaller facility sizes in those regions.      

     Summary of Insights
        Program Distribution (Akris)
            Highlights which locations have the most (or least) accredited training programs.
            Potentially reveals a gap if many courses are concentrated in one location and missing in others.

        Social Service Facilities
            Shows how municipalities differ in the number of social service facilities.
            A strong skew or “long tail” distribution suggests a few areas with many facilities, and many areas with few or none.

        RPSS Capacity
            Provides a regional breakdown of service capacity, helping identify potential disparities.
            Regions with very low average capacity might need more attention or investment in services.

    By comparing these three plots, we can identify correlations (e.g., do regions with a high average capacity in RPSS also have many accredited programs? Or do municipalities with many facilities also have corresponding training opportunities?).

## 6. Data Warehouse Diagram and Description

Star Schema Overview : The data warehouse is designed with a star schema to support analytical queries. The schema consists of:
    Dimension Tables:
        Dim_Provider: Contains provider details (name, accreditation).
        Dim_Program: Stores information about training programs (program name, scope).
        Dim_SocialService: Holds statistics from the social service dataset (facility counts, regional data).
        Dim_RPSS: Includes details from the RPSS dataset (provider information, capacity, and other attributes).
    
    Fact Table:
        Fact_CourseAccreditation: Records measures related to training programs (e.g., participant counts, duration, course dates).
            This table uses foreign keys linking to the dimension tables (e.g., provider_id, program_id).

Diagram (Text-Based)

                +-----------------+
                |  Dim_Provider   |
                |-----------------|
                | provider_id (PK)|
                | name            |
                | accreditation   |
                +-----------------+
                        |
                        | FK
                        v
                +-----------------+
                | Fact_Course     |
                | Accreditation   |
                |-----------------|
                | fact_id (PK)    |
                | provider_id (FK)|
                | program_id (FK) |
                | participants    |
                | duration        |
                | course_date     |
                +-----------------+
                        ^
                        | FK
                +-----------------+
                |  Dim_Program    |
                |-----------------|
                | program_id (PK) |
                | program_name    |
                | program_scope   |
                +-----------------+

A similar design applies to the social service and RPSS dimensions, each linked via foreign keys as necessary. This structure allows analytical queries to quickly aggregate training metrics by provider, program, or regional social service capacity.


        
