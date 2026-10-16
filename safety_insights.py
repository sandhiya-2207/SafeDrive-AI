def generate_safety_insights(
    speed,
    weather,
    road_condition,
    risk_score,
    driver_status,
    vehicle_health_status
):
    """
    Generate safety insights using the demonstration dashboard inputs.

    These are rule-based suggestions, not AI predictions or
    a validated vehicle-safety assessment.
    """

    insights = []

    # Speed insights
    if speed > 100:
        insights.append(
            "Speed is very high in this demonstration. "
            "Follow posted speed limits and adjust to road conditions."
        )
    elif speed > 80:
        insights.append(
            "Review your speed and ensure it is appropriate "
            "for the road and traffic conditions."
        )
    else:
        insights.append(
            "Continue observing posted speed limits and traffic conditions."
        )

    # Weather insights
    if weather == "Rainy":
        insights.append(
            "Rain can reduce tyre grip. Increase following distance "
            "and avoid sudden braking."
        )
    elif weather == "Foggy":
        insights.append(
            "Fog can reduce visibility. Slow down appropriately "
            "and use suitable vehicle lights."
        )
    else:
        insights.append(
            "Continue checking visibility and changing weather conditions."
        )

    # Road-condition insights
    if road_condition == "Poor":
        insights.append(
            "Poor road conditions may increase driving risk. "
            "Watch for potholes and avoid sudden manoeuvres."
        )
    elif road_condition == "Moderate":
        insights.append(
            "Remain alert for uneven surfaces and possible road hazards."
        )

    # Overall risk score
    if risk_score >= 60:
        insights.append(
            "The demonstration risk score is HIGH. Review the selected "
            "conditions and prioritise safe driving."
        )
    elif risk_score >= 30:
        insights.append(
            "The demonstration risk score is MEDIUM. Review the "
            "factors contributing to the score."
        )
    else:
        insights.append(
            "The demonstration risk score is LOW under the current "
            "simplified rules. This does not guarantee safety."
        )

    # Driver-monitoring status
    if driver_status == "HIGH":
        insights.append(
            "The simulated driver-monitoring indicators are HIGH. "
            "If you feel drowsy or distracted, stop somewhere safe "
            "before continuing."
        )
    elif driver_status == "MEDIUM":
        insights.append(
            "The simulated driver-monitoring indicators are MEDIUM. "
            "Review the selected inputs and remain attentive."
        )

    # Vehicle-health status
    if vehicle_health_status == "WARNING":
        insights.append(
            "The simulated vehicle-health status is WARNING. "
            "Have actual vehicle issues checked by a qualified mechanic."
        )
    elif vehicle_health_status == "CHECK":
        insights.append(
            "The simulated vehicle-health status indicates CHECK. "
            "Verify any concerns using the vehicle manufacturer's guidance."
        )

    return insights