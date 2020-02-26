---
layout: plugin

id: uTempFanRelay
title: uTempFanRelay
description: A hotend tool fan temperature-controlled relay
author: umbacos
license: AGPLv3

date: 2020-02-26

homepage: https://github.com/umbacos/uTempFanRelay
source: https://github.com/umbacos/uTempFanRelay
archive: https://github.com/umbacos/uTempFanRelay/archive/master.zip

tags:
- relay
- hotend
- fan
- silent
- noise
- Ender
- Creality

# TODO
screenshots:
- url: https://github.com/umbacos/uTempFanRelay/screenshot.jpg
  alt: plugin settings page
  caption: settings

featuredimage: https://github.com/umbacos/uTempFanRelay/Instructions.jpg

  os:
  - linux
  - windows
  - macos
  - freebsd
  

  python: ">=2.7,<4"

---

Control the "always on" fan that cools the hot end of your printer.
1. Unplug the fan from the main board 12 or 24V
2. connect it to a relay (normally closed contact suggested, but it is configurable)
3. connect the relay driving pin to the RPi (default is GPIO 14, but it is configurable)
See the schematics at https://github.com/umbacos/uTempFanRelay/Instructions.jpg
You are ready to go: the tool fan will be on only when you heat the part and anyways when the temperature is higher than a configurable parameter in the plugin setup page.
Use a temperature well below the glass temperature of your filament!!! (i.e. 40 degrees Celsius or below)
Enjoy a silent machine when not in use!!!
