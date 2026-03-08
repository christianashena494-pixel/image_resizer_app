from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from PIL import Image as PilImage
import os


class ResizerUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=5, padding=5, **kwargs)
        self.selected_path = None

        # display area for selected image
        self.img_widget = KivyImage(size_hint=(1, .6), allow_stretch=True)
        self.add_widget(self.img_widget)

        # controls
        ctrl = BoxLayout(size_hint=(1, .2), spacing=5)
        self.add_widget(ctrl)

        self.choose_btn = Button(text='Choose Image')
        self.choose_btn.bind(on_release=self.open_filechooser)
        ctrl.add_widget(self.choose_btn)

        self.resize_btn = Button(text='Resize & Save')
        self.resize_btn.bind(on_release=self.do_resize)
        ctrl.add_widget(self.resize_btn)

        # options area
        opts = BoxLayout(size_hint=(1, .2), spacing=5)
        self.add_widget(opts)

        self.unit_spinner = Spinner(text='Pixels', values=('Pixels','cm','mm'), size_hint=(.3,1))
        opts.add_widget(self.unit_spinner)
        self.dpi_input = TextInput(text='96', input_filter='int', multiline=False, size_hint=(.2,1))
        opts.add_widget(self.dpi_input)
        self.mode_spinner = Spinner(
            text='Maintain aspect ratio by width',
            values=('Maintain aspect ratio by width','Maintain aspect ratio by height','Fill and crop to dimensions (no distortion)'),
            size_hint=(.5,1))
        opts.add_widget(self.mode_spinner)

        # dimension inputs
        dims = BoxLayout(size_hint=(1, .2), spacing=5)
        self.add_widget(dims)
        dims.add_widget(Label(text='Width:'))
        self.width_input = TextInput(text='0', input_filter='int', multiline=False)
        dims.add_widget(self.width_input)
        dims.add_widget(Label(text='Height:'))
        self.height_input = TextInput(text='0', input_filter='int', multiline=False)
        dims.add_widget(self.height_input)

        # status line
        self.status = Label(size_hint=(1, .1), text='')
        self.add_widget(self.status)

    def open_filechooser(self, *args):
        chooser = FileChooserListView(path='.', filters=['*.png','*.jpg','*.jpeg','*.bmp','*.gif'])
        popup = Popup(title='Select image', content=chooser, size_hint=(.9,.9))
        chooser.bind(on_submit=lambda fc, selection, touch: self.load_image(selection, popup))
        popup.open()

    def load_image(self, selection, popup):
        if selection:
            self.selected_path = selection[0]
            self.img_widget.source = self.selected_path
            self.img_widget.reload()
            self.status.text = f'Loaded {os.path.basename(self.selected_path)}'
        popup.dismiss()

    def to_pixels(self, value: int) -> int:
        unit = self.unit_spinner.text
        dpi = int(self.dpi_input.text or 96)
        if unit == 'cm':
            return int(value * dpi / 2.54)
        elif unit == 'mm':
            return int(value * dpi / 25.4)
        return int(value)

    def do_resize(self, *args):
        if not self.selected_path:
            self.status.text = 'No image selected.'
            return
        try:
            img = PilImage.open(self.selected_path)
        except Exception as e:
            self.status.text = f'Could not open image: {e}'
            return
        w_val = int(self.width_input.text or 0)
        h_val = int(self.height_input.text or 0)
        if w_val <= 0 or h_val <= 0:
            self.status.text = 'Enter positive width and height.'
            return
        mode = self.mode_spinner.text
        width = self.to_pixels(w_val)
        height = self.to_pixels(h_val)
        if mode == 'Maintain aspect ratio by width':
            aspect = img.width / img.height
            height = int(width / aspect)
            resized = img.resize((width, height))
        elif mode == 'Maintain aspect ratio by height':
            aspect = img.width / img.height
            width = int(height * aspect)
            resized = img.resize((width, height))
        else:
            # fill and crop
            scale = max(width / img.width, height / img.height)
            new_w = int(img.width * scale)
            new_h = int(img.height * scale)
            temp = img.resize((new_w, new_h))
            left = (new_w - width) // 2
            top = (new_h - height) // 2
            resized = temp.crop((left, top, left+width, top+height))
        # save next to original
        base, ext = os.path.splitext(self.selected_path)
        outpath = f"{base}_resized{ext}"
        try:
            if ext.lower() not in ['.png','.gif','.bmp'] and resized.mode != 'RGB':
                resized.convert('RGB').save(outpath, 'JPEG')
            else:
                resized.save(outpath)
            self.status.text = f'Saved {os.path.basename(outpath)}'
        except Exception as e:
            self.status.text = f'Error saving: {e}'


class ResizerApp(App):
    def build(self):
        return ResizerUI()

if __name__ == '__main__':
    ResizerApp().run()
