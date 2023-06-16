
import polyline
import googlemaps
import time
from datetime import datetime
import random
import math
import numpy as np
from .map_socket import sio
import asyncio
from multiprocessing import Process
from .variables import arabic_male_names
from utils.mongo_connection import drivers_collection, orders_collection, restaurant_collection

gkey = 'AIzaSyAv4TshMqyQUcBc_oWM6w9hjlxIKqiUOvA'
gmaps = googlemaps.Client(key=gkey)

class SimulationClass:

    #Function to create a route, takes origin, waypoints and destination as args, and modifies the route to make it more accurate in the simulation, returns list with tuples full of corrdinates for a route.
    @classmethod
    def create_route(cls, orgn, wayp, dest):

        directions_result = gmaps.directions(origin=orgn,
                                            waypoints= wayp,
                                            destination= dest,
                                            mode='driving')
        ply_points = directions_result[0]['overview_polyline']['points']
        route = polyline.decode(ply_points)

        threshold = cls.convert_kmh(40)
        adjusted_route = []

        num_points = len(route)
        
        for i in range(num_points - 1):
            current_coord = route[i]
            next_coord = route[i + 1]
            adjusted_route.append(current_coord)
            
            distance = cls.calculate_distance(current_coord, next_coord)
            
            if distance > threshold:
                num_intermediate_points = math.ceil(distance / threshold)
                x_step = (next_coord[0] - current_coord[0]) / num_intermediate_points
                y_step = (next_coord[1] - current_coord[1]) / num_intermediate_points
                
                for j in range(1, num_intermediate_points):
                    intermediate_x = current_coord[0] + j * x_step
                    intermediate_y = current_coord[1] + j * y_step
                    adjusted_route.append((intermediate_x, intermediate_y))
        
        adjusted_route.append(route[-1]) 
        
        return adjusted_route
    

    #Convert speeds from KM/H to KM/S
    @classmethod
    def convert_kmh(cls, speed):
        factor = 3600
        conv_speed = speed / factor
        return conv_speed
    

    #Function to calculate the distance between 2 coords.
    @classmethod
    def calculate_distance(cls, coord1, coord2):
        
        R = 6371.0
        
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        lat1_rad = np.radians(lat1)
        lon1_rad = np.radians(lon1)
        lat2_rad = np.radians(lat2)
        lon2_rad = np.radians(lon2)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        distance = R * c

        return distance