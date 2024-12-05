import PySimpleGUI as sg
import serial
import time

# Serial connection settings (adjust the port to your Teensyduino serial port)
# Update to your actual port (e.g., COMx for Windows)
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

# Create a serial connection to the Teensyduino GPS


def get_gps_data():
    try:
        # Open serial connection to Teensyduino
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        while True:
            if ser.in_waiting > 0:
                # Read and return the incoming serial data
                gps_data = ser.readline().decode('utf-8').strip()
                return gps_data
    except Exception as e:
        print(f"Error reading GPS data: {e}")
        return "Error: Unable to read GPS data"


# PySimpleGUI layout
layout = [
    [sg.Text("GPS Data Viewer", font=("Helvetica", 16))],
    [sg.Text("Latitude:", size=(15, 1)), sg.Text(
        "", size=(20, 1), key="LATITUDE")],
    [sg.Text("Longitude:", size=(15, 1)), sg.Text(
        "", size=(20, 1), key="LONGITUDE")],
    [sg.Text("Altitude (m):", size=(15, 1)), sg.Text(
        "", size=(20, 1), key="ALTITUDE")],
    [sg.Text("Time:", size=(15, 1)), sg.Text("", size=(20, 1), key="TIME")],
    [sg.Button("Exit")]
]

# Create the window
window = sg.Window("GPS Data", layout, finalize=True)

# Main event loop to update the GUI with GPS data
while True:
    event, values = window.read(timeout=1000)  # Update every second

    if event == sg.WIN_CLOSED or event == "Exit":
        break

    # Get GPS data from the serial port
    gps_data = get_gps_data()

    if gps_data.startswith('$GPGGA'):
        # Parse the GPS data (simplified for GGA format, you can extend this for other types)
        try:
            fields = gps_data.split(',')

            # Extract relevant GPS information (GGA format)
            latitude = fields[2]
            longitude = fields[4]
            altitude = fields[9]
            time = fields[1]

            # Update the GUI elements with the GPS data
            window['LATITUDE'].update(latitude)
            window['LONGITUDE'].update(longitude)
            window['ALTITUDE'].update(altitude)
            window['TIME'].update(time)
        except IndexError:
            print("Error: Invalid GPS data format.")

window.close()
