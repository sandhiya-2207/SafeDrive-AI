import streamlit as st
import requests
import pandas as pd
import folium

from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

from risk_engine import (
    calculate_risk,
    calculate_stopping_distance,
    calculate_safe_following_distance,
)
from collision_engine import assess_collision_risk
from emergency_module import generate_sos_message, get_emergency_types
from driver_monitor import assess_driver_status
from vehicle_health import assess_vehicle_health
from safety_insights import generate_safety_insights
from incident_history import add_incident, get_incident_summary
from report_generator import generate_safety_report, generate_incident_csv
from voice_alerts import speak_alert

# Six new rule-based safety modules
from ai_warning_engine import generate_ai_warnings
from junction_analyzer import analyze_junction_risk
from overtaking_advisor import assess_overtaking_risk
from pedestrian_risk import predict_pedestrian_risk
from safety_priority import calculate_safety_priority
from ai_alert_manager import collect_safety_alerts, get_highest_priority_alert


st.set_page_config(page_title="SafeDrive AI", page_icon="🚗", layout="wide")
st.title("🚗 SafeDrive AI")
st.subheader("Real-Data Road Safety Research Prototype")
st.caption(
    "GPS and weather are retrieved from external services when available. "
    "Several driving, vehicle, junction, pedestrian and overtaking inputs are manual "
    "demonstrations; these features are not validated real-world safety systems."
)

# -------------------- SESSION STATE --------------------
for key, default in {
    "incidents": [],
    "sos_message": "",
    "route_destination": None,
    "route_result": None,
    "comparison_places": [],
    "comparison_routes": None,
    "comparison_destination": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# -------------------- LOCATION --------------------
st.header("📍 Device Location")
st.write(
    "Allow your browser to access your device location. A laptop's localhost "
    "location is the laptop/browser location, not automatically your phone's."
)
location_data = streamlit_geolocation()
latitude = longitude = location_accuracy = None

if isinstance(location_data, dict):
    try:
        lat = location_data.get("latitude")
        lon = location_data.get("longitude")
        if lat is not None and lon is not None:
            lat, lon = float(lat), float(lon)
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                latitude, longitude = lat, lon
                location_accuracy = location_data.get("accuracy")
    except (TypeError, ValueError):
        pass

if latitude is not None:
    c1, c2, c3 = st.columns(3)
    c1.metric("Latitude", f"{latitude:.6f}")
    c2.metric("Longitude", f"{longitude:.6f}")
    c3.metric(
        "Reported GPS Accuracy",
        f"{location_accuracy} m" if location_accuracy is not None else "Unavailable",
    )
else:
    st.warning("No device location received. Allow browser location access and retry.")

# -------------------- WEATHER --------------------
st.header("🌦️ Current Weather")
weather_data = None
weather_description = "Unavailable"
weather_codes = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle",
    53: "Moderate drizzle", 55: "Dense drizzle", 61: "Slight rain",
    63: "Moderate rain", 65: "Heavy rain", 71: "Slight snow",
    73: "Moderate snow", 75: "Heavy snow", 80: "Rain showers",
    81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}
if latitude is not None and longitude is not None:
    try:
        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,relative_humidity_2m,apparent_temperature,"
                    "is_day,precipitation,rain,showers,snowfall,weather_code,"
                    "wind_speed_10m,visibility"
                ),
                "timezone": "auto",
            },
            timeout=12,
        )
        weather_response.raise_for_status()
        weather_data = weather_response.json().get("current")
    except (requests.RequestException, ValueError) as error:
        st.warning(f"Unable to retrieve weather: {error}")

if weather_data:
    weather_code = weather_data.get("weather_code")
    weather_description = weather_codes.get(weather_code, "Unknown conditions")
    c1, c2, c3 = st.columns(3)
    c1.metric("Temperature", f"{weather_data.get('temperature_2m', 'N/A')} °C")
    c2.metric("Humidity", f"{weather_data.get('relative_humidity_2m', 'N/A')}%")
    c3.metric("Wind Speed", f"{weather_data.get('wind_speed_10m', 'N/A')} km/h")
    st.write(f"**Conditions:** {weather_description}")
    if weather_data.get("visibility") is not None:
        st.write(f"**Reported visibility estimate:** {weather_data['visibility']} metres")
else:
    st.info("Weather will appear when device coordinates are available and the service responds.")

