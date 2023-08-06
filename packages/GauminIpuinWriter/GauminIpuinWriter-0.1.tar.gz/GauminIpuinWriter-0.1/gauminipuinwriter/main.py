import os
import sys
from kivy.app import App
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.resources import resource_add_path
from kivy.core.window import Window
from kivy.adapters.dictadapter import DictAdapter
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton

from ipuin import Ipuin
from ipuin.step import StepConfig
from ipuin.games import registered_games

__version__ = "0.1"


class OpenIpuinWidget(BoxLayout):
    def __init__(self, *args, **kwargs):
        self.register_event_type('on_load')
        super(OpenIpuinWidget, self).__init__(*args, **kwargs)
        self.filechooser.bind(on_submit=self.load_with_double_tap)

    def load_with_double_tap(self, instance, value, motion):
        self.dispatch('on_load', value[0])

    def load(self, selection):
        self.dispatch('on_load', selection[0])

    def on_load(self, filepath):
        pass

    def new_ipuin_form(self):
        ipuinfile = os.path.join(self.filechooser.path, self.newipuintextinput.text)
        self.dispatch('on_load', ipuinfile)


class FileChooserPopup(Popup):
    def __init__(self, filters, *args, **kwargs):
        self.filters = filters
        self.register_event_type('on_choose')
        super(FileChooserPopup, self).__init__(*args, **kwargs)
        self.filechooser.bind(on_submit=self.choose_with_double_tap)

    def choose_with_double_tap(self, instance, value, motion):
        self.dispatch('on_choose', value[0])

    def on_choose(self, selection):
        pass


class IpuinEditorWidget(BoxLayout):
    title = StringProperty('Liburuaren izenburua')
    ipuin = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        self.empty_step = {
            'title': ' --- ',
        }

        step_args_converter = lambda index, step: {
            'text': step['title'],
            'size_hint_y': None,
            'height': 25
        }

        self.step_adapter = DictAdapter(
            data={'emptystep': self.empty_step},
            args_converter=step_args_converter,
            selection_mode='single',
            allow_empty_selection=False,
            cls=ListItemButton
        )

        super(IpuinEditorWidget, self).__init__(*args, **kwargs)

        self.stepindex = None

        self.update_step(self.step_adapter)
        self.step_adapter.bind(on_selection_change=self.update_step)

    def on_ipuin(self, instance, value):
        self.title = value.title
        self.step_adapter.data = self.ipuin.steps

    def update_step(self, adapter, *args):
        selection = adapter.selection[0]

        if self.stepindex is not None and self.stepeditor.changed:
            oldindex = self.stepindex
            oldkey = adapter.sorted_keys[oldindex]

            if self.stepeditor.title_changed:
                view = adapter.get_view(oldindex)
                view.text = self.stepeditor.title
                # force list view refresh, as somewhere the step button gets
                # cached and does not update any more
                self.step_list_view.populate()

            self.stepeditor.save()
            adapter.data[oldkey] = self.stepeditor.step
            self.ipuin.steps[oldkey] = self.stepeditor.step
            adapter.selection.append(selection)

        index = selection.index
        data = adapter.get_data_item(index)
        self.stepeditor.step = data
        self.stepindex = index

    def add_step(self):
        counter = 1
        newid = 'step-%d' % counter
        while newid in self.step_adapter.sorted_keys:
            counter += 1
            newid = 'step-%d' % counter
        self.step_adapter.data[newid] = self.empty_step
        self.step_adapter.sorted_keys = sorted(self.step_adapter.data.keys())
        self.step_adapter.handle_selection(self.step_adapter.get_view(self.step_adapter.sorted_keys.index(newid)))
        self.step_list_view.populate()

    def remove_selected_step(self):
        key = self.step_adapter.sorted_keys[self.stepindex]
        self.step_adapter.data.pop(key)
        self.step_adapter.initialize_selection()
        self.step_list_view.populate()

    def edit_metadata(self):
        popup = IpuinMetadataEditorPopup(ipuin=self.ipuin)

        def update_title(instance, title):
            self.title = title

        popup.bind(on_title_changed=update_title)
        popup.open()

    def save_ipuin(self):
        self.update_step(self.step_adapter)
        self.ipuin.steps = self.step_adapter.data
        self.ipuin.save()


