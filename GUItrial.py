import PySimpleGUI as sg
import serial
import threading

# Initialize variables
sats = 0
gps_data = {"latitude": "0.0000", "longitude": "0.0000",
            "elevation": "0.0", "satellites": 0}
imu_data = {"gyro_x": "0.0", "gyro_y": "0.0", "gyro_z": "0.0",
            "accel_x": "0.0", "accel_y": "0.0", "accel_z": "0.0",
            "mag_x": "0.0", "mag_y": "0.0", "mag_z": "0.0"}

# Define layout
home = [
    [sg.Button("Start Display", button_color="green"),
     sg.Button("End Session", button_color="red")]
]
dataDisplay = [
    [sg.Button("End Display", button_color="red")],
    [sg.Text("GPS", justification="center", font=('Arial Bold', 20))],
    [sg.Text("Latitude: ", justification="left"),
     sg.Text(gps_data["latitude"], key='latitude')],
    [sg.Text("Longitude: ", justification="left"), sg.Text(
        gps_data["longitude"], key='longitude')],
    [sg.Text("Elevation: ", justification="left"), sg.Text(
        gps_data["elevation"], key='elevation')],
    [sg.Text("Satellites: ", justification="left"),
     sg.Text(gps_data["satellites"], key='sats')],
    [sg.Text("IMU Data", justification="center", font=('Arial Bold', 20))],
    [sg.Text("Gyro X: ", justification="left"),
     sg.Text(imu_data["gyro_x"], key='gyro_x')],
    [sg.Text("Gyro Y: ", justification="left"),
     sg.Text(imu_data["gyro_y"], key='gyro_y')],
    [sg.Text("Gyro Z: ", justification="left"),
     sg.Text(imu_data["gyro_z"], key='gyro_z')],
    [sg.Text("Accel X: ", justification="left"),
     sg.Text(imu_data["accel_x"], key='accel_x')],
    [sg.Text("Accel Y: ", justification="left"),
     sg.Text(imu_data["accel_y"], key='accel_y')],
    [sg.Text("Accel Z: ", justification="left"),
     sg.Text(imu_data["accel_z"], key='accel_z')],
    [sg.Text("Mag X: ", justification="left"),
     sg.Text(imu_data["mag_x"], key='mag_x')],
    [sg.Text("Mag Y: ", justification="left"),
     sg.Text(imu_data["mag_y"], key='mag_y')],
    [sg.Text("Mag Z: ", justification="left"),
     sg.Text(imu_data["mag_z"], key='mag_z')]
]

layout = [
    [sg.Column(home, key='-COL1-'),
     sg.Column(dataDisplay, visible=False, key='-COL2-')]
]

# Create window
window = sg.Window("Serial Display GUI", layout, margins=(200, 100))

# Serial Communication Setup (simulating for now)


def read_data_from_serial(serial_port):
    global sats  # Ensure we modify the global 'sats' variable

    while True:
        # Simulate receiving GPS and IMU data via serial (replace with actual reading from serial port)
        data = serial_port.readline().decode('utf-8').strip()
        if data:
            print(f"Received data: {data}")  # Print data for debugging

            try:
                # Split the data into parts (assuming CSV format: lat, lon, elev, sats, gyro_x, gyro_y, ...)
                parsed_data = data.split(',')

                # Update GPS data
                gps_data["latitude"] = parsed_data[0]
                gps_data["longitude"] = parsed_data[1]
                gps_data["elevation"] = parsed_data[2]
                gps_data["satellites"] = parsed_data[3]
                window['latitude'].update(gps_data["latitude"])
                window['longitude'].update(gps_data["longitude"])
                window['elevation'].update(gps_data["elevation"])
                window['sats'].update(gps_data["satellites"])

                # Update IMU data
                imu_data["gyro_x"] = parsed_data[4]
                imu_data["gyro_y"] = parsed_data[5]
                imu_data["gyro_z"] = parsed_data[6]
                imu_data["accel_x"] = parsed_data[7]
                imu_data["accel_y"] = parsed_data[8]
                imu_data["accel_z"] = parsed_data[9]
                imu_data["mag_x"] = parsed_data[10]
                imu_data["mag_y"] = parsed_data[11]
                imu_data["mag_z"] = parsed_data[12]

                # Update IMU fields in the GUI
                window['gyro_x'].update(imu_data["gyro_x"])
                window['gyro_y'].update(imu_data["gyro_y"])
                window['gyro_z'].update(imu_data["gyro_z"])
                window['accel_x'].update(imu_data["accel_x"])
                window['accel_y'].update(imu_data["accel_y"])
                window['accel_z'].update(imu_data["accel_z"])
                window['mag_x'].update(imu_data["mag_x"])
                window['mag_y'].update(imu_data["mag_y"])
                window['mag_z'].update(imu_data["mag_z"])

                # Only update satellite count if valid GPS data is received
                # Ensure the satellite data is valid (numeric)
                if gps_data["satellites"].isdigit():
                    sats = int(gps_data["satellites"])

            except Exception as e:
                print(f"Error processing data: {e}")

        else:
            print("No data received...")

# Thread to handle serial reading without blocking the GUI


def start_serial_reading(serial_port):
    threading.Thread(target=read_data_from_serial,
                     args=(serial_port,), daemon=True).start()


# Main loop
layout_state = 1  # Initially show the home screen

while True:
    # 500ms timeout for periodic updates
    event, values = window.read(timeout=500)

    # If window is closed or 'End Session' is clicked
    if event in (None, 'End Session'):
        break

    if event == 'Start Display':
        # Hide current column
        window[f'-COL{layout_state}-'].update(visible=False)
        layout_state = 2  # Switch to data display column
        # Show data display
        window[f'-COL{layout_state}-'].update(visible=True)

        # Start serial reading in a separate thread
        try:
            # Adjust to your serial port
            serial_port = serial.Serial('COM3', baudrate=9600, timeout=1)
            start_serial_reading(serial_port)
        except Exception as e:
            sg.popup_error(f"Failed to connect to serial port: {e}")

    if event == 'End Display':
        window[f'-COL{layout_state}-'].update(visible=False)
        layout_state = 1
        window[f'-COL{layout_state}-'].update(visible=True)

    # Handle timeout event (data update)
    if event == sg.TIMEOUT_EVENT:
        # The timeout event doesn't do anything unless valid GPS data is received
        pass

# Clean up
window.close()
