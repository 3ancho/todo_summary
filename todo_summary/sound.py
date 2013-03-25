import subprocess
from sys import platform
import os

def play_sound(audio_file):
  audio_file = os.path.join("./sound_effects", audio_file) 
  if platform == "darwin":  
    return_code = subprocess.call(["afplay", audio_file])

def main():
  """docstring for main"""
  play_sound('paper.wav')


if __name__ == '__main__':
  main()