class StepEditorWidget(GridLayout):
    ipuin = ObjectProperty(None)
    step = ObjectProperty({})

    title = StringProperty('')
    image = StringProperty('-1')
    text = StringProperty('')

    def __init__(self, *args, **kwargs):

        self.emptytarget = {"type": "step", "target": " --- ", "title": " --- "}

        target_args_converter = lambda index, target: {
            'text': target['title'],
            'size_hint_y': None,
            'height': 25
        }

        self.target_adapter = ListAdapter(
            data=[],
            args_converter=target_args_converter,
            selection_mode='single',
            allow_empty_selection=False,
            cls=ListItemButton,
        )

        super(StepEditorWidget, self).__init__(*args, **kwargs)

    def on_step(self, instance, step):
        self.title = step.get('title', '')
        self.image = self.ipuin.get_step_image(step)
        self.text = self.ipuin.get_step_text(step)

        if 'targets' in self.step:
            self.target_adapter.data = self.step['targets']
        else:
            self.target_adapter.data = []

        self.target_list_view.populate()

    def save(self):
        if self.title_changed:
            self.step['title'] = self.title
        if self.image_changed:
            if self.image == '':
                if 'img' in self.step:
                    del(self.step['img'])
            else:
                self.step['img'] = self.image
        if self.text_changed:
            self.step['text'] = self.rstfile

        if self.targets_changed:
            self.step['targets'] = list(self.target_adapter.data)

    @property
    def title_changed(self):
        return not 'title' in self.step or self.title != self.step.get('title', '')

    @property
    def image_changed(self):
        return self.image != '-1' and \
            not 'img' in self.step or \
            self.image != self.ipuin.get_step_image(self.step)

    @property
    def text_changed(self):
        return not 'text' in self.step or self.text != self.ipuin.get_step_text(self.step)

    @property
    def targets_changed(self):
        if 'targets' in self.step:
            return self.step['targets'] != self.target_adapter.data
        else:
            return len(self.target_adapter.data) > 0

    @property
    def changed(self):
        return self.title_changed or self.image_changed or self.text_changed or self.targets_changed

    def choose_image(self):
        popup = FileChooserPopup(filters=['*.png', '*.jpg'])
        popup.bind(on_choose=self.update_image)
        popup.open()

    def update_image(self, instance, value):
        self.image = value
        instance.dismiss()

    def choose_text(self):
        popup = FileChooserPopup(filters=['*.rst'])
        popup.bind(on_choose=self.update_text)
        popup.open()

    def update_text(self, instance, value):
        if value:
            with open(value) as rstfile:
                self.text = rstfile.read()
                self.rstfile = value
        instance.dismiss()

    def add_target(self):
        target_popup = TargetEditorPopup(ipuin=self.ipuin, step=self.step, target={})
        target_popup.bind(on_update_target=self.save_target)
        target_popup.open()

    def update_target(self):
        index = self.target_adapter.selection[0].index
        target = self.target_adapter.data[index]
        target_popup = TargetEditorPopup(ipuin=self.ipuin, step=self.step, target=target, index=index)
        target_popup.bind(on_update_target=self.save_target)
        target_popup.open()

    def save_target(self, instance, target, index):
        if index is None:
            self.target_adapter.data.append(target)
        else:
            self.target_adapter.data[index] = target
        self.target_list_view.populate()

    def remove_target(self):
        index = self.target_adapter.selection[0].index
        self.target_adapter.data.pop(index)
        self.target_adapter.initialize_selection()
        self.target_list_view.populate()


class IpuinMetadataEditorPopup(Popup):
    ipuin = ObjectProperty(None)
    cover = StringProperty('')
    title = StringProperty('')
    description = StringProperty('')
    author = StringProperty('')
    start = StringProperty('')
    #endings = ListProperty([])

    __events__ = ['on_title_changed']

    def on_ipuin(self, instance, ipuin):
        self.cover = ipuin.cover
        self.title = ipuin.title
        self.author = ipuin.author
        self.description = ipuin.description
        self.start = ipuin.start

    def choose_cover(self):
        popup = FileChooserPopup(filters=['*.png', '*.jpg'])
        popup.bind(on_choose=self.update_cover)
        popup.open()

    def update_cover(self, instance, value):
        self.cover = value
        instance.dismiss()

    def update_ipuin(self):
        self.dismiss()
        self.ipuin.cover = self.cover
        self.ipuin.description = self.description
        self.ipuin.author = self.author
        self.ipuin.start = self.start
        if self.ipuin.title != self.title:
            self.ipuin.title = self.title
            self.dispatch('on_title_changed', self.title)

    def on_title_changed(self, title):
        pass


class TargetEditorPopup(Popup):
    ipuin = ObjectProperty(None)
    step = ObjectProperty(None)
    target = ObjectProperty(None)
    index = NumericProperty(None)

    __events__ = ('on_update_target',)

    def __init__(self, **kwargs):
        super(TargetEditorPopup, self).__init__(**kwargs)
        self.targettypespinner.bind(key=self.on_target_type)

        target_type = self.target.get('type', 'step')
        if target_type == 'game':
            target_type = self.target['target']
        self.on_target_type(self.targettypespinner, target_type)

    def on_target(self, instance, target):
        target_type = target.get('type', 'step')
        if target_type == 'game':
            target_type = target['target']
        self.target_type = target_type

    def on_target_type(self, instance, target_type):
        if target_type in registered_games:
            self.target['type'] = 'game'
            game = registered_games[target_type]
            self.config = game.config(self.ipuin, self.target)
        else:
            self.target['type'] = 'step'
            self.config = StepConfig(self.ipuin, self.target)

        self.extraform.clear_widgets()
        for widget in self.config.get_widgets():
            self.extraform.add_widget(widget)

    def update_target(self):
        self.config.save()
        target = self.config.target
        target['title'] = self.title_widget.text
        self.dispatch('on_update_target', target, self.index)
        self.dismiss()

    def on_update_target(self, target, index):
        pass

    def get_games(self):
        return registered_games


class WriterApp(App):
    def __init__(self, ipuinfile=None, *args, **kwargs):
        super(WriterApp, self).__init__(*args, **kwargs)
        self.ipuinfile = ipuinfile
        self.openipuinwidget = None

    def build(self):
        if self.ipuinfile is not None:
            ipuin = Ipuin(self.ipuinfile)
            return IpuinEditorWidget(ipuin=ipuin)
        else:
            self.openipuinwidget = OpenIpuinWidget()
            self.openipuinwidget.bind(on_load=self.load_ipuin)
            return self.openipuinwidget

    def load_ipuin(self, instance, value):
        ipuin = Ipuin(value)
        widget = IpuinEditorWidget(ipuin=ipuin)
        if self.openipuinwidget is not None:
            Window.remove_widget(self.openipuinwidget)
        Window.add_widget(widget)


def main():
    ipuin = None
    if len(sys.argv) == 2:
        ipuin = sys.argv[1]
    resource_add_path(os.path.dirname(__file__))
    WriterApp(ipuin).run()

if __name__ == '__main__':
    main()
