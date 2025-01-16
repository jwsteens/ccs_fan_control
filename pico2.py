import asyncio
import json
from machine import Pin, PWM # type: ignore
import pico_functions_v1_1 as pf # type: ignore
from fan_assignment_classes import Fan, Tachometer, Uart

# initialisatie
# potmeter = ADC(Pin(27))
fan = PWM(Pin(2))  # PWM control wire (blue)
fan.freq(25000) # 25 kHz is standaard voor computer fans

def display_values(screen, uart, tacho):
    screen.fill(0)
    screen.rotate(True)
    SP = uart.data["SP"] if uart.data else None
    try:
        pf.hor_level_indicator(SP, 0, 0, 64, 8, 'bar', screen)
        screen.text(f"{100 * SP:4.1f}%", 0, 15)
        screen.text(f"{tacho.rpm} rpm", 0, 30)
    except Exception:
        screen.text("NO DATA", 0, 15)
    screen.show()



async def main():
    fan = Fan(2, bias=.2)
    # potmeter = Potmeter(27, fan)
    tacho = Tachometer(3)
    screen = pf.display_init(ID=1, sda_pin=10, scl_pin=11)
    uart = Uart()

    fan.start()
    # potmeter.start()
    tacho.start()
    uart.start()

    while True:
        display_values(screen, uart, tacho)
        fan.duty = uart.data["SP"] if uart.data else 0
        uart.uart.write(json.dumps({"RPM": tacho.rpm}).encode() + b"\n")
        await asyncio.sleep(1/30)



async def calibration():
    fan = Fan(3)
    tacho = Tachometer(2)
    fan.start()
    tacho.start()
    
    for i in range(21):
        fan.duty = i/20
        await asyncio.sleep(2)

# asyncio.run(calibration())
asyncio.run(main())