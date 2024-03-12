from profile_model import ScrapedProfileModel, LocatedProfileModel
from mongoengine import connect, Document, LongField, StringField
from datetime import datetime, timedelta
import time
import pandas as pd
import numpy as np
import math
import math
import localization as lx
import matplotlib.pyplot as plt
import numpy as np
from math import radians, cos, sin, asin, sqrt

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

def select_indexes(distances, num_bins=5):
    # Filter out NaN values
    valid_distances = np.array([distance for distance in distances if not math.isnan(distance)])
    if valid_distances.size == 0:  # Check if the array is not empty to avoid errors
        return [], None

    # Use numpy histogram to find bins
    hist, bin_edges = np.histogram(valid_distances, bins=num_bins)

    # Use digitize to find out which bin each distance belongs to
    bin_indices = np.digitize(valid_distances, bin_edges[:-1]) - 1  # Adjust index to match bin placement

    # Calculate average values for each bin
    bin_averages = [np.mean(valid_distances[bin_indices == i]) for i in range(num_bins)]

    # Identify the two bins with the smallest average values
    smallest_bin_indices = np.argsort(bin_averages)[:2]

    # Find the original indexes of distances that fall into the two smallest bins
    selected_indexes = [i for i, distance in enumerate(distances) if bin_indices[i] in smallest_bin_indices]
    distances_array = np.array(distances)
    return selected_indexes, np.average(distances_array[selected_indexes])

def localize(ref_points,distances):
    P=lx.Project(mode='Earth1',solver='LSE')
    if any(math.isnan(distance) for distance in distances):
        return
    selected_indexes, cutoff = select_indexes(distances)
    if len(selected_indexes) < 3:
        return
    for i in selected_indexes:
        P.add_anchor(f'anchore_{i}',ref_points[i])
    t,label=P.add_target(ID=123)
    for i in selected_indexes:
        t.add_measure(f'anchore_{i}',distances[i])
    # print(selected_indexes)
    P.solve()

    return t.loc.x, t.loc.y

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

def localizeProfile(profiles):
    locations = {}
    # Convert the list of dictionaries to a pandas DataFrame
    profiles_df = pd.DataFrame(profiles)
    profile_id = profiles_df['profileId'].iloc[0]
    batch_timestamp = profiles_df['batch_timestamp'].iloc[0]
    localizedProfile = None
    if "distanceMeters" in profiles_df.columns:
        ref_points = [[lat, lon] for lat, lon in zip(profiles_df['lat'].tolist(), profiles_df['lon'].tolist())]
        distances = profiles_df['distanceMeters'].tolist()
        estimated_position = localize(ref_points,distances)
        locations[profile_id] = {
            "estimated_position": estimated_position,
            "batch_timestamp": batch_timestamp,
            "ref_points": ref_points,
            "distances": profiles_df['distanceMeters'].tolist()
        }
        if estimated_position:
            #sometimes not all fields are properly set in the request. This makes sure, that all data are available in database
            profile_sum = {}
            for profile in profiles:
                profile_sum.update(profile)
            localizedProfile = LocatedProfileModel(**profile_sum) # Create a new LocatedProfileModel instance
            localizedProfile.lat = estimated_position[0]  # Set the estimated latitude
            localizedProfile.lon = estimated_position[1]

    return locations, localizedProfile