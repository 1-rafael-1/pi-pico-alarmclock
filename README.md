# pi-pico-alarmclock

Building a working alarmclock based on a Raspberry Pi Pico W

The general idea is to build a device that can reliably wake up my kids who are in an age range, where this is a challenge. So it should sport these features:

+ be somewhat Star wars - themed (not my idea)
+ have a display that shows the time and some other information
+ have a speaker that can play music or sounds, and loudly so
  + have a way to hold music/sound files for that purpose
+ have a thingy that can turn on a bright light, ideally an array of RGB LEDs or some such. Because "when my room is still dark, I cannot properly wake up"
+ have some buttons to set the alarm time and to toggle the alarm
  + without making it too easy to silence the actual alarm when it is going off
+ have the ability to both run on battery power or be powered by a USB charger
+ be built into some enclosure that looks nice, is easy enough to print and assemble and can somehow house the components in a sensible way
+ be fun for daddy to build and program

State of affairs: Wiring and coding is done. There is one issue left to fix (Sound is unreliable, will not turn on as expected 50% of the time).
So this is next: Figure out this bug and then off to designing&printing a case.

## Disclaimer

This project is one of my first projects using MicroPython and electronics. I have some background in software development with niche/proprietary languages and no background at all in electronics and Python. So most of this I figured out as I went.
That being said: This is going to be full of imperfections. Use any of this at Your own risk and in case You spot my mistakes, I am glad to hear of them! Besides that I am happy if this is useful or fun for somebody.

## Description

+ The display shows the current time. A lightsaber-symbol indicates, if the alarm is active or not. A battery indicator shows the battery charge or indicated the device is currently usb-powered.
+ To get the current time, on startup and every 6 hours subsequently the device will connect to Wifi, get the time from a timeserver and update the RTC with that.
+ Button-driven operations:
  + The green button will toggle the alarm active/inactive, when in normal operation mode
  + The yellow button will toggle system info being displayed or the normal time mode being displayed
  + The blue button will enter the mode for setting the alarm time. The current alarm time will be displayed (blinking) and the top area will display a symbol indicating that we are doing some sort of setup.
    + In this mode the green button will increase the hour digits and the yellow button will increase the minutes digits. Pressing blue again will save the new alarm time and resume normal operation.
+ Analog clock: The NeoPixel will show an approximation of an analog clock when in normal operation. The blue light indicates seconds, the green light indicates minutes and the red one indicates hours. When hands meet, their color is mixed. (I know... but I had way too much fun)
+ Alarm:
  + 5 Minutes before the alarm time the NeoPixel will turn off the analog clock and simulate a sunrise, going from few and red lights to more and warm-white lights.
  + At the same time in the indicator area of the display we will show a random color as text, using the button colors. Pressing the appropriate button will proceed to show the next color, until one has pressed all three buttons in the order the device wanted them. Completing the sequence will abort the alarm at any stage. The assumption is: If You are awake enough to have found and pressed the buttons in the random order that You were presented, You should be awake enough to get out of bed.
  + At the actual alarm time the sunrise will becompleted and the NeoPixel will display some fancy lighshow-things. At the same time the Music starts tom play, in my case here I chose the Imperial March, because that is what the kids love.

![Prototype on breadboard](wiring/prototype-breadboard.png)

## Code

The code project is structured into these main parts: `main.py`, `classes`, and `drivers` as well as `settings` and `media`. 

|part|contents|
|:--|:--|
|main.py|Main script, doing very little besides instantiating.|
|drivers|Drivers and helpers for specific components. I have written none of these myself, each file has a comment saying where I found it.|
|classes|Classes for each logical component used in this project.|
|settings|A few `json` files to remember settings and magic strings.|

One file in settings is not checked into this repository for obvious reasons. Add one `wifi.json` to settings, structured like this:

```json
{
    "ssid": "YOUR SSID",
    "password": "YOUR PASSWORD"
}
```

### Testing and Tests

After a while this projects code got quite messy and I spent a fair amount of time restructuring it into classes with a small brother of dependency injection. This not only helped me to escape dependency hell but also allows for easy mocking and testing in isolation. I did write some tests here and there, typically where I ran into some problem that i was too lazy to iron out by manually testing the full application over and over again. None of this is perfect, but it sure was fun to do.

