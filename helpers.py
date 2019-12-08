import time

def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.

    val: float or int
    src: tuple
    dst: tuple

    example: print scale(99, (0.0, 99.0), (-1.0, +1.0))
    """
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]


def clamp(n, limits):
    """
    Given a number and a range, return the number, or the extreme it 
    is closest to.

    :param n: number
    :return: number
    """
    (minn, maxn) = limits
    return max(min(maxn, n), minn)


class Throttler(object):
    """
    Helper class to make sure a certain amount of time has passed before
    entering the next pass trough a loop
    """
    def __init__(self, framerate):
        self.fps = framerate
        self.timestamp = time.time()

    def throttle(self):
        wait_time = 1.0 / self.fps - (time.time() - self.timestamp)  
        # has enough time passed? If not, this is the remainder
        if wait_time > 0:
            time.sleep(wait_time)
        self.timestamp = time.time()


class motorPID(object):
    """
    Helper class that remembers the integral and derivative of an error and uses that to calculate
    motor power for a servo.
    """
    def __init__(self, KP=.6, KI=0.05, KD=0.0):
        self.Kp = KP
        self.Ki = KI
        self.Kd = KD
        self.integral = 0
        self.prev_error = 0
        self.timestamp = time.time()
        self.zero = 0

    def set_zero(self, zero_pos):
        self.zero = zero_pos

    def inc_zero(self, increment):
        self.zero += increment

    def get_power(self, error):
        dt = time.time() - self.timestamp
        error -= self.zero
        self.integral += error * dt  # shouldn't the integral be emptied sometime?
        derivative = (error - self.prev_error) / dt
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        self.prev_error = error
        self.timestamp = time.time()
        return int(-output)