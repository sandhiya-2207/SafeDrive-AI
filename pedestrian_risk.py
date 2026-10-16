# SafeDrive AI - Pedestrian Risk Predictor
# Estimates potential pedestrian risk from supplied inputs.
# This is a rule-based prototype, not a trained AI model.
# It does not detect pedestrians using a camera.

def predict_pedestrian_risk(
    speed=30,
    distance_to_crossing=100,
    pedestrian_present="Unknown",
    visibility="Good",
    weather="Clear"
):
    """
    Estimate pedestrian-related risk.

    speed:
        Vehicle speed in km/h.

    distance_to_crossing:
        Estimated distance to a pedestrian crossing or
        pedestrian-risk area, in metres.

    pedestrian_present:
        Yes, No, or Unknown.

    visibility:
        Good, Poor, or Unknown.

    weather:
        Current or reported weather condition.

    Note:
        The result is an estimate based only on the supplied
        inputs. It does not confirm that a pedestrian is present.
    """

    risk_score = 0
    reasons = []

    # Validate numerical inputs
    try:
        vehicle_speed = float(speed)
        crossing_distance = float(distance_to_crossing)
    except (TypeError, ValueError):
        return {
            "risk_score": 0,
            "risk_level": "UNKNOWN",
            "reasons": ["Valid speed and distance values are required."],
            "warning": "Pedestrian risk could not be assessed."
        }

    if vehicle_speed < 0 or crossing_distance < 0:
        return {
            "risk_score": 0,
            "risk_level": "UNKNOWN",
            "reasons": ["Speed and distance cannot be negative."],
            "warning": "Pedestrian risk could not be assessed."
        }

    # 1. Distance to crossing or pedestrian-risk area
    if crossing_distance <= 20:
        risk_score += 35
        reasons.append("The entered distance indicates a very nearby crossing or risk area.")
    elif crossing_distance <= 50:
        risk_score += 25
        reasons.append("A pedestrian crossing or risk area may be approaching.")
    elif crossing_distance <= 100:
        risk_score += 15
        reasons.append("A pedestrian-risk area may be ahead.")

    # 2. Vehicle speed
    if vehicle_speed >= 80:
        risk_score += 30
        reasons.append("High entered speed may reduce the time available to respond.")
    elif vehicle_speed >= 50:
        risk_score += 20
        reasons.append("Consider reducing speed appropriately near pedestrian areas.")
    elif vehicle_speed >= 30:
        risk_score += 10
        reasons.append("Remain attentive to pedestrians at the entered speed.")

    # 3. Pedestrian presence
    pedestrian_status = str(pedestrian_present).strip().lower()

    if pedestrian_status in ["yes", "present", "true"]:
        risk_score += 35
        reasons.append("A pedestrian is reported to be present.")
    elif pedestrian_status in ["unknown", "not sure"]:
        risk_score += 10
        reasons.append("Pedestrian presence has not been verified.")

    # 4. Visibility
    visibility_status = str(visibility).strip().lower()

    if visibility_status == "poor":
        risk_score += 20
        reasons.append("Poor visibility may make pedestrians harder to see.")
    elif visibility_status == "unknown":
        risk_score += 10
        reasons.append("Visibility conditions have not been verified.")

    # 5. Weather
    weather_text = str(weather).strip().lower()

    if any(term in weather_text for term in [
        "rain", "drizzle", "storm", "thunder", "fog", "snow"
    ]):
        risk_score += 15
        reasons.append("Reported weather may affect visibility or road grip.")

    # Keep the score within 0-100
    risk_score = min(risk_score, 100)

    # 6. Risk classification
    if risk_score >= 70:
        risk_level = "HIGH"
        warning = (
            "HIGH PEDESTRIAN RISK ESTIMATE: Reduce speed safely, "
            "remain alert, and be prepared to stop for pedestrians."
        )
    elif risk_score >= 40:
        risk_level = "MEDIUM"
        warning = (
            "MODERATE PEDESTRIAN RISK ESTIMATE: Approach cautiously "
            "and check both sides of the road."
        )
    else:
        risk_level = "LOW"
        warning = (
            "LOW ESTIMATED RISK FROM THE PROVIDED INPUTS. "
            "Continue watching for pedestrians and follow road signs."
        )

    if not reasons:
        reasons.append(
            "No additional pedestrian-risk factors were identified from the supplied inputs."
        )

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons,
        "warning": warning
    }