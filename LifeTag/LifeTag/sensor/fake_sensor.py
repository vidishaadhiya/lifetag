import random

def get_sensor_data():
    return {
        "heart_rate": random.randint(70, 100),
        "temperature": round(random.uniform(36.5, 37.5), 1),
        "spo2": random.randint(95, 100)
    }

