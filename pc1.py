import socket
import serial
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json

HOST = "localhost"
COM_PORT = "COM10"

connected = False

def connect_to_server():
    try:
        ip_address = ip_entry.get()
        port = int(port_entry.get())
        serial_port = serial_port_entry.get()
        print(serial_port)
        baudrate = int(baudrate_entry.get())

        def communication_thread():
            try:
                with socket.create_connection((ip_address, port)) as sock:
                    print("Connected to server")
                    with serial.Serial(serial_port, baudrate=baudrate, timeout=0.5) as ser:
                        ip_entry.config(state="disabled")
                        port_entry.config(state="disabled")
                        serial_port_entry.config(state="disabled")
                        baudrate_entry.config(state="disabled")
                        connect_button.config(text="Connected", state="disabled")
                        while True:
                            ser.reset_input_buffer()
                            ser.readline()
                            serial_data = ser.readline()
                            print(serial_data)
                            if serial_data:
                                serial_data_decoded = json.loads(serial_data.decode())
                                # sock.send(serial_data)
                                # print(f"Serial to Server: {serial_data.decode()}")

                                # Update the RPM display field
                                if serial_data_decoded.get("Local"):
                                    setpoint_entry.config(state="disabled")
                                    setpoint_var.set(serial_data_decoded["SP"])
                                else:
                                    setpoint_entry.config(state="normal")
                                    serial_data_decoded["SP"] = float(setpoint_entry.get())
                                
                                sock.send(json.dumps(serial_data_decoded).encode())

                                socket_data = sock.recv(1024)
                                print(socket_data)
                                ser.write(socket_data + b"\n")
                                print(f"Server to Serial: {socket_data.decode()}")


                                rpm_var.set(json.loads(socket_data.decode())["RPM"])

            except Exception as e:
                print(e)
                messagebox.showerror("Connection Error", str(e))

        thread = threading.Thread(target=communication_thread, daemon=True)
        thread.start()

    except ValueError as e:
        messagebox.showerror("Input Error", f"Invalid input: {e}")

# Create the main tkinter window
root = tk.Tk()
root.title("Serial to Socket Communication")

# Create UI elements
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# IP Address
ttk.Label(frame, text="IP Address:").grid(row=0, column=0, sticky=tk.W)
ip_entry = ttk.Entry(frame, width=20)
ip_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
ip_entry.insert(0, HOST)

# Port
ttk.Label(frame, text="Port:").grid(row=1, column=0, sticky=tk.W)
port_entry = ttk.Entry(frame, width=20)
port_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))
port_entry.insert(0, "8888")

# Serial Port
ttk.Label(frame, text="Serial Port:").grid(row=2, column=0, sticky=tk.W)
serial_port_entry = ttk.Entry(frame, width=20)
serial_port_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))
serial_port_entry.insert(0, COM_PORT)

# Baudrate
ttk.Label(frame, text="Baudrate:").grid(row=3, column=0, sticky=tk.W)
baudrate_entry = ttk.Entry(frame, width=20)
baudrate_entry.grid(row=3, column=1, sticky=(tk.W, tk.E))
baudrate_entry.insert(0, "9600")

# Setpoint
ttk.Label(frame, text="Setpoint:").grid(row=4, column=0, sticky=tk.W)
setpoint_var = tk.StringVar()
setpoint_entry = ttk.Entry(frame, width=20)
setpoint_entry.grid(row=4, column=1, sticky=(tk.W, tk.E))
setpoint_entry.configure(textvariable=setpoint_var)
setpoint_entry.insert(0, "0")

# RPM Display
ttk.Label(frame, text="RPM:").grid(row=5, column=0, sticky=tk.W)
rpm_var = tk.StringVar()
rpm_display = ttk.Label(frame, textvariable=rpm_var, relief="sunken", width=20)
rpm_display.grid(row=5, column=1, sticky=(tk.W, tk.E))
rpm_var.set("0")

# Connect Button
connect_button = ttk.Button(frame, text="Connect", command=connect_to_server)
connect_button.grid(row=6, column=0, columnspan=2, pady=10)

# Adjust column weights
frame.columnconfigure(1, weight=1)

# Run the tkinter main loop
root.mainloop()
