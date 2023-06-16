import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Switch from '@mui/material/Switch';
import TextField from '@mui/material/TextField';
import { startSimulation } from '../api/Simulation';
import FormattedInputs from './IntInput';


export default function SimDialog({socket}) {
  const [open, setOpen] = React.useState(false);
  const [fullWidth, setFullWidth] = React.useState(true);
  const [maxWidth, setMaxWidth] = React.useState('sm');
  const [Speed, setSpeed] = React.useState('R');

  const handleClickOpen = () => {
    socket.emit('print_message', "hello from socket" ,(result) => {
      console.log("result", result)
    });
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleSubmit = () => {
    setOpen(false);
    const speed = document.getElementById("sim-speed").value
    const drivers_number = document.getElementById("formatted-numberformat-input").value
    startSimulation(speed, drivers_number).then((res)=> {
      console.log(res);
    })
  };

  const handleSpeedChange = (event) => {
    setSpeed(
      event.target.value,
    );
  };

  const handleFullWidthChange = (event) => {
    setFullWidth(event.target.checked);
  };

  return (
    <React.Fragment>
      <Button onClick={handleClickOpen}>
        start simulation
      </Button>
      <Dialog
        fullWidth={fullWidth}
        maxWidth={maxWidth}
        open={open}
        onClose={handleClose}
      >
        <DialogTitle>Simulation Options</DialogTitle>
        <DialogContent>
          <Box
            noValidate
            component="form"
            sx={{
              display: 'flex',
              flexDirection: 'column',
              m: 'auto',
              width: 'fit-content',
            }}
          >
            <FormControl sx={{ mt: 2, minWidth: 120 }}>
              <InputLabel htmlFor="max-width">Drivers speed</InputLabel>
              <Select
                autoFocus
                value={Speed}
                onChange={handleSpeedChange}
                label="speed"
                inputProps={{
                  name: 'sim-speed',
                  id: 'sim-speed',
                }}
              >
                <MenuItem value="F">Fast</MenuItem>
                <MenuItem value="R">Real</MenuItem>
                <MenuItem value="S">Slow</MenuItem>

              </Select>
              <FormattedInputs/>

            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleSubmit}>Submit</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}