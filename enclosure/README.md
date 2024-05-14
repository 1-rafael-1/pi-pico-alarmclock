# Enclosure for the Pi-Pico Alarm Clock

This document outlines the design, 3D printing, and assembly process of the enclosure for the Pi-Pico Alarm Clock project.

## Design

The enclosure is designed using Autodesk Fusion. The design consists of two main parts: the bottom and the body.

### Outside

![Enclosure Outside View](/enclosure/enclosure-outside.png)

### Inside

![Enclosure Inside View](/enclosure/enclosure-inside.png)

### Bottom

![Enclosure Bottom View](/enclosure/enclosure-bottom.png)

The bottom part mounts the Raspberry Pi Pico and a few of the smaller components. The battery, the speaker, the buttons, the NeoPixel as well as the display are assembled into the main body.

## Modifying the Design

Most of the components used for this product are manufactured by a great variety of companies, many components being clones of other components. That makes them cheap and readily available but also makes them come in many different sizes.

It is highly likely, that the enclosure will not fit with the components and in that case adjustments have to be made. For this purpose find the Autodesk Fusion Archive File here:

[Fusion Archive File](enclosure.f3d)

This was my very first use of a CAD software, so be warned... that being said, this is how things are organized:

+ For the NeoPixel Ring, find the sketch for the `top` and locate the rectangle that is constrained by construction lines. Change dimensions to alter NeoPixel size or throw all the rectangles out and add Your own (in that case, extrude them).
+ For the Name, find the sketch `Name` and modify the text. As soon as You add letters, these new letters will not be extruded. Extrude from the bottom of the new letters 0.3mm up and that should do the trick.
+ For the buttons I am reasonably sure fitting buttons can be found. If the button design needs changing, a number of things need to be done:
  + sketch `front buttons` is for the holes in the front
  + sketch `front button mount base` is for the mounting of the buttons, part 1
  + sketch `front button mount bridge` is for the mounting of the buttons, part 2
+ For the display (a likely thing that won't fit) You need a hole for the display itself and then because the display has a flat cable on the underside on the front and maybe even also som soldered pins sticking out the front, some depressions in the wall are needed:
  + the display itsef is found in sketch `front`
  + sketch `display cable cover` handles the flat cable
  + sketch `front display pin allowance` handles the pins jutting out on the front side
+ For the speaker edit the sketch `right`
+ For the MicroUSB hole edit sketch `back`. You may want to change that to USB-C depending on the microcontroller used.
+ the sketch `left` is basically just a plain rectangle
+ the sketch `bottom` is almost plain, besides the four pins to attach the bottom to the enclosure. Not the most ideal engineering solution, but works well enough for now.

## 3D Printing

The enclosure is designed to be 3D printed. The STL files for the bottom and the body of the enclosure can be found in the project repository:

+ [Enclosure Body STL](enclosure-body.stl)
+ [Enclosure Bottom STL](enclosure-bottom.stl)

In my case I found that between the slicer and the print I need to add 0.63% to the objects sizes. Calibrate that by printing a plain square and using calipers to find how much the result diverges from the design. This will be very different depending on the filament, the print temperature and probably also on the printer itself.

I used these general settings in my slicer:

+ 2 wall layers and adaptive cubic infill of 15%
+ organic tree support, allow to add supports on the model itself. Supports with 2 wall layers and filled with a honeycomb pattern. They will lean out quite a bit and need to be stronger than usual.
+ no fan for the first 5 layers
+ no raft, no brim - not required in my case when the fan is off for the first few layers
  
## Assembly

TBD