# -------------------- NAVIGATION AND INPUTS --------------------
st.sidebar.title("SafeDrive Control Centre")
page = st.sidebar.radio(
    "Dashboard",
    [
        "Overview", "Collision Analysis", "Driver Monitoring", "Vehicle Health",
        "Road Map", "Route Comparison", "AI Warning System",
        "Junction Prediction", "Safe Overtaking Advisor",
        "Pedestrian Risk Predictor", "AI Safety Alerts",
        "Safety Insights", "Incident History", "Emergency SOS", "Safety Reports",
    ],
)
st.sidebar.divider()
st.sidebar.subheader("Demonstration Inputs")
speed = st.sidebar.slider("Vehicle Speed (km/h)", 0, 150, 60)
road_condition = st.sidebar.selectbox("Assumed Road Condition", ["Good", "Moderate", "Poor"])
hazard_distance = st.sidebar.slider("Distance to Hazard (metres)", 1, 200, 30)
relative_speed = st.sidebar.slider("Closing Speed (km/h)", 0, 120, 20)

if weather_data:
    code = weather_data.get("weather_code", -1)
    if code in (45, 48):
        weather_for_risk = "Foggy"
    elif (
        weather_data.get("rain", 0) > 0
        or weather_data.get("showers", 0) > 0
        or weather_data.get("precipitation", 0) > 0
        or code in (51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99)
    ):
        weather_for_risk = "Rainy"
    else:
        weather_for_risk = "Clear"
else:
    weather_for_risk = "Clear"

st.sidebar.write(f"Weather used by risk rules: **{weather_for_risk}**")
st.sidebar.caption("These inputs are manually entered and are not connected to car sensors.")

# -------------------- SHARED CALCULATIONS --------------------
risk_score, risk_level, risk_reasons = calculate_risk(
    speed, weather_for_risk, road_condition, hazard_distance
)
stopping_distance = calculate_stopping_distance(speed)
following_distance = calculate_safe_following_distance(speed, weather_for_risk)
collision_time, collision_level, collision_reason = assess_collision_risk(
    hazard_distance, relative_speed
)

# Shared outputs for the six new modules
ai_warnings = generate_ai_warnings(
    risk_score=risk_score,
    speed=speed,
    weather=weather_for_risk,
    road_condition=road_condition,
    time_to_hazard=collision_time,
)
junction_result = analyze_junction_risk(
    distance_to_junction=st.sidebar.slider("Assumed Distance to Junction (m)", 0, 1000, 250, 10),
    speed=speed,
    weather=weather_for_risk,
    road_condition=road_condition,
)
overtaking_result = assess_overtaking_risk(
    speed=speed,
    road_condition=road_condition,
    weather=weather_for_risk,
    oncoming_traffic=st.sidebar.selectbox(
        "Assumed Oncoming Traffic", ["Unknown", "No traffic seen", "Traffic present"],
        key="oncoming_traffic_input",
    ),
    road_visibility=st.sidebar.selectbox(
        "Assumed Road Visibility", ["Good", "Moderate", "Poor"],
        key="road_visibility_input",
    ),
    overtaking_permitted=st.sidebar.checkbox("Assume overtaking is permitted", value=False),
)
pedestrian_result = predict_pedestrian_risk(
    speed=speed,
    distance_to_crossing=st.sidebar.slider("Assumed Distance to Crossing (m)", 0, 500, 100, 5),
    pedestrian_present=st.sidebar.selectbox(
        "Pedestrian Presence", ["Unknown", "No pedestrian seen", "Pedestrian present"],
        key="pedestrian_presence_input",
    ),
    visibility=st.sidebar.selectbox(
        "Pedestrian Visibility", ["Good", "Moderate", "Poor"],
        key="pedestrian_visibility_input",
    ),
    weather=weather_for_risk,
)
all_alerts = collect_safety_alerts(
    ai_warnings=ai_warnings,
    junction_result=junction_result,
    overtaking_result=overtaking_result,
    pedestrian_result=pedestrian_result,
)
highest_alert = get_highest_priority_alert(all_alerts)
priority_result = calculate_safety_priority(
    risk_score=risk_score,
    time_to_hazard=collision_time,
    junction_risk=str(junction_result.get("risk_level", "")).upper() in ("HIGH", "CRITICAL"),
    overtaking_risk=str(overtaking_result.get("risk_level", "")).upper() in ("HIGH", "CRITICAL"),
    pedestrian_risk=str(pedestrian_result.get("risk_level", "")).upper() in ("HIGH", "CRITICAL"),
)

