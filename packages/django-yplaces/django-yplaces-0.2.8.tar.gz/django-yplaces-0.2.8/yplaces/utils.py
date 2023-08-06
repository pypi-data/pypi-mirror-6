import math


class Geo:
    """
    Methods regarding geolocation.
    """
    earth_radius = 6371
    
    @staticmethod
    def distance(origin, destination):
        """
        Calculate distance between two points on a sphere from their longitudes and latitudes.
        """
        lat1, lon1 = origin
        lat2, lon2 = destination
        radius = Geo.earth_radius # km
    
        dlat = math.radians(lat2-lat1)
        dlon = math.radians(lon2-lon1)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
            * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = radius * c
    
        return d

    @staticmethod
    def box(origin, radius):
        """
        Calculate latitude and longitude limit box.
        """
        earth_r = Geo.earth_radius
        
        # First-cut bounding box (in degrees)
        maxLat = origin[0] + math.degrees(radius/earth_r)
        minLat = origin[0] - math.degrees(radius/earth_r)
        
        # Compensate for degrees longitude getting smaller with increasing latitude
        maxLon = origin[1] + math.degrees(radius/earth_r/math.cos(math.radians(origin[0])))
        minLon = origin[1] - math.degrees(radius/earth_r/math.cos(math.radians(origin[0])))

        # Return.
        return {
            'maxLat': maxLat,
            'minLat': minLat,
            'maxLon': maxLon,
            'minLon': minLon
        }