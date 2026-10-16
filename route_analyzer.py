def analyze_route(route_name, traffic_level, weather, road_condition, hazard_count):
    """
    Estimate route risk using simplified demonstration rules.

    This is not a live navigation system and does not use real traffic data.
    """

    risk_score = 0
    reasons = []

    # Traffic assessment
    if traffic_level == "Heavy":
        risk_score += 30
        reasons.append("Heavy simulated traffic")
    elif traffic_level == "Moderate":
        risk_score += 15
        reasons.append("Moderate simulated traffic")

    # Weather assessment
    if weather == "Rainy":
        risk_score += 20
        reasons.append("Rainy weather")
    elif weather == "Foggy":
        risk_score += 25
        reasons.append("Foggy weather")

    # Road-condition assessment
    if road_condition == "Poor":
        risk_score += 25
        reasons.append("Poor road condition")
    elif road_condition == "Moderate":
        risk_score += 10
        reasons.append("Moderate road condition")

    # Hazard assessment
    if hazard_count >= 5:
        risk_score += 25
        reasons.append("Many simulated hazards")
    elif hazard_count >= 3:
        risk_score += 15
        reasons.append("Several simulated hazards")
    elif hazard_count >= 1:
        risk_score += 5
        reasons.append("Some simulated hazards")

    risk_score = min(risk_score, 100)

    if risk_score >= 60:
        risk_level = "HIGH"
    elif risk_score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    if not reasons:
        reasons.append(
            "No major risk factors identified by the simplified rules"
        )

    return {
        "route_name": route_name,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons
    }


def compare_routes(routes):
    """
    Sort route analysis results from lowest to highest demonstration risk.
    """

    return sorted(
        routes,
        key=lambda route: route["risk_score"]
    )