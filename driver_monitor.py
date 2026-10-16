def assess_driver_status(eye_closure_seconds, distraction_level, driving_minutes):
    """
    Simulated driver monitoring.
    This does not detect actual drowsiness or distraction.
    """

    risk_score = 0
    reasons = []

    # Simulated eye-closure indicator
    if eye_closure_seconds >= 2:
        risk_score += 50
        reasons.append("Prolonged eye closure reported")
    elif eye_closure_seconds >= 1:
        risk_score += 25
        reasons.append("Possible eye-closure warning")

    # Simulated distraction indicator
    if distraction_level == "High":
        risk_score += 35
        reasons.append("High distraction level selected")
    elif distraction_level == "Moderate":
        risk_score += 15
        reasons.append("Moderate distraction level selected")

    # Simulated continuous driving duration
    if driving_minutes >= 240:
        risk_score += 25
        reasons.append("Long continuous driving duration")
    elif driving_minutes >= 120:
        risk_score += 10
        reasons.append("Extended continuous driving duration")

    risk_score = min(risk_score, 100)

    if risk_score >= 60:
        status = "HIGH"
    elif risk_score >= 30:
        status = "MEDIUM"
    else:
        status = "LOW"

    if not reasons:
        reasons.append("No major risk indicators selected in this simulation")

    return risk_score, status, reasons