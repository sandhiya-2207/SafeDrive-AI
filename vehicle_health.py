def assess_vehicle_health(engine_temperature, tyre_pressure, battery_voltage, fuel_level):
    score = 100
    alerts = []

    # Simulated engine temperature
    if engine_temperature >= 120:
        score -= 35
        alerts.append("Critical simulated engine temperature")
    elif engine_temperature >= 105:
        score -= 20
        alerts.append("High simulated engine temperature")

    # Simulated tyre pressure
    if tyre_pressure < 25 or tyre_pressure > 40:
        score -= 25
        alerts.append("Tyre pressure is outside the demonstration range")

    # Simulated battery voltage
    if battery_voltage < 11.8:
        score -= 25
        alerts.append("Low simulated battery voltage")
    elif battery_voltage > 14.8:
        score -= 15
        alerts.append("Battery voltage is above the demonstration range")

    # Simulated fuel level
    if fuel_level < 10:
        score -= 15
        alerts.append("Low fuel level")

    score = max(0, score)

    if score >= 80:
        status = "GOOD"
    elif score >= 50:
        status = "CHECK"
    else:
        status = "WARNING"

    if not alerts:
        alerts.append("No issues identified by the simplified demonstration rules")

    return score, status, alerts