#!/usr/bin/env python3
__author__ = 'Antons Mindstorms Hacks'

# motors and maybe sensors
from ev3dev2.motor import Motor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
from helpers import scale, Throttler, clamp

# To start the camera subprocess
import shlex
import picamera

# To open sockets en receive data from client
import socket, time, select

try:
    import cPickle as pickle
except:
    import pickle

# To run motors on the brickpi, in a separate thread
import threading
import subprocess


################### Constants & inits ################
from settings import DATA_PORT, VIDEO_PORT, RECV_BUFFER, BLUETOOTH, VIDEO, \
    STICK_RANGE, STREAM_CMD, VIDEO_H, VIDEO_W, BITRATE, FRAME_RATE, \
    MOTOR_CMD_RATE

connection_list = []  # list of socket clients
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", DATA_PORT))
server_socket.listen(10)
connection_list.append(server_socket)

video_playing = True
running = True
gp_state = {}

################# Helper functions ######################

def clean_up():
    global running, video_playing, connection_list
    running = False  # Stop threads
    video_playing = False
    for sock in connection_list:
        sock.close()


def scaled_gamepad_input(gamepad_input_key, output_range):
    """
    Read a value from the gamepad and scale it to the desired output range.

    :param gamepad_input_key: string
    :param output_range: tuple
    :return: int
    """
    if 'btn' in gamepad_input_key:
        scale_src = (0, 1)
    else:
        scale_src = STICK_RANGE
    if gamepad_input_key in gp_state:
        return int(scale(gp_state[gamepad_input_key], scale_src, output_range))
    else:
        return 0


def all_buttons_pressed(btn_list):
    result = True
    for btn in btn_list:
        if btn in gp_state:
            if not gp_state[btn]:
                result = False
        else:
            result = False

    return result





##################### Threads ###########################

class sendVideo(threading.Thread):
    def __init__(self, ip_addr):
        threading.Thread.__init__(self)
        self.ip_addr = ip_addr

    def run(self):
        cmd = shlex.split(STREAM_CMD.format(self.ip_addr, VIDEO_PORT))
        streamer = subprocess.Popen(cmd, stdin=subprocess.PIPE)

        try:
            with picamera.PiCamera() as camera:
                camera.resolution = (VIDEO_W, VIDEO_H)
                camera.framerate = FRAME_RATE
                # camera.rotation = 90
                # Start a preview and let the camera warm up for 2 seconds
                camera.start_preview()
                time.sleep(2)
                camera.start_recording(streamer.stdin, format='h264', bitrate=BITRATE)
                while video_playing:
                    camera.wait_recording(1)
                camera.stop_recording()
        finally:
            # streamer.terminate() #apparently this crashes the brickpi. weird.
            print("Finally!")


class motorControl(threading.Thread):

    """
    Runs motors based on the state of the gamepad (gpstate)
    Use the robot layout as configured in the 'robot' dictionary
    """

    def run(self):
        global running
        motors = {}
        for motor_key in robot_config['motors']:
            motor = robot_config['motors'][motor_key]
            if motor['port'] == "A":
                motors["A"] = Motor(OUTPUT_A)
            if motor['port'] == "B":
                motors["B"] = Motor(OUTPUT_B)
            if motor['port'] == "C":
                motors["C"] = Motor(OUTPUT_C)
            if motor['port'] == "D":
                motors["D"] = Motor(OUTPUT_D)
        motorloop = Throttler(MOTOR_CMD_RATE)

        while running:
            # run if there is client, stop otherwise.
            if len(connection_list) > 1:
                for m_key in robot_config['motors']:
                    motor = robot_config['motors'][m_key] 

                    if motor['type'] == 'servo':
                        # Act like a servo, move towards the target as 
                        # fast and precise as possible.
                        # the movement speed is based on the error (err) 
                        # between current and target positions
                        target = scaled_gamepad_input(motor['control'], motor['range'])
                        err = motors[motor['port']].position - target

                        # Calibrate the servo
                        if 'trim_up' in motor:
                            if all_buttons_pressed(motor['trim_up']):
                                motors[motor['port']].position += motor['trim_step']

                        if 'trim_down' in motor:
                            if all_buttons_pressed(motor['trim_down']):
                                motors[motor['port']].position -= motor['trim_step']

                        # if 'co_rotate' in motor:
                        #     # when the head turns horizontally, the vertical axis has turn to match
                        #     # the rotation, because the axles are concentric.
                        #     co_motor = robot_config['motors'][motor['co_rotate']]
                        #     co_position = BrickPi.Encoder[co_motor['port']] - motorPIDs[motor['co_rotate']].zero  # get rotation of co-rotational motor
                        #     co_rotation_speed = BrickPi.Encoder[co_motor['port']] - scale(gp_state[co_motor['control']],
                        #                                                                 STICK_RANGE, co_motor['range'])
                        #     err += co_position * motor['co_rotate_pos'] + co_rotation_speed * motor[
                        #         'co_rotate_speed']  # offset motor target with this number to make it move along

                        pwr = clamp(err * -2, (-100, 100))
                        motors[motor['port']].run_direct(duty_cycle_sp=pwr)

                    if motor['type'] == 'dc':
                        target_speed = clamp(
                            scaled_gamepad_input(motor['control'], motor['range']),
                            (-100, 100)
                        )
                        motors[motor['port']].run_direct(duty_cycle_sp=target_speed)

                # Don't overload the brickpi too much, 
                # wait a bit before next loop
                motorloop.throttle()  

        # The 'running' loop has stopped. Shutting down all motors.


################## Main Loop #############################
   

while True:
    try:
        # Get the list sockets which are ready to be read through select
        if len(connection_list) > 0:
            read_sockets, write_sockets, error_sockets = select.select(connection_list, [], [])
            for sock in read_sockets:

                # New connection
                if sock == server_socket:
                    # Handle the case in which there is a new connection recieved through server_socket
                    sockfd, addr = server_socket.accept()
                    connection_list.append(sockfd)


                # Some incoming message from a connected client
                else:
                    # Data recieved from client, process it
                    try:
                        # In Windows, sometimes when a TCP program closes abruptly,
                        # a "Connection reset by peer" exception will be thrown

                        answer = ["Robot says:"]
                        send_data = pickle.dumps(answer)
                        data = sock.recv(RECV_BUFFER)
                        sock.send(send_data)
                        rcvd_dict = pickle.loads(data)

                        if 'ip_addr' in rcvd_dict:
                            # We have a destination for our video stream. setup and start the thread
                            if VIDEO:
                                video_playing = True
                                video_thread = sendVideo(rcvd_dict['ip_addr'])
                                video_thread.setDaemon(True)
                                video_thread.start()

                        if 'robot_config' in rcvd_dict:
                            # We have a robot definition! Setup and start the motor thread
                            robot_config = rcvd_dict['robot_config']
                            motor_thread = motorControl()
                            motor_thread.setDaemon(True)
                            motor_thread.start()

                        else:
                            gp_state = rcvd_dict
                            if gp_state['btn_Y']:
                                sock.close()
                                connection_list.remove(sock)
                                clean_up()
                                break
                                # acknowledge

                    # Client disconnected, so remove it from socket list
                    except:
                        sock.close()
                        connection_list.remove(sock)
                        clean_up()
                        break



    except KeyboardInterrupt:  # Triggered by pressing Ctrl+C. Time to clean up.
        clean_up()
        break  # Exit