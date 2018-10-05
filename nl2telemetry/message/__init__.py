"""
Implements aliases and default instances of the messages
"""
from . import request

Answer = request.Message

idle = request.IdleMessage()
get_version = request.GetVersionMessage()
get_telemetry = request.GetTelemetryMessage()
get_coaster_count = request.getCoasterCountMessage()
get_current_coaster_and_nearest_station = \
    request.GetCurrentCoasterAndNearestStationMessage()
get_coaster_name = request.GetCoasterNameMessage()
set_emergency_stop = request.SetEmergencyStopMessage()
get_station_state = request.GetStationStateMessage()
set_manual_mode = request.SetManualModeMessage()
dispatch = request.DispatchMessage()
set_gates = request.SetGatesMessage()
set_harness = request.SetHarnessMessage()
set_platform = request.SetPlatformMessage()
set_flyer_car = request.SetFlyerCarMessage()
quit_server = request.QuitServerMessage()
set_pause = request.SetPauseMessage()
select_seat = request.SelectSeatMessage()
recenter_vr = request.RecenterVrMessage()
set_custom_view = request.SetCustomViewMessage()
