"""Controller for the Power Supply Control Unit Solo.

this script deffines a class so that JSON can take data
directly from the beagle and send it to the PSUCsolo web
inteface.

Harvey Wornham, STFC Detector Systems Software Group
"""
import logging

from tornado.ioloop import PeriodicCallback

from odin.adapters.parameter_tree import ParameterTree
from pscusolo.pscusolo import PSCUSolo


class PSCUSoloController():
    """generates and updates the parameter tree."""

    def __init__(self):
        """Initalises the logging.debug command."""
        logging.debug("Initalising PSCU solo controller")

        # Create a PSCUSolo instance
        self.pscu = PSCUSolo()

        # Setup Parameter Tree
        self.param_tree = ParameterTree({
            "overall": (lambda: self.pscu.overall, None),
            "latched": (lambda: self.pscu.latched, None),
            "armed": (lambda: self.pscu.armed, self.pscu.set_armed),
            "tripped": (lambda: self.pscu.tripped, None),
            "temperature": {
                "healthy": (lambda: self.pscu.temp_healthy, None),
                "latched": (lambda: self.pscu.temp_latched, None),
                "sensors": [
                    {
                        "sensor_name": "Internal",
                        "trip_over": (lambda: self.pscu.temp1_trip_over, None),
                        "trip_under": (lambda: self.pscu.temp1_trip_under, None),
                        "temperature": (lambda: self.pscu.temp1, None),
                        "setpoint_over": (lambda: self.pscu.temp1_sp_over, None),
                        "setpoint_under": (lambda: self.pscu.temp1_sp_under, None),
                    },
                    {
                        "sensor_name": "Coolant",
                        "trip_over": (lambda: self.pscu.temp2_trip_over, None),
                        "trip_under": (lambda: self.pscu.temp2_trip_under, None),
                        "temperature": (lambda: self.pscu.temp2, None),
                        "setpoint_over": (lambda: self.pscu.temp2_sp_over, None),
                        "setpoint_under": (lambda: self.pscu.temp2_sp_under, None),
                    }
                ],
            },
            "humidity": {
                "healthy": (lambda: self.pscu.humid_healthy, None),
                "latched": (lambda: self.pscu.humid_latched, None),
                "sensors": [
                    {
                        "sensor_name": "Internal",
                        "trip_over": (lambda: self.pscu.humid_trip_over, None),
                        "value": (lambda: self.pscu.humidity, None),
                        "setpoint_over": (lambda: self.pscu.humid_sp, None),
                    },
                ]
            },
            "leak": {
                "healthy": (lambda: self.pscu.leak_healthy, None),
                "latched": (lambda: self.pscu.leak_latched, None),
                "sensors": [
                    {
                        "sensor_name": "Leak",
                        "trip_under": (lambda: self.pscu.leak_trip_under, None),
                        "value": (lambda: self.pscu.leak, None),
                        "setpoint_under": (lambda: self.pscu.leak_sp, None),
                        "trace": (lambda: self.pscu.leak_trace, None),
                    },
                ]
            },
            "pump": {
                "latched": (lambda: self.pscu.pump_latched, None),
                "healthy": (lambda: self.pscu.pump_healthy, None),
                "sensors": [
                    {
                        "sensor_name": "Pump",
                        "pump_trip": (lambda: self.pscu.pump_trip, None),
                    }
                ]
            },
            "fans": {
                "sensors": [
                    {
                        "sensor_name": "Fan 1",
                        "value": (lambda: self.pscu.fans[0].rpm_5, None),
                    },
                    {
                        "sensor_name": "Fan 2",
                        "value": (lambda: self.pscu.fans[1].rpm_5, None),
                    },
                ]
            }
        })

        self.update_task = PeriodicCallback(self.do_update, 250)
        self.update_task.start()

    def get(self, path):
        """Update the parameter tree when a get command is called."""
        return self.param_tree.get(path)

    def set(self, path, data):
        """Update the parameter tree when a set command is called."""
        self.param_tree.set(path, data)
        return self.param_tree.get(path)

    def do_update(self):
        """Run the update method from PSCUsolo.py."""
        self.pscu.update()
