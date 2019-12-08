# About #

This repo contains server and client scripts to remote control a Lego Mindstorms car. 

Hardware used:
* Macbook
* Dexter Industries BrickPi+
* Raspberry Pi 2 model B+ (1x)
* PiCamera (1x)
* Extended 30cm PiCamera ribbon
* WiPi wifi-stick (1x). A belkin or tp-link 2.4G stick should work too.
* PS3 sixaxis gamepad (any gamepad should do)
* Large EV3 motors (3x)


# Running the scripts #
TODO

# Known issues #
TODO

# Installation #

## Raspberry Pi ##
1. Start with a fresh [ev3dev image](https://www.ev3dev.org/downloads/). I used Debian Wheezy. 

2. Make sure you [edit config.txt](https://www.ev3dev.org/docs/getting-started/) as explained on the ev3dev home page!!

3. Connect to wifi. I was unable to make the Pi connect to WiFi on first boot. So I had to use an external monitor to set that up. A wired ethernet connection should work too. To set up wifi, use [sudo connmanctl](https://www.ev3dev.org/docs/tutorials/setting-up-wifi-using-the-command-line/)

4. To have a video stream install gstreamer. 
right away.
```shell
sudo apt update
sudo apt install gstreamer1.0 python3-pip
```

5. Install the python Picamera library for controlling the camera inside our python scripts
```
pip3 install picamera
```


## On the Mac ##
On Mac Os X I run VSCode which has very nice [launch target configurations](https://stackoverflow.com/questions/35327016/using-prelaunchtasks-and-naming-a-task-in-visual-studio-code). They are included in the repo, so you should be able to use them.

It's easiest if you start by installing [homebrew](http://brew.sh). I'm a big fan. 

Next, get sdl2 and gstreamer:
```shell
brew install sdl2 gstreamer gst-plugins-good
```

Next get the needed python libraries. If you don't have (or want hg) you can also download the whole repo, of course.
```
pip3 install pysdl2
```

I have built VS Code L

## Is this also needed? ##
TODO: Check.
We might also need this [gst-python](http://gstreamer.freedesktop.org/src/gst-python/)



gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, payload=96, width=1280, height=720 ! rtpjitterbuffer ! rtph264depay ! decodebin ! glimagesink