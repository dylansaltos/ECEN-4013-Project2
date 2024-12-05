import PySimpleGUI as sg
import serial
import threading
import time

# Serial communication setup (update the port as needed)
serial_port = serial.Serial("COM5", baudrate=9600, timeout=1)

# Function to read data from the serial port


def read_data_from_serial(serial_port):
    global gps_data, imu_data

    while True:
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
                window['elevation2'].update(gps_data["elevation"])
                window['sats2'].update(gps_data["satellites"])

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

            except Exception as e:
                print(f"Error parsing data: {e}")


# Start a thread for reading data from the serial port
def serial_thread():
    read_data_from_serial(serial_port)


# Start the serial reading thread
thread = threading.Thread(target=serial_thread, daemon=True)
thread.start()

# Initialize variables
sats = 0
gps_data = {"latitude": "0.0000", "longitude": "0.0000",
            "elevation": "0.0", "satellites": 0}
imu_data = {
    "gyro_x": "0.0", "gyro_y": "0.0", "gyro_z": "0.0", "accel_x": "0.0",
    "accel_y": "0.0", "accel_z": "0.0", "mag_x": "0.0", "mag_y": "0.0", "mag_z": "0.0"
}

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
                font=('Helvetica', 30), background_color="silver", text_color="white")

# GPS Data (left and right columns)
gps_left = [
    [sg.Frame("",  # No label for the frame
              [[sg.Text("Latitude:", size=(10, 1), font=('Helvetica', 10), background_color="grey", text_color="white")],
               [sg.Text(gps_data["latitude"], key='latitude', size=(12, 1), font=('Helvetica', 10), background_color="grey", text_color="white")]],
              background_color="grey", border_width=2, relief=sg.RELIEF_FLAT, element_justification="left")],

    # Spacer row for more space
    [sg.Text("", size=(1, 1), background_color="black")],

    [sg.Frame("",  # No label for the frame around Longitude
              [[sg.Text("Longitude:", size=(10, 1), font=('Helvetica', 10), background_color="grey", text_color="white")],
               [sg.Text(gps_data["longitude"], key='longitude', size=(12, 1), font=('Helvetica', 10), background_color="grey", text_color="white")]],
              # Orange frame for Longitude
              background_color="grey", border_width=2, relief=sg.RELIEF_FLAT, element_justification="left")]
]

gps_right = [
    # Frame for Elevation with blue background and reduced width
    [sg.Frame("",  # No label for the frame
              [[sg.Text("Elevation (m):", size=(10, 1), font=('Helvetica', 10), background_color="grey", text_color="white")],
               [sg.Text(gps_data["elevation"], key='elevation2', size=(12, 1), font=('Helvetica', 10), background_color="grey", text_color="white")]],
              background_color="grey", border_width=2, relief=sg.RELIEF_FLAT, element_justification="left")],

    # Spacer row to add space between Elevation and Satellites
    [sg.Text("", size=(1, 1), background_color="black")],

    # Frame for Satellites with green background and reduced width
    [sg.Frame("",  # No label for the frame
              [[sg.Text("Satellites:", size=(10, 1), font=('Helvetica', 10), background_color="grey", text_color="white")],
               [sg.Text(gps_data["satellites"], key='sats2', size=(12, 1), font=('Helvetica', 10), background_color="grey", text_color="white")]],
              background_color="grey", border_width=2, relief=sg.RELIEF_FLAT, element_justification="left")]
]


# IMU Data below the timer (labels directly above the values)
imu_data_display = [
    [sg.Text("Group 6", justification="center", font=('Arial Bold', 18), size=(
        40, 1), relief=sg.RELIEF_SUNKEN, background_color="black", text_color="white")],

    # Gyro data with labels directly above the values
    [sg.Text("Gyro X (rad/s):", size=(15, 1), font=('Helvetica', 12), background_color="black", text_color="white"),
     sg.Text(imu_data["gyro_x"], key='gyro_x', size=(12, 1), font=('Helvetica', 12), background_color="black", text_color="white")],
    [sg.Text("Gyro Y (rad/s):", size=(15, 1), font=('Helvetica', 12), background_color="black", text_color="white"),
     sg.Text(imu_data["gyro_y"], key='gyro_y', size=(12, 1), font=('Helvetica', 12), background_color="black", text_color="white")],
    [sg.Text("Gyro Z (rad/s):", size=(15, 1), font=('Helvetica', 12), background_color="black", text_color="white"),
     sg.Text(imu_data["gyro_z"], key='gyro_z', size=(12, 1), font=('Helvetica', 12), background_color="black", text_color="white")],

    # Acceleration data
    [sg.Text("Accel X (m/s²):", size=(15, 1), font=('Helvetica', 12), background_color="black", text_color="white"),
     sg.Text(imu_data["accel_x"], key='accel_x', size=(12, 1), font=('Helvetica', 12), background_color="black", text_color="white")],
    [sg.Text("Accel Y (m/s²):", size=(15, 1), font=('Helvetica', 12), background_color="black", text_color="white"),
     sg.Text(imu_data["accel_y"], key='accel_y', size=(12, 1), font=('Helvetica', 12), background_color="black", text_color="white")],
    [sg.Text("Accel Z (m/s²):", size=(15, 1), font=('Helvetica', 12), background_color="black", text_color="white"),
     sg.Text(imu_data["accel_z"], key='accel_z', size=(12, 1), font=('Helvetica', 12), background_color="black", text_color="white")],

    # Magnetometer data
    [sg.Text("Mag X (μT):", size=(15, 1), font=('Helvetica', 12), background_color="black", text_color="white"), sg.Text(
        imu_data["mag_x"], key='mag_x', size=(12, 1), font=('Helvetica', 12), background_color="black", text_color="white")],
    [sg.Text("Mag Y (μT):", size=(15, 1), font=('Helvetica', 12), background_color="black", text_color="white"), sg.Text(
        imu_data["mag_y"], key='mag_y', size=(12, 1), font=('Helvetica', 12), background_color="black", text_color="white")],
    [sg.Text("Mag Z (μT):", size=(15, 1), font=('Helvetica', 12), background_color="black", text_color="white"), sg.Text(
        imu_data["mag_z"], key='mag_z', size=(12, 1), font=('Helvetica', 12), background_color="black", text_color="white")]
]

# Layout
layout = [
    # Top Row: Timer in the center
    [sg.Text("", size=(2, 1), justification="center", font=(
        'Helvetica', 20), background_color="silver", text_color="white")],

    # Center: Timer centered
    [sg.Column([[timer]], element_justification="center",
               justification="center", vertical_alignment="center")],

    # Bottom Row: IMU Data inside a black rounded box
    [
        sg.Frame("IMU Data", imu_data_display, background_color="black", border_width=2, relief=sg.RELIEF_FLAT, font=(
            "Helvetica", 12), element_justification="center", expand_x=True, expand_y=True)
    ],

    # Bottom Row: GPS Data Left and Right inside a black rounded box (now moved under IMU Data)
    [
        sg.Frame("GPS Data", [[sg.Column(gps_left, background_color="black"), sg.Text("   "), sg.Column(gps_right, background_color="black")]],
                 background_color="black", border_width=2, relief=sg.RELIEF_FLAT, font=("Helvetica", 12), element_justification="center", expand_x=True, expand_y=True)
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
