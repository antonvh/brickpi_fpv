__author__ = 'Antons Mindstorms Hacks'

import socket
import sdl2
import time
import subprocess
import shlex
from helpers import scale, Throttler

try:
    import cPickle as pickle
except:
    import pickle

############Constants & configuration################

# Start a gstreamer instance to receive streaming video if true.
RCV_VIDEO = True

# Remote host configuration for opening sockets
HOST = 'ev3dev'  # The remote RPi with the server script running. Can also be ip number.
PORT = 50007  # The same port as used by the server
MY_IP = '192.168.188.22'

# General speed of the program
FRAMERATE = 30  # Number of loops (packets to send) per second

# initialise joysticking
sticks = sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)

# Gamepad config
sixaxis = {
    'gamepad_num': 0,
    'gp_object': sdl2.SDL_JoystickOpen(0),  # sixaxis is the first gamepad on my system
    'stick_range': (-32768, 32768),  # min stick position, max stick position. Input range.
    'sticks': {
        'right_h': {'id': 2, 'invert': 1},
        'right_v': {'id': 3, 'invert': 1},
        'left_h': {'id': 0, 'invert': 1},
        'left_v': {'id': 1, 'invert': -1}
    },
    'btns': {
        'dpad_up': 4,
        'dpad_right': 5,
        'dpad_down': 6,
        'dpad_left': 7,
        'btn_l2': 8,  # bottom shoulder buttons
        'btn_r2': 9,
        'btn_l1': 10,  # top shoulder buttons
        'btn_r1': 11,
        'btn_A': 14,
        'btn_B': 13,
        'btn_X': 15,
        'btn_Y': 12,
        'btn_start': 3,
        'btn_select': 0
    }
}

# Robot configuration, bind sticks and buttons to motors
robot_config = {
    'motors': {
        'steer': {
            'port': "A",
            'control': 'right_h',
            'type': 'servo',
            'range': (-100, 100),
            'trim_down': ['dpad_left'],
            'trim_up': ['dpad_right'],
            'trim_step': 5
        },
        'drive1': {
            'port': "B",
            'control': 'left_v',
            'type': 'dc',
            'range': (-100, 100),
        },
        'drive2': { 
            'port': "C",
            'control': 'left_v',
            'type': 'dc',
            'range': (-100, 100),
        },
    },
    'sensors': {}
}


def scaled_stick_value(gp, axis, invert, deadzone_pct=4):
    stick_value = scale(sdl2.SDL_JoystickGetAxis(gp['gp_object'], axis),
                        gp['stick_range'],
                        (-32768, 32768)
                        ) * invert

    deadzone_range = tuple(n * deadzone_pct / 100.0 for n in (-32768, 32768))

    if min(deadzone_range) < stick_value < max(deadzone_range):
        return 0
    else:
        return int(stick_value)


def get_gamepad_state(gp):
    # update joystick info
    sdl2.SDL_PumpEvents()
    gp_state = {}

    for stick in gp['sticks']:
        gp_state[stick] = scaled_stick_value(gp, gp['sticks'][stick]['id'], gp['sticks'][stick]['invert'])

    for btn in gp['btns']:
        gp_state[btn] = sdl2.SDL_JoystickGetButton(gp['gp_object'], gp['btns'][btn])
        # This way a pressed button outputs a number equivalent
        # to a fully bent stick
    print(gp_state)
    return gp_state


#################### Initialization #################

# Open socket to the Raspberry Pi
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# Send our IP address across, and maybe some other config info
# handshake = {'ip_addr': socket.gethostbyname(socket.gethostname())} 
# the slower way is: socket.gethostbyname(socket.getfqdn())
# Alas the above doesn't work on all networks. Manual ip config is more robust.
handshake = {'ip_addr': MY_IP, 'robot_config': robot_config}
msg = pickle.dumps(handshake)
s.send(msg)
time.sleep(3)

# Wait for answer
data = s.recv(1024*2)
print('Handshake rcv:', pickle.loads(data))

# New throttler #TODO refactor this name to a more legible one.
wait = Throttler(FRAMERATE)

# Start video player if needed
if RCV_VIDEO:
    cmd = "gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, payload=96 ! rtpjitterbuffer ! rtph264depay ! decodebin ! autovideosink sync=false text-overlay=false"
    args = shlex.split(cmd)
    vidprocess = subprocess.Popen(args, stdin=subprocess.PIPE)


################### Main Loop #######################

while 1:
    try:
        gp_data = get_gamepad_state(sixaxis)
        msg = pickle.dumps(gp_data)
        # print(gp_data)  # debug
        s.send(msg)

        # read back to make sure we can send again. 
        # Also nice to get sensor readings.
        data = s.recv(1024*2)  
        rcv = pickle.loads(data)
        print(rcv)
        wait.throttle()
    except: 
        if RCV_VIDEO:
            print("Cleaning up video...")
            vidprocess.terminate()
            break
