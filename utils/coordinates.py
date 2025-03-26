def xy_to_latlon(x, y, origin_lat, origin_lon):
    """
    Convert x, y in meters to latitude and longitude using equirectangular approximation.
    """
    # delta_lat = y / EARTH_RADIUS
    # delta_lon = x / (EARTH_RADIUS * math.cos(math.radians(origin_lat)))

    # lat = origin_lat + math.degrees(delta_lat)
    # lon = origin_lon + math.degrees(delta_lon)
    return origin_lat + y/100000, origin_lon + x/100000