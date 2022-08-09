import time


def say(message, new_line=False):
    currentTime = time.strftime("%H:%M:%S")
    adder = '\n' if new_line else ''
    print(f"{adder}{currentTime} : {message}")



