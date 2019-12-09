__author__ = 'Antons Mindstorms Hacks'

import socket
import sdl2
import time
import subprocess
import shlex
from helpers import scale, Throttler
from settings import VIDEO_ENABLED, EV3_HOST, DATA_PORT, PC_HOST, DATA_RATE,\
    SIXAXIS

try:
    import cPickle as pickle
except:
    import pickle


# ______ Constants & configuration ______ #

# initialise joysticking
error = sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
numsticks = sdl2.SDL_NumJoysticks()
for stick in range(numsticks):
    name = sdl2.SDL_JoystickNameForIndex(stick)
    print("Name of stick {} is {}".format(stick, name))
    if name == b"PLAYSTATION(R)3 Controller":
        gamepad_obj = sdl2.SDL_JoystickOpen(stick)
        if sdl2.SDL_JoystickNumAxes(gamepad_obj) == 4:
            break

# Gamepad config
gamepad = SIXAXIS.copy()
gamepad['gp_object'] = gamepad_obj

# Robot configuration, bind sticks and buttons to motors
robot_config = {
    'motors': {
        'steer': {
            'port': "A",
            'control': 'right_h',
            'type': 'servo',
            'range': (50, -50),
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
    # print(gp_state)
    return gp_state


# _____ Initialization _____ #

# Open socket to the Raspberry Pi
time.sleep(3)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((EV3_HOST, DATA_PORT))

# Send our IP address across, and maybe some other config info
# handshake = {'ip_addr': socket.gethostbyname(socket.gethostname())} 
# the slower way is: socket.gethostbyname(socket.getfqdn())
# Alas the above doesn't work on all networks. Manual ip config is more robust.
handshake = {'ip_addr': PC_HOST, 'robot_config': robot_config}
msg = pickle.dumps(handshake)
s.send(msg)
time.sleep(3)

# Wait for answer
data = s.recv(1024*2)
print('Handshake rcv:', pickle.loads(data))

# New throttler #TODO refactor this name to a more legible one.
wait = Throttler(DATA_RATE)

# ______ Main processes _____ #
# Start video player if needed
if VIDEO_ENABLED:
    cmd = "gst-launch-1.0 udpsrc port=5000 ! application/x-rtp, payload=96 ! rtpjitterbuffer ! rtph264depay ! decodebin ! autovideosink sync=false text-overlay=false"
    args = shlex.split(cmd)
    vidprocess = subprocess.Popen(args, stdin=subprocess.PIPE)

while 1:
    try:
        gp_data = get_gamepad_state(gamepad)
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
        if VIDEO_ENABLED:
            print("Cleaning up video...")
            vidprocess.terminate()
            break
            raise
