def get_hazard_database():
    """
    Return fictional road hazards for the SafeDrive AI demonstration.

    These records are simulated and are not verified accident locations.
    """

    hazards = [
        {
            "id": 1,
            "name": "Simulated Hazard Zone A",
            "latitude": 11.0168,
            "longitude": 76.9558,
            "hazard_type": "Accident-Prone Demonstration Zone",
            "severity": "High",
            "description": "Fictional demonstration of a high-risk road zone."
        },
        {
            "id": 2,
            "name": "Simulated Hazard Zone B",
            "latitude": 11.0250,
            "longitude": 76.9700,
            "hazard_type": "Poor Road Condition",
            "severity": "Medium",
            "description": "Fictional demonstration of a damaged road section."
        },
        {
            "id": 3,
            "name": "Simulated Hazard Zone C",
            "latitude": 11.0050,
            "longitude": 76.9400,
            "hazard_type": "Low Visibility",
            "severity": "High",
            "description": "Fictional demonstration of a low-visibility zone."
        },
        {
            "id": 4,
            "name": "Simulated Hazard Zone D",
            "latitude": 11.0350,
            "longitude": 76.9500,
            "hazard_type": "Traffic Congestion",
            "severity": "Medium",
            "description": "Fictional demonstration of a congested road."
        },
        {
            "id": 5,
            "name": "Simulated Hazard Zone E",
            "latitude": 11.0100,
            "longitude": 76.9800,
            "hazard_type": "Road Obstruction",
            "severity": "Low",
            "description": "Fictional demonstration of a road obstruction."
        }
    ]

    return hazards


def get_hazards_by_severity(severity):
    """
    Filter simulated hazards by severity.
    """

    hazards = get_hazard_database()

    return [
        hazard
        for hazard in hazards
        if hazard["severity"].lower() == severity.lower()
    ]


def get_hazards_by_type(hazard_type):
    """
    Filter simulated hazards by their type.
    """

    hazards = get_hazard_database()

    return [
        hazard
        for hazard in hazards
        if hazard["hazard_type"].lower() == hazard_type.lower()
    ]