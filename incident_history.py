from datetime import datetime


def create_incident(incident_type, severity, description):
    """
    Create a record of a simulated SafeDrive AI incident.
    """

    incident = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": incident_type,
        "severity": severity,
        "description": description,
        "data_source": "Simulation"
    }

    return incident


def add_incident(incident_history, incident_type, severity, description):
    """
    Add a new incident to the current incident history.
    """

    incident = create_incident(
        incident_type,
        severity,
        description
    )

    incident_history.append(incident)

    return incident_history


def get_incident_summary(incident_history):
    """
    Summarise the incidents recorded during the current session.
    """

    total = len(incident_history)

    high = sum(
        1 for incident in incident_history
        if incident["severity"].upper() == "HIGH"
    )

    medium = sum(
        1 for incident in incident_history
        if incident["severity"].upper() == "MEDIUM"
    )

    low = sum(
        1 for incident in incident_history
        if incident["severity"].upper() == "LOW"
    )

    return {
        "total": total,
        "high": high,
        "medium": medium,
        "low": low
    }