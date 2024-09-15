import sys
import shutil

def updateProgressBar(percentage):
    bar_length = shutil.get_terminal_size().columns - 10
    blocks = int(percentage * bar_length)
    progress_bar = "[" + "█" * blocks + "░" * (bar_length - blocks) + "]"
    sys.stdout.write("\r" + progress_bar + f" {int(percentage * 100)}% ")
    sys.stdout.write('\n')
    sys.stdout.flush()
