# For the case that nl2telemetry has not been added to PYTHONPATH
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).absolute().parent.parent))

"""
Shows a simple interface to control NL2 stations using a tkinter GUI

Launch NoLimits 2 with the "--telemetry" option, then execute.
"""
import tkinter as tk
from typing import Union

from nl2telemetry.message import Answer
from nl2telemetry.message.request import SetEmergencyStopMessage, \
    SetManualModeMessage, SetGatesMessage, SetHarnessMessage, \
    SetFlyerCarMessage, SetPlatformMessage, DispatchMessage, \
    GetStationStateMessage, GetCurrentCoasterAndNearestStationMessage, \
    GetCoasterNameMessage
from nl2telemetry.message.reply import StationStateData, IntValuePairData, \
    StringData

from nl2telemetry import NoLimits2


class Status(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, args, **kwargs)
        self.parent = parent

        self.coaster = tk.Label(self, text="Coaster: ", anchor='w')
        self.coaster.pack(side='top', anchor='w', fill='x')

        self.station = tk.Label(self, text="Station: ", anchor='w')
        self.station.pack(side='top', anchor='w', fill='x')


class Controls(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, args, **kwargs)
        self.parent = parent

        self.manual_status = tk.IntVar()
        self.gates_status = tk.IntVar()
        self.harness_status = tk.IntVar()
        self.platform_status = tk.IntVar()
        self.flyer_car_status = tk.IntVar()

        self.emergency = tk.Button(self, text="Emergency")
        self.emergency.pack(side='top', fill='x', expand=1)

        self.manual = tk.Checkbutton(
            self, text="Manual", anchor='e', variable=self.manual_status)
        self.manual.pack(side='top', fill='x')

        self.gates = tk.Checkbutton(
            self, text="Gates", anchor='w', variable=self.gates_status)
        self.gates.pack(side='top', fill='x')

        self.harness = tk.Checkbutton(
            self, text="Harness", anchor='w', variable=self.harness_status)
        self.harness.pack(side='top', fill='x')

        self.platform = tk.Checkbutton(
            self, text="Platform", anchor='w', variable=self.platform_status)
        self.platform.pack(side='top', fill='x')

        self.flyer_car = tk.Checkbutton(
            self, text="Flyer Car", variable=self.flyer_car_status, anchor='w')
        self.flyer_car.pack(side='top', fill='x')

        self.dispatch = tk.Button(self, text="Dispatch", anchor='center')
        self.dispatch.pack(side='top', fill='x')


class Application(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, args, **kwargs)
        self.parent = parent
        self.status = Status(self)
        self.controls = Controls(self)

        self.status.pack(side='top', fill='x')
        self.controls.pack(side='bottom', fill='x')

    def bind_commands(self, emergency, manual, gates, harness, platform,
                      flyer_car, dispatch):
        self.controls.emergency.configure(command=emergency)
        self.controls.manual.configure(command=manual)
        self.controls.gates.configure(command=gates)
        self.controls.harness.configure(command=harness)
        self.controls.platform.configure(command=platform)
        self.controls.flyer_car.configure(command=flyer_car)
        self.controls.dispatch.configure(command=dispatch)

    @staticmethod
    def _set_checkbox_from_status(control: tk.Checkbutton,
                                  control_variable: tk.IntVar,
                                  status: int):
        if status == -1:
            control_variable.set(0)
            control.configure(state='disabled')
        else:
            control.configure(state='normal')
            control_variable.set(status)

    @staticmethod
    def _set_button_from_status(control: tk.Button, status: int):
        if status > -1:
            control.configure(state='normal')
        else:
            control.configure(state='disabled')

    @staticmethod
    def _set_label_(control: tk.Widget, text):
        control.configure(text=text)

    def set_status(self, coaster: str, station: str, manual: int,
                   gates: int, harness: int, platform: int,
                   flyer_car: int, dispatch: int):
        self._set_label_(self.status.coaster, "Coaster: " + coaster)
        self._set_label_(self.status.station, "Station: " + station)
        self._set_checkbox_from_status(
            self.controls.manual, self.controls.manual_status, manual)
        self._set_checkbox_from_status(
            self.controls.gates, self.controls.gates_status, gates)
        self._set_checkbox_from_status(
            self.controls.harness, self.controls.harness_status, harness)
        self._set_checkbox_from_status(
            self.controls.platform, self.controls.platform_status, platform)
        self._set_checkbox_from_status(
            self.controls.flyer_car, self.controls.flyer_car_status, flyer_car)
        self._set_button_from_status(self.controls.dispatch, dispatch)


def test_gui():
    root = tk.Tk()
    app = Application(root)
    app.pack(side="top", fill="both", expand=True)

    def test_binding():
        print("COMMAND")

    app.bind_commands(
        test_binding,
        test_binding,
        test_binding,
        test_binding,
        test_binding,
        test_binding,
        test_binding,
    )

    def test_status():
        app.set_status("my coaster", "5", 1, 1, 0, -1, -1, -1)

    root.after(5000, test_status)
    root.mainloop()


def inverted_bool_int(b: bool) -> int:
    return 0 if b else 1


