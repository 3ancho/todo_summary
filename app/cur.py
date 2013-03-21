# when using py2app, this includes a lot of packages
import pygame.mixer as sound_player
import time

import urwid 
import summary

class App:
  CMD_MODE = 0
  INPUT_MODE = 1

  def __init__(self):
#    palette = [ ('header', 'black', 'light gray'),
#                ('body', 'black', 'dark red'),
#                ('bg', 'black', 'dark blue'),]

    # init sound, register alerm
    sound_player.init()
    self.alarm = sound_player.Sound("thermo.wav")

    # reusable widges
    self.divider = urwid.Divider(u"-");

    # widgets
    header_text = summary.Summary.bootstrap()
    self.header = urwid.Text("Editing: %s\n" % header_text)

    self.footer = urwid.Edit(u"", "footer")

    self.content = urwid.Edit(u"Content:\n", multiline=True)

    self.tag = urwid.Edit(u"Tags:\n")

    self.txt = urwid.Text(u"display")

    self.tag_focused = True

    self.pre_focus = 1
    self.mode = App.INPUT_MODE

    self.pile = urwid.Pile([self.header, 
      self.tag, self.divider, self.content,
      self.divider, self.footer, self.txt])


    self.fill = urwid.Filler(self.pile, 'top')

    # set main loop
    self.loop = urwid.MainLoop(self.fill, unhandled_input=self.keypress_handler)

    # last_press
    self.pres_thres = 0.8
    self.last_press = 598233600

    self.key_buf = []


  def run(self):
    self.loop.run()

  def change_mode(self):
    if self.mode == App.CMD_MODE:
      self.mode = App.INPUT_MODE
      self.pile.set_focus(self.pre_focus)
      self.txt.set_text("input mode")
    elif self.mode == App.INPUT_MODE:
      self.mode = App.CMD_MODE
      self.pre_focus = self.pile.focus_position
      self.pile.set_focus(6)
      self.txt.set_text("cmd mode")

  def keypress_handler(self, key):

    if time.time() - self.last_press > self.pres_thres:
      self.key_buf = []
      self.last_press = time.time()
    else:
      self.last_press = time.time()
      self.key_buf.append(key)

    # 1. Change mode
    if key == 'esc':
      print "change mode"
      self.change_mode()
    # input mode
    elif self.mode == App.INPUT_MODE:
      if key in ('tab'):
        self.txt.set_text(" %s  " % self.pile.focus_position)
        if (self.tag_focused):
          self.pile.set_focus(3)
          self.tag_focused = False
        else:
          self.pile.set_focus(1)
          self.tag_focused = True
    # command mode
    elif self.mode == App.CMD_MODE:
      self.txt.set_text(str(self.key_buf))
      if key in ('p', 'P'):
        self.alarm.play()
      if key in ('s', 'S'):
        self.txt.set_text(summary.Summary.bootstrap())
      if key in ('i', 'I'):
        self.txt.set_text('input mode')
        self.change_mode()
        

      #if key in ('esc'):
      #  if (self.footer_focused):
      #    self.footer_focused = False
      #  else:
      #    self.pile.set_focus(1)
      #    self.footer_focused = True


def main():
  app = App()
  app.run()

if __name__ == '__main__':
  main()

