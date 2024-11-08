import PySimpleGUI as sg
import serial
import threading
import time

# Initialize variables
sats = 0
gps_data = {"latitude": "0.0000", "longitude": "0.0000",
            "elevation": "0.0", "satellites": 0}
imu_data = {"gyro_x": "0.0", "gyro_y": "0.0", "gyro_z": "0.0",
            "accel_x": "0.0", "accel_y": "0.0", "accel_z": "0.0",
            "mag_x": "0.0", "mag_y": "0.0", "mag_z": "0.0"}

# Timer state
start_time = 0
running = False

# Define layout with background colors and sections
home = [
    [sg.Button("Start Display", button_color=("white", "green"), size=(15, 2), font=('Helvetica', 14)),
     sg.Button("End Session", button_color=("white", "red"), size=(15, 2), font=('Helvetica', 14))]
]

# Timer element (centered)
timer = sg.Text("00:00", size=(10, 1), justification="center",
                font=('Helvetica', 30), background_color="silver")

# GPS Data (left and right columns)
gps_left = [
    [sg.Text("Latitude:", size=(15, 1), font=('Helvetica', 12)), sg.Text(
        gps_data["latitude"], key='latitude', size=(12, 1), font=('Helvetica', 12))],
    [sg.Text("Longitude:", size=(15, 1), font=('Helvetica', 12)), sg.Text(
        gps_data["longitude"], key='longitude', size=(12, 1), font=('Helvetica', 12))],
    [sg.Text("Elevation (m):", size=(15, 1), font=('Helvetica', 12)), sg.Text(
        gps_data["elevation"], key='elevation', size=(12, 1), font=('Helvetica', 12))],
    [sg.Text("Satellites:", size=(15, 1), font=('Helvetica', 12)), sg.Text(
        gps_data["satellites"], key='sats', size=(12, 1), font=('Helvetica', 12))],
]

gps_right = [
    [sg.Text("Latitude:", size=(15, 1), font=('Helvetica', 12)), sg.Text(
        gps_data["latitude"], key='latitude2', size=(12, 1), font=('Helvetica', 12))],
    [sg.Text("Longitude:", size=(15, 1), font=('Helvetica', 12)), sg.Text(
        gps_data["longitude"], key='longitude2', size=(12, 1), font=('Helvetica', 12))],
    [sg.Text("Elevation (m):", size=(15, 1), font=('Helvetica', 12)), sg.Text(
        gps_data["elevation"], key='elevation2', size=(12, 1), font=('Helvetica', 12))],
    [sg.Text("Satellites:", size=(15, 1), font=('Helvetica', 12)), sg.Text(
        gps_data["satellites"], key='sats2', size=(12, 1), font=('Helvetica', 12))],
]

# IMU Data below the timer (labels directly above the values)
imu_data_display = [
    [sg.Text("IMU Data", justification="center", font=('Arial Bold', 18), size=(
        20, 1), relief=sg.RELIEF_SUNKEN, background_color="lightgreen")],

    # Gyro data with labels directly above the values
    [sg.Text("Gyro X (rad/s):", size=(15, 1), font=('Helvetica', 12)),
     sg.Text(imu_data["gyro_x"], key='gyro_x', size=(12, 1), font=('Helvetica', 12))],
    [sg.Text("Gyro Y (rad/s):", size=(15, 1), font=('Helvetica', 12)),
     sg.Text(imu_data["gyro_y"], key='gyro_y', size=(12, 1), font=('Helvetica', 12))],
    [sg.Text("Gyro Z (rad/s):", size=(15, 1), font=('Helvetica', 12)),
     sg.Text(imu_data["gyro_z"], key='gyro_z', size=(12, 1), font=('Helvetica', 12))],

    # Acceleration data
    [sg.Text("Accel X (m/s²):", size=(15, 1), font=('Helvetica', 12)),
     sg.Text(imu_data["accel_x"], key='accel_x', size=(12, 1), font=('Helvetica', 12))],
    [sg.Text("Accel Y (m/s²):", size=(15, 1), font=('Helvetica', 12)),
     sg.Text(imu_data["accel_y"], key='accel_y', size=(12, 1), font=('Helvetica', 12))],
    [sg.Text("Accel Z (m/s²):", size=(15, 1), font=('Helvetica', 12)),
     sg.Text(imu_data["accel_z"], key='accel_z', size=(12, 1), font=('Helvetica', 12))],

    # Magnetometer data
    [sg.Text("Mag X (μT):", size=(15, 1), font=('Helvetica', 12)),
     sg.Text(imu_data["mag_x"], key='mag_x', size=(12, 1), font=('Helvetica', 12))],
    [sg.Text("Mag Y (μT):", size=(15, 1), font=('Helvetica', 12)),
     sg.Text(imu_data["mag_y"], key='mag_y', size=(12, 1), font=('Helvetica', 12))],
    [sg.Text("Mag Z (μT):", size=(15, 1), font=('Helvetica', 12)),
     sg.Text(imu_data["mag_z"], key='mag_z', size=(12, 1), font=('Helvetica', 12))],
]

# Layout
layout = [
    # Top Row: Timer in the center
    [sg.Text("", size=(2, 1), justification="center",
             font=('Helvetica', 20), background_color="silver")],

    # Center: Timer centered
    [sg.Column([[timer]], element_justification="center",
               justification="center", vertical_alignment="center")],

    # Bottom Row: IMU Data inside a black rounded box
    [
        sg.Frame("IMU Data",
                 imu_data_display,
                 background_color="black", border_width=2, relief=sg.RELIEF_FLAT,
                 font=("Helvetica", 12), element_justification="center",
                 expand_x=True, expand_y=True)
    ],

    # Bottom Row: GPS Data Left and Right inside a black rounded box (now moved under IMU Data)
    [
        sg.Frame("GPS Data",
                 [[sg.Column(gps_left, background_color="lightblue"),
                   sg.Text("   "),  # Spacer between columns
                   sg.Column(gps_right, background_color="lightblue")]],
                 background_color="black", border_width=2, relief=sg.RELIEF_FLAT,
                 font=("Helvetica", 12), element_justification="center",
                 expand_x=True, expand_y=True)
    ],

    # Bottom Row: End Session Button
    [sg.Button("End Session", button_color=("white", "red"),
               size=(15, 2), font=('Helvetica', 14))]
]

# Create window with silver background for the main window
window = sg.Window("Serial Display GUI", layout, margins=(
    30, 30), background_color="silver", finalize=True)

# Function to update the timer


def update_timer():
    global start_time, running
    if running:
        # Get elapsed time in seconds
        elapsed_time = int(time.time() - start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        formatted_time = f"{minutes:02}:{seconds:02}"
        window['timer'].update(formatted_time)
        window.after(1000, update_timer)

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

            except Exception as e:
                print(f"Error parsing data: {e}")


# Event Loop
while True:
    event, values = window.read(timeout=100)

    if event == sg.WINDOW_CLOSED:
        break

    elif event == "Start Display":
        # Start the timer when the button is clicked
        start_time = time.time()  # Record the start time
        running = True  # Start the timer running
        update_timer()  # Begin updating the timer

    elif event == "End Session":
        # Stop the session
        running = False
        break

window.close()
