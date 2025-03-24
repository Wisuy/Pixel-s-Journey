import pygame
import serial
import serial.tools.list_ports

with open("./port.txt", "r") as f:
    port = f.readline()
try:
    print(port)
    serial_port = serial.Serial(port, 9600, timeout=0.1)
except:
    serial_port = None

def arduino_controller():
    control = {
        "JUMP": False,
        "LEFT": False,
        "RIGHT": False
    }
    while serial_port.in_waiting > 0:
        key = serial_port.readline().decode().strip()
        

        if key == "JUMP":
            control["JUMP"] = True
        if key == "LEFT":
            control["LEFT"] = True
        if key == "RIGHT":
            control["RIGHT"] = True
    
    return control



def keyboard_controller():
    control = {
        "JUMP": False,
        "LEFT": False,
        "RIGHT": False
    }
    key = pygame.key.get_pressed()
    if key[pygame.K_SPACE]:
        control["JUMP"] = True
    if key[pygame.K_LEFT]:
        control["LEFT"] = True
    if key[pygame.K_RIGHT]:
        control["RIGHT"] = True

    return control

def select_controller():
    """
    If arduino is connected, the controller will be set to arduino_controller, otherwise default to keyboard_controller
    """
    arduino_port = None
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in port.description or "CH340" in port.description:
            arduino_port = port.device
            break

    if arduino_port and serial_port:
        return "arduino"
    else:
        return "keyboard"
        

def controller(device):
    if device == "arduino":
        return arduino_controller()
    else:
        return keyboard_controller()
