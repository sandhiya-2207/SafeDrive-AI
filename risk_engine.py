def calculate_risk(speed, weather, road_condition, distance):
    risk_score = 0
    reasons = []

    # Speed risk
    if speed > 100:
        risk_score += 35
        reasons.append("Very high vehicle speed")
    elif speed > 80:
        risk_score += 25
        reasons.append("High vehicle speed")
    elif speed > 60:
        risk_score += 15
        reasons.append("Moderately high vehicle speed")

    # Weather risk
    if weather == "Rainy":
        risk_score += 20
        reasons.append("Rain may reduce road grip")
    elif weather == "Foggy":
        risk_score += 25
        reasons.append("Fog may reduce visibility")

    # Road condition risk
    if road_condition == "Poor":
        risk_score += 25
        reasons.append("Poor road condition")
    elif road_condition == "Moderate":
        risk_score += 10
        reasons.append("Moderate road condition")

    # Distance from hazard
    if distance < 10:
        risk_score += 30
        reasons.append("Hazard is extremely close")
    elif distance < 25:
        risk_score += 20
        reasons.append("Hazard is nearby")
    elif distance < 40:
        risk_score += 10
        reasons.append("Hazard is approaching")

    risk_score = min(risk_score, 100)

    if risk_score >= 60:
        risk_level = "HIGH"
    elif risk_score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    if not reasons:
        reasons.append("No major risk factors detected by the simplified rules")

    return risk_score, risk_level, reasons


def calculate_stopping_distance(speed):
    # Simplified educational estimate, not a vehicle safety calculation
    reaction_time = 1.5
    reaction_distance = (speed / 3.6) * reaction_time

    # Simplified braking-distance approximation
    braking_distance = (speed / 10) ** 2

    return round(reaction_distance + braking_distance, 2)


def calculate_safe_following_distance(speed, weather):
    # Demonstration rule: approximately a 3-second following gap
    time_gap = 3

    if weather == "Rainy":
        time_gap = 4
    elif weather == "Foggy":
        time_gap = 5

    distance = (speed / 3.6) * time_gap
    return round(distance, 2)


def calculate_collision_risk(speed, obstacle_distance, relative_speed):
    """
    Simplified demonstration model.

    relative_speed is the closing speed in km/h.
    Positive values mean the vehicle is approaching the obstacle.
    This is not a validated collision-prediction model.
    """

    if relative_speed <= 0:
        time_to_collision = None
    else:
        time_to_collision = obstacle_distance / (relative_speed / 3.6)

    if obstacle_distance <= 0:
        risk_level = "HIGH"
    elif time_to_collision is None:
        risk_level = "LOW"
    elif time_to_collision <= 1.5:
        risk_level = "HIGH"
    elif time_to_collision <= 3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return time_to_collision, risk_level