def show_reasons(items):
    if not items:
        st.write("No reasons supplied by this rule set.")
        return
    for item in items:
        st.write(f"• {item}")

def show_risk_card(title, result, score_key="risk_score", level_key="risk_level"):
    st.subheader(title)
    c1, c2 = st.columns(2)
    if score_key in result:
        c1.metric("Rule-Based Risk Score", f"{result[score_key]}/100")
    if level_key in result:
        c2.metric("Risk Level", str(result[level_key]))
    if result.get("warning"):
        st.warning(result["warning"])
    if result.get("recommendation"):
        st.info(result["recommendation"])
    show_reasons(result.get("reasons", []))

# -------------------- OVERVIEW --------------------
if page == "Overview":
    st.header("📊 Driving Safety Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rule-Based Risk", f"{risk_score}/100")
    c2.metric("Risk Level", risk_level)
    c3.metric("Stopping Estimate", f"{stopping_distance} m")
    c4.metric("Following Gap Estimate", f"{following_distance} m")
    st.subheader("Risk Factors")
    show_reasons(risk_reasons)
    st.subheader("Collision-Risk Demonstration")
    st.write(collision_reason)
    c1, c2 = st.columns(2)
    c1.metric("Estimated Time to Hazard", f"{collision_time} seconds" if collision_time is not None else "Not approaching")
    c2.metric("Collision Indicator", collision_level)
    if str(risk_level).upper() == "HIGH":
        st.error("High risk according to the simplified rules.")
    elif str(risk_level).upper() == "MEDIUM":
        st.warning("Medium risk according to the simplified rules.")
    else:
        st.info("Low risk according to the simplified rules.")
    st.subheader("Location on Map")
    if latitude is not None and longitude is not None:
        st.map(pd.DataFrame([{"latitude": latitude, "longitude": longitude}]), latitude="latitude", longitude="longitude", zoom=15)
    else:
        st.info("Allow device location to display your position.")
    st.warning("This score does not establish that a road is safe. Obstacle detection and vehicle-speed sensors are not connected.")

# -------------------- COLLISION ANALYSIS --------------------
elif page == "Collision Analysis":
    st.header("⚠️ Collision-Risk Analysis")
    st.write(f"Hazard distance: {hazard_distance} metres")
    st.write(f"Closing speed: {relative_speed} km/h")
    st.write(f"Estimated time to hazard: {collision_time}")
    st.write(f"Indicator: {collision_level}")
    st.write(collision_reason)
    c1, c2 = st.columns(2)
    c1.metric("Estimated Stopping Distance", f"{stopping_distance} m")
    c2.metric("Illustrative Following Gap", f"{following_distance} m")
    st.warning("Simplified estimates from manual inputs; not validated collision predictions.")
    if st.button("Record Collision Indicator"):
        st.session_state.incidents = add_incident(st.session_state.incidents, "Collision Indicator", collision_level, collision_reason)
        st.success("Record added to this session.")

# -------------------- DRIVER MONITORING --------------------
elif page == "Driver Monitoring":
    st.header("🧠 Driver Monitoring")
    st.info("Simulation only; no camera is connected to detect real drowsiness or distraction.")
    eye_closure = st.slider("Simulated Eye-Closure Duration (seconds)", 0.0, 5.0, 0.0, 0.5)
    distraction = st.selectbox("Simulated Distraction Level", ["Low", "Moderate", "High"])
    driving_minutes = st.slider("Continuous Driving Duration (minutes)", 0, 360, 30, 15)
    score, status, reasons = assess_driver_status(eye_closure, distraction, driving_minutes)
    st.metric("Driver Risk Score", f"{score}/100")
    st.metric("Driver Status", status)
    show_reasons(reasons)
    if st.button("Record Driver Indicator"):
        st.session_state.incidents = add_incident(st.session_state.incidents, "Driver Monitoring", status, "; ".join(reasons))
        st.success("Record added to this session.")

# -------------------- VEHICLE HEALTH --------------------
elif page == "Vehicle Health":
    st.header("🔧 Vehicle Health")
    st.warning("These are manually entered values, not readings from your actual car.")
    temperature = st.slider("Engine Temperature (°C)", 40, 150, 90)
    tyre_pressure = st.slider("Tyre Pressure (PSI)", 15, 45, 32)
    battery_voltage = st.slider("Battery Voltage (V)", 10.0, 16.0, 12.6, 0.1)
    fuel_level = st.slider("Fuel Level (%)", 0, 100, 70)
    score, status, alerts = assess_vehicle_health(temperature, tyre_pressure, battery_voltage, fuel_level)
    st.metric("Health Score", f"{score}/100")
    st.metric("Health Status", status)
    show_reasons(alerts)
    if st.button("Record Vehicle Health Indicator"):
        st.session_state.incidents = add_incident(st.session_state.incidents, "Vehicle Health", status, "; ".join(alerts))
        st.success("Record added to this session.")

