# Video config
VIDEO_ENABLED = True
RASPIVID_CMD = "raspivid -t 999999 -b 2000000 -rot 90 -o -"
STREAM_CMD = "gst-launch-1.0 -e -vvv fdsrc ! h264parse ! rtph264pay pt=96 config-interval=5 ! udpsink host={0} port={1}"

FRAME_RATE = 24
VIDEO_W = 1280
VIDEO_H = 720
BITRATE = 10000000

# Data connections
PC_HOST = "192.168.188.44"
EV3_HOST = "ev3dev"  # An IP address will work too
RECV_BUFFER = 2048  # Advisable to keep it as an exponent of 2
DATA_PORT = 50007  # data port
VIDEO_PORT = 5000
DATA_RATE = 25  # Number of loops (packets to send) per second

# Bluetooth NXT slave config
BLUETOOTH = False
BRICK_ADDR = '00:16:53:0E:1C:AC'  # change this to the bt address of your brick
BRICK_NAME = 'NXT'  # fallback if the address is not found
BT_CMD_RATE = 30

# Motor configs
MOTOR_CMD_RATE = 15  # Max number of motor commands per second

# Gamepad
STICK_RANGE = (-32768, 32768)   # min, max stick position. Input range.
SIXAXIS = {
    'gamepad_num': 0,
    'stick_range': STICK_RANGE,
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