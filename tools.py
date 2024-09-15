import sys


def updateProgressBar(percentage):
    bar_length = 25
    blocks = int(percentage * bar_length)
    progress_bar = "[" + "█" * blocks + "░" * (bar_length - blocks) + "]"
    sys.stdout.write("\r" + progress_bar + f" {int(percentage * 100)}% ")
    sys.stdout.flush()