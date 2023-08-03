from odin_devices.i2c_device import I2CDevice
from odin_devices.tca9548 import TCA9548
from odin_devices.ad5593r import AD5593R
from odin_devices.mcp23008 import MCP23008

def temp1_adc(adc_val):

    temp1 = ((adc_val / 4095.)*218.75 - 66.875)
    return temp1

def temp1_raw_adc(adc_val):

    temp1 = (adc_val / 4095.)
    return temp1

def temp2_adc(adc_val):

    temp2 = ((adc_val / 4095.)*1000 - 273.15)
    return temp2

def temp2_raw_adc(adc_val):

    temp2 = (adc_val / 4095.)
    return temp2

def humid_adc(adc_val):

    humid = ((adc_val / 4095.)*125.0) - 12.5
    return humid

def humid_raw_adc(adc_val):

    humid = (adc_val / 4095.)
    return humid

def leak_adc(adc_val):

    leak = ((adc_val / 4095.)*5)/ 150e-3
    return leak

class PSCUSolo():

    ADC_PINS = {
        "leak_value": (0, 0),
        "temp1_value": (0, 2),
        "humidity_value": (0, 3),
        "temp2_value": (0, 6),
        "temp1_sp_under": (1 , 2),
        "temp1_sp_over": (1, 3),
        "humidity_sp": (1, 4),
        "temp2_sp_over": (1, 5),
        "temp2_sp_under": (1, 6),
        "leak_sp": (1, 7),
    }

    INPUT_PINS = {
        "humid_healthy": (0, 0),
        "pump_healthy": (0, 1),
        "temp_healthy": (0, 2),
        "leak_healthy": (0, 3),
        "leak_tripped": (0, 4),
        "tripped": (0, 7),
        "leak_latched": (1, 0),
        "humid_latched": (1, 1),
        "pump_latched": (1, 2),
        "temp_latched": (1, 3),
        "leak_trace": (1, 4),
        "armed": (1, 5),
        "temp1_over": (2, 0),
        "temp1_under": (2, 1),
        "humid_over": (2, 2),
        "temp2_over": (2, 3),
        "temp2_under": (2, 4),
        "pump_trip": (2, 5),
    }

    OUTPUT_PINS = {
        "disarm": (0, 5),
        "arm": (0, 6),
    }

    def __init__(self):

        I2CDevice.set_default_i2c_bus(2)

        self.tca = TCA9548(address=0x70)

        self.adc = []
        for addr in [0x10 , 0x11]:
            self.adc.append(self.tca.attach_device(4, AD5593R, addr))

        self.adc[0].setup_adc(0x4d)
        self.adc[1].setup_adc(0xfc)

        self.mcp = []
        for addr in [0x24, 0x27, 0x25]:
            self.mcp.append(self.tca.attach_device(5, MCP23008, addr))

        for (pin_name, (mcp_idx, pin)) in self.INPUT_PINS.items():
            self.mcp[mcp_idx].setup(pin, MCP23008.IN)

        for (pin_name, (mcp_idx, pin)) in self.OUTPUT_PINS.items():
            self.mcp[mcp_idx].setup(pin, MCP23008.OUT)

        self.armed = False

        self.temp_latched = False

        self.temp1 = 0.0
        self.temp1_raw = 0.0
        self.temp1_trip_over = False
        self.temp1_trip_under = False
        self.temp1_sp_over = 0.0
        self.temp1_sp_over_raw = 0.0
        self.temp1_sp_under = 0.0
        self.temp1_sp_under_raw = 0.0

        self.temp2 = 0.0
        self.temp2_raw = 0.0
        self.temp2_trip_over = False
        self.temp2_trip_under = False
        self.temp2_sp_over = 0.0
        self.temp2_sp_over_raw = 0.0
        self.temp2_sp_under = 0.0
        self.temp2_sp_under_raw = 0.0

        self.humidity = 0.0
        self.humid_raw = 0.0
        self.humid_healthy = False
        self.humid_latched = False
        self.humid_trip_over = False
        self.humid_sp = 0.0
        self.humid_sp_raw = 0.0

        self.leak = 0.0
        self.leak_sp = 0.0
        self.leak_healthy = False
        self.leak_latched = False
        self.leak_trip_under = False
        self.leak_trace = False
        self.pump_healthy = False
        self.pump_trip = False
        self.pump_latched = False

        self.tripped = False

        self.update()

    def read_adc(self, adc_name):
        (adc_idx, pin) = self.ADC_PINS[adc_name]
        return self.adc[adc_idx].read_adc(pin)

    def read_gpio(self, gpio_name):

        (mcp_idx, pin) = self.INPUT_PINS[gpio_name]
        return self.mcp[mcp_idx].input(pin)

    def write_gpio(self, gpio_name, value):
        (mcp_idx , pin) = self.OUTPUT_PINS[gpio_name]
        self.mcp[mcp_idx].output(pin, value)

    def update(self):

        self.armed = self.read_gpio("armed")
        self.tripped = not self.read_gpio("tripped")

        self.update_temp()
        self.update_humid()
        self.update_leak()
        self.update_pump()

    def update_temp(self):

        self.temp_healthy = self.read_gpio("temp_healthy")
        self.temp_latched = not self.read_gpio("temp_latched")
        self.update_temp1()
        self.update_temp2()

    def update_temp1(self):

        adc_val = self.read_adc("temp1_value")
        self.temp1 = temp1_adc(adc_val)
        self.temp1_raw = temp1_raw_adc(adc_val)
        adc_val = self.read_adc("temp1_sp_under")
        self.temp1_sp_under = temp1_adc(adc_val)
        self.temp1_sp_under_raw = temp1_raw_adc(adc_val)
        self.temp1_trip_over = not self.read_gpio("temp1_over")
        self.temp1_trip_under = not self.read_gpio("temp1_under")
        adc_val = self.read_adc("temp1_sp_over")
        self.temp1_sp_over = temp1_adc(adc_val)
        self.temp1_sp_over_raw = temp1_raw_adc(adc_val)

    def update_temp2(self):

        adc_val = self.read_adc("temp2_value")
        self.temp2 = temp2_adc(adc_val)
        self.temp2_raw = temp2_raw_adc(adc_val)
        adc_val = self.read_adc("temp2_sp_under")
        self.temp2_sp_under = temp2_adc(adc_val)
        self.temp2_sp_under_raw = temp2_raw_adc(adc_val)
        self.temp2_trip_over = not self.read_gpio("temp2_over")
        self.temp2_trip_under = not self.read_gpio("temp2_under")
        adc_val = self.read_adc("temp2_sp_over")
        self.temp2_sp_over = temp2_adc(adc_val)
        self.temp2_sp_over_raw = temp2_raw_adc(adc_val)

    def update_humid(self):

        adc_val = self.read_adc("humidity_value")
        self.humidity = humid_adc(adc_val)
        self.humid_raw = humid_raw_adc(adc_val)
        adc_val = self.read_adc("humidity_sp")
        self.humid_sp = humid_adc(adc_val)
        self.humid_sp_raw = humid_raw_adc(adc_val)
        self.humid_trip_over = not self.read_gpio("humid_over")
        self.humid_healthy = self.read_gpio("humid_healthy")
        self.humid_latched = not self.read_gpio("humid_latched")

    def update_leak(self):

        self.leak = leak_adc(self.read_adc("leak_value"))
        self.leak_sp = leak_adc(self.read_adc("leak_sp"))
        self.leak_healthy = self.read_gpio("leak_healthy")
        self.leak_latched = not self.read_gpio("leak_latched")
        self.leak_trip_under = not self.read_gpio("leak_tripped")
        self.leak_trace = self.read_gpio("leak_trace")

    def update_pump(self):

        self.pump_healthy = self.read_gpio("pump_healthy")
        self.pump_trip = self.read_gpio("pump_trip")
        self.pump_latched = not self.read_gpio("pump_latched")

    def set_armed(self, arm):

        pin = "arm" if arm else "disarm"
        self.write_gpio(pin, MCP23008.LOW)
        self.write_gpio(pin, MCP23008.HIGH)
        self.write_gpio(pin, MCP23008.LOW)

        self.armed = self.read_gpio("armed")










