"""
etl_airflow_dag.py

This DAG implements an end-to-end ETL workflow for the Czech Social Services & Training Data project.
It is decomposed into four task groups:
  - Extraction: Downloads akris.csv and retrieves rpss.json, while waiting for social_service.csv via a FileSensor.
  - Transformation: Performs data cleaning, standardization, type conversion, and creates an optional joined dataset.
  - Loading: Inserts transformed CSVs into PostgreSQL tables using a custom bulk load operator.
  - Visualization: Generates PNG charts from the transformed data.
  
Data paths and file names are shared between tasks using XComs. The DAG is scheduled to run monthly using a Cron expression.
The PostgreSQL connection ID is set to “postgres_webik”.
"""

import os
from datetime import datetime, timedelta

from airflow.decorators import dag, task, task_group
from airflow.operators.empty import EmptyOperator
from airflow.sensors.filesystem import FileSensor
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.utils.dates import days_ago

# -----------------------------------------------
# Custom Operator: PostgresBulkLoadOperator
# -----------------------------------------------
class PostgresBulkLoadOperator(BaseOperator):
    """
    Custom operator to bulk load CSV data into a PostgreSQL table.
    The file path is templated so it can use XComs.
    """
    template_fields = ("table_name", "file_path")

    @apply_defaults
    def __init__(self, *, postgres_conn_id: str, table_name: str, file_path: str, **kwargs):
        super().__init__(**kwargs)
        self.postgres_conn_id = postgres_conn_id
        self.table_name = table_name
        self.file_path = file_path

    def execute(self, context):
        from airflow.hooks.postgres_hook import PostgresHook
        try:
            hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
            self.log.info(f"Bulk loading data from {self.file_path} into {self.table_name}")
            with open(self.file_path, "r") as f:
                # Read header line to get column names
                columns = f.readline().strip().split(",")
                copy_sql = f"COPY {self.table_name} ({', '.join(columns)}) FROM STDIN WITH CSV HEADER"
                # Use the hook's copy_expert to execute the COPY command
                hook.copy_expert(copy_sql, f.name)
            self.log.info(f"Successfully loaded data into {self.table_name}")
        except FileNotFoundError:
            self.log.error(f"File '{self.file_path}' not found.")
            raise
        except Exception as ex:
            self.log.error(f"An error occurred: {ex}")
            raise


# -----------------------------------------------
# Default DAG arguments
# -----------------------------------------------
default_args = {
    "owner": "your_username",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}


