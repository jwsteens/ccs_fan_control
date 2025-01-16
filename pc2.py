import socket
import serial

ADDRESS = ("192.168.0.22", 8888)
PORT = "COM9"

with socket.create_server(ADDRESS) as socket:
    socket.listen()
    conn, addr = socket.accept()

    print("Client connected:", addr)

    with serial.Serial(PORT, baudrate=9600, timeout=.5) as ser:
        while True:
            try:
                socketData = conn.recv(1024)
                if not socketData:
                    continue

                ser.write(socketData + b"\n")

                ser.reset_input_buffer()
                ser.readline()
                serialData = ser.readline()

                print("")
                print("From socket:", socketData)
                print("From serial:", serialData)

                conn.send(serialData)

            except Exception as e:
                print(e)