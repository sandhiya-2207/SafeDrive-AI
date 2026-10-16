# SafeDrive AI - Safety Priority Engine
# Prioritises safety warnings according to urgency.
# This is a rule-based prototype, not a trained AI model.


def calculate_safety_priority(
    risk_score=0,
    time_to_hazard=None,
    junction_risk=False,
    overtaking_risk=False,
    pedestrian_risk=False
):
    """
    Selects the highest-priority warning using available inputs.

    risk_score: Overall risk score from 0 to 100.
    time_to_hazard: Estimated seconds before reaching a hazard.
    junction_risk: Whether a junction risk has been identified.
    overtaking_risk: Whether overtaking risk has been identified.
    pedestrian_risk: Whether pedestrian risk has been identified.
    """

    warnings = []

    # General driving risk
    if risk_score >= 75:
        warnings.append({
            "priority": 1,
            "level": "CRITICAL",
            "message": "High driving risk. Reduce speed safely and assess the situation."
        })

    elif risk_score >= 50:
        warnings.append({
            "priority": 2,
            "level": "HIGH",
            "message": "High-risk conditions detected. Drive cautiously."
        })

    elif risk_score >= 25:
        warnings.append({
            "priority": 3,
            "level": "MEDIUM",
            "message": "Moderate risk detected. Increase attention."
        })

    # Estimated time to hazard
    if time_to_hazard is not None:
        if 0 <= time_to_hazard <= 2:
            warnings.append({
                "priority": 1,
                "level": "CRITICAL",
                "message": "Hazard is very close. Take immediate safe action."
            })

        elif 2 < time_to_hazard <= 5:
            warnings.append({
                "priority": 2,
                "level": "HIGH",
                "message": "Hazard approaching. Prepare to slow down safely."
            })

    # Junction risk
    if junction_risk:
        warnings.append({
            "priority": 2,
            "level": "HIGH",
            "message": "Junction risk indicated. Slow down safely and check surroundings."
        })

    # Overtaking risk
    if overtaking_risk:
        warnings.append({
            "priority": 2,
            "level": "HIGH",
            "message": "Overtaking may be unsafe. Avoid overtaking until the road is clear."
        })

    # Pedestrian risk
    if pedestrian_risk:
        warnings.append({
            "priority": 1,
            "level": "CRITICAL",
            "message": "Potential pedestrian risk indicated. Slow down safely and remain alert."
        })

    # Sort warnings: priority 1 comes first
    warnings.sort(key=lambda item: item["priority"])

    # Return a safe default if no warnings were generated
    if not warnings:
        return {
            "level": "LOW",
            "message": "No elevated risk identified by the current rules.",
            "priority": 4,
            "all_warnings": []
        }

    highest = warnings[0]

    return {
        "level": highest["level"],
        "message": highest["message"],
        "priority": highest["priority"],
        "all_warnings": warnings
    }