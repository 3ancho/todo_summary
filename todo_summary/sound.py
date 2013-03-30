import subprocess
from sys import platform
import os
import logging

def play_sound(audio_file):
  logger = logging.getLogger('tosu')

  logger.debug("play")
  audio_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sound_effects', audio_file) 
  if platform == "darwin":  
    p = subprocess.Popen(["afplay", audio_file])
  elif platform == "linux":
    p = subprocess.Popen(["play", audio_file])
  logger.debug("play end")

#  p.terminate()


def main():
  """docstring for main"""
  play_sound('paper.wav')


if __name__ == '__main__':
  main()
