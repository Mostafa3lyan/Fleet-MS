
import React, { useState, useEffect } from "react";
import Button from '@mui/material/Button';
import {
    withScriptjs,
    withGoogleMap,
    GoogleMap,
    InfoWindow,
    Polyline
  } from "react-google-maps";
import Markers from "../components/Markers";
import SimDialog from "../components/SimModal";
import { io } from 'socket.io-client';

const socket = io(process.env.REACT_APP_SOCKET_URL, {
  path: process.env.REACT_APP_SOCKET_PATH
});
  
  function Map() {
    const [selectedMarker, setSelectedMarker] = useState(null);
    useEffect(() => {

      function onConnect() {
        console.log("onConnect");
      }
  
      function onDisconnect() {
        console.log("onDisconnect");
      }
  
      socket.on('connect', onConnect);
      socket.on('disconnect', onDisconnect);


      const listener = e => {
        if (e.key === "Escape") {
          setSelectedMarker(null);
        }
      };

      window.addEventListener("keydown", listener);
      return () => {
        window.removeEventListener("keydown", listener);
      };
    }, []);
  

    return (
      <GoogleMap
        defaultZoom={13}
        defaultCenter={{ lat: 30.1491, lng: 31.6290}}
        onClick={ev => {
          console.log("latitide = ",  ev.latLng.lat());
          console.log("longitude = ", ev.latLng.lng());
        }}
      >
        <Markers 
        setSelectedMarker={setSelectedMarker}
        socket={socket}
        />
        {selectedMarker && (
          <InfoWindow
            onCloseClick={() => {
              setSelectedMarker(null);
            }}
            position={{
              lat: selectedMarker.lat,
              lng: selectedMarker.lng
            }}
          >
            <div>
              <h2>{selectedMarker.name}</h2>
              <p>{selectedMarker.details}</p>
            </div>
          </InfoWindow>
        )}

      </GoogleMap>
      
    );
  }
  
  const MapWrapped = withScriptjs(withGoogleMap(Map));
  
  export default function MainMap() {

    function assignOrderHandler(){
      console.log("Assigning order handler clicked");
      socket.emit('assign_order')        
    }

    return (
      <div>
      <SimDialog socket={socket}/>
      <Button
      onClick={assignOrderHandler}
      >
        Assign Order
      </Button>
      <div style={{ width: "97vw", height: "100vh" }}>
        <MapWrapped
          googleMapURL={`https://maps.googleapis.com/maps/api/js?key=AIzaSyAv4TshMqyQUcBc_oWM6w9hjlxIKqiUOvA&v=3.exp&libraries=geometry,drawing,places}`}
          loadingElement={<div style={{ height: `80%` }} />}
          containerElement={<div style={{ height: `80%` }} />}
          mapElement={<div style={{ height: `80%` }} />}
        />
      </div>
      </div>
    
      );
}
  