# -------------------- ROAD MAP AND PLACE SEARCH --------------------
elif page == "Road Map":
    st.header("🗺️ Detailed Road Map and Navigation")
    st.caption("OpenStreetMap place/road data and OSRM routing. Live traffic is not included.")
    with st.form("destination_search_form"):
        destination = st.text_input("Search destination", placeholder="Enter a college, town, street or landmark")
        search_route = st.form_submit_button("🔎 Find Route")
    if search_route:
        if not destination.strip():
            st.warning("Please enter a destination.")
        elif latitude is None or longitude is None:
            st.warning("Obtain your current device location before searching for a route.")
        else:
            try:
                with st.spinner("Searching for the destination..."):
                    geo = requests.get(
                        "https://nominatim.openstreetmap.org/search",
                        params={"q": destination.strip(), "format": "jsonv2", "limit": 5, "addressdetails": 1, "countrycodes": "in"},
                        headers={"User-Agent": "SafeDriveAI/1.0"}, timeout=15,
                    )
                    geo.raise_for_status()
                    matches = geo.json()
                if not matches:
                    st.session_state.route_result = None
                    st.session_state.route_destination = None
                    st.warning("No matching place found. Try a more specific name or include the town.")
                else:
                    place = matches[0]
                    dest_lat, dest_lon = float(place["lat"]), float(place["lon"])
                    route_response = requests.get(
                        "https://router.project-osrm.org/route/v1/driving/"
                        f"{longitude},{latitude};{dest_lon},{dest_lat}",
                        params={"overview": "full", "geometries": "geojson", "alternatives": "true", "steps": "true"},
                        timeout=25,
                    )
                    route_response.raise_for_status()
                    route_data = route_response.json()
                    if route_data.get("code") != "Ok" or not route_data.get("routes"):
                        st.session_state.route_result = None
                        st.session_state.route_destination = None
                        st.warning("A driving route could not be calculated.")
                    else:
                        st.session_state.route_destination = {
                            "name": place.get("display_name", destination.strip()),
                            "latitude": dest_lat, "longitude": dest_lon,
                        }
                        st.session_state.route_result = route_data
            except (requests.RequestException, ValueError, KeyError) as error:
                st.session_state.route_result = None
                st.session_state.route_destination = None
                st.error(f"Could not retrieve place or route information: {error}")

    if latitude is not None and longitude is not None:
        road_map = folium.Map(location=[latitude, longitude], zoom_start=16, control_scale=True, tiles="OpenStreetMap")
        folium.Marker([latitude, longitude], tooltip="Your current location", popup="Current browser-reported location", icon=folium.Icon(color="blue", icon="car", prefix="fa")).add_to(road_map)
        try:
            overpass_query = f'[out:json][timeout:20];way(around:800,{latitude},{longitude})["highway"];out geom tags;'
            roads_response = requests.post(
                "https://overpass-api.de/api/interpreter", data={"data": overpass_query},
                headers={"User-Agent": "SafeDriveAI/1.0"}, timeout=25,
            )
            roads_response.raise_for_status()
            road_features = roads_response.json().get("elements", [])
            for road in road_features:
                tags, geometry = road.get("tags", {}), road.get("geometry", [])
                points = [[p["lat"], p["lon"]] for p in geometry if "lat" in p and "lon" in p]
                if len(points) < 2:
                    continue
                road_name = tags.get("name", "Unnamed mapped road")
                folium.PolyLine(
                    points, color="#2878B5", weight=4, opacity=0.65, tooltip=road_name,
                    popup=f"<b>{road_name}</b><br>Road type: {tags.get('highway', 'Unknown')}<br>Surface: {tags.get('surface', 'Not mapped')}<br>Speed limit: {tags.get('maxspeed', 'Not mapped')}",
                ).add_to(road_map)
            st.caption(f"Loaded {len(road_features)} nearby mapped road features. Select a road to see available details.")
        except (requests.RequestException, ValueError) as error:
            st.warning(f"Detailed road geometry is temporarily unavailable: {error}")

        route_data = st.session_state.route_result
        destination_info = st.session_state.route_destination
        if route_data and destination_info:
            routes = route_data.get("routes", [])
            for index, route in reversed(list(enumerate(routes))):
                route_points = [[coord[1], coord[0]] for coord in route["geometry"]["coordinates"]]
                folium.PolyLine(route_points, color="#0877FF" if index == 0 else "#888888", weight=7 if index == 0 else 4, opacity=0.9 if index == 0 else 0.65, tooltip=f"Route {index + 1} — {route['distance'] / 1000:.2f} km").add_to(road_map)
            folium.Marker([destination_info["latitude"], destination_info["longitude"]], tooltip="Destination", popup=destination_info["name"], icon=folium.Icon(color="red", icon="flag", prefix="fa")).add_to(road_map)
            road_map.fit_bounds([[coord[1], coord[0]] for coord in routes[0]["geometry"]["coordinates"]])
        st_folium(road_map, height=600, width=None, key="navigation_road_map")

        if st.session_state.route_result and st.session_state.route_destination:
            destination_info = st.session_state.route_destination
            st.subheader("📍 Selected Destination")
            st.write(destination_info["name"])
            st.subheader("🛣️ Available Driving Routes")
            for index, route in enumerate(st.session_state.route_result.get("routes", []), start=1):
                st.write(f"**Route {index}:** {route['distance'] / 1000:.2f} km · Estimated {route['duration'] / 60:.0f} minutes")
            google_maps_url = (
                "https://www.google.com/maps/dir/?api=1"
                f"&origin={latitude},{longitude}"
                f"&destination={destination_info['latitude']},{destination_info['longitude']}"
                "&travelmode=driving"
            )
            st.link_button("Open turn-by-turn navigation in Google Maps", google_maps_url)
            st.caption("Route times are estimates, not live-traffic predictions.")
    else:
        st.warning("Allow browser location access first to use the map and route search.")

