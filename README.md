# uTempFanRelay

Control the "always on" fan that cools the cooling part of the hot end of your printer.

<image src=Fan.png width=30%></image>
![Cool end fan](Fan.png "Cool end fan" =800x) 

## Disclaimers

I have been using this on my Creality Ender 3 for the last two months and it works like a charm. If you decide to use it as well, you need to:
<UL>
<LI>know how your 3D printer works,</LI>
<LI>have basic understanding of electronics and electrical circuits.</LI>
</UL>
USE AT YOUR OWN RISK. I cannot be held responsible for any damage to your printer, property, people or whatsoever happens, good or bad. Anyways, remember:
UNATTENDED 3D PRINTING IS ALWAYS AN HAZARD: always stand by your printer when in use.
NEVER shut down your printer if the nozzle is still hot (above glass temperature of your filament), or you will melt the filament in the part and create clogs.

## Instructions

1. Unplug the fan from the main board 12 or 24V connector
2. connect it to a relay (normally closed contact suggested, but it is configurable later in the plugin)
3. connect the relay driving pin to the RPi (default is GPIO 14, but it is configurable in the plugin)

<image src=Instructions.jpg width=80%></image>

You are ready to go: the tool fan will be on only when you heat the part and anyways when the temperature is higher than a configurable parameter in the plugin setup page.
Use a temperature well below the glass temperature of your filament!!! (i.e. 40 degrees Celsius or below)
Enjoy a silent machine when not in use!!!

## Setup the plugin in Octoprint

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/umbacos/uTempFanRelay/archive/master.zip

Then access the Setup page of the plugin under Octoprint seetup page

## Configuration

Enabled: fan is on only when heating the part or then the part's temperature is above the configured threshold
Disabled: the fan is always on (factory default)

GPIO pin: which pin of the Raspberry PI drives the relay

Normally closed/normally Open: tell the Raspberry how you connected the relay

Temperature threshold: temperature above which the fan is on. Keep it under your filament glass temperature (i.e. do not exceed 40 degrees Celsius)

Screenshot of the settings page:

<image src=screenshot.jpg width=80%></image>
