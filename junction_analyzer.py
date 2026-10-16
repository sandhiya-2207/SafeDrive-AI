# SafeDrive AI - Junction Risk Analyzer
# Assesses potential risks near mapped road junctions.
# This is a rule-based prototype, not a trained AI model.


def analyze_junction_risk(
    distance_to_junction=500,
    speed=40,
    weather="Clear",
    road_condition="Good"
):
    """
    Estimate junction-related risk from available inputs.

    distance_to_junction: Estimated distance to the junction in metres.
    speed: Vehicle speed in km/h.
    weather: Reported weather condition.
    road_condition: Reported road condition.

    Note:
    This function does not detect moving vehicles, pedestrians,
    traffic signals, or actual collisions.
    """

    risk_score = 0
    reasons = []

    # Validate basic inputs
    try:
        distance = float(distance_to_junction)
        vehicle_speed = float(speed)
    except (TypeError, ValueError):
        return {
            "risk_score": 0,
            "risk_level": "UNKNOWN",
            "reasons": ["Valid distance and speed inputs are required."],
            "warning": "Junction risk could not be assessed."
        }

    if distance < 0 or vehicle_speed < 0:
        return {
            "risk_score": 0,
            "risk_level": "UNKNOWN",
            "reasons": ["Distance and speed cannot be negative."],
            "warning": "Junction risk could not be assessed."
        }

    # 1. Distance to junction
    if distance <= 50:
        risk_score += 35
        reasons.append("The entered distance indicates a nearby junction.")

    elif distance <= 150:
        risk_score += 25
        reasons.append("The junction may be approaching.")

    elif distance <= 300:
        risk_score += 10
        reasons.append("A junction may be ahead.")

    # 2. Vehicle speed
    if vehicle_speed >= 80:
        risk_score += 30
        reasons.append(
            "High entered speed may increase the difficulty of responding."
        )

    elif vehicle_speed >= 50:
        risk_score += 20
        reasons.append("Consider the speed appropriate for the junction.")

    elif vehicle_speed >= 30:
        risk_score += 10
        reasons.append("Remain attentive when approaching the junction.")

    # 3. Weather conditions
    weather_text = str(weather).strip().lower()

    if any(
        term in weather_text
        for term in ["rain", "storm", "fog", "snow", "drizzle"]
    ):
        risk_score += 15
        reasons.append(
            "Reported adverse weather may affect visibility or grip."
        )

    # 4. Road condition
    road_text = str(road_condition).strip().lower()

    if any(
        term in road_text
        for term in ["poor", "wet", "slippery", "damaged", "bad"]
    ):
        risk_score += 15
        reasons.append(
            "Reported road conditions may require additional caution."
        )

    # Keep score between 0 and 100
    risk_score = min(risk_score, 100)

    # 5. Categorise estimated risk
    if risk_score >= 60:
        risk_level = "HIGH"
        warning = (
            "Junction risk estimate is high. Reduce speed safely "
            "and check the surroundings."
        )

    elif risk_score >= 30:
        risk_level = "MEDIUM"
        warning = (
            "Junction risk estimate is moderate. Approach cautiously "
            "and observe road signs."
        )

    else:
        risk_level = "LOW"
        warning = (
            "No elevated junction risk was identified by these rules. "
            "Continue to observe road signs and traffic."
        )

    if not reasons:
        reasons.append("No additional risk factors were identified.")

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons,
        "warning": warning
    }