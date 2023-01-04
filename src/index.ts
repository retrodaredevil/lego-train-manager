
import PoweredUP from "node-poweredup";
const poweredUP = new PoweredUP();

poweredUP.on("discover", async (hub) => { // Wait to discover a Hub
    console.log(`Discovered ${hub.name}!`);
    const promise: Promise<any> = hub.connect();
    const success = promise.then(result => {
        return true;
    }, reason => {
        console.error("Got an error");
        console.error(reason);
        poweredUP.scan();
        return false;
    });
    if (!success) {
        console.log("Did not get success!");
        return;
    }
    poweredUP.scan();
    const motorA = await hub.waitForDeviceAtPort("A"); // Make sure a motor is plugged into port A
    console.log("Connected");

    while (true) { // Repeat indefinitely
        console.log("Running motor B at speed 50");
        console.log("Running motor A at speed 100 for 2 seconds");
        motorA.setPower(10); // Run a motor attached to port A for 2 seconds at maximum speed (100) then stop
        await hub.sleep(2000);
        motorA.brake();
        await hub.sleep(1000); // Do nothing for 1 second
        console.log("Running motor A at speed -30 for 1 second");
        motorA.setPower(-30); // Run a motor attached to port A for 2 seconds at 1/2 speed in reverse (-50) then stop
        await hub.sleep(2000);
        motorA.brake();
        await hub.sleep(1000); // Do nothing for 1 second
    }
});

poweredUP.scan(); // Start scanning for Hubs
console.log("Scanning for Hubs...");