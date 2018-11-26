import requests
import datetime

print(requests.post("http://127.0.0.1:5000/api/new_patient", json={
    "patient_id": 4,
    "attending_email": "abg28@duke.edu",
    "user_age": 25
}).json())

print(requests.post("http://127.0.0.1:5000/api/heart_rate", json={
    "patient_id": 4,
    "heart_rate": 250
}).json())

print(requests.get("http://127.0.0.1:5000/api/status/4").json())

print(requests.get("http://127.0.0.1:5000/api/heart_rate/4").json())

print(requests.get("http://127.0.0.1:5000/api/heart_rate/average/4").json())

print(requests.post("http://127.0.0.1:5000/api/heart_rate/interval_average",
                    json={"patient_id": 4,
                          "heart_rate_average_since":
                              str(datetime.datetime.now())}
                    ).json())
