# SafeDrive AI - Warning Engine
# Generates safety warnings from available driving conditions.
# This is a rule-based prototype, not a trained ML model.


def generate_ai_warnings(
    risk_score=0,
    speed=0,
    weather="Clear",
    road_condition="Good",
    time_to_hazard=None
):
    """
    Generate warnings using the driving information available.

    Inputs are estimates or user-provided values.
    This function does not detect hazards using a camera.
    """

    warnings = []

    # 1. Overall driving risk
    if risk_score >= 75:
        warnings.append({
            "type": "Driving Risk",
            "level": "CRITICAL",
            "message": (
                "Very high estimated driving risk. "
                "Reduce speed safely and assess the road conditions."
            )
        })

    elif risk_score >= 50:
        warnings.append({
            "type": "Driving Risk",
            "level": "HIGH",
            "message": (
                "High estimated driving risk. "
                "Increase attention and drive cautiously."
            )
        })

    elif risk_score >= 25:
        warnings.append({
            "type": "Driving Risk",
            "level": "MEDIUM",
            "message": (
                "Moderate estimated driving risk. "
                "Remain alert and maintain a safe distance."
            )
        })

    # 2. Speed-related warning
    if speed >= 100:
        warnings.append({
            "type": "Speed",
            "level": "HIGH",
            "message": (
                "High speed entered. Follow the posted speed limit "
                "and reduce speed safely when necessary."
            )
        })

    # 3. Weather-related warning
    weather_text = str(weather).strip().lower()

    bad_weather_terms = [
        "rain",
        "drizzle",
        "storm",
        "thunder",
        "snow",
        "fog"
    ]

    if any(term in weather_text for term in bad_weather_terms):
        warnings.append({
            "type": "Weather",
            "level": "MEDIUM",
            "message": (
                "Potentially adverse weather reported. "
                "Increase following distance and drive cautiously."
            )
        })

    # 4. Road-condition warning
    road_text = str(road_condition).strip().lower()

    if any(
        term in road_text
        for term in ["poor", "wet", "damaged", "slippery", "bad"]
    ):
        warnings.append({
            "type": "Road Condition",
            "level": "HIGH",
            "message": (
                "Potentially unsafe road condition reported. "
                "Reduce speed safely and avoid sudden manoeuvres."
            )
        })

    # 5. Time-to-hazard warning
    if time_to_hazard is not None:
        try:
            hazard_time = float(time_to_hazard)

            if 0 <= hazard_time <= 2:
                warnings.append({
                    "type": "Nearby Hazard",
                    "level": "CRITICAL",
                    "message": (
                        "The estimated time to the hazard is very short. "
                        "Take immediate safe action."
                    )
                })

            elif 2 < hazard_time <= 5:
                warnings.append({
                    "type": "Nearby Hazard",
                    "level": "HIGH",
                    "message": (
                        "A hazard may be approaching soon. "
                        "Prepare to slow down safely."
                    )
                })

        except (TypeError, ValueError):
            pass

    # Sort warnings by severity
    severity_order = {
        "CRITICAL": 1,
        "HIGH": 2,
        "MEDIUM": 3,
        "LOW": 4
    }

    warnings.sort(
        key=lambda warning: severity_order.get(
            warning["level"], 5
        )
    )

    # No elevated warning found
    if not warnings:
        warnings.append({
            "type": "General Safety",
            "level": "LOW",
            "message": (
                "No elevated risk was identified by these rules. "
                "Continue following road signs and safe-driving practices."
            )
        })

    return warnings