# -----------------------------------------------
# DAG Definition using TaskFlow API and Task Groups
# -----------------------------------------------
@dag(
    dag_id="etl_workflow_dag",
    default_args=default_args,
    description="ETL workflow for Czech Social Services & Training Data",
    schedule_interval="0 0 1 * *",  # Cron: Run at midnight on the 1st day of every month
    start_date=days_ago(1),
    catchup=False,
    tags=["etl", "airflow"],
)
def etl_workflow():
    # ----------------------------------------------------------
    # 1) Extraction Task Group
    # ----------------------------------------------------------
    @task_group(group_id="extraction")
    def extraction_group():
        """
        Extraction Group:
        - Wait for the manual file social_service.csv via FileSensor.
        - Download akris.csv from a URL.
        - Retrieve rpss.json via an API call.
        Returns an empty anchor operator after all extraction tasks are complete.
        """
        # Wait for social_service.csv to be present in data/raw/
        social_service_sensor = FileSensor(
            task_id="social_service_sensor",
            filepath=os.path.join("data", "raw", "social_service.csv"),
            poke_interval=30,
            timeout=300,
            mode="poke",
        )

        @task
        def extract_akris():
            from src.extract import download_file
            akris_url = "https://data.mpsv.cz/documents/1749923/7049685/akris.csv"
            path = download_file(akris_url, "akris.csv")
            return path  # XCom: return file path

        @task
        def extract_rpss():
            from src.extract import extract_json
            rpss_url = "https://data.mpsv.cz/od/soubory/rpss/rpss.json"
            path = extract_json(rpss_url, "rpss.json")
            return path

        akris_path = extract_akris()
        rpss_path = extract_rpss()

        extraction_done = EmptyOperator(task_id="extraction_done")
        social_service_sensor >> extraction_done
        akris_path >> extraction_done
        rpss_path >> extraction_done
        return extraction_done

    # ----------------------------------------------------------
    # 2) Transformation Task Group
    # ----------------------------------------------------------
    @task_group(group_id="transformation")
    def transformation_group():
        """
        Transformation Group:
        - Transforms akris.csv into akris_transformed.csv.
        - Transforms social_service.csv into social_service_transformed.csv.
        - Transforms rpss.json into rpss_transformed.csv.
        - Joins akris and social_service datasets into joined_transformed.csv.
        Returns an empty anchor operator after transformations.
        """
        @task
        def transform_akris():
            from src.transform import transform_akris
            transform_akris()  # writes to data/transformed/akris_transformed.csv internally
            return os.path.join("data", "transformed", "akris_transformed.csv")

        @task
        def transform_social_service():
            from src.transform import transform_social_service
            transform_social_service()  # writes to data/transformed/social_service_transformed.csv
            return os.path.join("data", "transformed", "social_service_transformed.csv")

        @task
        def transform_rpss():
            from src.transform import transform_rpss
            transform_rpss()  # writes to data/transformed/rpss_transformed.csv
            return os.path.join("data", "transformed", "rpss_transformed.csv")

        @task
        def transform_join():
            from src.transform import transform_join
            transform_join()  # writes to data/transformed/joined_transformed.csv
            return os.path.join("data", "transformed", "joined_transformed.csv")

        akris_tf = transform_akris()
        social_tf = transform_social_service()
        rpss_tf = transform_rpss()
        joined_tf = transform_join()

        transform_done = EmptyOperator(task_id="transform_done")
        [akris_tf, social_tf, rpss_tf, joined_tf] >> transform_done
        return transform_done

    # ----------------------------------------------------------
    # 3) Loading Task Group
    # ----------------------------------------------------------
    @task_group(group_id="loading")
    def loading_group():
        """
        Loading Group:
        - Loads Provider & Program data from akris_transformed.csv into their respective tables.
        - Loads Social Service data from social_service_transformed.csv.
        - Loads RPSS data from rpss_transformed.csv.
        - Loads the joined dataset into a fact table.
        Uses the custom PostgresBulkLoadOperator (or equivalent Python tasks) to perform bulk loading.
        Returns an empty anchor operator after loading is complete.
        """
        @task
        def load_provider_program():
            from src.load import load_csv_to_table
            path = os.path.join("data", "transformed", "akris_transformed.csv")
            # In production, pass an actual connection using postgres_conn_id "postgres_webik"
            load_csv_to_table(path, "29471679_Dim_Provider", "postgres_webik")
            load_csv_to_table(path, "29471679_Dim_Program", "postgres_webik")
            return "Loaded Provider & Program."

        @task
        def load_social_service():
            from src.load import load_csv_to_table
            path = os.path.join("data", "transformed", "social_service_transformed.csv")
            load_csv_to_table(path, "29471679_Dim_SocialService", "postgres_webik")
            return "Loaded Social Service."

        @task
        def load_rpss():
            from src.load import load_csv_to_table
            path = os.path.join("data", "transformed", "rpss_transformed.csv")
            load_csv_to_table(path, "29471679_Dim_RPSS", "postgres_webik")
            return "Loaded RPSS."

        @task
        def load_joined():
            from src.load import load_csv_to_table
            path = os.path.join("data", "transformed", "joined_transformed.csv")
            load_csv_to_table(path, "29471679_fact_joined", "postgres_webik")
            return "Loaded Joined Fact."

        provider_status = load_provider_program()
        social_status = load_social_service()
        rpss_status = load_rpss()
        joined_status = load_joined()

        load_done = EmptyOperator(task_id="load_done")
        [provider_status, social_status, rpss_status, joined_status] >> load_done
        return load_done

    # ----------------------------------------------------------
    # 4) Visualization Task Group
    # ----------------------------------------------------------
    @task_group(group_id="visualization")
    def visualization_group():
        """
        Visualization Group:
        - Generates data visualizations from the transformed datasets.
        Calls the visualization script from src/visualize.py which outputs PNG charts.
        Returns an empty anchor operator after visualizations are complete.
        """
        @task
        def visualize():
            from src.visualize import main as visualize_main
            visualize_main()
            return "Visualizations generated."

        viz_status = visualize()
        viz_done = EmptyOperator(task_id="viz_done")
        viz_status >> viz_done
        return viz_done

    # ----------------------------------------------------------
    # Final DAG Chain: Extraction -> Transformation -> Loading -> Visualization
    # ----------------------------------------------------------
    extraction_anchor = extraction_group()
    transformation_anchor = transformation_group()
    loading_anchor = loading_group()
    visualization_anchor = visualization_group()

    extraction_anchor >> transformation_anchor >> loading_anchor >> visualization_anchor

# Instantiate the DAG
etl_dag = etl_workflow()
