# About brickpi fpv #

This repo contains server and client scripts to remote control a Lego Mindstorms car. It's easy to run this from the excellent free VS Code, because it has those nice launch targets.

Hardware used:

* Macbook
* Dexter Industries BrickPi+
* Raspberry Pi 2 model B+ (1x)
* PiCamera (1x)
* Extended 30cm PiCamera ribbon
* WiPi wifi-stick (1x). A belkin or tp-link 2.4G stick should work too.
* PS3 sixaxis gamepad (any gamepad should do)
* Large EV3 motors (3x)


## Installation ##

### Raspberry Pi ###

1. Start with a fresh [ev3dev image](https://www.ev3dev.org/downloads/). 

2. Make sure you [edit config.txt](https://www.ev3dev.org/docs/getting-started/) as explained on the ev3dev getting started page!!

3. Connect to wifi. I was unable to make the Pi connect to WiFi on first boot. So I had to use an external monitor to set that up. A wired ethernet connection should work too. To set up wifi, use [connmanctl](https://www.ev3dev.org/docs/tutorials/setting-up-wifi-using-the-command-line/).

4. To have a video stream with the Picamera install gstreamer.

    ```shell
    sudo apt update
    sudo apt install gstreamer1.0 python3-pip
    pip3 install picamera
    ```



## Mac OS X & VS Code installation ##

1. It's easiest if you start by installing [homebrew](http://brew.sh).

2. Next, get sdl2 and gstreamer:

    ```shell
    brew install sdl2 gstreamer gst-plugins-good gst-plugins-bad
    pip3 install pysdl2
    ```

3. In VSCode, be sure to get these extensions from the marketplace:
    * LEGO MINDSTORMS EV3 Python
    * Python
    * Not necessary, but awesome anyway: Nasc VSCode Touchbar.

4. When you have all the extensions, open a new main window. (cmd-shift-N)

5. Open the command palette (cmd-shift-P or F1) and type 'Git clone' + enter

6. Paste the URL of this repository

7. Choose a nice location to save it


## Running the scripts ##

On Mac Os X I run VSCode which has very nice launch target configurations. They are included.

1. Open 'ev3dev device browser' at the very bottom left of your screen
2. Right click your ev3dev device and choose connect or reconnect
3. Open the command palette (cmd-shift-P or F1) and type 'select and start debugging' + enter
4. Select 'Run server on ev3 and rc script'


## Known issues ##
This scripts are a collection of hacks. There is little error catching. Results might be unpredictable with different hardware. Some contributions to better error handling would be appreciated.