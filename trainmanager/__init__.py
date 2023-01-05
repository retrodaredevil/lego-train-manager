import logging

from bricknil import start

from trainmanager.trains import GreenTrain, CrocodileTrain, RemoteControl


async def system():
    green = GreenTrain('Lavender Green')
    # crocodile = CrocodileTrain('Lavender Orange')
    # RemoteControl(green, crocodile)
    RemoteControl(green, None)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start(system)
