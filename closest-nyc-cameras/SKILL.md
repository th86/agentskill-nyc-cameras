---
name: closest-nyc-cameras
description: "Given a user-provided address, find the 4 closest traffic cameras from https://webcams.nyctmc.org/cameras-list, screenshot their real-time images, and send the images back with timestamps and camera location descriptions."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [cameras, nyc, geolocation, screenshot]
    related_skills: []
---
# Closest NYC Cameras Skill

**Description**: Given a user-provided address, find the N closest traffic cameras from the NYC traffic cameras API (https://webcams.nyctmc.org/api/cameras), download their real-time images, and send the images back with timestamps and camera names.

**When to invoke**: User asks for nearest cameras to an address, or wants to see live camera views near a location.

**Assumptions**: 
- The user will provide an address (or approximate location) in New York City.
- The API https://webcams.nyctmc.org/api/cameras returns a JSON array of camera objects with fields: id, name, latitude, longitude, imageUrl, area, isOnline.
- The imageUrl points to a JPEG/PNG image of the current camera view.
- The Nominatim OpenStreetMap API is available for geocoding the user address.

**Steps**:

1. **Get user address**
   - Use `clarify` tool to ask the user for the address (if not already provided in the request).
   - Store the address string.

2. **Geocode the user address**
   - Call the Nominatim API via `terminal` with:
     `curl -A "HermesAgent/1.0" "https://nominatim.openstreetmap.org/search?format=json&q=<URL-encoded address>&limit=1"`
   - Extract the first result's `lat` and `lon` as floats.
   - If no results, ask user to refine address.

3. **Fetch camera list from API**
   - Use `terminal` to call:
     `curl -s "https://webcams.nyctmc.org/api/cameras"`
   - Parse the JSON response into a list of camera objects.

4. **Compute distances**
   - For each camera, compute the Haversine distance (in kilometers) between the user’s coordinates and the camera’s latitude/longitude.
   - Sort cameras by distance ascending.
   - Select the top N cameras (default N = 4, but can be overridden by user request; if user asks for 1 closest, use N=1).

5. **Download and send images for each selected camera**
   For each selected camera:
   a. Build the image URL: use camera.imageUrl (may already include a timestamp; to avoid caching we can append `&t=<current_unix_ms>` if the URL does not already contain a query string).
   b. Download the image via `terminal`:
        `curl -s -L "<image_url>" -o /tmp/herscam_<camera_id>.jpg`
   - Optionally verify the download succeeded (non-zero file size).
   - Generate an ISO timestamp for the moment of download.
   - Send the image to the user:
        - First, determine the correct target by running `send_message(action='list')` to see available targets (e.g., `telegram:Tai (dm)`).
        - Compose a caption: `📸 Camera: <camera.name>\n🕒 Captured at: <ISO timestamp>\n📍 Area: <camera.area>`.
        - Append `MEDIA:/tmp/herscam_<camera_id>.jpg` to the caption.
        - Use `send_message` with the obtained target to deliver.
   - Clean up the temporary file after sending (optional).

6. **Completion**
   - After all selected cameras have been processed, inform the user that the task is complete.

**Required Tools**: `clarify`, `terminal`, `send_message`.

**Helper Functions** (see reference file `geocode.py`):
- `geocode(address) -> (lat, lon)`: wraps Nominatim request.
- `haversine(lat1, lon1, lat2, lon2) -> distance_km`.
- `fetch_cameras() -> list of dicts`: fetches and parses the JSON from the API.
- `select_closest_cameras(user_lat, user_lon, cameras, n=4) -> list of dicts`: returns the n closest cameras sorted by distance.

**Notes**:
- The skill assumes internet access and that both Nominatim and the NYC cameras API are responsive.
- If any step fails, the skill should report the error and stop processing further cameras.
- The images are downloaded directly from the imageUrl, guaranteeing we receive only the camera frame (no extra browser UI).
- Timestamp is generated at the moment of download.

**Reference Files**:
- `geocode.py`: Python script with geocoding, haversine, and API helper functions.
- `geocode.py`: Python script with geocoding and distance utilities.