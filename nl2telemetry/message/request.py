"""
Classes for building NL2 request data
"""
import struct
from typing import Union

from . import reply


class Message(object):
    magic_packer = struct.Struct('!c')
    magic_start = b'N'
    magic_end = b'L'
    head_packer = struct.Struct('!HIH')
    type_name = ''

    """msg is an argument because its buffer will be set to the bytearray
    used here when it is valid"""

    @classmethod
    def is_valid(cls, bytes, msg):
        length = len(bytes)
        if (length >= 10):
            buffer = bytearray(bytes)
            (magic_start,) = cls.magic_packer.unpack(buffer[:1])
            (magic_end,) = cls.magic_packer.unpack_from(buffer, length - 1)
            if (magic_start == cls.magic_start and magic_end == cls.magic_end):
                msg.buffer = buffer
                return True
        return False

    @classmethod
    def build(cls, received_bytes) -> Union['Message', None]:
        msg = Message()
        if cls.is_valid(received_bytes, msg):
            (
                msg.type_id, msg.request_id, msg.data_size
            ) = cls.head_packer.unpack(msg.buffer[1:9])
            msg._set_data_from_type()
            msg._set_name_from_data()
            return msg
        else:
            return None

    @classmethod
    def get_data(cls, received_bytes) -> Union['reply.ReplyData', None]:
        message = cls.build(received_bytes)
        if message is not None:
            return message.data_object
        else:
            return None

    def _set_data_from_type(self):
        self.data_object = reply.data_types.get(
            self.type_id, reply.empty_instance
        )
        self.data_object._set_data(self.buffer[9:9 + self.data_size])

    def _set_name_from_data(self):
        self.type_name = self.data_object.data_name


class Request(Message):
    def __init__(self):
        Message.__init__(self)
        self.request_id = 0
        self.request_packer = struct.Struct('!I')
        self._generate_buffer()

    def _generate_buffer(self):
        pass

    def set_request_id(self, id):
        self.request_id = id
        self.request_packer.pack_into(self.buffer, 3, self.request_id)


class NoData(object):
    def __init__(self):
        self.data_size = 0
        self.packer = struct.Struct('!cHIHc')

    def _generate_buffer(self):
        raw_buffer = self.packer.pack(
            self.magic_start,
            self.type_id,
            self.request_id,
            self.data_size,
            self.magic_end
        )
        self.buffer = bytearray(raw_buffer)


class FixedDataSize(object):
    def __init__(self, format, size):
        self.data_format = format
        self.data_size = size
        self.packer = struct.Struct('!cHIH' + format + 'c')
        self.data_packer = struct.Struct('!' + format)

    def _generate_buffer(self):
        self.buffer = bytearray(self.packer.size)
        self.magic_packer.pack_into(self.buffer, 0, self.magic_start)
        struct.pack_into('!H', self.buffer, 1, self.type_id)
        struct.pack_into('!H', self.buffer, 7, self.data_size)
        self.magic_packer.pack_into(
            self.buffer, 9 + self.data_size, self.magic_end
        )


class DynamicDataSize(object):
    def __init__(self):
        self.data_format = format
        self.packer = struct.Struct('!cHIH')

    def _generate_buffer(self):
        self.buffer = bytearray(self.packer.size)
        self.head_buffer = self.buffer
        self.magic_packer.pack_into(self.buffer, 0, self.magic_start)
        struct.pack_into('!H', self.buffer, 1, self.type_id)

    def _finish_buffer(self):
        self.size_packer.pack_into(self.head_buffer, 7, self.data_size)
        end_buffer = self.magic_packer.pack(self.magic_end)
        self.buffer = self.head_buffer + self.data_buffer + end_buffer


class IdleMessage(NoData, Request):
    def __init__(self):
        self.type_name = "idle"
        self.type_id = 0
        NoData.__init__(self)
        Request.__init__(self)


class GetVersionMessage(NoData, Request):
    def __init__(self):
        self.type_name = "get version"
        self.type_id = 3
        NoData.__init__(self)
        Request.__init__(self)


class GetTelemetryMessage(NoData, Request):
    def __init__(self):
        self.type_name = "get telemetry"
        self.type_id = 5
        NoData.__init__(self)
        Request.__init__(self)


class getCoasterCountMessage(NoData, Request):
    def __init__(self):
        self.type_name = "get coaster count"
        self.type_id = 7
        NoData.__init__(self)
        Request.__init__(self)


class GetCurrentCoasterAndNearestStationMessage(NoData, Request):
    def __init__(self):
        self.type_name = "get current coaster and nearest station"
        self.type_id = 11
        NoData.__init__(self)
        Request.__init__(self)


class GetCoasterNameMessage(FixedDataSize, Request):
    def __init__(self):
        self.type_name = "get coaster name"
        self.type_id = 9
        FixedDataSize.__init__(self, 'i', 4)
        Request.__init__(self)

    def set_coaster_index(self, index):
        self.data_packer.pack_into(self.buffer, 9, index)


