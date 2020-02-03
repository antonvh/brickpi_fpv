__author__ = 'Antons Mindstorms Hacks'
import sdl2
import time
from settings import VIDEO_ENABLED, EV3_HOST, DATA_PORT, PC_HOST, DATA_RATE,\
    SIXAXIS


# ______ Constants & configuration ______ #

# initialise joysticking
error = sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
numsticks = sdl2.SDL_NumJoysticks()
print("{} Sticks found".format(numsticks+1))
for stick in range(numsticks):
    name = sdl2.SDL_JoystickNameForIndex(stick)
    print("Name of stick {} is {}".format(stick, name))
    if name == b"PLAYSTATION(R)3 Controller":
        gamepad_obj = sdl2.SDL_JoystickOpen(stick)
        if sdl2.SDL_JoystickNumAxes(gamepad_obj) == 4:
            # Let's do a test read
            sdl2.SDL_PumpEvents()
            result = sdl2.SDL_JoystickGetAxis(gamepad_obj, 0)
            if result < -30000:
                print("Stick {} disconnected".format(stick))
            else:
                print("Selected stick {}".format(stick))
                break

# Gamepad config

for i in range(5):
    # update joystick info
    sdl2.SDL_PumpEvents()
    state = []
    for axis in range(4):
        state += [sdl2.SDL_JoystickGetAxis(gamepad_obj, axis)]
    print(state)

