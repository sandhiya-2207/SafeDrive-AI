# SafeDrive AI - Safe Overtaking Advisor
# Estimates overtaking risk using available driving inputs.
# This is a rule-based prototype, not a trained AI model.


def assess_overtaking_risk(
    speed=40,
    road_condition="Good",
    weather="Clear",
    oncoming_traffic="Unknown",
    road_visibility="Good",
    overtaking_permitted=True
):
    """
    Assess potential overtaking risk.

    Inputs:
    speed: Current vehicle speed in km/h.
    road_condition: Reported road condition.
    weather: Reported weather.
    oncoming_traffic: Clear, Present, or Unknown.
    road_visibility: Good, Poor, or Unknown.
    overtaking_permitted: Whether overtaking is permitted
                          according to available information.

    This function cannot see traffic or verify road markings.
    """ 

    risk_score = 0
    reasons = []

    # Validate speed
    try:
        vehicle_speed = float(speed)
    except (TypeError, ValueError):
        return {
            "risk_score": 0,
            "risk_level": "UNKNOWN",
            "reasons": ["A valid speed value is required."],
            "recommendation": "Overtaking risk cannot be assessed."
        }

    if vehicle_speed < 0:
        return {
            "risk_score": 0,
            "risk_level": "UNKNOWN",
            "reasons": ["Speed cannot be negative."],
            "recommendation": "Overtaking risk cannot be assessed."
        }

    # 1. Oncoming traffic information
    traffic = str(oncoming_traffic).strip().lower()

    if traffic == "present":
        risk_score += 60
        reasons.append("Oncoming traffic is reported.")

    elif traffic == "unknown":
        risk_score += 25
        reasons.append(
            "Oncoming traffic information is unavailable."
        )

    # 2. Visibility
    visibility = str(road_visibility).strip().lower()

    if visibility == "poor":
        risk_score += 25
        reasons.append("Road visibility is reported as poor.")

    elif visibility == "unknown":
        risk_score += 15
        reasons.append("Road visibility has not been verified.")

    # 3. Weather
    weather_text = str(weather).strip().lower()

    if any(
        term in weather_text
        for term in ["rain", "storm", "fog", "snow", "drizzle"]
    ):
        risk_score += 15
        reasons.append(
            "Adverse weather may reduce visibility or road grip."
        )

    # 4. Road condition
    road_text = str(road_condition).strip().lower()

    if any(
        term in road_text
        for term in ["poor", "wet", "slippery", "damaged", "bad"]
    ):
        risk_score += 15
        reasons.append("The reported road condition needs caution.")

    # 5. Permission and road rules
    if not overtaking_permitted:
        risk_score = 100
        reasons.append(
            "Overtaking is reported as not permitted."
        )

    # Keep score within 0-100
    risk_score = min(risk_score, 100)

    # Determine recommendation
    if not overtaking_permitted:
        risk_level = "CRITICAL"
        recommendation = (
            "Do not overtake where overtaking is prohibited."
        )

    elif traffic == "present":
        risk_level = "HIGH"
        recommendation = (
            "Do not begin overtaking while oncoming traffic "
            "is reported. Wait for a legal, verified safe opportunity."
        )

    elif risk_score >= 60:
        risk_level = "HIGH"
        recommendation = (
            "Overtaking risk is elevated. Avoid overtaking "
            "until the conditions can be verified as safe."
        )

    elif risk_score >= 30:
        risk_level = "MEDIUM"
        recommendation = (
            "Use caution. Verify visibility, road markings, "
            "traffic, and road conditions before making any manoeuvre."
        )

    else:
        risk_level = "LOW"
        recommendation = (
            "No major risk factors were identified by the supplied "
            "inputs. This does not confirm that overtaking is safe."
        )

    if not reasons:
        reasons.append(
            "No elevated risk factors were identified from the inputs."
        )

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons,
        "recommendation": recommendation
    }