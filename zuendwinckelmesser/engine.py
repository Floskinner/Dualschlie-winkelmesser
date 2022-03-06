from typing import List, Tuple, Dict
import statistics


class Cycle:

    # angle of one zylinder
    full_cycle = 60

    def __init__(self, ts_start_zu: int, ts_end_zu: int, ts_ende_oeffnen: int) -> None:
        self.ts_start_zu = ts_start_zu
        self.ts_end_zu = ts_end_zu
        self.total_zu = ts_end_zu - ts_start_zu

        self.ts_start_offen = self.ts_end_zu
        self.ts_end_offen = ts_ende_oeffnen

        self.total_time = ts_ende_oeffnen - ts_start_zu

    def get_angles(self) -> Tuple[float, float]:
        """Calculate the angle of one zuendung

        Returns:
            Tuple[float, float]: (open_angle, close_angle)
        """
        close_angle = self.full_cycle / self.total_time * self.total_zu
        open_angle = self.full_cycle - close_angle
        return (open_angle, close_angle)


class Engine:
    def __init__(self) -> None:
        self.full_cycel: Dict[int, Cycle] = {}

    def add_cycle(self, zylinder: int, cycle: Cycle) -> None:
        if not self.is_engine_full():
            self.full_cycel[zylinder] = cycle
        else:
            # TODO: Only logging
            raise Exception("More than 6 Cycle in one engine is not valid!")

    def is_engine_full(self) -> bool:
        """
        Returns:
            bool: True if Engine is full
        """
        return len(self.full_cycel) >= 6

    def get_open_angle_1(self) -> float:
        """Return the median open angle of the zylinder 1, 2, 3

        Returns:
            float: Angle of the ignition time
        """
        angels = []
        angels.append(self.full_cycel.get(1).get_angles()[0])
        angels.append(self.full_cycel.get(2).get_angles()[0])
        angels.append(self.full_cycel.get(3).get_angles()[0])
        return statistics.median(angels)

    def get_close_angle_1(self) -> float:
        """Return the median close angle of the zylinder 1, 2, 3

        Returns:
            float: Angle of the ignition time
        """
        angels = []
        angels.append(self.full_cycel.get(1).get_angles()[1])
        angels.append(self.full_cycel.get(2).get_angles()[1])
        angels.append(self.full_cycel.get(3).get_angles()[1])
        return statistics.median(angels)

    def get_open_angle_2(self) -> float:
        """Return the median open angle of the zylinder 4, 5, 6

        Returns:
            float: Angle of the ignition time
        """
        angels = []
        angels.append(self.full_cycel.get(4).get_angles()[0])
        angels.append(self.full_cycel.get(5).get_angles()[0])
        angels.append(self.full_cycel.get(6).get_angles()[0])
        return statistics.median(angels)

    def get_close_angle_2(self) -> float:
        """Return the median close angle of the zylinder 4, 5, 6

        Returns:
            float: Angle of the ignition time
        """
        angels = []
        angels.append(self.full_cycel.get(4).get_angles()[1])
        angels.append(self.full_cycel.get(5).get_angles()[1])
        angels.append(self.full_cycel.get(6).get_angles()[1])
        return statistics.median(angels)
