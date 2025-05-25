import random
import threading
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty, ListProperty
from kivy.metrics import dp, sp
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.config import Config

class PuzzleApp(App):
    
    class ThemeButton(Button):
        border_width = NumericProperty(0)
        border_color = ListProperty([0, 0, 0, 1])

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.bind(
                pos=self._update_border,
                size=self._update_border,
                border_width=self._update_border,
                border_color=self._update_border
            )

        def _update_border(self, *args):
            self.canvas.after.clear()
            with self.canvas.after:
                Color(*self.border_color)
                Line(width=self.border_width,
                    rectangle=(self.x, self.y, self.width, self.height))
    
    class AnimatedLabel(Label):
        visible_chars = NumericProperty(0)
        full_text = ""

        def start_animation(self, text):
            self.full_text = text
            self.visible_chars = 0
            self._animation_event = Clock.schedule_interval(self.animate_text, 0.1)

        def animate_text(self, dt):
            self.visible_chars += 1
            if self.visible_chars > len(self.full_text):
                Clock.schedule_once(lambda dt: self.reset_animation(), 1.0)
                self._animation_event.cancel()

        def reset_animation(self):
            self.visible_chars = 0
            self._animation_event = Clock.schedule_interval(self.animate_text, 0.1)

        def on_visible_chars(self, instance, value):
            self.text = self.full_text[:int(value)]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Config.setdefaults('puzzle', {'theme': 'Cotton Candy'})
        theme_name = Config.get('puzzle', 'theme')
        self.mode = "easy"
        self.themes = [
            {
                'name': 'Cotton Candy',
                'button_colors': ["#FFB6C1", "#FF69B4", "#FF1493", "#FFC0CB",
                                "#FFA07A", "#FF7F50", "#FF6347", "#FFDAB9",
                                "#FFE4E1", "#F0FFF0", "#E0FFFF", "#87CEEB",
                                "#ADD8E6", "#B0E0E6", "#AFEEEE"],
                'bg_color': (0.98, 0.85, 0.90, 1),
                'blank_color': (0.9, 0.9, 0.95, 1),
                'your_moves_label_color' : '#0000ff'
            },
            {
                'name': 'Ocean Blue',
                'button_colors': ["#1f77b4", "#aec7e8", "#17becf", "#7f7f7f",
                                 "#c7c7c7", "#8c564b", "#e377c2", "#bcbd22",
                                 "#98df8a", "#ff9896", "#d62728", "#9467bd",
                                 "#c5b0d5", "#ff7f0e", "#ffbb78"],
                'bg_color': (0.12, 0.56, 0.73, 1),
                'blank_color': (0.1, 0.1, 0.1, 1),
                'your_moves_label_color' : '#1a07b8'
            },
            {
                'name': 'Forest Green',
                'button_colors': ["#2e7d32", "#388e3c", "#43a047", "#4caf50",
                                 "#66bb6a", "#81c784", "#a5d6a7", "#c8e6c9",
                                 "#1b5e20", "#009688", "#4db6ac", "#80cbc4",
                                 "#b2dfdb", "#e0f2f1", "#00695c"],
                'bg_color': (0.23, 0.35, 0.23, 1),
                'blank_color': (0.15, 0.15, 0.15, 1),
                'your_moves_label_color' : '#1afb00'
            },
            {
                'name': 'Midnight Purple',
                'button_colors': ["#6b46c1", "#553c9a", "#44337a", "#322659",
                                "#4c1d95", "#5b21b6", "#6d28d9", "#7c3aed",
                                "#8b5cf6", "#a78bfa", "#c4b5fd", "#ddd6fe",
                                "#ede9fe", "#f5f3ff", "#e9d8fd"],
                'bg_color': (0.11, 0.07, 0.18, 1),
                'blank_color': (0.05, 0.03, 0.1, 1),
                'your_moves_label_color' : '#2291ff'
            },
            {
                'name': 'Sunset',
                'button_colors': ["#ff6b6b", "#ff8e8e", "#ffaaaa", "#ffc4c4",
                                 "#ffd8d8", "#ff9f43", "#ffb88c", "#ffd4b2",
                                 "#fff3cd", "#f6e58d", "#fffa65", "#d4efdf",
                                 "#a9dfbf", "#7dcea0", "#48c9b0"],
                'bg_color': (0.93, 0.56, 0.45, 1),
                'blank_color': (0.2, 0.2, 0.2, 1),
                'your_moves_label_color' : '#b33a00'
            },
            {
                'name': 'Royal Gold',
                'button_colors': ["#D4AF37", "#B8860B", "#FFD700", "#EEE8AA",
                                "#F0E68C", "#BDB76B", "#8B4513", "#CD853F",
                                "#DAA520", "#FF8C00", "#FFA500", "#FF4500",
                                "#DA70D6", "#9932CC", "#4B0082"],
                'bg_color': (0.05, 0.05, 0.15, 1),
                'blank_color': (0.1, 0.1, 0.2, 1),
                'your_moves_label_color' : '#d3f807'
            },
            {
                'name': 'Cyber Neon',
                'button_colors': ["#00FF00", "#39FF14", "#7FFF00", "#CCFF00",
                                "#FFFF00", "#FF6BFF", "#FF00FF", "#FF0099",
                                "#00FFFF", "#00FFCC", "#00CED1", "#1E90FF",
                                "#4169E1", "#8A2BE2", "#9400D3"],
                'bg_color': (0.25, 0.35, 0.90, 1),
                'blank_color': (0.1, 0.1, 0.1, 1),
                'your_moves_label_color' : '#ffff80'
            },
            {
                'name': 'Earth Tones',
                'button_colors': ["#8B4513", "#A0522D", "#D2691E", "#CD853F",
                                "#F4A460", "#DEB887", "#D2B48C", "#BC8F8F",
                                "#A52A2A", "#800000", "#556B2F", "#6B8E23",
                                "#808000", "#BDB76B", "#EEE8AA"],
                'bg_color': (0.35, 0.25, 0.20, 1),
                'blank_color': (0.25, 0.15, 0.10, 1),
                'your_moves_label_color' : '#d3f807'
            },
            {
                'name': 'Monochrome',
                'button_colors': ["#FFFFFF", "#F0F0F0", "#E0E0E0", "#D0D0D0",
                                "#C0C0C0", "#B0B0B0", "#A0A0A0", "#909090",
                                "#808080", "#707070", "#606060", "#505050",
                                "#404040", "#303030", "#202020"],
                'bg_color': (0.5, 0.5, 0.5, 1),
                'blank_color': (0.2, 0.2, 0.2, 1),
                'your_moves_label_color' : '#d3f807'
            },
            {
                'name': 'Sunrise',
                'button_colors': ["#FF4500", "#FF6347", "#FF7F50", "#FF8C00",
                                "#FFA500", "#FFD700", "#FFFF00", "#FFDAB9",
                                "#FFE4B5", "#FFE4E1", "#FFF0F5", "#FAFAD2",
                                "#F0E68C", "#E6E6FA", "#D8BFD8"],
                'bg_color': (0.98, 0.65, 0.45, 1),
                'blank_color': (0.9, 0.5, 0.3, 1),
                'your_moves_label_color' : '#007d00'
            },
            {
                'name': 'Ocean Depth',
                'button_colors': ["#000080", "#00008B", "#0000CD", "#0000FF",
                                "#1E90FF", "#00BFFF", "#87CEEB", "#87CEFA",
                                "#4682B4", "#5F9EA0", "#20B2AA", "#008080",
                                "#008B8B", "#00CED1", "#40E0D0"],
                'bg_color': (0.0, 0.15, 0.35, 1),
                'blank_color': (0.0, 0.25, 0.5, 1),
                'your_moves_label_color' : '#d3f807'
            },
            {
                'name': 'Berry Mix',
                'button_colors': ["#8B0000", "#A52A2A", "#B22222", "#DC143C",
                                "#FF0000", "#FF1493", "#FF69B4", "#FFB6C1",
                                "#DA70D6", "#BA55D3", "#9932CC", "#8A2BE2",
                                "#9400D3", "#4B0082", "#8B008B"],
                'bg_color': (0.35, 0.0, 0.15, 1),
                'blank_color': (0.5, 0.0, 0.25, 1),
                'your_moves_label_color' : '#d3f807'
            },
            {
                'name': 'Retro Vibes',
                'button_colors': ["#FF6F61", "#FFA177", "#FFB347", "#FFD700",
                                "#AADB1E", "#7FDBB6", "#7FDBFF", "#92C3F4",
                                "#A17FFF", "#D47FFF", "#FF7FD4", "#FF4F8B",
                                "#FF2D55", "#C10020", "#8B0000"],
                'bg_color': (0.95, 0.85, 0.75, 1),
                'blank_color': (0.9, 0.8, 0.7, 1),
                'your_moves_label_color' : '#0315bc'
            },
            {
                'name': 'Winter Frost',
                'button_colors': ["#F0FFFF", "#E0FFFF", "#D1E0E0", "#C0D9D9",
                                "#B0C4DE", "#A7C7E7", "#87CEEB", "#87CEFA",
                                "#778899", "#708090", "#6495ED", "#4682B4",
                                "#5F9EA0", "#48D1CC", "#00CED1"],
                'bg_color': (0.9, 0.95, 1.0, 1),
                'blank_color': (0.8, 0.85, 0.9, 1),
                'your_moves_label_color' : '#00aa00'
            }
        ]
        self.current_theme = self.themes[0]
        self.current_theme = next((t for t in self.themes if t['name'] == theme_name), self.themes[0])
        self.solved_tiles = list(range(1, 15)) + [None, None]
        self.your_moves = 0
        self.initial_tiles = []
        self.initial_remaining_moves = 0
        Window.clearcolor = self.current_theme['bg_color']
        self.setup_puzzle()

    def build(self):
        self.setup_puzzle()
        self.sound = SoundLoader.load(r"assets/click.wav")
        self.buttons = []
        self.root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        game_over_layout = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(8),
            padding=[dp(20), 0, dp(20), 0]
        )
        self.remaining_moves_label = Label(
            text=f"Remaining Moves: {self.remaining_moves}",
            font_size=sp(16),
            size_hint_x = 0.5,
            halign='left',
            color = '#d20000',
            bold = True,
            text_size=(None, None),
            valign='center',
            padding=[dp(10), 0]
        )
        self.remaining_moves_label.bind(size=self.remaining_moves_label.setter('text_size'))
        self.your_moves_label = Label(
            text=f"Your Moves: {self.your_moves}",
            font_size=sp(16),
            size_hint_x=0.5,
            halign='right',
            color =  self.current_theme['your_moves_label_color'],
            bold = True,
            text_size=(None, None),
            valign='center',
            padding=[0, 0, dp(10), 0]
        )
        self.your_moves_label.bind(size=self.your_moves_label.setter('text_size'))
        top_buttons = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(50),
            spacing=dp(10)
        )
        self.easy_mode_button = self.ThemeButton(
            text="EASY",
            size_hint=(1, None),
            height=dp(50),
            font_size=sp(18),
            background_color='#4affed',
            border_width=2 if self.mode == "easy" else 0,
            background_normal='',
            on_press=lambda x: self.switch_mode("easy"))
        self.hard_mode_button = self.ThemeButton(
            text="HARD",
            size_hint=(1, None),
            height=dp(50),
            font_size=sp(18),
            background_color='#cccccc',
            border_width=2 if self.mode == "easy" else 0,
            background_normal='',
            on_press=lambda x: self.switch_mode("hard"))
        next_button = Button(
            text="NEXT",
            background_color=(0.6, 1, 0.6, 1),
            on_press=self.next_puzzle)
        theme_btn = Button(
            text="Themes",
            background_color='#45bada',
            on_press=self.open_theme)
        top_buttons.add_widget(self.easy_mode_button)
        top_buttons.add_widget(self.hard_mode_button)
        top_buttons.add_widget(next_button)
        top_buttons.add_widget(theme_btn)
        game_over_layout.add_widget(self.remaining_moves_label)
        game_over_layout.add_widget(self.your_moves_label)
        self.root.add_widget(game_over_layout)
        self.root.add_widget(top_buttons)
        self.grid = GridLayout(cols=4, spacing=dp(5), padding=dp(5), size_hint=(1, 0.8))
        for i in range(16):
            btn = self.ThemeButton(font_size=sp(18), size_hint=(1, 1))
            btn.bind(on_press=lambda instance, i=i: self.tile_click(i))
            self.grid.add_widget(btn)
            self.buttons.append(btn)
        self.root.add_widget(self.grid)
        self.update_buttons()
        self.update_mode_buttons()
        return self.root

    def update_buttons(self):
        for i, val in enumerate(self.tiles):
            btn = self.buttons[i]
            if val is None:
                btn.text = ""
                btn.disabled = True
                btn.background_color = self.current_theme['blank_color']
                self.your_moves_label.color = self.current_theme['your_moves_label_color']
            else:
                btn.text = str(val)
                btn.disabled = False
                color_index = val % len(self.current_theme['button_colors'])
                hex_color = self.current_theme['button_colors'][color_index]
                rgb = self.hex_to_rgb(hex_color)
                btn.background_color = rgb + [1]
                btn.color = (1, 1, 1, 1)

    def tile_click(self, index):
        if self.mode == "easy":
            blank_indices = [i for i, x in enumerate(self.tiles) if x is None]
            for blank in blank_indices:
                if self.can_swap(index, blank):
                    self.swap_tiles(index, blank)
                    break
        else:
            blank_index = self.tiles.index(None)
            if self.can_swap(index, blank_index):
                self.swap_tiles(index, blank_index)

    def swap_tiles(self, a, b):
        self.tiles[b], self.tiles[a] = self.tiles[a], self.tiles[b]
        threading.Thread(target=self.play_sound, daemon=True).start()
        self.remaining_moves -= 1
        self.your_moves += 1
        self.remaining_moves_label.text = f"Remaining Moves: {self.remaining_moves}"
        self.your_moves_label.text = f"Your Moves: {self.your_moves}"
        self.update_buttons()
        solved = self.check_solution()
        if not solved and self.remaining_moves <= 0:
            self.show_game_over_popup()

    def check_solution(self):
        solved = False
        if self.mode == "easy" and self.tiles == self.solved_tiles:
            SoundLoader.load(r"assets/win.wav").play()
            self.show_popup("Solved!", "CONGRATULATIONS...!", on_close=self.load_new_puzzle)
            solved = True
        elif self.mode == "hard" and self.tiles[:-1] == list(range(1, 16)):
            SoundLoader.load(r"assets/win.wav").play()
            self.show_popup("Solved!", "Congratulations!", on_close=self.load_new_puzzle)
            solved = True
        return solved

    def can_swap(self, idx1, idx2):
        row1, col1 = divmod(idx1, 4)
        row2, col2 = divmod(idx2, 4)
        return abs(row1 - row2) + abs(col1 - col2) == 1

    def is_solvable(self):
        tiles = [x for x in self.tiles if x is not None]
        inv_count = 0
        for i in range(len(tiles)):
            for j in range(i + 1, len(tiles)):
                if tiles[i] > tiles[j]:
                    inv_count += 1
        if self.mode == "easy":
            blank_row = (self.tiles.index(None) // 4)
            return (inv_count + blank_row) % 2 == 0
        else:
            blank_row = 3 - (self.tiles.index(None) // 4)
            return (inv_count + blank_row) % 2 == 0

    def next_puzzle(self, instance):
        self.setup_puzzle()
        self.update_buttons()

    def load_new_puzzle(self):
        self.setup_puzzle()
        self.update_buttons()

    def show_popup(self, title, message, on_close=None):
        label = self.AnimatedLabel(
            text_size=(None, None),
            halign='center',
            valign='middle',
            font_size=sp(24)
        )
        label.start_animation(message)
        popup = Popup(
            title=title,
            content=label,
            size_hint=(0.7, 0.4),
            auto_dismiss=True
        )

        def handle_dismiss(instance):
            Clock.unschedule(label._animation_event)
            if on_close:
                on_close()
        popup.bind(on_dismiss=handle_dismiss)
        popup.open()

    def play_sound(self):
        if self.sound:
            self.sound.play()

    def hex_to_rgb(self, hex_color):
        return [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]

    def open_theme(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        scroll = ScrollView()
        theme_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        theme_grid.bind(minimum_height=theme_grid.setter('height'))
        for theme in self.themes:
            btn = self.ThemeButton(
                text=theme['name'],
                size_hint_y=None,
                height=dp(40),
                background_color=theme['bg_color'],
                on_press=lambda x, t=theme: self.apply_theme(t)
            )
            if theme == self.current_theme:
                btn.border_width = 2
                btn.border_color = (1,1,1,1)
            theme_grid.add_widget(btn)
        scroll.add_widget(theme_grid)
        content.add_widget(scroll)
        close_btn = Button(text="Close", size_hint=(1, None), height=40)
        close_btn.bind(on_press=lambda x: self.popup.dismiss())
        content.add_widget(close_btn)
        self.popup = Popup(title='Choose Theme', content=content,
                          size_hint=(0.7, 0.8))
        self.popup.open()

    def apply_theme(self, theme):
        self.current_theme = theme
        Window.clearcolor = theme['bg_color']
        Config.set('puzzle', 'theme', theme['name'])
        Config.write()
        self.update_buttons()
        self.popup.dismiss()

    def on_start(self):
        Window.bind(on_resize=self.update_layout)

    def update_layout(self, *args):
        for btn in self.buttons:
            btn.font_size = sp(Window.width * 0.06)

    def is_puzzle_solved(self):
        return self.tiles[:-1] == list(range(1, 16))

    def get_adjacent_indices(self, index):
        row, col = divmod(index, 4)
        indices = []
        if row > 0:
            indices.append(index - 4)
        if row < 3:
            indices.append(index + 4)
        if col > 0:
            indices.append(index - 1)
        if col < 3:
            indices.append(index + 1)
        return indices

    def find_solving_move(self):
        blank_indices = [i for i, x in enumerate(self.tiles) if x is None]
        for blank in blank_indices:
            for idx in self.get_adjacent_indices(blank):
                if 0 <= idx < 16:
                    temp = self.tiles.copy()
                    temp[blank], temp[idx] = temp[idx], temp[blank]
                    if temp == self.solved_tiles:
                        return idx
        return None

    def highlight_suggestion(self, tile_index):
        btn = self.buttons[tile_index]
        Animation.cancel_all(btn)
        btn.border_width = 0
        btn.border_color = [1, 1, 0, 1]

        def animate_border(*args):
            btn.border_width = 0
            anim = (
                Animation(border_width=4, duration=0.3) +
                Animation(border_width=0, duration=0.3)
            )
            anim.repeat = True
            anim.start(btn)
        animate_border()

    def setup_puzzle(self):
        if self.mode == "easy":
            self.solved_tiles = list(range(1, 15)) + [None, None]
            self.tiles = self.solved_tiles.copy()
        else:
            self.solved_tiles = list(range(1, 16)) + [None]
            self.tiles = self.solved_tiles.copy()
        random.shuffle(self.tiles)
        while not self.is_solvable():
            random.shuffle(self.tiles)
        self.initial_remaining_moves = random.randint(160, 180)
        self.remaining_moves = self.initial_remaining_moves
        self.initial_tiles = self.tiles.copy()
        self.your_moves = 0
        if hasattr(self, 'remaining_moves_label'):
            self.update_labels()

    def switch_mode(self, mode):
        self.mode = mode
        self.setup_puzzle()
        self.update_buttons()
        self.update_mode_buttons()
        self.easy_mode_button.border_width = 2 if self.mode == "easy" else 0
        self.hard_mode_button.border_width = 2 if self.mode == "hard" else 0

    def update_mode_buttons(self):
        self.easy_mode_button.border_width = 2 if self.mode == "easy" else 0
        self.hard_mode_button.border_width = 2 if self.mode == "hard" else 0
        self.easy_mode_button.background_color = 'green' if self.mode == "easy" else 'red'
        self.hard_mode_button.background_color = 'green' if self.mode == "hard" else 'red'

    def show_game_over_popup(self):
        SoundLoader.load(r"assets/game_over.wav").play()
        self.show_popup("Game Over", "OUT OF MOVES!\nTRY AGAIN...", on_close=self.reset_puzzle)

    def reset_puzzle(self):
        self.tiles = self.initial_tiles.copy()
        self.remaining_moves = self.initial_remaining_moves
        self.your_moves = 0
        self.update_labels()
        self.update_buttons()

    def update_labels(self):
        self.remaining_moves_label.text = f"Remaining Moves: {self.remaining_moves}"
        self.your_moves_label.text = f"Your Moves: {self.your_moves}"

if __name__ == '__main__':
    PuzzleApp().run()
