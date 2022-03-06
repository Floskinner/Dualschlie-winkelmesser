from zuendwinckelmesser import __version__
from zuendwinckelmesser import engine
from zuendwinckelmesser.main import create_cycle
from zuendwinckelmesser.engine import Engine, Cycle
import time
import pytest
from pytest_mock import MockerFixture

def test_version():
    assert __version__ == "0.1.0"


def simulate_cycles(mocker: MockerFixture):

    # Erste Flanke -> Zu start
    mocker.patch("time.time_ns", return_value=100)
    assert create_cycle() is None

    # Zweite Flanke -> Zu ende / Auf start
    mocker.patch("time.time_ns", return_value=110) # Delta 10 sec
    assert create_cycle() is None

    # Dritte Flanke -> Auf ende / Zu start -> Zyl1 fertig
    mocker.patch("time.time_ns", return_value=120) # Delta 10 sec -> 30 Grad zu und auf
    engine_1 = create_cycle()
    assert engine_1 is not None
    assert round(engine_1.get_close_angle_1()) == 30
    assert round(engine_1.get_close_angle_2()) == 30
    assert round(engine_1.get_open_angle_1()) == 30
    assert round(engine_1.get_open_angle_2()) == 30

    # Vierte Flanke -> Zu ende / Auf start
    mocker.patch("time.time_ns", return_value=140) # Delta 20 sec
    assert create_cycle() is None

    # Fuenfte Flanke -> Auf ende / Zu start -> Zyl5 fertig
    mocker.patch("time.time_ns", return_value=153) # Delta 13 sec
    engine_2 = create_cycle()
    assert engine_2 is not None
    assert round(engine_2.get_close_angle_1()) == 36
    assert round(engine_2.get_close_angle_2()) == 36
    assert round(engine_2.get_open_angle_1()) == 23
    assert round(engine_2.get_open_angle_2()) == 23

    # Sechste Flanke -> Zu ende / Auf start
    mocker.patch("time.time_ns", return_value=166) # Delta 13 sec
    assert create_cycle() is None

    # Sechste Flanke -> Auf ende / Zu start -> Zyl3 fetig
    mocker.patch("time.time_ns", return_value=186) # Delta 20 sec
    engine_3 = create_cycle()
    assert engine_3 is not None
    assert round(engine_3.get_close_angle_1()) == 23
    assert round(engine_3.get_close_angle_2()) == 23
    assert round(engine_3.get_open_angle_1()) == 36
    assert round(engine_3.get_open_angle_2()) == 36


def test_angels():
    # 20 sec zu und 13 sec offen
    # -> 36.36363636363637 Grad zu und 23.636363636363637 Grad auf
    ts_start_zu = 10
    ts_end_zu = 30
    ts_end_oeffnen = 43

    total_zu = ts_end_zu - ts_start_zu
    total_offen = ts_end_oeffnen - ts_end_zu
    total_time = ts_end_oeffnen - ts_start_zu

    assert total_zu == 20
    assert total_offen == 13
    assert total_time == 33

    angle_zu = (60 * total_zu) / total_time
    angle_offen = (60 * total_offen) / total_time

    assert int(angle_zu) == 36
    assert int(angle_offen) == 23
    assert round(angle_zu + angle_offen) == 60

    cycle = Cycle(ts_start_zu, ts_end_zu, ts_end_oeffnen)

    assert cycle.total_time == total_time
    assert cycle.total_zu == total_zu

    angle_open_return, angle_close_return = cycle.get_angles()
    assert round(angle_open_return, 3) == round(angle_offen, 3)
    assert round(angle_close_return, 3) == round(angle_zu, 3)

def test_engine():
    # 30 Grad zu und auf
    ts_start_zu = 10
    ts_end_zu = 20
    ts_end_oeffnen = 30

    cycle = Cycle(ts_start_zu, ts_end_zu, ts_end_oeffnen)
    engine = Engine()

    # Add Cycle for cylinder 1 to 6
    engine.add_cycle(1, cycle) # 1
    engine.add_cycle(2, cycle) # 2
    engine.add_cycle(3, cycle) # 3
    engine.add_cycle(4, cycle) # 4
    engine.add_cycle(5, cycle) # 5
    engine.add_cycle(6, cycle) # 6

    assert engine.get_close_angle_1() == 30.0
    assert engine.get_close_angle_2() == 30.0

    assert engine.get_open_angle_1() == 30.0
    assert engine.get_open_angle_2() == 30.0

    with pytest.raises(Exception):
        engine.add_cycle(1, cycle) # 7
