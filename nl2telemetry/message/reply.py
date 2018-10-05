"""
Classes that represent the replyed data by the Server
"""
import struct

data_types = {}


class ReplyData(object):
    data_name = ''

    def _set_data(self, data):
        self._blob = data
        self._set_attributes()

    def _set_attributes(self):
        pass


empty_instance = ReplyData()


class OkData(ReplyData):
    data_name = 'ok'
    data_format = ''


data_types[1] = OkData()


class ErrorData(ReplyData):
    data_name = 'error'
    data_format = ''

    def _set_attributes(self):
        self.text = self._blob.decode("utf-8")


data_types[2] = ErrorData()


class VersionData(ReplyData):
    data_name = 'version'
    data_format = '!bbbb'
    packer = struct.Struct(data_format)

    def _set_attributes(self):
        (
            self.main,
            self.minor,
            self.revision,
            self.build,
        ) = self.packer.unpack(self._blob)


data_types[4] = VersionData()


class TelemetryData(ReplyData):
    data_name = 'telemetry'
    data_format = '!iiiiiiiifffffffffff'
    packer = struct.Struct(data_format)

    def _set_attributes(self):
        (
            state,
            self.rendered_frame,
            self.view_mode,
            self.current_coaster,
            self.coaster_style_id,
            self.current_train,
            self.current_car,
            self.current_seat,
            self.speed,
            self.position_x,
            self.position_y,
            self.position_z,
            self.rotation_quaternion_x,
            self.rotation_quaternion_y,
            self.rotation_quaternion_z,
            self.rotation_quaternion_w,
            self.gforce_x,
            self.gforce_y,
            self.gforce_z,
        ) = self.packer.unpack(self._blob)
        self.in_play_mode = is_bit_set(state, 0)
        self.braking = is_bit_set(state, 1)
        self.paused_state = is_bit_set(state, 2)


data_types[6] = TelemetryData()


class IntValueData(ReplyData):
    data_name = 'int value'
    data_format = '!i'
    packer = struct.Struct(data_format)

    def _set_attributes(self):
        (
            self.value,
        ) = self.packer.unpack(self._blob)


data_types[8] = IntValueData()


class StringData(ReplyData):
    data_name = 'string'
    data_format = ''

    def _set_attributes(self):
        self.value = self._blob.decode("utf-8")


data_types[10] = StringData()


class IntValuePairData(ReplyData):
    data_name = 'int value pair'
    data_format = '!ii'
    packer = struct.Struct(data_format)

    def _set_attributes(self):
        (
            self.value0,
            self.value1,
        ) = self.packer.unpack(self._blob)


data_types[12] = IntValuePairData()


class StationStateData(ReplyData):
    data_name = 'station state'
    data_format = '!I'
    packer = struct.Struct(data_format)

    def _set_attributes(self):
        (integer,) = self.packer.unpack(self._blob)

        self.e_stop = is_bit_set(integer, 0)
        self.manual_dispatch = is_bit_set(integer, 1)
        self.can_dispatch = is_bit_set(integer, 2)
        self.can_close_gates = is_bit_set(integer, 3)
        self.can_open_gates = is_bit_set(integer, 4)
        self.can_close_harness = is_bit_set(integer, 5)
        self.can_open_harness = is_bit_set(integer, 6)
        self.can_raise_platform = is_bit_set(integer, 7)
        self.can_lower_platform = is_bit_set(integer, 8)
        self.can_lock_flyer_car = is_bit_set(integer, 9)
        self.can_unlock_flyer_car = is_bit_set(integer, 10)
        self.train_in_station = is_bit_set(integer, 11)
        self.train_in_station_is_current = is_bit_set(integer, 12)


data_types[15] = StationStateData()


def is_bit_set(integer, position):
    return integer >> position & 1 > 0