# -------------------- ROUTE COMPARISON --------------------
elif page == "Route Comparison":
    st.header("🛣️ Real Route Comparison")
    st.caption("OpenStreetMap place search and OSRM route estimates; no live traffic.")
    with st.form("route_comparison_search"):
        destination_query = st.text_input("Where do you want to go?", placeholder="Example: Karamadai, Coimbatore, Tamil Nadu")
        find_destination = st.form_submit_button("Search Destination")
    if find_destination:
        st.session_state.comparison_places = []
        st.session_state.comparison_routes = None
        st.session_state.comparison_destination = None
        if not destination_query.strip():
            st.warning("Please enter a destination.")
        else:
            try:
                with st.spinner("Searching for places..."):
                    response = requests.get(
                        "https://nominatim.openstreetmap.org/search",
                        params={"q": destination_query.strip(), "format": "jsonv2", "limit": 6, "addressdetails": 1, "countrycodes": "in"},
                        headers={"User-Agent": "SafeDriveAI/1.0"}, timeout=15,
                    )
                    response.raise_for_status()
                    places = response.json()
                if places:
                    st.session_state.comparison_places = places
                    st.success(f"Found {len(places)} matching place(s). Select your destination below.")
                else:
                    st.warning("No matching destination found. Include the town or district.")
            except (requests.RequestException, ValueError) as error:
                st.error(f"Destination search failed: {error}")

    places = st.session_state.comparison_places
    if places:
        labels = [place.get("display_name", "Unnamed place") for place in places]
        selected_index = st.selectbox("Choose your destination", options=list(range(len(places)),), format_func=lambda i: labels[i], key="comparison_place_selection")
        selected_place = places[selected_index]
        st.write(f"**Selected destination:** {selected_place.get('display_name', 'Unnamed place')}")
        if latitude is None or longitude is None:
            st.warning("Current device location is unavailable. Allow browser location access.")
        elif st.button("🚗 Compare Driving Routes", type="primary"):
            try:
                dest_lat, dest_lon = float(selected_place["lat"]), float(selected_place["lon"])
                route_url = f"https://router.project-osrm.org/route/v1/driving/{longitude},{latitude};{dest_lon},{dest_lat}"
                with st.spinner("Calculating available driving routes..."):
                    rr = requests.get(route_url, params={"overview": "full", "geometries": "geojson", "steps": "true", "alternatives": "true"}, timeout=30)
                    rr.raise_for_status()
                    route_data = rr.json()
                if route_data.get("code") != "Ok" or not route_data.get("routes"):
                    st.session_state.comparison_routes = None
                    st.error("No driving route could be calculated for this destination.")
                else:
                    st.session_state.comparison_routes = route_data
                    st.session_state.comparison_destination = {"name": selected_place.get("display_name", "Selected destination"), "latitude": dest_lat, "longitude": dest_lon}
            except (requests.RequestException, ValueError, KeyError) as error:
                st.session_state.comparison_routes = None
                st.error(f"Route calculation failed: {error}")

    route_data = st.session_state.comparison_routes
    destination_info = st.session_state.comparison_destination
    if route_data and destination_info:
        routes = route_data.get("routes", [])
        st.subheader("📊 Route Comparison")
        route_df = pd.DataFrame([{
            "Route": f"Route {i + 1}",
            "Distance (km)": round(route["distance"] / 1000, 2),
            "Estimated time (min)": round(route["duration"] / 60),
        } for i, route in enumerate(routes)])
        shortest_index = min(range(len(routes)), key=lambda i: routes[i]["distance"])
        quickest_index = min(range(len(routes)), key=lambda i: routes[i]["duration"])
        c1, c2 = st.columns(2)
        c1.metric("Shortest available route", f"Route {shortest_index + 1}", f"{routes[shortest_index]['distance'] / 1000:.2f} km")
        c2.metric("Quickest estimated route", f"Route {quickest_index + 1}", f"{routes[quickest_index]['duration'] / 60:.0f} min")
        st.dataframe(route_df, use_container_width=True, hide_index=True)
        comparison_map = folium.Map(location=[latitude, longitude], zoom_start=12, control_scale=True, tiles="OpenStreetMap")
        folium.Marker([latitude, longitude], tooltip="Starting point", popup="Current device-reported location", icon=folium.Icon(color="green", icon="play", prefix="fa")).add_to(comparison_map)
        folium.Marker([destination_info["latitude"], destination_info["longitude"]], tooltip="Destination", popup=destination_info["name"], icon=folium.Icon(color="red", icon="flag", prefix="fa")).add_to(comparison_map)
        route_colours = ["#0877FF", "#E67E22", "#8E44AD", "#16A085", "#C0392B"]
        all_points = []
        for index, route in enumerate(routes):
            points = [[coord[1], coord[0]] for coord in route["geometry"]["coordinates"]]
            all_points.extend(points)
            folium.PolyLine(points, color=route_colours[index % len(route_colours)], weight=7 if index == 0 else 5, opacity=0.9, tooltip=f"Route {index + 1}: {route['distance'] / 1000:.2f} km, {route['duration'] / 60:.0f} minutes estimated").add_to(comparison_map)
        if all_points:
            comparison_map.fit_bounds(all_points)
        st.subheader("🗺️ Routes on Map")
        st_folium(comparison_map, height=550, width=None, key="route_comparison_map")
        route_choice = st.selectbox("Choose a route to open in Google Maps", options=list(range(len(routes))), format_func=lambda i: f"Route {i + 1} — {routes[i]['distance'] / 1000:.2f} km, {routes[i]['duration'] / 60:.0f} min estimated", key="comparison_route_choice")
        google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={latitude},{longitude}&destination={destination_info['latitude']},{destination_info['longitude']}&travelmode=driving"
        st.link_button("Open destination directions in Google Maps", google_maps_url)
        chosen_route = routes[route_choice]
        with st.expander("View available turn-by-turn route steps"):
            for leg in chosen_route.get("legs", []):
                for step_number, step in enumerate(leg.get("steps", []), start=1):
                    road_name = step.get("name") or "Unnamed road"
                    instruction = step.get("maneuver", {}).get("type", "Continue")
                    st.write(f"{step_number}. {instruction.title()} — {road_name} ({step.get('distance', 0):.0f} m)")

