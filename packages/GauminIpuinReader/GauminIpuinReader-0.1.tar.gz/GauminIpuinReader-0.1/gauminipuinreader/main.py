import os
import sys
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.dropdown import DropDown
from kivy.resources import resource_add_path

from ipuin import Ipuin
from ipuin.games import registered_games

Window.allow_vkeyboard = True

from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'dock')
Config.write()


__version__ = "0.1"


class MenuDropDown(DropDown):
    pass


class LoadIpuinWidget(Screen):
    def __init__(self, *args, **kwargs):
        self.register_event_type('on_choose')
        super(LoadIpuinWidget, self).__init__(*args, **kwargs)

    def load_ipuin(self, path, selection):
        filepath = os.path.join(path, selection[0])
        print "Choosen file: ", filepath
        self.dispatch('on_choose', filepath)

    def on_choose(self, *args):
        pass


class StepWidget(Screen):
    rsttext = StringProperty('No ipuin loaded')
    img = ObjectProperty(None)
    has_image = BooleanProperty(True)
    container = ObjectProperty(None)

    stepname = StringProperty(None)
    ipuin = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        self.register_event_type('on_target')
        super(StepWidget, self).__init__(*args, **kwargs)

    def on_stepname(self, instance, value):
        step = self.ipuin.steps[value]
        self.rsttext = self.ipuin.get_step_text(step)

        if self.ipuin.step_has_image(step):
            self.img.source = self.ipuin.get_step_image(step)
            self.has_image = True
        else:
            self.img.source = 'imgs/empty.png'
            self.has_image = False

        self.targets.clear_widgets()
        for target in self.ipuin.get_step_targets(value):
            self._add_target_button(target)

        if self.ipuin.is_end_step(value):
            self._add_target_button({
                "type": "step",
                "target": self.ipuin.start,
                "title": "Start again!"
            })

    def on_target(self, target, *args):
        pass

    def _add_target_button(self, target):
        btn = Button(
            text=target['title'],
        )
        btn.target = target
        btn.bind(on_release=lambda button: self.dispatch('on_target', button.target))
        self.targets.add_widget(btn)


class ReaderWidget(BoxLayout):
    title = StringProperty('Gaumin Ipuin')
    step = ObjectProperty(None)
    stepname = StringProperty(None)
    ipuin = ObjectProperty(None)
    cover = StringProperty(None)
    ipuin_info = StringProperty(None)

    about = open('about.rst').read()

    screenmanager = ObjectProperty(None)

    #def __init__(self, *args, **kwargs):
    #    super(ReaderWidget, self).__init__(*args, **kwargs)
    #    self.screenmanager.bind(on_current=self._set_title)

    def load_ipuin(self, ipuinfile, *args):
        self.ipuin = Ipuin(ipuinfile)
        self.step.bind(on_target=self.on_target)
        self.screenmanager.current = "cover"
        self._set_title()

    def on_target(self, stepwidget, target, *args):
        print "Going to target: %s" % target['title']
        if target['type'] == 'step':
            self.stepname = target['target']
        elif target['type'] == 'game':
            Game = registered_games[target['target']]
            game = Game(spec=target, name="game")
            game.bind(on_game_exit=lambda w, stepname: setattr(self, 'stepname', stepname))
            self.screenmanager.add_widget(game)
            self.screenmanager.current = "game"
        return True

    def start_reading(self):
        self.stepname = self.ipuin.start
        self.screenmanager.current = "step"

    def on_ipuin(self, instance, ipuin):
        self.cover = ipuin.cover
        self.ipuin_info = ipuin.info

    def open_menu(self, button, *args, **kwargs):
        menu = MenuDropDown()
        menu.open(button)
        menu.bind(on_select=self._menu_select)

    def _set_title(self, *args):
        if self.screenmanager.current == "cover":
            self.title = self.ipuin.title
        elif self.screenmanager.current == "step":
            self.title = "%s: %s" % (self.ipuin.title, self.ipuin.get_step_title(self.stepname))
        elif self.screenmanager.current == "game":
            self.title = "%s: %s - jokua" % (self.ipuin.title, self.ipuin.get_step_title(self.stepname))
        elif self.screenmanager.current == "load":
            self.title = "Gaumin Ipuin: Liburua aukeratu"
        else:
            self.title = "Gaumin Ipuin"

    def _menu_select(self, widget, selected):
        if selected == 'load':
            self.screenmanager.current = 'load'
        elif selected == 'start':
            self.screenmanager.current = 'cover'
        elif selected == 'about':
            self.screenmanager.current = 'about'
        self._set_title()

    def on_stepname(self, instance, value):
        self.screenmanager.current = 'step'
        self._set_title(None, 'step')
        if self.screenmanager.has_screen('game'):
            self.screenmanager.remove_widget(self.screenmanager.get_screen('game'))


class ReaderApp(App):
    def __init__(self, *args, **kwargs):
        super(ReaderApp, self).__init__(*args, **kwargs)
        self.ipuinfile = kwargs.get('ipuinfile', None)

    def build(self):
        reader = ReaderWidget()
        if self.ipuinfile is not None:
            reader.load_ipuin(ipuinfile=self.ipuinfile)
        return reader


def main():
    ipuin = None
    if len(sys.argv) == 2:
        ipuin = sys.argv[1]
    resource_add_path(os.path.dirname(__file__))
    ReaderApp(ipuinfile=ipuin).run()

if __name__ == '__main__':
    main()
