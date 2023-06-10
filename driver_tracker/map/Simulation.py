
import polyline
import googlemaps
import time
import random
import threading
import math
import numpy as np
from .driver_thread import Driver_Thread, sio
import asyncio
from multiprocessing import Process
from .variables import arabic_male_names
from utils.mongo_connection import drivers_collection

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
        self.states = ['busy', 'available', 'not_available']
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
        for i in range(1, self.drivers_num+1):
            driver_num = "driver{}_marker".format(i)
            
            driver_thread_num = "driver{}_thread".format(i)

            driver = self.generate_random_location()
            driver_val, driver_thread_val = self.driver_state(driver, i)
            
            self.drivers.append((driver_num, driver_val))
            self.drivers_threads[driver_thread_num] = driver_thread_val
        return {"success": "drivers created successfully"}

    #Driver movment before order selection function.
    def driver_state(self, driver, num):
        gen_states = random.choice(self.states)
        destination = self.generate_random_location()
        route = self.create_route(driver, None, destination)
        driver_name = self.generate_random_name()
        driver_obj =  self.create_driver_db(
            driver_name,
            gen_states,
            driver[0],
            driver[1],
            num
            )

        if gen_states in self.states:
            process_1 = Process(target=self.sio_emit, args=("setBusyDriver", driver_obj))
            process_1.start()
            process_2 = Process(target=self.run_random_driver, args=(route, num))
            process_2.start()
            return driver, None

        elif gen_states == self.states[1]:
            process = Process(target=self.sio_emit, args=("UpdateActiveDriverLocation", driver_obj))
            process.start()
            return driver, None
        
        elif gen_states == self.states[2]:
            process = Process(target=self.sio_emit, args=("setNotAvailableDriver", driver_obj))
            process.start()
            return driver, None
        
    def run_random_driver(self, route, driver_number):
        self.update_driver_status("busy")
        for j in range(1, len(route)-1):  
            driver_num = str(driver_number) 
            location = route[j + 1]
            process = Process(target=self.sio_emit, args=("updateBusyDriver",{driver_num:location}))
            process.start()
            time.sleep(self.speed)
        self.update_driver_location(driver_num, location[0], location[1])

    def create_driver_db(self, name, status, lat, lng, num):
        driver_obj = {
            "name": name,
            "number": num,
            "status": status,
            "lat": lat,
            "lng": lng
        }
        result = drivers_collection.insert_one(driver_obj)
        return driver_obj
    def update_driver_location(self, num, lat, lng):
        updated_data = {
            "lat": lat,
            "lng": lng
        }
        drivers_collection.update_one({"number": num}, {'$set': updated_data})

    def update_driver_status(self, num, status):
        drivers_collection.update_one({"number": num}, {'$set': {"status": status}})
    
    def sio_emit(self, event, args):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async_result = loop.run_until_complete(sio.emit(event, args))
        print("async_result = ", async_result)


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

    def generate_random_name(self):
        first_name = random.choice(arabic_male_names)
        last_name = random.choice(arabic_male_names)
        return first_name + ' ' + last_name