# Marlin For Sand Printer by Maajor

<img align="top" width=175 src="buildroot/share/pixmaps/logo/marlin-250.png" />

Forked from Marlin 3D Printer Firmware, repository can be found at [Marlin](https://github.com/MarlinFirmware/Marlin) and documentation at [The Marlin Documentation Project](http://www.marlinfw.org/).



  - Add two more external axis for `G0`: `W` for sand-feeding platform and `S` for a sweeper. For example, we can use `G0 X120 Y100 Z10 W10 S6` now.
  - Finetuned parameters in configuration and pins since my hardware is Arduino Mega2560 + RAMPS1.4 + CNC Shield v3
