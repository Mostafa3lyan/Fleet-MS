
import polyline
import googlemaps
import time
import random
import threading
import math
import numpy as np
from .driver_thread import Driver_Thread, sio



gkey = 'AIzaSyAv4TshMqyQUcBc_oWM6w9hjlxIKqiUOvA'
gmaps = googlemaps.Client(key=gkey)

class Simulation:
    def __init__(self, drivers_num, speed, restaurant_list):
        self.center_lat = 30.1491
        self.center_lon = 31.6290
        self.radius = 6000
        self.drivers_num = drivers_num
        self.speed = speed
        self.restaurant_list = restaurant_list
        self.states = ['available', 'busy', 'not_available']
        self.drivers_threads = {}
        self.drivers = []
        self.drivers_active = {}
        self.busy_drivers = {}
        self.not_available_drivers = {}

    def start(self):
        random_location = self.generate_random_location()
        destination = self.generate_random_location()
        route = self.create_route(random_location, None, destination)
        return route
    
    def create_drivers(self):
        for i in range(self.drivers_num+1):
            driver_num = "driver{}_marker".format(i)
            
            driver_thread_num = "driver{}_thread".format(i)

            driver = self.generate_random_location()
            driver_val, driver_thread_val = self.driver_state(driver, i)
            
            self.drivers.append((driver_num, driver_val))
            self.drivers_threads[driver_thread_num] = driver_thread_val
        return {"success": "drivers created successfully"}

    #Driver movment before order selection function.
    def driver_state(self, driver, i):
        gen_states = random.choice(self.states)
        destination = self.generate_random_location()
        route = self.create_route(driver, None, destination)

        if gen_states == self.states[0]:

            self.drivers_active[str(i)] = driver
            # driver_th = Driver_Thread(route, i, self.speed)
            # driver_th.start()
        
            return driver, None

        elif gen_states == self.states[1]:
            self.busy_drivers[str(i)] = driver
            sio.emit("setBusyDriver", self.busy_drivers)
            return driver, None
        
        elif gen_states == self.states[2]:
            self.not_available_drivers[str(i)] = driver
            sio.emit("setNotAvailableDriver", self.busy_drivers)
            return driver, None



    #Function to create a route, takes origin, waypoints and destination as args, and modifies the route to make it more accurate in the simulation, returns list with tuples full of corrdinates for a route.
    def create_route(self, orgn, wayp, dest):

        directions_result = gmaps.directions(origin=orgn,
                                            waypoints= wayp,
                                            destination= dest,
                                            mode='driving')
        ply_points = directions_result[0]['overview_polyline']['points']
        route = polyline.decode(ply_points)

        threshold = self.convert_kmh(40)
        adjusted_route = []

        num_points = len(route)
        
        for i in range(num_points - 1):
            current_coord = route[i]
            next_coord = route[i + 1]
            adjusted_route.append(current_coord)
            
            distance = self.calculate_distance(current_coord, next_coord)
            
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
    def convert_kmh(self, speed):
        factor = 3600
        conv_speed = speed / factor
        return conv_speed

    #Function to calculate the distance between 2 coords.
    def calculate_distance(self, coord1, coord2):
        
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
    
    #Function to generate a random location in a given radius.
    def generate_random_location(self):
        bearing = np.radians(np.random.uniform(0, 360))
        distance = np.random.uniform(0, self.radius)

        lat1 = np.radians(self.center_lat)
        lon1 = np.radians(self.center_lon)
        lat2 = np.arcsin(np.sin(lat1) * np.cos(distance / 6371000) +
                        np.cos(lat1) * np.sin(distance / 6371000) * np.cos(bearing))
        lon2 = lon1 + np.arctan2(np.sin(bearing) * np.sin(distance / 6371000) * np.cos(lat1),
                                np.cos(distance / 6371000) - np.sin(lat1) * np.sin(lat2))

        lat2 = np.degrees(lat2)
        lon2 = np.degrees(lon2)
        
        return lat2, lon2
