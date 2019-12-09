# Video config
VIDEO = True
RASPIVID_CMD = "raspivid -t 999999 -b 2000000 -rot 90 -o -"
STREAM_CMD = "gst-launch-1.0 -e -vvv fdsrc ! h264parse ! rtph264pay pt=96 config-interval=5 ! udpsink host={0} port={1}"

FRAME_RATE = 24
VIDEO_W = 1280
VIDEO_H = 720
BITRATE = 10000000

# Data connections
PC_HOST = "192.168.188.22"
EV3_HOST = "ev3dev"  # An IP address will work too
RECV_BUFFER = 2048  # Advisable to keep it as an exponent of 2
DATA_PORT = 50007  # data port
VIDEO_PORT = 5000

# Bluetooth NXT slave config
BLUETOOTH = False
BRICK_ADDR = '00:16:53:0E:1C:AC'  # change this to the bt address of your brick
BRICK_NAME = 'NXT'  # fallback if the address is not found
BT_CMD_RATE = 30

# Motor configs
MOTOR_CMD_RATE = 20  # Max number of motor commands per second
STICK_RANGE = (-32768, 32768)