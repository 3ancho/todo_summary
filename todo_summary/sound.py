import subprocess
from sys import platform
import os
import logging

def play_sound(audio_file):
  audio_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sound_effects', audio_file) 
  if platform == "darwin":  
    p = subprocess.Popen(["afplay", audio_file])
  elif platform == "linux2":
    p = subprocess.Popen(["aplay", audio_file])
#  p.terminate()

def main():
  """docstring for main"""
  play_sound('paper.wav')

if __name__ == '__main__':
  main()
