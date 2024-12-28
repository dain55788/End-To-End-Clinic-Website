from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow import DAG
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the API_KEY
api_key = os.getenv("SENDGRID_API_KEY")


def email(arr, to_mail):
    # ssl._create_default_https_context = ssl._create_unverified_context
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)
    import base64
    message = Mail(
        from_email='dainnguyen1307@gmail.com',
        to_emails=to_mail,
        subject='Nhắc Nhở Lịch Khám',
        html_content='<img src="https://static.vecteezy.com/system/resources/previews/019/956/427/non_2x/healthy-food-logo-premium-vector.jpg"'
                     'style="width:300px; height:auto;">'
                     '<h1> Nhắc nhở lịch khám </h1>'
                     f'<br>Tên bệnh nhân: <b>{arr["patient_name"]}</b><br>'
                     f'<br>Số điện thoại: <b>{arr["phone"]}</b><br>'
                     f'<br>Ngày khám: <b>{arr["appointment_date"]}</b><br>'
                     f'<br>Địa chỉ: 97 Võ Văn Tần, Quận 3, Thành phố Hồ Chí Minh<br>'   
                     f'<br>Ghi chú: Nhớ mang theo <b>CĂN CƯỚC CÔNG DÂN</b> và <b>BẢO HIỂM Y TẾ</b> bạn nhé!!<br>'
    )

    # main execution
    sg = SendGridAPIClient("")
    # your actual Sendgrid API key here
    sg.send(message)


def send_emails():
    # Get valid arrangements
    with open("/opt/airflow/Private-Clinic-Website/data/arrangements.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    # Extract list of arrangements
    valid_arrangements = data.get("arrangements", [])
    # Loop through each arrangement and send an email
    for arr in valid_arrangements:
        patient_email = arr.get("email")
        print(f"Sending email to: {patient_email} for patient: {arr['patient_name']}")
        email(arr, patient_email)


# default arguments of a DAG
default_args = {
    'owner' : 'DainyNgyn',
    'depends_on_past':False,
    'start_date': datetime(2024, 12, 13),
    'email': ['dain55788@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries':1,
    'retry_delay':timedelta(seconds=5),
    'catchup_by_default':False
}


# Define a DAG
email_dag = DAG(
    'Arrangement_Email',
    description='Automatically sending arrangement announcement email to patient ',
    default_args=default_args,
    schedule_interval='0 11 * * *',  # send arrangement email to patient at 8p.m daily
    tags=['arrangement_email_sendgrid'],
    catchup=False,
)


email_sender = PythonOperator(
    task_id='Arrangement_Email_Sending',
    python_callable=send_emails,
    dag=email_dag
)

# DAG task dependencies (EXTRACT - TRANSFORM - LOAD)
email_sender