What I still sorely miss is a way to debug MicroPython Code. Writing anything remotely complex without is no fun.

### media

The folder contains images used for displaying things on the OLED display. The OLED driver provides only very limited support for text, there is no way i found to change font, font size and also (not an issue here) we cannot display all German letters. So if one wants some nicer numbers, some nice state indicators and the like one has to use images. I have used [GIMP](https://www.gimp.org/) to create these images. I have used the `Export as...` function to export them as 'pbm' files. They have to be converted to indexed color and when exporting to pbm they have to be exported as 'raw' format. The OLED driver can then read these files and display them on the screen.

A really good tutorial on how to create these images can be found [here](https://blog.martinfitzpatrick.com/displaying-images-oled-displays/). I would not have figured this out without.

## Components and Wiring

The central part of this project is the Raspberry Pi Pico W. I am sure everything could be done with a different microcontroller, as long as MicroPython is supported. I chose the Pico W because... I had one.

### Components

|Component|Description|
|---------|---------|
|Microcontroller|Raspberry Pi Pico W|
|OLED Display|SSD1306 compatible I²C OLED Display 128*64 pixels with two color yellow/blue. Input Voltage 3.3V - 5V, but must support 3.3V because that is what we are using. Single-color will work just as well, since the colors are actually fixed to sections of the display and cannot be coded.|
|battery|I use a 18650 Lithium-Polymer battery with 3350mAh. Anything else will work, als long as it fits with the charger module, battery holder and puts out no more than 5V, since You will be plugging it into Pi Pico and the step-up-converter.|
|battery holder|really anything will do, that can hold one Lithium-Polymer unit. Consider adding a switch between battery and charger or be as lazy as me and take out the battery whenever You want to truly power down.|
|charger module|I used a TC4056A module, capable of drawing power from Micro-USB or input pads and capable to charge/discharge the above battery safely.|
|NeoPixel ring|I used WS2812B with 16 RGB LED on it. If You want more LED make sure to check if You can power them safely. Each LED will draw ~60mA and that quickly exceeds either the 300mA the Pico can supply directly or what the step-up-converter attached to the USB or battery power supplies can deliver. In my case here the step-up-converter is rated for 1000mA and so this should be okay.|
|step-up converter|A step up capable to convert 2.5V - 5V to steady 5V. I used BS01 (sometimes found as MT-3608 or HW-085). Required to power the NeoPixel-Ring. There are a ton of these things available everywhere, make sure it is DC-DC and can put out 1000mA for 5V and can convert to that from whatever You expect to come out of Your power supply.|
|speaker|I have used DFplayer Mini 3 Watt 8 Ohm speaker, 70*30*15mm. They can be found in some flavors from multiple vendors. Depending on the form factor You may need to adjust the case, but I guess that cannot be helped since there are so many different of these speakers around.|
|p-channel MOSFET|Two used to switch power modules. I have used IRF9540 which is overkill and and more efficient options exist. These things are rated for up to 100V and the switching voltage is uncomfortably close to USB typical ~5V. So, maybe they now have a higher voltage drop from source to drain, than I would like.|
|n-channel MOSFET|One used to control power supply to mp3 module. I have used IRLZ44N.|
|Schottky diode|One used to prevent power from flowing back into Pi Picos VBUS when powering from battery. Anything rated for up to 5V will do.|
|mp3 module|I have used DFR0299 (DFPlayer), which was easy to wire. It has a micro-sd card slot and an internal amplifier, greatly reducing overall complexity compared to other solutions I found. Also unfortunately my last struggle left... not yet reliable.|
|micro sd card|Really, anything You have lying around, formatted to FAT32.|
|push button|Three used. 13mm diameter, 8mm hight caps on 12x12x7.3mm button - these should be fairly standard. One caps each in yellow, green and blue.|

### Wiring

Here is my best attempt at a wiring diagram. I have used [Circuit Diagram](https://www.circuit-diagram.org/) to create it.

![Alarm Clock Circuit Power Bypassing Pico](wiring/circuit.png)

A few things to note here:

+ The buttons are debounced in code, so they have no debouncing circuits.
+ The mp3-module does not normally require a switchable power supply. In my case here I struggled with the DFPlayer I bought, it just would not work anymore after a certain time of idling. The same problem could be replicated by sending it into standby. Not all drivers I found even have the wake-up command implemented and even the ones I tested with never seemed to wake the device up again. At the same time the mp3-module is the most unused one in this entire application, but draws 20mA regardless of whether it does anything or not. So: I decided to power it up and down as needed. To achieve this I used an n-channel-MOSFET. The gate is connected to a GPIO and source to drain sit between the power and the device. That way I can pull the GPIO high to allow the mp3-module to be powered and pull it back low as soon as I do not need it any more. Solves my standby issue and enhances battery life.
+ The power circuit is strongly inspired by the Raspberry Pi Pico documentation. I use one p-channel-MOSFET to cut power from the battery supply, as long as VBUS is powered externally. This is achieved by running a wire from VBUS to the MOSFET gate (VBUS is directly connected to the Micro-USB of the Pico). The second p-channel-MOSFET is used in the same fashion to cut power from the battery to the NeoPixel, as long as VBUS is powered.
+ The NeoPixel needs 5V and so is either supplied from VBUS or from the battery via the step-up-converter. The wire from VBUS to the step-up-converter has a Schottky-diode to prevent power from backfeeding into VBUS when powered from the battery. 
  
### Enclosure and Assembly

See [enclosure](/enclosure/README.md) for information on hoe to print and assemble.

### Power Consumption

These are the assumptions I made regarding power consumption. I did not measure any of these but researched online to arrive at some idea. In general my calculation based on these assumptions matches what I can observe.

|Component|Current (mA)|Current (Ah)|
|:--|:--|:--|
|Pi Pico|40.00|0.04|
|OLED|11.00|0.011|
|NeoPixel|18.00|0.018|
|all Wires, Diodes, MOSFET|8.00|0.0080|
|Step-up-converter loss|4.30|0.0043|

The DRF0299 mp3-module is powered down the entire time, until it needs to play the alarm sound. After that it is powered down again. I am not inclufing it in the above table. In the specs it is rated for 20mA when powered.

The NeoPixel is only active when the alarm is not active and of course during alarm. I put it into the table, as a worst-case scenario where it is never switched off.

The hardest part to put a number on is the Pi Pico itself. Online sources say that under full load it consumes a fraction under .1Ah but then I do not put it under very much load here. On the other hand we also never not use the Pico, there is at least one timer firing every 3.7s to drive the analog clock. I am also still unsure if the main loop iterating over `sleep`n and then `idle` is really the best way to keep the application alive, power-wise. Anyway, I guessed .04Ah for constantly doing stuff but not doing very heavy calculations.

For the OLED I found sources where people measured power consumption of similar devices and from one diagram I found I took the .011Ah. For the NeoPixel I found in the specs that one uses 60mA on full power. The analog clock running most of the time has three LEDs on at 10% brightness, so that should be .018Ah. For all the wires and MOSFET and the diode I basically asked ChatGPT for typical loss and got a fairly believable answer, broken down into a number of assumptions. Best I have, so that would be .0085Ah. The step-up converter actually has an efficiency in the specs and that could be used to calculate the power loss with some accuracy, but in my case here the step-up will either be used to convert from ~5V to 5 or if the battery is powering the battery will be at a voltage somewhere between 2.5V and 4V... so the conversion required will differ all the time. So I assume we will be on 3.5V input on average and to be safe I assume on average 90% efficiency and that ends us at .0043Ah.

So here is what I did to reduce power consumption:

+ **Pico**: The microcontroller is the most power-hungry component by a long shot. The only reason we need it doing things frequently is the seconds hand on the analog clock. I reduced clock speed to 80Mhz in normal operation, when the NeoPixel is not needed. Unfortunately one has to use the full frequency if the NeoPixel is used, because it is driven by state machines and they in turn cycle with the clock -> anything else than 125Mhz throws the timing off balance and the Neopixel will show weird things. I tried to go lower than 80Mhz, but then the OLED Display starts acting strangely.
+ **OLED**: Is not needed at full brightness and should use less power when dimmed. For now I have set contrast to 10 (maximum is 255), that is bright enough.
+ I managed to cut the power to DFPlayer while not used - actually when troubleshooting it not returning from sleep and requiring a fair bit of additional wiring.
+ I managed to cut power to Wifi while not used - also actually when trobleshooting it not being capable of reconnecting properly.

So... before all that I observed ~36h of battery life. I am curious if I now can do better.