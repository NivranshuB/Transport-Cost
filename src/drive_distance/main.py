import os
import requests
from dotenv import load_dotenv

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
