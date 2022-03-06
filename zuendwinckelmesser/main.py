import threading
import time
from typing import List, Optional

from zuendwinckelmesser.engine import Cycle, Engine

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!")

TRIGGER_ZYL_4_GPIO = 11
SIGNAL_INPUT_GPIO = 15
OUTPUT_SWITCH_GPIO = 35
# ANGLE_OUTPUT = TODO

BOUNCTIME_TRIGGER_ZYL_4 = 100  # in ms
BOUNCTIME_SIGNAL_INPUT = 7  # in ms

CYCLE_ORDER = (1, 5, 3, 6, 2, 4)
CYCLE_COUNTER = 0

zylinder_switch = False  # 0 means 1, 2, 3 and 1 means 4, 5, 6

ts_start_zu: int = 0
ts_end_zu: int = 0
ts_ende_oeffnen: int = 0

engine_buffer: List[Engine] = []


def setup() -> None:
    setup_pins()
    setup_interrups()


def setup_pins() -> None:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(TRIGGER_ZYL_4_GPIO, GPIO.IN)
    GPIO.setup(SIGNAL_INPUT_GPIO, GPIO.IN)
    GPIO.setup(OUTPUT_SWITCH_GPIO, GPIO.IN)
    # GPIO.setup(ANGLE_OUTPUT, GPIO.OUT)


def setup_interrups() -> None:
    GPIO.add_event_callback(SIGNAL_INPUT_GPIO, create_cycle)
    GPIO.add_event_callback(OUTPUT_SWITCH_GPIO, toggle_switch)


def activate_messure() -> None:
    GPIO.add_event_detect(SIGNAL_INPUT_GPIO, GPIO.BOTH)


def create_cycle() -> Optional[Engine]:
    global engine_buffer
    if not ts_start_zu:
        ts_start_zu = time.time_ns()
    elif not ts_end_zu:
        ts_end_zu = time.time_ns()
    elif not ts_ende_oeffnen:
        ts_ende_oeffnen = time.time_ns()

        last_engine = engine_buffer[-1]
        if last_engine.is_engine_full():
            CYCLE_ORDER = 0     # Wenn die letzte Engine voll ist, startet es automatisch bei 0
            engine = Engine.add_cycle(CYCLE_ORDER[CYCLE_COUNTER], Cycle(ts_start_zu, ts_end_zu, ts_ende_oeffnen))
            engine_buffer.append(engine)
        else:
            last_engine.add_cycle(CYCLE_ORDER[CYCLE_COUNTER], Cycle(ts_start_zu, ts_end_zu, ts_ende_oeffnen))

        # Reset
        ts_start_zu = ts_ende_oeffnen
        ts_end_zu = 0
        ts_ende_oeffnen = 0

        CYCLE_COUNTER += 1

        return engine


def output_signal() -> None:
    global engine_buffer
    while True:
        if len(engine_buffer) >= 10:
            engine = engine_buffer.pop(0)
            if zylinder_switch:
                open_angle = engine.get_open_angle_1()
                close_angle = engine.get_close_angle_1()
            else:
                open_angle = engine.get_open_angle_2()
                close_angle = engine.get_close_angle_2()

        else:
            time.sleep(0.050)  # 50ms


def toggle_switch() -> None:
    zylinder_switch = not zylinder_switch


# def my_callback(*args, **kwargs) -> None:
#     print(args)
#     print(kwargs)


def start() -> None:
    """Warte auf Zuendfunke bei Zylinder 4 und starte dann den interrupt fuer das messen"""
    channel = GPIO.wait_for_edge(TRIGGER_ZYL_4_GPIO, GPIO.RISING)
    if channel is None:
        # TODO: Logging
        raise Exception("ERROR")
    else:
        GPIO.add_event_detect(SIGNAL_INPUT_GPIO, GPIO.BOTH, bouncetime=7)
        io_thread = threading.Thread(target=output_signal, daemon=True)
        io_thread.start()


def main():
    try:
        setup()
        start()
    except Exception as error:
        raise error
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
