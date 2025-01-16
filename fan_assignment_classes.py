from machine import ADC, PWM, Pin, UART
import asyncio
import json
import pico_functions_v1_1 as pf

class Fan():
    def __init__(self, pin, frequency=25000, bias=0):
        self.fan = PWM(Pin(pin))
        self.fan.freq(frequency)
        self.bias = bias
        
        self.fan.duty_u16(0)
        
        self._running = False

    def start(self):
        self._running = True

    def stop(self):
        self._running = False
    
    async def _controlloop(self):
        while True:
            if not self._running:
                self.fan.duty_u16(0)
                await asyncio.sleep(0.1)
                continue

    @property
    def duty(self):
        realDuty = self.fan.duty_u16() / 65535
        return ( realDuty - self.bias ) / (1 - self.bias)
    
    @duty.setter
    def duty(self, setpoint):
        if setpoint is None: setpoint = 0  # noqa: E701
        realDuty = (setpoint * (1 - self.bias) + self.bias)
        self.fan.duty_u16(int(realDuty * 65535))



pot_min = 223
pot_max = 65305

class Potmeter():
    def __init__(self, pin):
        self.potmeter = ADC(Pin(pin))
        self.value = 0
        self._running = False

    def start(self):
        self._running = True
        asyncio.create_task(self._readloop())
        

    def _read(self):
        return pf.adc_average(self.potmeter, 1000)

    @property
    def percentage(self):
        return pf.norm(self.value, pot_min, pot_max)
    
    async def _readloop(self):
        while self._running:
            self.value = self._read()
            await asyncio.sleep(0.1)



class Tachometer():
    def __init__(self, pin):
        self.tacho = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.tacho_counter = 0
        self.rpm = 0

    def start(self):
        self._running = True
        self.tacho.irq(trigger=Pin.IRQ_FALLING, handler=self._tacho_handler)
        asyncio.create_task(self._tacho_rpm())

    def stop(self):
        self._running = False
        self.tacho.irq(handler=None)
        self.rpm = False
    
    def _tacho_handler(self, t):
        self.tacho_counter += 1

    async def _tacho_rpm(self):
        period = 1
        while True:
            if not self._running:
                return

            self.rpm = self.tacho_counter * 30 / period
            self.tacho_counter = 0
            await asyncio.sleep(period)



class Uart():
    def __init__(self, uart=0, baudrate=9600):
        self.uart = UART(uart, baudrate=baudrate)
        self.uart.init(timeout=1000)

        self.data = None
        self._running = False

    def start(self):
        if self._running: return  # noqa: E701
        self._running = True
        asyncio.create_task(self._readloop())

    def stop(self):
        self._running = False

    async def _readloop(self):
        while self._running:            
            await asyncio.sleep(0.1)
            rxDataRaw = self.uart.readline()

            if not rxDataRaw:
                self.data = None
                continue
            
            try:
                parsedData = json.loads(rxDataRaw.decode())
                self.data = parsedData
                print(parsedData)

            except Exception as e:
                self.output = None
                print(e)

