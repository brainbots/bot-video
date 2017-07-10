import os, fnmatch
from functools import partial

from PyQt5.QtCore import QProcess
from pykeyboard import PyKeyboard

from bots.abstract_bot import AbstractBot
from bots.action import Action
from bots.utility import waitForWindowByTitle
from local_settings import VIDEO_DIR


class VideoBot(AbstractBot):
  def __init__(self, id):
    actions = ['video.play']
    super().__init__(id, actions)
    #REQUIRED
    self.query = None
    self.process = QProcess()
    self.commands = ['⏯', '⏪', '⏩']
    self.keyboard = None

  def extract_attr(self, intent):
    query = intent.parameters['video'].lower()
    for root, dirs, files in os.walk(VIDEO_DIR):
      for f in files:
        _lower = f.lower()
        if _lower.endswith(('.avi', '.mkv', '.mp4')) and fnmatch.fnmatch(_lower, "*{}*".format(query)):
          self.video_path = os.path.abspath(os.path.join(root, f))
          self.video_title = f
          #TODO: if many matches, allow the user to choose which one
          break

  def execute(self):
    try:
      self.process.start("/usr/bin/xdg-open \"{}\"".format(self.video_path))
      wnd = waitForWindowByTitle(self.video_title)
      self.keyboard = PyKeyboard()
      return Action(action_type = 'embed', body = {'hwnd': wnd['hwnd'], 'commands': self.commands}, bot = self.id, keep_context = False)
    except Exception as e:
      raise(e)

  def request_missing_attr(self):
    #TODO: Check for missing attr
    pass

  def has_missing_attr(self):
    return False

  def is_long_running(self):
    return True

  def run_command(self, command_index):
    arg = None
    if command_index == 0:
      arg = self.keyboard.space
    elif command_index == 1:
      arg = self.keyboard.left_key
    elif command_index == 2:
      arg = self.keyboard.right_key

    #fn = lambda: [self.keyboard.tap_key(self.keyboard.escape_key), self.keyboard.tap_key(arg)]
    fn = lambda: self.keyboard.tap_key(arg)
    return Action(action_type = 'keyboard_event', body = {'fn': fn}, bot = self.id, keep_context = False)

  def terminate(self):
    self.keyboard = None
    self.process.terminate()
    self.process = None
