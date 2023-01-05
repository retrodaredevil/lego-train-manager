import abc
from typing import Callable, Optional, Tuple


class SpeedHandler(abc.ABC):

    @property
    @abc.abstractmethod
    def desired_velocity(self) -> float:
        pass

    @desired_velocity.setter
    @abc.abstractmethod
    def desired_velocity(self, velocity: float):
        pass

    @abc.abstractmethod
    def immediate(self):
        pass

    @abc.abstractmethod
    def update(self) -> float:
        pass


class LinearSpeedHandler(SpeedHandler):

    def __init__(self, acceleration: float, time_getter: Callable[[], float]):
        """
        :param acceleration: The acceleration in velocity per second
        :param time_getter: The function supplying the time in seconds (can be arbitrary, as long as it counts up)
        """
        self.acceleration = acceleration
        self.time_getter = time_getter
        self.current_velocity = 0.0
        self.__desired_velocity = 0.0
        self.__last_time: Optional[float] = None
        self.__needs_update = False

    @property
    def desired_velocity(self) -> float:
        return self.__desired_velocity

    @desired_velocity.setter
    def desired_velocity(self, velocity: float):
        self.__desired_velocity = velocity

    def immediate(self):
        self.current_velocity = self.__desired_velocity
        self.__needs_update = True

    def update(self) -> Tuple[float, bool]:
        """
        :return: A tuple of (velocity, has velocity changed)
        """
        now = self.time_getter()
        last_time = self.__last_time
        self.__last_time = now
        if last_time is None:
            needs_update = self.__needs_update
            self.__needs_update = False
            return self.current_velocity, needs_update

        offset = self.__desired_velocity - self.current_velocity
        if offset == 0.0:
            needs_update = self.__needs_update
            self.__needs_update = False
            return self.current_velocity, needs_update

        max_change = (now - last_time) * self.acceleration
        if abs(offset) < max_change:
            self.current_velocity = self.__desired_velocity
        else:
            self.current_velocity += (1.0 if offset > 0.0 else -1.0) * max_change
            if self.current_velocity > 1.0:
                self.current_velocity = 1.0
            elif self.current_velocity < -1.0:
                self.current_velocity = -1.0
        return self.current_velocity, True

