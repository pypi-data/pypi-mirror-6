import time

def run(bridge, delay=0):
    '''Fade up light at a specified delay.

    Keyword arguments:
    bridge -- the bridge that will be controlled (required)
    delay -- delay between fade up commands (default 0)
    '''

    if hasattr(bridge, 'set_brightness') and callable(getattr(bridge, 'set_brightness')):
        for i in range(2,28):
            bridge.set_brightness(i)
            time.sleep(delay)
        return

    # Number of steps between min and max
    max_loop = 9

    # Main loop
    i = 0
    while i < max_loop:
        bridge.brightness_up()

        i += 1
        if i == max_loop:
            break

        time.sleep(delay)
