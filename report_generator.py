from datetime import datetime
import csv
import io


def generate_safety_report(
    risk_score,
    risk_level,
    speed,
    weather,
    road_condition,
    stopping_distance,
    following_distance,
    collision_level,
    driver_status,
    vehicle_health_status,
    incidents
):
    """
    Generate a text safety report using simulated dashboard data.
    """

    report = []

    report.append("=" * 55)
    report.append("             SAFEDRIVE AI SAFETY REPORT")
    report.append("=" * 55)

    report.append(
        f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    report.append("")
    report.append("1. DRIVING CONDITIONS")
    report.append(f"Vehicle Speed: {speed} km/h")
    report.append(f"Weather Condition: {weather}")
    report.append(f"Road Condition: {road_condition}")

    report.append("")
    report.append("2. RISK ANALYSIS")
    report.append(f"Driving Risk Score: {risk_score}/100")
    report.append(f"Driving Risk Level: {risk_level}")
    report.append(f"Illustrative Stopping Distance: {stopping_distance} m")
    report.append(f"Illustrative Following Distance: {following_distance} m")
    report.append(f"Collision Risk Indicator: {collision_level}")

    report.append("")
    report.append("3. DRIVER MONITORING")
    report.append(f"Simulated Driver Status: {driver_status}")

    report.append("")
    report.append("4. VEHICLE HEALTH")
    report.append(f"Simulated Vehicle Health: {vehicle_health_status}")

    report.append("")
    report.append("5. INCIDENT HISTORY")

    if incidents:
        for number, incident in enumerate(incidents, start=1):
            report.append(f"Incident {number}")
            report.append(f"Time: {incident.get('time', 'Unknown')}")
            report.append(f"Type: {incident.get('type', 'Unknown')}")
            report.append(f"Severity: {incident.get('severity', 'Unknown')}")
            report.append(
                f"Description: {incident.get('description', 'No description')}"
            )
            report.append("")
    else:
        report.append("No incidents recorded in this session.")

    report.append("")
    report.append("IMPORTANT DISCLAIMER")
    report.append(
        "This report is generated from a demonstration prototype."
    )
    report.append(
        "Values may be simulated and are not validated vehicle measurements."
    )
    report.append(
        "Do not use this report as a substitute for professional driving "
        "judgement, vehicle diagnostics, or emergency services."
    )

    report.append("=" * 55)

    return "\n".join(report)


def generate_incident_csv(incidents):
    """
    Convert incident history into downloadable CSV text.
    """

    output = io.StringIO()

    fieldnames = [
        "time",
        "type",
        "severity",
        "description",
        "data_source"
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for incident in incidents:
        writer.writerow({
            field: incident.get(field, "")
            for field in fieldnames
        })

    return output.getvalue()