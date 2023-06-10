
import React, { useState, useEffect } from "react";
import { Marker } from "react-google-maps";
import { get_restaurants } from "../api/getResturent";
import { get_orders } from "../api/getOrdres";
import { get_drivers } from "../api/getDrivers";
import DriverIconRed  from "../icons/driverRed.png";
import DriverIconOrange  from "../icons/driverOrange.png";
import DriverIconGreen  from "../icons/driverGreen.png";
import { Icon } from "@mui/material";

  
export default function Markers({setSelectedMarker, socket}) {
    const [Orders, setOrders] = useState([]);
    const [Restaurants, setRestaurants] = useState([]);
    const [Drivers, setDrivers] = useState({});
    const [ActiveDrivers, setActiveDrivers] = useState({});
    const [BusyDrivers, setBusyDrivers] = useState({});
    const [NotAvailableDrivers, setNotAvailableDrivers] = useState({});



    function getDriversMarkers(obj, DriverIcon){
      const DriversMarkersArray = [];
      Object.keys(obj).forEach(function(key, index) {
        const driver = obj[key];
        DriversMarkersArray.push(
          <Marker
            key={key}
            position={{
              lat: driver.lat,
              lng: driver.lng
            }}
            onClick={() => {
              setSelectedMarker(driver);
            }}
            icon={{
              url: DriverIcon,
              scaledSize: new window.google.maps.Size(30, 30)
            }}
          />
        )
      })
      return DriversMarkersArray
    }


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

      socket.on('setBusyDriver', (BusyDriver) => {
        console.log("setBusyDriver > ", BusyDriver);
        setBusyDrivers(Driver => ({
          ...Driver,
          ...BusyDriver
        }));
      });

      socket.on('setNotAvailableDriver', (NotAvailableDriver) => {
        console.log("setNotAvailableDriver > ", NotAvailableDriver);
        setNotAvailableDrivers(Driver => ({
          ...Driver,
          ...NotAvailableDriver
        }));
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
        {
        Object.keys(BusyDrivers).length > 0 ? 
        (getDriversMarkers(BusyDrivers, DriverIconOrange))
        :
        ('')
        }
        {
        Object.keys(ActiveDrivers).length > 0 ? 
        (getDriversMarkers(ActiveDrivers, DriverIconRed))
        :
        ('')
        }
        {
        Object.keys(NotAvailableDrivers).length > 0 ? 
        (getDriversMarkers(NotAvailableDrivers, DriverIconRed))
        :
        ('')
        }
      </>
    );
  }

  // {ActiveDrivers.map(driver => (
  //   <Marker
  //     key={driver.number}
  //     position={{
  //       lat: driver.lat,
  //       lng: driver.lng
  //     }}
  //     onClick={() => {
  //       setSelectedMarker(driver);
  //     }}
  //     icon={{
  //       url:  "https://img.icons8.com/fluency/48/delivery-scooter.png",
  //       scaledSize: new window.google.maps.Size(30, 30)
  //     }}
  //   />
  // ))}