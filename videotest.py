#!/usr/bin/env python3
__author__ = 'Antons Mindstorms Hacks'
import shlex, subprocess, picamera, time
from settings import STREAM_CMD, VIDEO_PORT, VIDEO_H, VIDEO_W, FRAME_RATE, \
    BITRATE, PC_HOST

video_playing = True
cmd = shlex.split(STREAM_CMD.format(PC_HOST, VIDEO_PORT))
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
