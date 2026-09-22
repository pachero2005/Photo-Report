from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
import json
import os

try:
    from PIL import Image as PilImage, ImageOps
except ImportError:
    PilImage = None
    ImageOps = None

try:
    from jnius import autoclass, cast
    ANDROID = True
except ImportError:
    ANDROID = False

class CardLayout(BoxLayout):
    def __init__(self, bg_color=(0.15, 0.18, 0.22, 1), **kwargs):
        super(CardLayout, self).__init__(**kwargs)
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class RoundedButton(Button):
    def __init__(self, bg_color=(0.1, 0.65, 0.3, 1), radius=[25], **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.bg_color = bg_color
        self.radius = radius
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        
        with self.canvas.before:
            self.inst_color = Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def set_bg_color(self, color):
        self.bg_color = color
        self.inst_color.rgba = color

class SequenceCameraApp(App):
    def build(self):
        from kivy.core.window import Window
        Window.clearcolor = (0.08, 0.10, 0.12, 1)

        default_photo_names = [
            "ETIQUETA DE CAJA",
            "ETIQUETA DE COLCHON",
            "FOTO FRONTAL",
            "FOTO ESQUINA",
            "FOTO LATERAL",
            "MEDIDA DE ANCHO",
            "MEDIDA DE LARGO",
            "MEDIDA DE ESPESOR",
            "COLCHON Y CAJA",
            "COLCHON EMBALADO",
            "MEDIDA DE CAJA"
        ]

        saved_lote, saved_modelo, saved_index, saved_names, saved_status, saved_width, saved_height = self.load_state(default_photo_names)
        self.current_index = saved_index
        self.photo_names = saved_names
        self.photo_status = saved_status

        self.sincronizar_estados_con_disco()

        root_scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        header_lbl = Label(
            text='CONTROL DE FOTOS DE LOTE', 
            font_size=50, 
            bold=True, 
            size_hint_y=None, 
            height=70, 
            color=(0.9, 0.9, 0.9, 1),
            halign='center'
        )
        self.layout.add_widget(header_lbl)

        lote_card = CardLayout(orientation='vertical', padding=15, spacing=8, size_hint_y=None, height=190, bg_color=(0.14, 0.18, 0.24, 1))
        lote_card.add_widget(Label(text='NUMERO DE LOTE:', font_size=70, size_hint_y=None, height=75, color=(0.7, 0.8, 1, 1)))
        
        self.lote_input = TextInput(
            text=saved_lote, 
            font_size=80, 
            multiline=False, 
            size_hint_y=None, 
            height=100, 
            halign='center',
            background_color=(0.2, 0.24, 0.3, 1),
            foreground_color=(1, 1, 1, 1)
        )
        self.lote_input.bind(text=self.on_input_change)
        lote_card.add_widget(self.lote_input)
        self.layout.add_widget(lote_card)

        modelo_card = CardLayout(orientation='vertical', padding=15, spacing=8, size_hint_y=None, height=190, bg_color=(0.14, 0.18, 0.24, 1))
        modelo_card.add_widget(Label(text='MODELO (SUB-CARPETA):', font_size=70, size_hint_y=None, height=60, color=(0.7, 0.8, 1, 1)))
        
        self.modelo_input = TextInput(
            text=saved_modelo, 
            font_size=80, 
            multiline=False, 
            size_hint_y=None, 
            height=100, 
            halign='center',
            background_color=(0.2, 0.24, 0.3, 1),
            foreground_color=(1, 1, 1, 1)
        )
        self.modelo_input.bind(text=self.on_input_change)
        modelo_card.add_widget(self.modelo_input)
        self.layout.add_widget(modelo_card)

        dim_card = CardLayout(orientation='vertical', padding=15, spacing=8, size_hint_y=None, height=190, bg_color=(0.14, 0.18, 0.24, 1))
        dim_card.add_widget(Label(text='ANCHO x ALTO:', font_size=42, size_hint_y=None, height=40, color=(0.7, 0.8, 1, 1)))
        
        dim_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=80)
        
        self.width_input = TextInput(
            text=saved_width,
            hint_text='900',
            font_size=60,
            multiline=False,
            halign='center',
            background_color=(0.2, 0.24, 0.3, 1),
            foreground_color=(1, 1, 1, 1)
        )
        self.width_input.bind(text=self.on_input_change)
        
        self.height_input = TextInput(
            text=saved_height,
            hint_text='506',
            font_size=60,
            multiline=False,
            halign='center',
            background_color=(0.2, 0.24, 0.3, 1),
            foreground_color=(1, 1, 1, 1)
        )
        self.height_input.bind(text=self.on_input_change)
        
        dim_box.add_widget(self.width_input)
        dim_box.add_widget(self.height_input)
        dim_card.add_widget(dim_box)
        self.layout.add_widget(dim_card)

        info_card = CardLayout(orientation='vertical', padding=15, spacing=8, size_hint_y=None, height=220, bg_color=(0.14, 0.18, 0.24, 1))
        
        display_index = self.current_index if self.current_index < len(self.photo_names) else len(self.photo_names) - 1
        
        self.update_progress_display()
        info_card.add_widget(self.progress_label)
        
        current_display_name = self.photo_names[display_index] if self.current_index < len(self.photo_names) else 'TODAS LAS FOTOS LISTAS'
        
        self.name_input = TextInput(
            text=current_display_name, 
            font_size=48, 
            multiline=False, 
            size_hint_y=None, 
            height=80, 
            halign='center',
            background_color=(0.2, 0.24, 0.3, 1),
            foreground_color=(1, 0.82, 0, 1)
        )
        self.name_input.bind(text=self.on_name_text_change)
        info_card.add_widget(self.name_input)
        
        self.layout.add_widget(info_card)

        btn_layout_single = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=130)
        
        self.btn_back = RoundedButton(text='<', font_size=130, bold=True, bg_color=(0.4, 0.4, 0.5, 1), radius=[20])
        self.btn_back.bind(on_press=self.previous_photo)
        btn_layout_single.add_widget(self.btn_back)

        self.btn_open_cam = RoundedButton(text='FOTO', font_size=84, bold=True, bg_color=(0.1, 0.65, 0.3, 1), radius=[20])
        if self.current_index >= len(self.photo_names):
            self.btn_open_cam.disabled = True
            self.btn_open_cam.set_bg_color((0.4, 0.4, 0.4, 1))
        self.btn_open_cam.bind(on_press=self.open_native_camera)
        btn_layout_single.add_widget(self.btn_open_cam)

        self.btn_skip = RoundedButton(text='>', font_size=130, bold=True, bg_color=(0.85, 0.5, 0.1, 1), radius=[20])
        self.btn_skip.bind(on_press=self.skip_photo)
        btn_layout_single.add_widget(self.btn_skip)

        self.btn_reset = RoundedButton(text='RESET', font_size=62, bold=True, bg_color=(0.75, 0.2, 0.2, 1), radius=[20])
        self.btn_reset.bind(on_press=self.reset_sequence)
        btn_layout_single.add_widget(self.btn_reset)

        self.layout.add_widget(btn_layout_single)

        status_card = CardLayout(orientation='vertical', padding=10, size_hint_y=None, height=110, bg_color=(0.12, 0.15, 0.20, 1))
        status_text = 'LISTO PARA CAPTURAR' if self.current_index > 0 else 'ESPERANDO INICIO'
        if self.current_index >= len(self.photo_names):
            status_text = 'SECUENCIA FINALIZADA'

        self.status_label = Label(
            text=status_text, 
            font_size=56, 
            size_hint_y=None, 
            height=90, 
            color=(0.8, 0.8, 0.8, 1),
            halign='center',
            valign='middle'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        status_card.add_widget(self.status_label)
        self.layout.add_widget(status_card)

        root_scroll.add_widget(self.layout)

        Clock.schedule_interval(self.daemon_redimensionador_pil, 2.0)

        return root_scroll

    def get_state_file_path(self):
        return os.path.join(self.user_data_dir, "inspection_state_v21.json")

    def load_state(self, default_names):
        path = self.get_state_file_path()
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    names = data.get('photo_names', default_names)
                    status = data.get('photo_status', ['PENDIENTE'] * len(names))
                    if len(status) < len(names):
                        status.extend(['PENDIENTE'] * (len(names) - len(status)))
                    return (
                        data.get('lote', '6LC0100'), 
                        data.get('modelo', 'SC14K'), 
                        data.get('index', 0), 
                        names, 
                        status,
                        data.get('max_width', '900'),
                        data.get('max_height', '506')
                    )
            except Exception:
                pass
        return '6LC0100', 'SC14K', 0, default_names, ['PENDIENTE'] * len(default_names), '900', '506'

    def save_state(self):
        path = self.get_state_file_path()
        try:
            data = {
                'lote': self.lote_input.text.strip().upper(),
                'modelo': self.modelo_input.text.strip().upper(),
                'index': self.current_index,
                'photo_names': self.photo_names,
                'photo_status': self.photo_status,
                'max_width': self.width_input.text.strip(),
                'max_height': self.height_input.text.strip()
            }
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
                
            if ANDROID:
                try:
                    Environment = autoclass('android.os.Environment')
                    File = autoclass('java.io.File')
                    dcim_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM)
                    python_folder = File(dcim_dir, "PYTHON")
                    lote_text = self.lote_input.text.strip().upper() or "6LC0100"
                    lote_folder = File(python_folder, lote_text)
                    if not lote_folder.exists():
                        lote_folder.mkdirs()
                    
                    json_file_path = os.path.join(lote_folder.getAbsolutePath(), "inspection_state.json")
                    with open(json_file_path, 'w') as jf:
                        json.dump(data, jf, indent=4)
                except Exception:
                    pass

        except Exception as e:
            print(f"Error guardando JSON: {e}")

    def sincronizar_estados_con_disco(self):
        if not ANDROID:
            return
        lote_text = self.lote_input.text.strip().upper() if hasattr(self, 'lote_input') else "6LC0100"
        modelo_text = self.modelo_input.text.strip().upper() if hasattr(self, 'modelo_input') else "SC14K"
        
        try:
            Environment = autoclass('android.os.Environment')
            File = autoclass('java.io.File')
            dcim_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM)
            python_folder = File(dcim_dir, "PYTHON")
            lote_folder = File(python_folder, lote_text)
            modelo_folder = File(lote_folder, modelo_text)

            for i, name in enumerate(self.photo_names):
                filename = f"{i + 1:02d}_{name}.jpg"
                file_obj = File(modelo_folder, filename)
                
                if file_obj.exists() and file_obj.length() > 0:
                    if self.photo_status[i] != 'OMITIDA':
                        self.photo_status[i] = 'TOMADA'
                else:
                    if self.photo_status[i] == 'TOMADA':
                        self.photo_status[i] = 'PENDIENTE'
        except Exception:
            pass

    def daemon_redimensionador_pil(self, dt):
        if not ANDROID or not PilImage:
            return
        
        w_str = self.width_input.text.strip() if hasattr(self, 'width_input') else "900"
        h_str = self.height_input.text.strip() if hasattr(self, 'height_input') else "506"
        
        target_w = int(w_str) if w_str.isdigit() else 900
        target_h = int(h_str) if h_str.isdigit() else 506

        lote_text = self.lote_input.text.strip().upper() if hasattr(self, 'lote_input') else "6LC0100"
        modelo_text = self.modelo_input.text.strip().upper() if hasattr(self, 'modelo_input') else "SC14K"

        try:
            Environment = autoclass('android.os.Environment')
            File = autoclass('java.io.File')
            dcim_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM)
            python_folder = File(dcim_dir, "PYTHON")
            lote_folder = File(python_folder, lote_text)
            modelo_folder = File(lote_folder, modelo_text)

            if not modelo_folder.exists():
                return

            for i, name in enumerate(self.photo_names):
                filename = f"{i + 1:02d}_{name}.jpg"
                file_obj = File(modelo_folder, filename)
                if file_obj.exists() and file_obj.length() > 0:
                    file_path = file_obj.getAbsolutePath()
                    
                    try:
                        with PilImage.open(file_path) as img:
                            if ImageOps:
                                img = ImageOps.exif_transpose(img)
                            
                            orig_w, orig_h = img.size
                            tw, th = target_w, target_h
                            
                            if orig_w < orig_h:
                                if tw > th:
                                    tw, th = th, tw
                            else:
                                if tw < th:
                                    tw, th = th, tw

                            if orig_w > tw or orig_h > th:
                                img_resized = img.resize((tw, th), PilImage.Resampling.LANCZOS)
                                img_resized.save(file_path, "JPEG", quality=90)
                            else:
                                img.save(file_path, "JPEG", quality=90)
                    except Exception:
                        pass
        except Exception as e:
            print(f"Error en daemon PIL rotación: {e}")

    def on_input_change(self, instance, value):
        self.sincronizar_estados_con_disco()
        self.update_progress_display()
        self.save_state()

    def update_progress_display(self):
        if not hasattr(self, 'progress_label'):
            self.progress_label = Label(font_size=42, size_hint_y=None, height=50)
            
        display_idx = self.current_index if self.current_index < len(self.photo_names) else len(self.photo_names) - 1
        self.sincronizar_estados_con_disco()
        current_status = self.photo_status[display_idx] if display_idx < len(self.photo_status) else 'PENDIENTE'
        
        if current_status == 'TOMADA':
            marca = "[O]"
            color_txt = (0.2, 1, 0.2, 1)
        elif current_status == 'OMITIDA':
            marca = "[X]"
            color_txt = (1, 0.2, 0.2, 1)
        else:
            marca = "[ ]"
            color_txt = (0.7, 0.7, 0.7, 1)

        self.progress_label.text = f'FOTO {min(self.current_index + 1, len(self.photo_names))} DE {len(self.photo_names)}  {marca}'
        self.progress_label.color = color_txt

    def on_name_text_change(self, instance, value):
        display_index = self.current_index if self.current_index < len(self.photo_names) else len(self.photo_names) - 1
        if 0 <= display_index < len(self.photo_names):
            self.photo_names[display_index] = value.strip().upper()
            self.save_state()

    def reset_sequence(self, instance):
        self.current_index = 0
        self.photo_status = ['PENDIENTE'] * len(self.photo_names)
        self.sincronizar_estados_con_disco()
        self.save_state()
        
        self.update_progress_display()
        self.name_input.text = self.photo_names[0]
        self.btn_open_cam.disabled = False
        self.btn_open_cam.set_bg_color((0.1, 0.65, 0.3, 1))
        self.status_label.text = 'SECUENCIA REINICIADA'

    def skip_photo(self, instance):
        if self.current_index < len(self.photo_names):
            if self.photo_status[self.current_index] != 'TOMADA':
                self.photo_status[self.current_index] = 'OMITIDA'
                
            if self.current_index < len(self.photo_names) - 1:
                self.current_index += 1
                self.save_state()
                self.update_progress_display()
                self.name_input.text = self.photo_names[self.current_index]
                self.status_label.text = 'FOTO OMITIDA'
            else:
                self.save_state()
                self.update_progress_display()
                self.status_label.text = 'ESTÁS EN LA ÚLTIMA FOTO'

    def previous_photo(self, instance):
        if self.current_index > 0:
            self.current_index -= 1
            self.save_state()
            self.update_progress_display()
            self.name_input.text = self.photo_names[self.current_index]
            self.btn_open_cam.disabled = False
            self.btn_open_cam.set_bg_color((0.1, 0.65, 0.3, 1))
            self.status_label.text = 'REGRESASTE A LA FOTO ANTERIOR'
        else:
            self.status_label.text = 'ESTÁS EN LA PRIMERA FOTO'

    def open_native_camera(self, instance):
        if not ANDROID:
            self.status_label.text = 'SOLO FUNCIONA EN ANDROID'
            return
            
        if self.current_index >= len(self.photo_names):
            self.status_label.text = 'TODAS LAS FOTOS COMPLETADAS'
            return

        lote_text = self.lote_input.text.strip().upper() or "6LC0100"
        modelo_text = self.modelo_input.text.strip().upper() or "SC14K"

        base_name = self.photo_names[self.current_index]
        full_filename = f"{self.current_index + 1:02d}_{base_name}"

        try:
            StrictMode = autoclass('android.os.StrictMode')
            builder = autoclass('android.os.StrictMode$VmPolicy$Builder')
            StrictMode.setVmPolicy(builder().build())

            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            MediaStore = autoclass('android.provider.MediaStore')
            Environment = autoclass('android.os.Environment')
            File = autoclass('java.io.File')
            Uri = autoclass('android.net.Uri')
            
            current_activity = PythonActivity.mActivity
            
            dcim_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM)
            python_folder = File(dcim_dir, "PYTHON")
            lote_folder = File(python_folder, lote_text)
            modelo_folder = File(lote_folder, modelo_text)
            
            if not modelo_folder.exists():
                modelo_folder.mkdirs()
                
            photo_file = File(modelo_folder, f"{full_filename}.jpg")
            photo_path = photo_file.getAbsolutePath()

            photo_uri = Uri.parse("file://" + photo_path)
            uri_parcelable = cast('android.os.Parcelable', photo_uri)
            
            intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            intent.putExtra(MediaStore.EXTRA_OUTPUT, uri_parcelable)
            
            current_activity.startActivityForResult(intent, 0x123)
            
            self.photo_status[self.current_index] = 'TOMADA'
            self.status_label.text = f'GUARDADA: {modelo_text}'

            self.current_index += 1
            self.save_state()

            if self.current_index < len(self.photo_names):
                self.update_progress_display()
                self.name_input.text = self.photo_names[self.current_index]
            else:
                self.update_progress_display()
                self.name_input.text = 'TODAS LAS FOTOS LISTAS'
                self.btn_open_cam.disabled = True
                self.btn_open_cam.set_bg_color((0.4, 0.4, 0.4, 1))
            
        except Exception as e:
            self.status_label.text = f'ERROR: {str(e)}'.upper()

if __name__ == '__main__':
    SequenceCameraApp().run()
