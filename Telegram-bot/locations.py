from geopy.distance import geodesic
from config import LOCATIONS # Import LOCATIONS from config.py

def get_nearest_location(lat, lon, category):
    """Find the nearest location in a given category."""
    if category not in LOCATIONS:
        return None
    
    user_location = (lat, lon)
    nearest = None
    min_distance = float('inf')
    
    for name, data in LOCATIONS[category].items():
        location = (data['lat'], data['lon'])
        distance = geodesic(user_location, location).kilometers
        
        if distance < min_distance:
            min_distance = distance
            nearest = {
                'name': name,
                'description': data['description'],
                'distance': round(distance, 2)
            }
    
    return nearest

def get_locations_by_category(category):
    """Get all locations in a given category."""
    return LOCATIONS.get(category, {})

def get_location_info(name):
    """Get information about a specific location."""
    # Iterate through all categories to find the location
    for category_data in LOCATIONS.values():
        if name in category_data:
            return category_data[name]
    return None 