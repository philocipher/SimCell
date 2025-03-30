import pandas as pd
from .gnb import gNB

def load_gnbs_from_csv(filepath, lat_range=None, lon_range=None):
    """
    Load gNBs from OpenCelliD CSV file with optional latitude and longitude filtering.

    Parameters:
        filepath (str): Path to CSV file.
        lat_range (tuple): (min_latitude, max_latitude)
        lon_range (tuple): (min_longitude, max_longitude)

    Returns:
        List[gNB]: List of instantiated gNB objects.
    """
    df = pd.read_csv(filepath, names=[
        "radio", "mcc", "net", "area", "cellid", "unit", "lon", "lat", "range",
        "samples", "changeable", "created", "updated", "averageSignal"
    ])
    # Filter based on latitude and longitude if specified
    if lat_range:
        df = df[(df['lat'] >= lat_range[0]) & (df['lat'] <= lat_range[1])]
    if lon_range:
        df = df[(df['lon'] >= lon_range[0]) & (df['lon'] <= lon_range[1])]

    gnbs = []
    for _, row in df.iterrows():
        gnbs.append(gNB(
            gn_id=row['cellid'],
            latitude=row['lat'],
            longitude=row['lon'],
            radio=row['radio'],
            mcc=row['mcc'],
            net=row['net'],
            area=row['area'],
            unit=row['unit'],
            range=row['range'],
            samples=row['samples'],
            changeable=row['changeable'],
            created=row['created'],
            updated=row['updated'],
            averageSignal=row['averageSignal']
        ))

    return gnbs



import random
import math
from .gnb import gNB

import random
import math

def generate_random_gnbs(density_per_km2, lat_range, lon_range, min_distance_km=0.1):
    """
    Generate random gNBs within the given latitude and longitude range,
    ensuring they are not too close to each other, based on desired density.

    Parameters:
        density_per_km2 (float): Number of gNBs per square kilometer.
        lat_range (tuple): (min_latitude, max_latitude)
        lon_range (tuple): (min_longitude, max_longitude)
        min_distance_km (float): Minimum distance between points in kilometers.

    Returns:
        List[gNB]: List of randomly generated gNB objects.
    """
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) *
             math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def approximate_area_km2(lat_range, lon_range):
        lat1, lat2 = lat_range
        lon1, lon2 = lon_range
        avg_lat = (lat1 + lat2) / 2
        lat_km = 111  # Roughly 111 km per degree of latitude
        lon_km = 111 * math.cos(math.radians(avg_lat))  # Varies with latitude
        return abs(lat2 - lat1) * lat_km * abs(lon2 - lon1) * lon_km

    area_km2 = approximate_area_km2(lat_range, lon_range)
    count = int(density_per_km2 * area_km2)

    generated = []

    while len(generated) < count:
        lat = random.uniform(*lat_range)
        lon = random.uniform(*lon_range)

        too_close = any(
            haversine(lat, lon, existing.lat, existing.lon) < min_distance_km
            for existing in generated
        )

        if not too_close:
            generated.append(gNB(
                gn_id=random.randint(100000, 999999),
                latitude=lat,
                longitude=lon,
                radio='LTE',
                mcc=262,
                net=1,
                area=1,
                unit=0,
                range=500,
                samples=1,
                changeable=1,
                created='2024-01-01',
                updated='2025-01-01',
                averageSignal=-70
            ))

    return generated