# -------------------- AI WARNING SYSTEM --------------------
elif page == "AI Warning System":
    st.header("🚨 AI Warning System")
    st.caption("Rule-based prototype using the current demonstration inputs; not a trained model.")
    st.metric("Overall driving risk", f"{risk_score}/100")
    if not ai_warnings:
        st.success("No warnings were generated by the current rules.")
    for warning in ai_warnings:
        level = str(warning.get("level", "INFO")).upper()
        message = warning.get("message", str(warning))
        if level in ("CRITICAL", "HIGH"):
            st.error(f"**{level} — {warning.get('type', 'Safety warning')}:** {message}")
        elif level in ("MEDIUM", "MODERATE"):
            st.warning(f"**{level} — {warning.get('type', 'Safety warning')}:** {message}")
        else:
            st.info(f"**{level} — {warning.get('type', 'Safety warning')}:** {message}")
    with st.expander("Risk factors used"):
        show_reasons(risk_reasons)
    if st.button("Record AI Warning Summary"):
        st.session_state.incidents = add_incident(st.session_state.incidents, "AI Warning System", risk_level, "; ".join(str(w.get("message", "")) for w in ai_warnings) or "No warnings generated")
        st.success("Warning summary recorded in this session.")

# -------------------- JUNCTION PREDICTION --------------------
elif page == "Junction Prediction":
    st.header("🚦 AI Junction Collision Prediction")
    st.caption("Junction distance and conditions are manually entered; no live junction or vehicle detection is connected.")
    show_risk_card("Junction risk assessment", junction_result)
    st.warning("Treat the output as a demonstration only. Slow down near junctions and obey signs and signals.")
    if st.button("Record Junction Assessment"):
        st.session_state.incidents = add_incident(st.session_state.incidents, "Junction Risk", junction_result.get("risk_level", "UNKNOWN"), "; ".join(junction_result.get("reasons", [])) or junction_result.get("warning", "No details"))
        st.success("Junction assessment recorded.")

