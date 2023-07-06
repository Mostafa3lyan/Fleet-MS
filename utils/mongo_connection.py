import pymongo
MONGO_DETAILS = 'mongodb+srv://ahmed:2233@fleetmanagementsystem.5xv0klr.mongodb.net/test'

client = pymongo.MongoClient('mongodb+srv://ahmed:2233@fleetmanagementsystem.5xv0klr.mongodb.net/test')
dbname = client['FleetManagementSystem']


orders_collection = dbname.get_collection("orders")
restaurant_collection = dbname.get_collection("restaurants")
drivers_collection = dbname.get_collection("drivers")
sim_collection = dbname.get_collection("simulation")
