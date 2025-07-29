import os
import requests
import folium
from folium.features import CustomIcon
import time
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from dotenv import load_dotenv

BRAND_LOGOS = {
    "z": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Z_Energy_logo.svg/1024px-Z_Energy_logo.svg.png",
    "bp": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5e/BP_logo.svg/1024px-BP_logo.svg.png",
    "caltex": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f8/Caltex_Logo.svg/1024px-Caltex_Logo.svg.png",
    "mobil": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Mobil_logo.svg/1280px-Mobil_logo.svg.png",
    "waitomo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Waitomo_Group_logo.svg/1024px-Waitomo_Group_logo.svg.png",
}

def get_brand_logo_path(station_name, logo_dir="logos"):
    # Get the absolute path to the logos folder, relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_dir, logo_dir)

    if not os.path.exists(logo_path):
        raise FileNotFoundError(f"Logo directory not found: {logo_path}")

    station_lower = station_name.lower()
    for file in os.listdir(logo_path):
        brand = os.path.splitext(file)[0]  # e.g., "bp"
        if brand in station_lower:
            return os.path.join(logo_path, file)
    return None

# Load API key
load_dotenv()
API_KEY = os.getenv("ORS_API_KEY")

def geocode_address(address):
    """
    Convert a human-readable address into coordinates using ORS geocoding API.
    """
    url = "https://api.openrouteservice.org/geocode/search"
    params = {
        "api_key": API_KEY,
        "text": address
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "features" not in data or not data["features"]:
        raise Exception(f"Address not found: {address}")

    coords = data["features"][0]["geometry"]["coordinates"]  # [lon, lat]
    return coords[::-1]  # return as [lat, lon]

def get_drive_distance(origin, destination):
    """
    Calculate driving distance and duration between two coordinates.
    """
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    coordinates = [origin[::-1], destination[::-1]]  # [[lon, lat], [lon, lat]]
    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    response = requests.post(url, headers=headers, json={"coordinates": coordinates})
    
    print("Route request payload:", {"coordinates": coordinates})
    print("Response status code:", response.status_code)
    #print("Response body:", response.text)

    if response.status_code != 200:
        print("Response status code:", response.status_code)
        raise Exception("Request to ORS failed.")

    data = response.json()

    # Debug: Print full response if 'routes' missing
    if "routes" not in data or not data["routes"]:
        print("Invalid response from ORS:", data)
        raise Exception("No route found or invalid response.")

    try:
        summary = data["routes"][0]["summary"]
        distance_km = summary["distance"] / 1000
        duration_min = summary["duration"] / 60
        return round(distance_km, 2), round(duration_min, 1)
    except (KeyError, IndexError) as e:
        print("Response JSON parsing error:", data)
        raise Exception("Failed to parse route data.")
    

def get_petrol_stations_nz():
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Overpass QL query to find all petrol stations in New Zealand
    overpass_query = """
    [out:json][timeout:60];
    area["ISO3166-1"="NZ"][admin_level=2]->.nz;
    (
      node["amenity"="fuel"](area.nz);
      way["amenity"="fuel"](area.nz);
      relation["amenity"="fuel"](area.nz);
    );
    out center;
    """
    
    print("Fetching petrol station data from Overpass API...")
    response = requests.post(overpass_url, data={"data": overpass_query})
    
    if response.status_code != 200:
        raise Exception(f"Overpass API error: {response.status_code}")

    data = response.json()
    stations = []

    for element in data["elements"]:
        lat = element.get("lat") or element.get("center", {}).get("lat")
        lon = element.get("lon") or element.get("center", {}).get("lon")
        name = element.get("tags", {}).get("name", "Unnamed")
        
        if lat and lon:
            stations.append({
                "name": name,
                "lat": lat,
                "lon": lon
            })

    return stations

def create_petrol_station_map(stations, output_html="nz_petrol_stations_map.html"):
    print("Creating map...")
    # Set a rough center over New Zealand
    m = folium.Map(location=[-41.0, 174.5], zoom_start=5)

    for station in stations:
        popup_text = f"{station['name']}<br>Lat: {station['lat']:.4f}, Lon: {station['lon']:.4f}"
        folium.Marker(
            location=[station['lat'], station['lon']],
            popup=popup_text,
            icon=folium.Icon(color="blue", icon="gas-pump", prefix="fa")
        ).add_to(m)

    m.save(output_html)
    print(f"Map saved to {output_html}")

def find_petrol_stations(origin_lat, origin_lon, radius_m=5000):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["amenity"="fuel"](around:{radius_m},{origin_lat},{origin_lon});
    );
    out center;
    """
    response = requests.post(overpass_url, data=query)
    response.raise_for_status()
    data = response.json()

    stations = []
    origin = (origin_lat, origin_lon)

    for element in data.get("elements", []):
        name = element.get("tags", {}).get("name", "Unnamed Station")
        lat = element["lat"]
        lon = element["lon"]

        try:
            drive_dist_km, drive_time_min = get_drive_distance(origin, (lat, lon))
        except Exception as e:
            print(f"Skipping {name} due to routing error: {e}")
            continue

        stations.append({
            "name": name,
            "lat": lat,
            "lon": lon,
            "distance_km": drive_dist_km,
            "duration_min": drive_time_min
        })

    stations.sort(key=lambda x: x["distance_km"])
    return stations[:10]

def plot_stations_on_map(origin, stations):
    map_obj = folium.Map(location=origin, zoom_start=13)

    folium.Marker(
        origin,
        tooltip="Origin",
        icon=folium.Icon(color='red', icon='home', prefix='fa')
    ).add_to(map_obj)

    for i, s in enumerate(stations):
        popup_html = f"""
        <b>{'🏆 Closest: ' if i == 0 else ''}{s['name']}</b><br>
        Distance: {s['distance_km']:.2f} km<br>
        ETA: {s['duration_min']:.1f} minutes
        """

        # Set larger icon for nearest station
        icon_size = (50, 50) if i == 0 else (30, 30)

        logo_path = get_brand_logo_path(s["name"])
        if logo_path and os.path.exists(logo_path):
            icon = CustomIcon(logo_path, icon_size=icon_size)
        else:
            icon = folium.Icon(
                color='green' if i == 0 else 'blue',
                icon='star' if i == 0 else 'gas-pump',
                prefix='fa'
            )

        folium.Marker(
            location=(s["lat"], s["lon"]),
            popup=popup_html,
            icon=icon
        ).add_to(map_obj)

    return map_obj


if __name__ == "__main__":
    origin_addr = input("Enter origin address: ")
    destination_addr = input("Enter destination address: ")

    try:
        origin_coords = geocode_address(origin_addr)
        destination_coords = geocode_address(destination_addr)

        print(f"Origin coordinates: {origin_coords}")
        print(f"Destination coordinates: {destination_coords}")


        distance, duration = get_drive_distance(origin_coords, destination_coords)
        print(f"\nDriving distance: {distance} km")
        print(f"Estimated travel time: {duration} minutes")
    except Exception as e:
        print("Error:", e)

    stations = get_petrol_stations_nz()
    print(f"Found {len(stations)} petrol stations in NZ.")
    create_petrol_station_map(stations)
    for s in stations[:10]:  # Print just a sample
        print(f"{s['name']}: ({s['lat']}, {s['lon']})")

    stations = find_petrol_stations(*origin_coords)

    print("\n📍 Nearest Petrol Stations:")
    for s in stations:
        print(f"{s['name']} - {s['distance_km']:.2f} km")

    petrol_map = plot_stations_on_map(origin_coords, stations)
    petrol_map.save("nearest_petrol_stations_map.html")
    print("\n✅ Map saved as 'nearest_petrol_stations_map.html'")


