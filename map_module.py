
# File: map_module.py
# Project: SafeDrive AI
# Purpose: Show vehicle location, road names, and nearby places

import folium
import requests


def get_place_name(latitude, longitude):
    """Find the closest available address for the GPS coordinates."""
    try:
        url = "https://nominatim.openstreetmap.org/reverse"

        response = requests.get(
            url,
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "jsonv2",
                "zoom": 18,
                "addressdetails": 1
            },
            headers={
                "User-Agent": "SafeDriveAI/1.0"
            },
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        return data.get("display_name", "Exact place name unavailable")

    except requests.RequestException:
        return "Place name unavailable (network issue)"


def get_nearby_places(latitude, longitude):
    """Retrieve mapped roads and nearby points of interest."""
    query = f"""
    [out:json][timeout:20];
    (
      way(around:700,{latitude},{longitude})["highway"]["name"];
      node(around:500,{latitude},{longitude})["name"];
      way(around:500,{latitude},{longitude})["name"]["amenity"];
      way(around:500,{latitude},{longitude})["name"]["shop"];
      way(around:500,{latitude},{longitude})["name"]["leisure"];
    );
    out center tags;
    """

    try:
        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=25,
            headers={"User-Agent": "SafeDriveAI/1.0"}
        )

        response.raise_for_status()
        return response.json().get("elements", [])

    except (requests.RequestException, ValueError):
        return []


def create_map(latitude=11.0168, longitude=76.9558):
    # Look up the closest available address
    place_name = get_place_name(latitude, longitude)

    # Create a closer map view
    vehicle_map = folium.Map(
        location=[latitude, longitude],
        zoom_start=18,
        control_scale=True,
        tiles="OpenStreetMap"
    )

    # Add the current vehicle location
    folium.Marker(
        location=[latitude, longitude],
        popup=folium.Popup(
            f"<b>SafeDrive AI - Current Location</b><br>{place_name}",
            max_width=350
        ),
        tooltip="Your current location",
        icon=folium.Icon(
            color="blue",
            icon="car",
            prefix="fa"
        )
    ).add_to(vehicle_map)

    # Add the address as a visible map label
    folium.Marker(
        location=[latitude, longitude],
        icon=folium.DivIcon(
            html=f"""
            <div style="
                font-size: 12px;
                font-weight: bold;
                color: #111;
                background: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px 6px;
                width: 230px;
                transform: translate(20px, -15px);
            ">
                📍 {place_name}
            </div>
            """
        )
    ).add_to(vehicle_map)

    # Illustrative safety circle
    folium.Circle(
        location=[latitude, longitude],
        radius=200,
        color="blue",
        fill=True,
        fill_opacity=0.10,
        popup="Illustrative safety zone - not a collision detection boundary"
    ).add_to(vehicle_map)

    # Add nearby mapped road names and places
    nearby_places = get_nearby_places(latitude, longitude)

    for place in nearby_places:
        tags = place.get("tags", {})
        name = tags.get("name")

        if not name:
            continue

        # Roads and mapped features can have different coordinate formats
        if "lat" in place and "lon" in place:
            place_lat = place["lat"]
            place_lon = place["lon"]
        elif "center" in place:
            place_lat = place["center"]["lat"]
            place_lon = place["center"]["lon"]
        else:
            continue

        # Avoid putting another label directly on the vehicle marker
        if (
            abs(place_lat - latitude) < 0.00015
            and abs(place_lon - longitude) < 0.00015
        ):
            continue

        category = tags.get("highway", "place")

        folium.Marker(
            location=[place_lat, place_lon],
            tooltip=name,
            popup=folium.Popup(
                f"<b>{name}</b><br>Map category: {category}",
                max_width=250
            ),
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    color: #222;
                    background: rgba(255,255,255,0.90);
                    border: 1px solid #888;
                    border-radius: 3px;
                    padding: 2px 4px;
                    font-size: 10px;
                    font-weight: 600;
                    white-space: nowrap;
                ">{name}</div>
                """
            )
        ).add_to(vehicle_map)

    return vehicle_map
