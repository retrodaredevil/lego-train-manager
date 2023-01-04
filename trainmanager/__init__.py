import asyncio

from bleak import discover, BleakScanner
from pylgbst import get_connection_bleak
from pylgbst.hub import MoveHub


async def run():
    # devices = await BleakScanner.discover(timeout=10.0)
    # print(f"got devices: {devices}")
    # connection = get_connection_auto()
    connection = get_connection_bleak(hub_name="Lavender Green")
    print(f"Got connection: {connection} mac: {connection.hub_mac}")
    hub = MoveHub(connection)
    print("Made hub")
    hub.led.set_color("red")
    hub.motor_A.timed(1.0, 0.5)
    print("done")


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())


if __name__ == '__main__':
    main()
