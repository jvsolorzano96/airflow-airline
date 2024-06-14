from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pandas as pd
import requests
import json
import re
import pytz
from pytz.exceptions import UnknownTimeZoneError
from pytz import timezone
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import numpy as np
import os

def airline_pipeline():

    def transform_column_name(name):
        parts = name.split('.')
        camel_case = parts[0] + ''.join(part.capitalize() for part in parts[1:])
        snake_case_to_camel_case = re.sub(r'_(\w)', lambda m: m.group(1).upper(), camel_case)
        return snake_case_to_camel_case

    def convert_to_cordoba_timezone(dt_series):
        try:
            cordoba_tz = pytz.timezone('America/Argentina/Cordoba')
            dt_series = pd.to_datetime(dt_series, utc=True)
            return dt_series.apply(lambda x: x.tz_convert(cordoba_tz) if pd.notnull(x) else x)
        except UnknownTimeZoneError:
            return pd.NaT
        
    def truncate_value(value, max_length=50):
        if isinstance(value, str) and len(value) > max_length:
            return value[:max_length]
        return value

    access_key = os.getenv("ACCESS_KEY_API")
    endpoint = os.getenv("ENDPOINT_API")

    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST_DAG")
    POSTGRES_PORT = "5432"  

    params = {
        "access_key": access_key,
        "limit": 100
    }

    try:
        response = requests.get(url=endpoint, params=params)
        response.raise_for_status()
        print("Respuesta obtenida con éxito")
    except requests.exceptions.RequestException as e:
        print(f"Error conectando con API: {e}")
        return

    response_text = response.text

    print(f"responde_text: {response_text}")

    response_dict = json.loads(response_text)

    print(f"response_dict: {response_dict}")

    flight_data = response_dict["data"]

    print(f"flight_data: {flight_data}")

    df = pd.json_normalize(flight_data)
    df.columns = [transform_column_name(col) for col in df.columns]

    print("Transformacion a dataframe exitosa")

    df['departureScheduledCordoba'] = convert_to_cordoba_timezone(df['departureScheduled'])
    df['arrivalScheduledCordoba'] = convert_to_cordoba_timezone(df['arrivalScheduled'])
    df["flightDuration"] = df['arrivalScheduledCordoba'] - df['departureScheduledCordoba']

    cordoba_tz = timezone('America/Argentina/Cordoba')
    current_time_cordoba = datetime.now(cordoba_tz)
    df["createdAt"] = current_time_cordoba

    df['departureScheduledCordoba'] = df['departureScheduledCordoba'].astype(str)
    df['arrivalScheduledCordoba'] = df['arrivalScheduledCordoba'].astype(str)
    df["flightDuration"] = df['flightDuration'].astype(str)
    df["createdAt"] = df['createdAt'].astype(str)

    columns_to_normalize = ['departureTimezone', 'arrivalTimezone']
    df[columns_to_normalize] = df[columns_to_normalize].applymap(lambda x: x.replace('/', '-') if isinstance(x, str) else x)

    df = df[['flightDate', 'flightStatus', 'departureAirport', 'departureTimezone', 'departureTerminal', 'departureGate', 'departureDelay',
             'departureScheduled', 'departureEstimated', 'arrivalAirport', 'arrivalTimezone', 'arrivalTerminal', 'arrivalGate', 'arrivalBaggage',
             'arrivalDelay', 'arrivalScheduled', 'arrivalEstimated', 'airlineName', 'flightNumber', 'departureScheduledCordoba',
             'arrivalScheduledCordoba', 'flightDuration','createdAt']]

    df = df.replace({np.nan: None}).applymap(lambda x: None if pd.isna(x) else x)
    df.fillna("0", inplace=True)

    for col in df.columns:
        df[col] = df[col].apply(truncate_value)

    try:
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        cursor = conn.cursor()
        print("Conexion exitosa con BD")
    except psycopg2.OperationalError as e:
        print(f"Error conectando a la base de datos: {e}")
        return

    table_name = 'testdata'

    insert_query = sql.SQL("""
        INSERT INTO {} ({})
        VALUES %s
    """).format(sql.Identifier(table_name), sql.SQL(', ').join(map(sql.Identifier, df.columns)))

    data_tuples = [tuple(x) for x in df.to_numpy()]
    try:
        execute_values(cursor, insert_query.as_string(conn), data_tuples)
        conn.commit()
        print("Registros insertados")
    except Exception as e:
        print(f"Error insertando datos: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

### AIRFLOW ARGS

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 6, 13),
    'email': ['solorzano.vco@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'airline_pipeline',
    default_args=default_args,
    description='DAG ejecutando pipeline de datos aerolinea Fligoo',
    schedule_interval=timedelta(days=1),
    catchup=False
)

tarea = PythonOperator(
    task_id='airline_pipeline',
    python_callable=airline_pipeline,
    dag=dag,
)
