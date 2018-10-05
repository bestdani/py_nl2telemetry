# For the case that nl2telemetry has not been added to PYTHONPATH
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).absolute().parent.parent))

"""
Draws a live plot of the current G Force Data (requires matplotlib)

Launch NoLimits 2 with the "--telemetry" option, then execute.
"""

import matplotlib.pyplot as plt

from nl2telemetry import NoLimits2
from nl2telemetry.message import get_telemetry, Answer
from nl2telemetry.message.reply import TelemetryData


def new_data(data):
    no_pause = not data.paused_state
    new_frame = data.rendered_frame > new_data.last_rendered_frame
    position = data.position_x, data.position_z, data.position_z
    new_position = position != new_data.last_position

    new_data.last_position = position
    new_data.last_rendered_frame = data.rendered_frame

    return no_pause and new_frame and new_position


new_data.last_position = 0, 1, 0
new_data.last_rendered_frame = 0


def update_plot(history, nl2, vector, x_values, y_values):
    nl2.send(get_telemetry)
    data = Answer.get_data(nl2.receive())
    if isinstance(data, TelemetryData):
        if new_data(data):
            x_values.append(data.gforce_x)
            y_values.append(data.gforce_y)
            history.set_data(x_values, y_values)
            vector.set_data([0, data.gforce_x], [0, data.gforce_y])


def start_g_force_plot(nl2, refresh_rate):
    refresh_interval = 1 / refresh_rate

    fig, ax = plt.subplots(1, 1)
    ax.set_aspect('equal')
    ax.set_xlim(-3, 3)
    ax.set_ylim(6, -2)

    x_values = []
    y_values = []
    history = ax.plot(x_values, y_values, '-')[0]
    vector = ax.plot([0, 0], [0, 1], '-')[0]

    try:
        while True:
            update_plot(history, nl2, vector, x_values, y_values)
            plt.pause(refresh_interval)
    except Exception as e:
        plt.close(fig)
        raise e
    finally:
        plt.close(fig)


def main():
    with NoLimits2() as nl2:
        start_g_force_plot(nl2, 10)


if __name__ == "__main__":
    main()
