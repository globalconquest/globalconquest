import plotly.graph_objects as go
import json
import math
from math import sqrt
from get_price import get_bsc_token_price



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

# Debug: Validate country codes
#selected_codes = [data['country'] for data in country_selected]
selected_codes = [data for data in country_data]
print("Selected country codes:", selected_codes)

# Create choropleth map
fig = go.Figure()

for i in range(len(name)):
    fig.add_trace(go.Choropleth(
        locations=selected_countries[i],
        z=[1] * len(selected_countries[i]),
        colorscale=[[0, 'gray'], [1, color[i]]],
        locationmode='ISO-3',
        showscale=False,
        marker_line_color="black",
        marker_line_width=1,
        text=selected_countries[i],
        hovertemplate='<b>%{text}</b><br>Conquered by '+name[i]+'<extra></extra>'
    ))

# Update layout for 3D globe
fig.update_geos(
    bgcolor="rgba(0,0,0,1)",
    projection_type="orthographic",
    showcountries=True,
    countrycolor="black",
    showocean=True,
    oceancolor="LightBlue",
    showlakes=True,
    lakecolor="LightBlue",
    showland=True,
    landcolor="white"
)
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,1)",
    margin={"r":10, "t":10, "l":10, "b":10},
    showlegend=True,
    legend=dict(
        x=0.01,
        y=0.99,
        xanchor="left",
        yanchor="top",
        bgcolor="rgba(255,255,255,0.7)",
        bordercolor="black",
        borderwidth=1
    ),
    autosize=True,
    font=dict(size=12)
)


for i in range(len(name)):
    fig.add_trace(go.Scattergeo(
        lon=[lon[i]], lat=[lat[i]],
        mode='markers',
        marker=dict(size=10, color=color[i]),
        showlegend=True,
        legendgroup="legend",
        name=name[i]
    ))

# Save as HTML
fig.write_html(
    "world_map.html",
    include_plotlyjs='cdn',
    full_html=True,
    config={
        'responsive': True,
        'displayModeBar': True,
        'scrollZoom': True
    }
)

print("Map generated as 'world_map.html'. Open in a browser to view.")