class Nl2Station:
    from nl2telemetry.transmitter import TcpTransmitter
    sent_request = 0

    def __init__(self, nl2: TcpTransmitter):
        self._latest_status = None

        self._coaster_id = 0
        self._coaster_name = ""
        self._station_id = 0

        self._coaster_name_request = GetCoasterNameMessage()
        self._status_request = GetStationStateMessage()
        self._emergency_request = SetEmergencyStopMessage()
        self._manual_request = SetManualModeMessage()
        self._gates_request = SetGatesMessage()
        self._harness_request = SetHarnessMessage()
        self._platform_request = SetPlatformMessage()
        self._flyer_car_request = SetFlyerCarMessage()
        self._dispatch_request = DispatchMessage()
        self._nl2 = nl2

    @property
    def latest_status(self):
        return self._latest_status

    @property
    def coaster_name(self):
        return self._coaster_name

    @property
    def coaster_id(self):
        return self._coaster_id

    @property
    def station_id(self):
        return self._station_id

    def _update_coaster_name(self):
        self._coaster_name_request.set_coaster_index(self._coaster_id)
        self._nl2.send(self._coaster_name_request)
        data = Answer.get_data(self._nl2.receive())
        if isinstance(data, StringData):
            self._latest_status = data
            self._coaster_name = data.value

    def update_status(self):
        self._nl2.send(self._status_request)
        data = Answer.get_data(self._nl2.receive())
        if isinstance(data, StationStateData):
            self._latest_status = data

    def set_to_station(self, coaster_id, station_id):
        self._coaster_id = coaster_id
        self._station_id = station_id
        self._update_coaster_name()

    def toggle_emergency(self):
        if self._latest_status is None:
            return

        if self._latest_status.e_stop:
            self._emergency_request.set_emergency_for(
                self._coaster_id, 0)
        else:
            self._emergency_request.set_emergency_for(
                self._coaster_id, 1)

        self._nl2.send(self._emergency_request)

    def toggle_manual(self):
        if self._latest_status is None:
            return

        self._manual_request.set_manual_for(
            self._coaster_id, self._station_id, inverted_bool_int(
                self._latest_status.manual_dispatch)
        )
        self._nl2.send(self._manual_request)

    def toggle_gates(self):
        if self._latest_status is None:
            return

        if self._latest_status.can_close_gates:
            status = 0
        elif self._latest_status.can_open_gates:
            status = 1
        else:
            status = -1

        if status > -1:
            self._gates_request.set_gates_for(
                self._coaster_id, self._station_id, status)
            self._nl2.send(self._gates_request)

    def toggle_harness(self):
        if self._latest_status is None:
            return

        if self._latest_status.can_close_harness:
            status = 0
        elif self._latest_status.can_open_harness:
            status = 1
        else:
            status = -1

        if status > -1:
            self._harness_request.set_harness_for(
                self._coaster_id, self._station_id, status)
            self._nl2.send(self._harness_request)

    def toggle_platform(self):
        if self._latest_status is None:
            return

        if self._latest_status.can_close_platform:
            status = 0
        elif self._latest_status.can_open_platform:
            status = 1
        else:
            status = -1

        if status > -1:
            self._platform_request.set_platform_for(
                self._coaster_id, self._station_id, status)
            self._nl2.send(self._platform_request)

    def toggle_flyer_car(self):
        if self._latest_status is None:
            return

        if self._latest_status.can_close_flyer_car:
            status = 0
        elif self._latest_status.can_open_flyer_car:
            status = 1
        else:
            status = -1

        if status > -1:
            self._flyer_car_request.set_flyer_car_for(
                self._coaster_id, self._station_id, status)
            self._nl2.send(self._flyer_car_request)

    def dispatch(self):
        self._dispatch_request.set_for(self._coaster_id, self._station_id)
        self._nl2.send(self._dispatch_request)


def bools_to_int_status(set_0: bool, set_1: bool) -> int:
    if set_1:
        return 1
    elif set_0:
        return 0
    else:
        return -1


def run(update_interval=250):
    root = tk.Tk()
    app = Application(root)
    app.pack(side="top", fill="both", expand=True)
    update_request = GetCurrentCoasterAndNearestStationMessage()
    update_interval = 500

    with NoLimits2() as nl2:
        closest_station = Nl2Station(nl2)

        app.bind_commands(
            emergency=closest_station.toggle_emergency,
            manual=closest_station.toggle_manual,
            gates=closest_station.toggle_gates,
            harness=closest_station.toggle_harness,
            platform=closest_station.toggle_platform,
            flyer_car=closest_station.toggle_flyer_car,
            dispatch=closest_station.dispatch
        )

        def update_station():
            nl2.send(update_request)
            data = Answer.get_data(nl2.receive())
            if isinstance(data, IntValuePairData):
                closest_station.set_to_station(data.value0, data.value1)
            closest_station.update_status()
            status = closest_station.latest_status
            if status is not None:
                app.set_status(
                    closest_station.coaster_name,
                    str(closest_station.station_id),
                    bools_to_int_status(not status.manual_dispatch,
                                        status.manual_dispatch),
                    bools_to_int_status(status.can_close_gates,
                                        status.can_open_gates),
                    bools_to_int_status(status.can_close_harness,
                                        status.can_open_harness),
                    bools_to_int_status(status.can_raise_platform,
                                        status.can_lower_platform),
                    bools_to_int_status(status.can_lock_flyer_car,
                                        status.can_unlock_flyer_car),
                    bools_to_int_status(status.can_dispatch, False)
                )
            root.after(update_station.interval, update_station)

        update_station.interval = update_interval
        update_station()
        root.minsize(width=300, height=0)
        root.title("Dispatch Control Demo")
        root.mainloop()


if __name__ == '__main__':
    run()