class SetEmergencyStopMessage(FixedDataSize, Request):
    def __init__(self):
        self.type_name = "set emergency stop"
        self.type_id = 13
        FixedDataSize.__init__(self, 'iB', 5)
        Request.__init__(self)

    def set_emergency_for(self, coaster_index, status):
        self.data_packer.pack_into(self.buffer, 9, coaster_index, status)


class GetStationStateMessage(FixedDataSize, Request):
    def __init__(self):
        self.type_name = "set station state"
        self.type_id = 14
        FixedDataSize.__init__(self, 'ii', 8)
        Request.__init__(self)

    def get_state_for(self, coaster_index, station_index):
        self.data_packer.pack_into(self.buffer, 9, coaster_index,
                                   station_index)


class SetManualModeMessage(FixedDataSize, Request):
    def __init__(self):
        self.type_name = "set manual mode"
        self.type_id = 16
        FixedDataSize.__init__(self, 'iiB', 9)
        Request.__init__(self)

    def set_manual_for(self, coaster_index, station_index, status):
        self.data_packer.pack_into(
            self.buffer, 9, coaster_index, station_index, status
        )


class DispatchMessage(FixedDataSize, Request):
    def __init__(self):
        self.type_name = "dispatch"
        self.type_id = 17
        FixedDataSize.__init__(self, 'ii', 8)
        Request.__init__(self)

    def set_for(self, coaster_index, station_index):
        self.data_packer.pack_into(self.buffer, 9, coaster_index,
                                   station_index)


class SetGatesMessage(FixedDataSize, Request):
    def __init__(self):
        self.type_name = "set gates"
        self.type_id = 18
        FixedDataSize.__init__(self, 'iiB', 9)
        Request.__init__(self)

    def set_gates_for(self, coaster_index, station_index, status):
        self.data_packer.pack_into(
            self.buffer, 9, coaster_index, station_index, status
        )


class SetHarnessMessage(FixedDataSize, Request):
    def __init__(self):
        self.type_name = "set harness"
        self.type_id = 19
        FixedDataSize.__init__(self, 'iiB', 9)
        Request.__init__(self)

    def set_harness_for(self, coaster_index, station_index, status):
        self.data_packer.pack_into(
            self.buffer, 9, coaster_index, station_index, status
        )


class SetPlatformMessage(FixedDataSize, Request):
    def __init__(self):
        self.type_name = "set platform"
        self.type_id = 20
        FixedDataSize.__init__(self, 'iiB', 9)
        Request.__init__(self)

    def set_platform_for(self, coaster_index, station_index, status):
        self.data_packer.pack_into(
            self.buffer, 9, coaster_index, station_index, status
        )


class SetFlyerCarMessage(FixedDataSize, Request):
    def __init__(self):
        self.type_name = "set flyer car"
        self.type_id = 21
        FixedDataSize.__init__(self, 'iiB', 9)
        Request.__init__(self)

    def set_flyer_car_for(self, coaster_index, station_index, status):
        self.data_packer.pack_into(
            self.buffer, 9, coaster_index, station_index, status
        )


class QuitServerMessage(NoData, Request):
    def __init__(self):
        self.type_name = "quit server"
        self.type_id = 26
        NoData.__init__(self)
        Request.__init__(self)


class SetPauseMessage(FixedDataSize, Request):
    def __init__(self):
        self.type_name = "set pause"
        self.type_id = 27
        FixedDataSize.__init__(self, 'B', 1)
        Request.__init__(self)

    def set_pause_to_enabled(self):
        self.data_packer.pack_into(
            self.buffer, 9, 1
        )

    def set_pause_to_disabled(self):
        self.data_packer.pack_into(
            self.buffer, 9, 0
        )


class SelectSeatMessage(FixedDataSize, Request):
    def __init__(self):
        self.type_name = "select seat"
        self.type_id = 29
        FixedDataSize.__init__(self, 'iiii', 16)
        Request.__init__(self)

    def set_to_seat(self, coaster_index, train_index, car_index, seat_index):
        self.data_packer.pack_into(
            self.buffer, 9, coaster_index, train_index, car_index, seat_index
        )


class RecenterVrMessage(NoData, Request):
    def __init__(self):
        self.type_name = "recenter VR"
        self.type_id = 31
        NoData.__init__(self)
        Request.__init__(self)


class SetCustomViewMessage(FixedDataSize, Request):
    def __init__(self):
        self.type_name = "set custom view"
        self.type_id = 32
        FixedDataSize.__init__(self, 'fffffB', 21)
        Request.__init__(self)

    def _set_custom_view(self, position_x, position_y, position_z,
                         azimuth_angle, elevation_angle, mode):
        self.data_packer.pack_into(
            self.buffer, 9, position_x, position_y, position_z, azimuth_angle,
            elevation_angle, mode
        )

    def set_fly_view(self, position_x, position_y, position_z, azimuth_angle,
                     elevation_angle):
        self._set_custom_view(position_x, position_y, position_z,
                              azimuth_angle, elevation_angle, 0)

    def set_walk_view(self, position_x, position_y, position_z, azimuth_angle,
                      elevation_angle):
        self._set_custom_view(position_x, position_y, position_z,
                              azimuth_angle, elevation_angle, 1)