# -------------------- OVERTAKING ADVISOR --------------------
elif page == "Safe Overtaking Advisor":
    st.header("🛣️ AI Safe Overtaking Advisor")
    st.caption("Traffic and visibility are assumed manual inputs, not detected from the road.")
    show_risk_card("Overtaking risk assessment", overtaking_result)
    st.error("Never use this prototype as permission to overtake. Only overtake when it is legal and clearly safe; follow road signs and local rules.")
    if st.button("Record Overtaking Assessment"):
        st.session_state.incidents = add_incident(st.session_state.incidents, "Overtaking Risk", overtaking_result.get("risk_level", "UNKNOWN"), "; ".join(overtaking_result.get("reasons", [])) or overtaking_result.get("recommendation", "No details"))
        st.success("Overtaking assessment recorded.")

# -------------------- PEDESTRIAN RISK --------------------
elif page == "Pedestrian Risk Predictor":
    st.header("🚶 AI Pedestrian Risk Predictor")
    st.caption("Pedestrian presence and crossing distance are manually selected; no camera/computer vision detection is connected.")
    show_risk_card("Pedestrian risk assessment", pedestrian_result)
    st.warning("Reduce speed near crossings, schools, bus stops and areas where pedestrians may appear.")
    if st.button("Record Pedestrian Assessment"):
        st.session_state.incidents = add_incident(st.session_state.incidents, "Pedestrian Risk", pedestrian_result.get("risk_level", "UNKNOWN"), "; ".join(pedestrian_result.get("reasons", [])) or pedestrian_result.get("warning", "No details"))
        st.success("Pedestrian assessment recorded.")

# -------------------- ALERT MANAGER AND PRIORITY ENGINE --------------------
elif page == "AI Safety Alerts":
    st.header("🧠 AI Safety Alerts & Safety Priority Engine")
    st.caption("Alerts are combined from the prototype's rule-based modules.")
    priority_level = str(priority_result.get("level", "LOW")).upper()
    st.metric("Safety Priority", priority_level)
    st.write(priority_result.get("message", "No priority message available."))
    st.metric("Priority Score", priority_result.get("priority", "N/A"))
    st.subheader("Highest-priority alert")
    if isinstance(highest_alert, dict):
        highest_level = str(highest_alert.get("level", "LOW")).upper()
        highest_message = highest_alert.get("message", "No message available.")
        if highest_level in ("CRITICAL", "HIGH"):
            st.error(f"{highest_level}: {highest_message}")
        elif highest_level in ("MEDIUM", "MODERATE"):
            st.warning(f"{highest_level}: {highest_message}")
        else:
            st.info(f"{highest_level}: {highest_message}")
    else:
        st.info(str(highest_alert))
    st.subheader("All collected alerts")
    if all_alerts:
        for alert in all_alerts:
            level = str(alert.get("level", "INFO")).upper()
            message = alert.get("message", "")
            source = alert.get("source", "Safety module")
            if level in ("CRITICAL", "HIGH"):
                st.error(f"**{source} — {level}:** {message}")
            elif level in ("MEDIUM", "MODERATE"):
                st.warning(f"**{source} — {level}:** {message}")
            else:
                st.info(f"**{source} — {level}:** {message}")
    else:
        st.success("No alerts returned by the current rules.")
    with st.expander("Priority-engine details"):
        st.json(priority_result)
    if st.button("Record Highest-Priority Alert"):
        st.session_state.incidents = add_incident(st.session_state.incidents, "AI Safety Priority", priority_level, str(priority_result.get("message", "")))
        st.success("Priority alert recorded.")

