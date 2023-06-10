
import React, { useState, useEffect } from "react";
import { Marker } from "react-google-maps";
import { get_restaurants } from "../api/getResturent";
import { get_orders } from "../api/getOrdres";
import { get_drivers } from "../api/getDrivers";

  
export default function Markers({setSelectedMarker, socket}) {
    const [Orders, setOrders] = useState([]);
    const [Restaurants, setRestaurants] = useState([]);
    const [Drivers, setDrivers] = useState([]);
    const [ActiveDrivers, setActiveDrivers] = useState({});


    useEffect(() => {

      get_orders().then(res =>{
        setOrders(res.orders);
      })

      get_restaurants().then(res =>{
        setRestaurants(res.restaurants);
      })

      get_drivers().then(res =>{
        setDrivers(res.drivers);
      })



      socket.on('UpdateActiveDriverLocation', (ActiveDriver) => {
        console.log("UpdateActiveDriverLocation > ", ActiveDriver);
        setActiveDrivers(Driver => ({
          ...Driver,
          ...ActiveDriver
        }));
      });

      socket.on('setBusyDriver', (ActiveDriver) => {
        console.log("setBusyDriver > ", ActiveDriver);

      });

      socket.on('setNotAvailableDriver', (ActiveDriver) => {
        console.log("setNotAvailableDriver > ", ActiveDriver);

      });

    }, []);
  

    return (
      <>
        {Restaurants.map(restaurant => (
          <Marker
            key={restaurant._id.$oid}
            position={{
              lat: restaurant.lat,
              lng: restaurant.lng
            }}
            onClick={() => {

              setSelectedMarker(restaurant);
            }}
            icon={{
              url:  "https://static.slickdealscdn.com/attachment/1/8/6/3/2/3/2/9853645.attach",
              scaledSize: new window.google.maps.Size(40, 22)
            }}
          />
        ))
        }
        {Orders.map(order => (
          <Marker
            key={order._id.$oid}
            position={{
              lat: order.lat,
              lng: order.lng
            }}
            onClick={() => {
              setSelectedMarker(order);
            }}
            icon={{
              url:  "https://img.icons8.com/cotton/64/take-away-food.png",
              scaledSize: new window.google.maps.Size(30, 30)
            }}
          />
        ))}

        {Drivers.map(driver => (
          <Marker
            key={driver._id.$oid}
            position={{
              lat: driver.lat,
              lng: driver.lng
            }}
            onClick={() => {
              setSelectedMarker(driver);
            }}
            icon={{
              url:  "https://img.icons8.com/fluency/48/delivery-scooter.png",
              scaledSize: new window.google.maps.Size(30, 30)
            }}
          />
        ))}
      </>
    );
  }
