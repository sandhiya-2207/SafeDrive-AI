# File: emergency_module.py
# Project: SafeDrive AI
# Purpose: Generate an emergency SOS message


def generate_sos_message(latitude, longitude, emergency_type):
    message = f"""
        SAFEDRIVE AI - EMERGENCY SOS

        Emergency Type: {emergency_type}

        Vehicle Location:
        Latitude: {latitude}
        Longitude: {longitude}

        Please contact the driver and provide assistance.
    """

    return message.strip()


def get_emergency_types():
    return [
        "Accident",
        "Vehicle Breakdown",
        "Medical Emergency",
        "Other Emergency"
    ]