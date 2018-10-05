"""
A simple test of the telemetry client components.

No automatic testing framework is involved since NL2 must be put into suitable
states manually anyway.
"""
import nl2telemetry.transmitter
import nl2telemetry.message as message
import binascii

IP = '127.0.0.1'
PORT = 15151


def print_msg_data(msg):
    header_out = "type request data_size"
    data_out = "{0:4} {1:7} {2:9}".format(
        msg.type_id, msg.request_id, msg.data_size
    )
    print(" header:")
    print(" ", header_out)
    print(" ", data_out)
    print(" type:", msg.type_name)
    if msg.data_size > 0:
        try:
            data = msg.data_object
        except AttributeError:
            pass
        else:
            print("  data:")
            for key, value in data.__dict__.items():
                print("  ", key, value)


def send_test(transmitter, msg):
    print("sending:")
    print(" raw:", binascii.hexlify(msg.buffer))
    print_msg_data(msg)
    transmitter.send(msg)


def receive_test(transmitter):
    print("receiving:")
    data = transmitter.receive()
    print(" raw:", binascii.hexlify(data))
    msg = message.Answer.build(data)
    print_msg_data(msg)


def test(transmitter, request_id, msg):
    msg.set_request_id(request_id)
    send_test(transmitter, msg)
    receive_test(transmitter)
    print()


def test_all(ip, port, test_server_quitting=False):
    with nl2telemetry.transmitter.TcpTransmitter(ip, port) as transmitter:
        test(transmitter, 0, message.idle)
        test(transmitter, 1, message.get_version)
        test(transmitter, 2, message.get_telemetry)
        test(transmitter, 3, message.get_coaster_count)
        test(transmitter, 4, message.get_current_coaster_and_nearest_station)
        test(transmitter, 5, message.get_coaster_name)
        test(transmitter, 6, message.set_emergency_stop)
        test(transmitter, 7, message.get_station_state)
        test(transmitter, 8, message.set_manual_mode)
        test(transmitter, 9, message.dispatch)
        test(transmitter, 10, message.set_gates)
        test(transmitter, 11, message.set_harness)
        test(transmitter, 12, message.set_platform)
        test(transmitter, 13, message.set_flyer_car)
        test(transmitter, 14, message.select_seat)
        test(transmitter, 15, message.set_pause)
        test(transmitter, 16, message.select_seat)
        test(transmitter, 17, message.recenter_vr)
        test(transmitter, 18, message.set_custom_view)
        if test_server_quitting:
            test(transmitter, 19, message.quit_server)


def main():
    try:
        test_all(IP, PORT)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
