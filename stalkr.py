import sys
from datetime import datetime
from contextlib import contextmanager
from math import radians, cos, isnan
import pandas as pd
import numpy as np
import localization as lx
import pygeohash as gh
import matplotlib.pyplot as plt
from db_models import profileLocationModel

# Define a context manager to suppress stdout
@contextmanager
def suppress_print():
    original_stdout = sys.stdout  # Save the original stdout
    sys.stdout = open('/dev/null', 'w')  # Redirect stdout to null
    try:
        yield
    finally:
        sys.stdout.close()  # Close the null file
        sys.stdout = original_stdout  # Restore stdout to original

def generate_grid_points(center_lat, center_lon, side_m, points_per_side, jitter_m=100):
    # Approximate conversion factor: 1 degree latitude = 111,000 meters
    deg_per_m = 1 / 111000
    # Jitter in degrees
    jitter_deg = jitter_m * deg_per_m
    # Calculate half side in degrees
    half_side_deg = (side_m / 2) * deg_per_m

    # Define the rectangle corners
    top_lat = center_lat + half_side_deg
    bottom_lat = center_lat - half_side_deg
    # Adjust for longitude using cos(), now considering meters
    left_lon = center_lon - half_side_deg / cos(radians(center_lat))
    right_lon = center_lon + half_side_deg / cos(radians(center_lat))

    # Generate latitude and longitude points
    lat_steps = np.linspace(bottom_lat, top_lat, points_per_side)
    lon_steps = np.linspace(left_lon, right_lon, points_per_side)

    grid_points = [(lat+ np.random.uniform(-jitter_deg, jitter_deg), lon+ np.random.uniform(-jitter_deg, jitter_deg)) for lat in lat_steps for lon in lon_steps]
    # Initialize list to store grid points with jitter

    return grid_points

def select_indices(distances):
    # Convert distances to numpy array for efficient operations
    distances = np.array(distances)

    # Get the indices of the smallest 20 distances
    closest_indices = distances.argsort()[:30]
    return closest_indices

def localize(ref_points,distances)->list:
    P=lx.Project(mode='Earth1',solver='LSE')
    if any(isnan(distance) for distance in distances):
        return
    selected_indexes = select_indices(distances)
    if len(selected_indexes) < 3:
        return
    for i in selected_indexes:
        P.add_anchor(f'anchore_{i}',ref_points[i])
    t,label=P.add_target(ID=123)
    for i in selected_indexes:
        t.add_measure(f'anchore_{i}',distances[i])
    with suppress_print():
        P.solve()

    return [t.loc.x, t.loc.y]

def localizeProfile(profiles, max_distance=1000):
    localizations = {}
    # Convert the list of dictionaries to a pandas DataFrame
    profiles_df = pd.DataFrame(profiles)
    profiles_df = profiles_df[profiles_df['distance_from_anchor'] <= max_distance]
    if profiles_df.empty:
        return localizations, None
    profile_id = profiles_df['profileId'].iloc[0]
    batch_timestamp = profiles_df['batch_timestamp'].iloc[0]
    localizedProfile = None
    if "distance_from_anchor" in profiles_df.columns:
        ref_points = [[lat, lon] for lat, lon in zip(profiles_df['anchor_lat'].tolist(), profiles_df['anchor_lon'].tolist())]
        distances = profiles_df['distance_from_anchor'].tolist()
        estimated_position = localize(ref_points,distances)
        estimated_gh = gh.encode(estimated_position[0], estimated_position[1],12) if estimated_position else ""
        localizations[profile_id] = {
            "estimated_position": estimated_position,
            "estimated_gh": estimated_gh,
            "batch_timestamp": batch_timestamp,
            "ref_points": ref_points,
            "distances": profiles_df['distance_from_anchor'].tolist()
        }
        if estimated_position:
            #sometimes not all fields are properly set in the request. This makes sure, that all data are available in database
            loc_prof = {
                "lat": estimated_position[0],
                "lon": estimated_position[1],
                "geoHash": estimated_gh,
                "profileId": profile_id,
                "timestamp": int(datetime.now().timestamp() * 1000),
                "batch_timestamp": batch_timestamp
            }
            localizedProfile = profileLocationModel(**loc_prof) # Create a new LocatedProfileModel instance


    return localizations, localizedProfile

def visualize(locations):
    # Example reference points and distances (lat, lon) and meters
    reference_points = locations['ref_points']
    distances = locations['distances']
    calculated_point = locations['estimated_position']

    # Plotting
    fig, ax = plt.subplots()

    # Convert distances to degrees approximately (quick approximation, valid for short distances)
    # Assuming a rough conversion factor (not accurate for large distances or near the poles)
    distance_degrees = [d / 111139 for d in distances]

    # Plot reference points

    selected_indexes, cutoff = select_indexes(distance_degrees)
    for (lat, lon), distance_degree in zip(reference_points, distance_degrees):
        ax.plot(lon, lat, 'bo')  # Reference points in blue
        if distance_degree <= cutoff:
            color = 'b'
            linewidth = 0.4
        else:
            color = 'r'
            linewidth = 0.1
        circle = plt.Circle((lon, lat), distance_degree, color=color, fill=False, linestyle='--', linewidth=linewidth)
        ax.add_artist(circle)

    # Plot the calculated point
    ax.plot(calculated_point[1], calculated_point[0], 'rx')  # Calculated point in red

    # Set labels and show plot
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Multilateration Visualization')
    plt.grid(True)
    plt.axis('equal')  # Equal aspect ratio to ensure circles look like circles
    plt.show()

def visualize_grid(reference_points):
    # Plotting
    fig, ax = plt.subplots()

    for lat, lon in reference_points:
        ax.plot(lon, lat, 'bo')  # Reference points in blue

    # Set labels and show plot
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Multilateration Visualization')
    plt.grid(True)
    plt.axis('equal')  # Equal aspect ratio to ensure circles look like circles
    plt.show()