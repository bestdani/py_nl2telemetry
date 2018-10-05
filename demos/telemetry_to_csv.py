# For the case that nl2telemetry has not been added to PYTHONPATH
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).absolute().parent.parent))

"""
Writes NL2 Telemetry Data into CSV files.

To get a reasonable amount of clean data it is recommended to limit NL2's
frame rate to for example 10 per second before running the simulation.

Launch NoLimits 2 with the "--telemetry" option, then execute.
"""

import pathlib
import csv
import tkinter
from tkinter import filedialog

from nl2telemetry.message import Answer, get_telemetry
from nl2telemetry.message.reply import ErrorData, TelemetryData
from nl2telemetry import NoLimits2


def save_collected_data(collected_data, save_file):
    save_file = pathlib.Path(save_file).with_suffix('.csv')
    print("saving as", save_file)
    with open(save_file, 'w', newline='') as file_handle:
        writer = csv.writer(file_handle, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(
            (
                "record_number",
                "position_x",
                "position_y",
                "position_z",
                "rotation_quaternion_x",
                "rotation_quaternion_y",
                "rotation_quaternion_z",
                "rotation_quaternion_w",
                "speed",
                "gforce_x",
                "gforce_y",
                "gforce_z"
            )
        )
        for entry in collected_data:
            writer.writerow(entry)
    print("Saved! Bye and have a nice day!")


def new_data(data):
    no_pause = not data.paused_state
    new_frame = data.rendered_frame > new_data.last_rendered_frame
    position = data.position_x, data.position_z, data.position_z
    new_position = position != new_data.last_position

    new_data.last_position = position
    new_data.last_rendered_frame = data.rendered_frame

    return no_pause and new_frame and new_position


new_data.last_position = 0, 0, 0
new_data.last_rendered_frame = 0


def collect_loop(collected_data, has_received_data, record_number,
                 nl2):
    while True:
        get_telemetry.set_request_id(record_number)
        nl2.send(get_telemetry)
        data = Answer.get_data(nl2.receive())

        if isinstance(data, TelemetryData):
            if data.in_play_mode:
                if not has_received_data:
                    print("")
                    has_received_data = True
                print("\rcollecting data", end='')

            elif has_received_data:
                raise KeyboardInterrupt()

            else:
                print("\rwaiting for simulation start", end='')

            if new_data(data):
                collected_data.append((
                    record_number,
                    data.position_x,
                    data.position_y,
                    data.position_z,
                    data.rotation_quaternion_x,
                    data.rotation_quaternion_y,
                    data.rotation_quaternion_z,
                    data.rotation_quaternion_w,
                    data.speed,
                    data.gforce_x,
                    data.gforce_y,
                    data.gforce_z,
                ))
                record_number += 1

        elif isinstance(data, ErrorData):
            if has_received_data:
                raise KeyboardInterrupt()


def collect_data():
    collected_data = []
    with NoLimits2('127.0.0.1', 15151) as nl2:
        record_number = 0
        has_received_data = False
        try:
            collect_loop(collected_data, has_received_data, record_number,
                         nl2)

        except KeyboardInterrupt:
            print("\nStopped")

        except Exception as e:
            print("\nAn error occurred:\n", e)
    return collected_data


def query_save_location():
    root = tkinter.Tk()
    root.withdraw()

    file_name = filedialog.asksaveasfilename(
        initialdir=".",
        title="Save as",
        filetypes=(
            ("Comma Separated Values", '*.csv'),
        )
    )
    return file_name


def run():
    save_file = query_save_location()
    if save_file == '':
        print("Aborting! Bye and have a nice day!")
        exit(0)
    print("Selected file", save_file)

    try:
        collected_data = collect_data()
    except Exception as e:
        print("An error occurred:\n", e)
    else:
        save_collected_data(collected_data, save_file)


if __name__ == '__main__':
    run()
