from typing import Optional

from bricknil.const import Color
from curio import sleep
from bricknil import attach, start
from bricknil.hub import PoweredUpHub
from bricknil.sensor import TrainMotor, LED, Light
import logging


@attach(TrainMotor, name='motor')
@attach(LED, name='hub_led')
@attach(Light, name='train_light')
class GreenTrain(PoweredUpHub):

    def __init__(self, args, **kwargs):
        super().__init__(args, *kwargs)
        self.motor: Optional[TrainMotor] = None
        self.hub_led: Optional[LED] = None
        self.train_light: Optional[Light] = None

    async def run(self):
        self.message_info("Running")
        await self.train_light.set_brightness(100)
        for i in range(2):
            self.message_info('Increasing speed')
            await self.hub_led.set_color(Color.black)
            await self.motor.ramp_speed(80,5000)
            await sleep(5)
            self.message_info('Coming to a stop')
            await self.hub_led.set_color(Color.red)
            await self.motor.ramp_speed(0,1000)
            await sleep(2)


async def system():
    train = GreenTrain('Lavender Green')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start(system)
