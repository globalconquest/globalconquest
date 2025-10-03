import json
import math
from math import sqrt
from get_price import get_bsc_token_price
import os


def calculate_distance(lat1, lon1, lat2, lon2, unit='km'):
    R_km = 6371.0  # Earth's radius in kilometers
    R_mi = 3958.8  # Earth's radius in miles

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Calculate distance
    if unit.lower() == 'mi':
        distance = R_mi * c
    else:
        distance = R_km * c

    return round(distance, 2)


with open("tokens.json", 'r') as file:
    data = json.load(file)
    token = [tok['token'] for tok in data['tokens']]
    name = [tok['name'] for tok in data['tokens']]
    color = [tok['color'] for tok in data['tokens']]
    lat = [tok['lat'] for tok in data['tokens']]
    lon = [tok['lon'] for tok in data['tokens']]
    print(token)

power = []
power.append(get_bsc_token_price(token[0])[0])
power.append(get_bsc_token_price(token[1])[0])
power.append(get_bsc_token_price(token[2])[0])

selected_countries = []
selected_countries.append([])
selected_countries.append([])
selected_countries.append([])


print(power)

# Load your JSON file (uncomment and replace with your file path)
try:
    with open('country.json') as f:
        country_data = json.load(f)
except FileNotFoundError:
    print("JSON file not found. Using example country_data.")

for data in country_data:
    distances = {i: calculate_distance(country_data[data]['lat'], country_data[data]['lon'], lat[i], lon[i], unit='km')/sqrt(power[i]) for i in range(len(name))}
    zone = min(distances, key=lambda x: distances[x])
    selected_countries[zone].append(data)

print(selected_countries)
output = {
    "selected_countries": selected_countries
}

print(output)

# Chemin vers wwwroot (App Service)
wwwroot = os.environ["HOME"] + "/site/wwwroot"
out_file = os.path.join(wwwroot, "data.json")

with open(out_file, "w") as f:
    json.dump(data, f)

print("data.json mis à jour :", out_file)