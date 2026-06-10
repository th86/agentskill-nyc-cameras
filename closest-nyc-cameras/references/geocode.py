import json
import urllib.request
import urllib.parse
import math
import time

def geocode(address, delay=0.1):
    """
    Geocode an address string using Nominatim OpenStreetMap API.
    Returns (latitude, longitude) as floats, or (None, None) if not found.
    Respects usage policy by adding a delay between calls.
    """
    time.sleep(delay)
    encoded = urllib.parse.quote(address)
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded}&limit=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'HermesAgent/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
    except Exception as e:
        # In case of network error or invalid response
        pass
    return None, None

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points
    on the Earth specified in decimal degrees.
    Returns distance in kilometers.
    """
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    # haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    # Radius of Earth in kilometers: 6371
    km = 6371 * c
    return km

def fetch_cameras():
    """
    Fetch the list of cameras from the NYC API.
    Returns a list of dicts with keys: id, name, latitude, longitude, imageUrl, area, isOnline.
    """
    url = "https://webcams.nyctmc.org/api/cameras"
    req = urllib.request.Request(url, headers={'User-Agent': 'HermesAgent/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
            # Ensure each entry has expected fields
            cameras = []
            for cam in data:
                cameras.append({
                    'id': cam.get('id'),
                    'name': cam.get('name'),
                    'latitude': float(cam.get('latitude')) if cam.get('latitude') is not None else None,
                    'longitude': float(cam.get('longitude')) if cam.get('longitude') is not None else None,
                    'imageUrl': cam.get('imageUrl'),
                    'area': cam.get('area'),
                    'isOnline': cam.get('isOnline')
                })
            return cameras
    except Exception as e:
        # In case of network error or invalid response
        return []

def select_closest_cameras(user_lat, user_lon, cameras, n=4):
    """
    Given user latitude/longitude and a list of camera dicts,
    return the n closest cameras sorted by distance (ascending).
    Each returned dict will include an extra key 'distance_km'.
    """
    if user_lat is None or user_lon is None:
        return []
    # Filter out cameras with missing coordinates
    valid = [c for c in cameras if c['latitude'] is not None and c['longitude'] is not None]
    for cam in valid:
        cam['distance_km'] = haversine(user_lat, user_lon, cam['latitude'], cam['longitude'])
    valid.sort(key=lambda x: x['distance_km'])
    return valid[:n]