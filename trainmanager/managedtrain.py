import abc
from enum import Enum

LightLevel = Enum("LightLevel", ["OFF", "LOW", "HIGH"], start=0)
StopType = Enum("StopType", ["HALT", "NORMAL", "GRACEFUL"], start=0)


class ManagedTrain(abc.ABC):
    @property
    @abc.abstractmethod
    def has_light(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def light_level(self) -> LightLevel:
        pass

    @light_level.setter
    @abc.abstractmethod
    def light_level(self, level: LightLevel):
        pass

    @abc.abstractmethod
    def stop(self, stop_type: StopType):
        pass

    @abc.abstractmethod
    def increment_speed(self, amount: int) -> bool:
        """

        :param amount:
        :return: True if successful (even if a limit is hit), False if no change
        """
        pass