# -------------------- SAFETY INSIGHTS --------------------
elif page == "Safety Insights":
    st.header("💡 Safety Insights")
    driver_status = st.selectbox("Driver Status", ["LOW", "MEDIUM", "HIGH"])
    vehicle_status = st.selectbox("Vehicle Health Status", ["GOOD", "CHECK", "WARNING"])
    insights = generate_safety_insights(speed, weather_for_risk, road_condition, risk_score, driver_status, vehicle_status)
    for number, insight in enumerate(insights, start=1):
        st.write(f"**{number}.** {insight}")

# -------------------- INCIDENT HISTORY --------------------
elif page == "Incident History":
    st.header("📋 Incident History")
    incidents = st.session_state.incidents
    summary = get_incident_summary(incidents)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", summary.get("total", 0))
    c2.metric("High", summary.get("high", 0))
    c3.metric("Medium", summary.get("medium", 0))
    c4.metric("Low", summary.get("low", 0))
    if incidents:
        st.dataframe(pd.DataFrame(incidents), use_container_width=True, hide_index=True)
        st.download_button("Download Incidents CSV", generate_incident_csv(incidents), "safedrive_incidents.csv", "text/csv")
    else:
        st.info("No incidents have been recorded in this session.")
    if st.button("Clear Session Incidents"):
        st.session_state.incidents = []
        st.rerun()

# -------------------- EMERGENCY SOS --------------------
elif page == "Emergency SOS":
    st.header("🆘 Emergency SOS")
    st.warning("This creates a message only. It does not call emergency services or transmit your location.")
    emergency_type = st.selectbox("Emergency Type", get_emergency_types())
    if latitude is not None and longitude is not None:
        sos_latitude, sos_longitude = latitude, longitude
        st.write("Using current browser-provided coordinates.")
    else:
        st.warning("Device location unavailable. Enter coordinates manually.")
        sos_latitude = st.number_input("Latitude", value=11.0168, format="%.6f")
        sos_longitude = st.number_input("Longitude", value=76.9558, format="%.6f")
    if st.button("Generate SOS Message"):
        st.session_state.sos_message = generate_sos_message(sos_latitude, sos_longitude, emergency_type)
    if st.session_state.sos_message:
        st.text_area("Generated SOS", st.session_state.sos_message, height=220)
        st.download_button("Download SOS Message", st.session_state.sos_message, "safedrive_sos.txt", "text/plain")

# -------------------- SAFETY REPORTS --------------------
elif page == "Safety Reports":
    st.header("📄 Safety Reports")
    report_driver_status = st.selectbox("Driver Status for Report", ["LOW", "MEDIUM", "HIGH"])
    report_vehicle_status = st.selectbox("Vehicle Status for Report", ["GOOD", "CHECK", "WARNING"])
    report_text = generate_safety_report(
        risk_score=risk_score,
        risk_level=risk_level,
        speed=speed,
        weather=weather_for_risk,
        road_condition=road_condition,
        stopping_distance=stopping_distance,
        following_distance=following_distance,
        collision_level=collision_level,
        driver_status=report_driver_status,
        vehicle_health_status=report_vehicle_status,
        incidents=st.session_state.incidents,
    )
    st.text_area("Report Preview", report_text, height=350)
    st.download_button("Download Safety Report", report_text, "safedrive_safety_report.txt", "text/plain")
    st.download_button("Download Incident CSV", generate_incident_csv(st.session_state.incidents), "safedrive_incidents.csv", "text/csv")

# -------------------- VOICE ALERT --------------------
st.sidebar.divider()
st.sidebar.subheader("🔊 Voice Alert")
if st.sidebar.button("Speak Current Risk"):
    message = f"Driving risk level is {risk_level}. Weather condition is {weather_for_risk}."
    try:
        success, result = speak_alert(message)
        if success:
            st.sidebar.success(result)
        else:
            st.sidebar.error(result)
    except Exception as error:
        st.sidebar.error(f"Voice alert failed: {error}")

st.divider()
st.caption(
    "SafeDrive AI | Research prototype. GPS/weather are available only when "
    "retrieved successfully. Road clearance, live traffic, vehicle sensors and "
    "collision/pedestrian detection are not validated or connected."
)
