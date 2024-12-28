from datetime import datetime, timedelta
from app.src.models import Arrangement
import app.data
import json
import os


def get_valid_arrangements():  # compare using the appointment_date information
    # Get today's date and the next day's date
    today = datetime.now().date()
    next_day = today + timedelta(days=1)
    next_day = str(next_day)
    # Query to get all arrangements that are scheduled for the next day
    # arrangements = Arrangement.query.all()
    valid_arrangements = []
    # for arr in arrangements:
    #     arr.appointment_date = str(arr.appointment_date)
    #     if arr.appointment_date.__eq__(next_day):
    #         valid_arrangements.append(arr)
    return valid_arrangements


def save_arrangements_to_json():
    valid_arrangements = get_valid_arrangements()

    # Prepare the data to be written to JSON
    arrangements_data = {
        "sum_number_of_arrangements": len(valid_arrangements),
        "arrangements": []
    }

    # Extract relevant details from each arrangement
    for arr in valid_arrangements:
        arrangements_data["arrangements"].append({
            "email": arr.email,
            "patient_name": arr.patient_name,
            "phone": arr.phone,
            "appointment_date": arr.appointment_date
        })

    # Write data to a JSON file
    output_file = "data/arrangements.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(arrangements_data, file, indent=4, ensure_ascii=False)

    print(f"Valid arrangements saved to {output_file}")


save_arrangements_to_json()
