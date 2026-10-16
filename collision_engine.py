def calculate_time_to_collision(distance, relative_speed):
    """
    Calculate illustrative time to collision.

    distance: distance to the hazard in metres.
    relative_speed: closing speed in km/h.

    This is a simplified demonstration, not a validated
    real-world collision prediction.
    """

    if distance <= 0:
        return 0.0

    if relative_speed <= 0:
        return None

    closing_speed_mps = relative_speed / 3.6

    time_seconds = distance / closing_speed_mps

    return round(time_seconds, 2)


def assess_collision_risk(distance, relative_speed):
    """
    Return a demonstration collision-risk level and explanation.
    """

    time_to_collision = calculate_time_to_collision(
        distance,
        relative_speed
    )

    if distance <= 0:
        return time_to_collision, "HIGH", "Hazard distance is zero or less."

    if time_to_collision is None:
        return (
            None,
            "LOW",
            "The selected relative speed indicates no closing movement."
        )

    if time_to_collision <= 1.5:
        return (
            time_to_collision,
            "HIGH",
            "Very short estimated time before reaching the hazard."
        )

    elif time_to_collision <= 3:
        return (
            time_to_collision,
            "MEDIUM",
            "The estimated time before reaching the hazard is short."
        )

    else:
        return (
            time_to_collision,
            "LOW",
            "The estimated time before reaching the hazard is longer."
        )