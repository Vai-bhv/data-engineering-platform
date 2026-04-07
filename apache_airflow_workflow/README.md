# ETL Workflow for Czech Social Services & Training Data

This repository contains an Apache Airflow DAG that implements an end-to-end ETL workflow for integrating data from Czech social service and training datasets. The repository includes system requirements, installation instructions, a description of the DAG script, an MIT License file, and a .gitignore file.

---

## System Requirements

- **Operating System:** Linux, macOS, or Windows  
- **Python:** Version 3.x (tested with Python 3.8+)  
- **Apache Airflow:** Version 2.x (configured via Docker Compose)  
- **PostgreSQL:** A database accessible from Airflow (connection ID used: `postgres_webik`)  
- **Required Python Libraries:**  
  - requests  
  - pandas  
  - psycopg2  
  - (Other libraries required by your Airflow providers can be installed through the Docker container or your environment)

---

## Installation Instructions

1. **Set Up Airflow with Docker Compose:**
Make sure you have Docker and Docker Compose installed. Then, create and configure an .env file (optional but recommended) to set the AIRFLOW_UID environment variable. See the Airflow Docker Compose documentation for details.

2. **Initialize and Run the Airflow Environment:**
sudo docker compose up airflow-init
sudo docker compose up

3. **Place the Raw Data File:**
Ensure that the file social_service.csv (the social service dataset) is present in the data/raw/ folder. The other files (akris.csv and rpss.json) are downloaded automatically by the DAG.

4. **Access the Airflow UI:**
Open your browser and navigate to http://localhost:8080 to view and trigger your DAG.



## Description of the Script File

The only Python script in this repository is the Apache Airflow DAG, which is implemented in the file:
-   File: etl_airflow_dag.py
-   Description:
        Extraction Group:
                Waits for social_service.csv using a FileSensor.
                Downloads akris.csv from a remote URL.
                Retrieves rpss.json via an API call.
                File paths are passed via XCom.
        Transformation Group:
            Processes the raw datasets using functions defined in src/transform.py (files are transformed and saved to data/transformed/).
            Creates an optional joined dataset for integration of training and social service data.
        Loading Group:
            Loads the transformed CSVs into PostgreSQL tables using a custom bulk load operator (or equivalent Python functions from src/load.py).
            Uses the PostgreSQL connection with ID postgres_webik.
        Visualization Group:
            Runs the visualization script (src/visualize.py) to generate PNG charts.
        Scheduling:
            The DAG is scheduled to run monthly on the 1st day at midnight using the cron expression 0 0 1 * *.
        Task Groups & XComs:
            The workflow is clearly organized into task groups for better readability, and file paths are shared via XComs between tasks.
                    

