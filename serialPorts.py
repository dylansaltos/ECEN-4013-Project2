import serial.tools.list_ports

# List all available serial ports
ports = serial.tools.list_ports.comports()

if not ports:
    print("No serial ports found.")
else:
    print("Available serial ports:")
    for port in ports:
        # This will print the port name, like COM3, COM4, etc.
        print(port.device)
