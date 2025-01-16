import asyncio
import json
from time import ticks_ms
import pico_functions_v1_1 as pf # type: ignore
from fan_assignment_classes import Potmeter, Uart # type: ignore
from machine import Pin

potmeter = Potmeter(28)
responsibility = Pin(16, Pin.IN, Pin.PULL_DOWN)
led = Pin(17, Pin.OUT)
led.on()
responsibility_ticks = 0
screen = pf.display_init(ID=1, sda_pin=10, scl_pin=11)
uart = Uart()
local = True

def display_values():
    screen.fill(0)
    screen.rotate(True)
    try:
        screen.text("Local" if local else "Remote", 0, 45)
        if local:
            pf.hor_level_indicator(potmeter.percentage, 0, 0, 64, 8, 'bar', screen)
            screen.text(f"{round(potmeter.percentage * 100, 1)}%", 0, 15)
        screen.text(f"{uart.data['RPM']} RPM", 0, 30) if uart.data['RPM'] is not None else screen.text("NO DATA", 0, 30)
        
    except Exception as e:
        print(e)

    screen.show()



def send_setpoint():
    uart.uart.write(json.dumps({ "SP": potmeter.percentage, "Local": local }).encode() + b"\n")




async def main():
    potmeter.start()
    uart.start()

    while True:
        send_setpoint()
        display_values()
        await asyncio.sleep(.1)

def responsibility_toggle(t):
    global local, responsibility_ticks
    if ticks_ms() < responsibility_ticks + 100:
        return

    local = not local
    led.toggle()

responsibility.irq(responsibility_toggle, Pin.IRQ_RISING)

asyncio.run(main())