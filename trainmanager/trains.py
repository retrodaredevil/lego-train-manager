import time
from typing import Optional

from bricknil import attach
from bricknil.const import Color
from bricknil.hub import PoweredUpHub, PoweredUpRemote
from bricknil.sensor import TrainMotor, LED, Light, RemoteButtons, Button
from bricknil.sensor.motor import CPlusLargeMotor, ExternalMotor
from curio import sleep

from trainmanager.managedtrain import ManagedTrain, StopType, LightLevel
from trainmanager.speed import LinearSpeedHandler


@attach(RemoteButtons, name='left_buttons', port=RemoteButtons.Port.L, capabilities=["sense_press"])
@attach(RemoteButtons, name='right_buttons', port=RemoteButtons.Port.R, capabilities=["sense_press"])
@attach(Button, name='green_button')
class RemoteControl(PoweredUpRemote):

    def __init__(self, train_a: Optional[ManagedTrain], train_b: Optional[ManagedTrain], **kwargs):
        super().__init__("Handset", *kwargs)
        self.train_a = train_a
        self.train_b = train_b
        self.left_buttons: Optional[RemoteButtons] = None
        self.right_buttons: Optional[RemoteButtons] = None
        self.green_button: Optional[Button] = None

    def all_halt(self):
        if self.train_a is not None:
            self.train_a.stop(StopType.HALT)
        if self.train_b is not None:
            self.train_b.stop(StopType.HALT)

    def check_all_halt(self) -> bool:
        return self.left_buttons.red_pressed() and self.right_buttons.red_pressed()

    async def run(self):
        while True:
            await sleep(999)

    @staticmethod
    def on_change(buttons: RemoteButtons, train: ManagedTrain):
        if buttons.red_pressed():
            if buttons.plus_pressed():
                if train.has_light:
                    current_light = train.light_level
                    if current_light is LightLevel.OFF:
                        new_level = LightLevel.LOW
                    elif current_light is LightLevel.LOW:
                        new_level = LightLevel.HIGH
                    else:
                        new_level = LightLevel.OFF
                    train.light_level = new_level
                else:
                    print("Light not supported on this train!")
            elif buttons.minus_pressed():
                pass
            else:
                train.stop(StopType.NORMAL)
        else:
            direction = 0
            if buttons.plus_pressed():
                direction += 1
            if buttons.minus_pressed():
                direction -= 1
            if direction != 0:
                train.increment_speed(direction)

    async def left_buttons_change(self):
        if self.check_all_halt():
            self.all_halt()
            return
        if self.train_a is not None:
            self.on_change(self.left_buttons, self.train_a)

    async def right_buttons_change(self):
        if self.check_all_halt():
            self.all_halt()
            return
        if self.train_b is not None:
            self.on_change(self.right_buttons, self.train_b)

    async def green_button_change(self):
        is_pressed = self.green_button.value[0] == 1  # get first element of byte array
        print(f"green pressed: {is_pressed}")


@attach(TrainMotor, name='motor')
@attach(LED, name='hub_led')
@attach(Light, name='train_light')
class GreenTrain(PoweredUpHub, ManagedTrain):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.motor: Optional[TrainMotor] = None
        self.hub_led: Optional[LED] = None
        self.train_light: Optional[Light] = None
        self.speed_handler = LinearSpeedHandler(1.0/2.0, time.time)

        self.__light_level = LightLevel.OFF
        self.__update_light_level = False

    @property
    def has_light(self) -> bool:
        return True

    @property
    def light_level(self) -> LightLevel:
        return self.__light_level

    @light_level.setter
    def light_level(self, level: LightLevel):
        if level != self.__light_level:
            self.__light_level = level
            self.__update_light_level = True

    def stop(self, stop_type: StopType):
        self.speed_handler.desired_velocity = 0.0
        if stop_type is StopType.HALT:
            self.speed_handler.immediate()

    def increment_speed(self, amount: int) -> bool:
        new_speed = round(self.speed_handler.desired_velocity * 10 + amount) / 10.0
        if new_speed > 1.0 and self.speed_handler.desired_velocity == 1.0:
            return False
        if new_speed < -1.0 and self.speed_handler.desired_velocity == -1.0:
            return False
        self.speed_handler.desired_velocity = new_speed
        return True

    async def run(self):
        await self.hub_led.set_color(Color.black)
        current_color = Color.black
        while True:
            now = time.time()
            period_clock = now % 2.0
            if period_clock < 0.3:
                desired_color = Color.green
            else:
                desired_color = Color.black
            if desired_color != current_color:
                await self.hub_led.set_color(desired_color)
                current_color = desired_color

            if self.__update_light_level:
                self.__update_light_level = False
                level = self.__light_level
                if level is LightLevel.OFF:
                    brightness = 0
                elif level is LightLevel.LOW:
                    brightness = 30
                else:
                    brightness = 100
                print(f"Brightness now: {brightness}")
                await self.train_light.set_brightness(brightness)
            new_velocity, is_updated_velocity = self.speed_handler.update()
            if is_updated_velocity:
                speed = round(new_velocity * 100)
                await self.motor.set_speed(speed if speed != 0 else 127)  # use 127 for hard brake (documentation is wrong)
            await sleep(0.1)


@attach(ExternalMotor, name='motor')
@attach(LED, name='hub_led')
class CrocodileTrain(PoweredUpHub, ManagedTrain):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.speed_handler = LinearSpeedHandler(1.0/4.0, time.time)
        self.motor: Optional[ExternalMotor] = None
        self.hub_led: Optional[LED] = None

    @property
    def has_light(self) -> bool:
        return False

    @property
    def light_level(self) -> LightLevel:
        raise NotImplementedError()

    def stop(self, stop_type: StopType):
        self.speed_handler.desired_velocity = 0.0
        if stop_type is StopType.HALT:
            self.speed_handler.immediate()

    def increment_speed(self, amount: int) -> bool:
        new_speed = round(self.speed_handler.desired_velocity * 10 + amount) / 10.0
        if new_speed > 1.0 and self.speed_handler.desired_velocity == 1.0:
            return False
        if new_speed < -1.0 and self.speed_handler.desired_velocity == -1.0:
            return False
        self.speed_handler.desired_velocity = new_speed
        return True

    async def run(self):
        await self.hub_led.set_color(Color.black)
        while True:
            new_velocity, is_updated_velocity = self.speed_handler.update()
            if is_updated_velocity:
                await self.motor.set_speed(round(new_velocity * 100))
            await sleep(0.02)

