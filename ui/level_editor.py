from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
import json

class LevelEditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board = [[0 for _ in range(7)] for _ in range(7)]
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(20))
        
        # Top toolbar
        toolbar = BoxLayout(
            size_hint_y=None, 
            height=dp(50),
            spacing=dp(10)
        )
        
        # Tool buttons
        self.tools = {
            'empty': Button(text='Empty (0)', on_press=lambda x: self.select_tool(0)),
            'team_a': Button(text='Team A (1)', on_press=lambda x: self.select_tool(1)),
            'team_b': Button(text='Team B (2)', on_press=lambda x: self.select_tool(2)),
            'obstacle': Button(text='Obstacle (9)', on_press=lambda x: self.select_tool(9))
        }
        
        for button in self.tools.values():
            toolbar.add_widget(button)
            
        # Save and Cancel buttons
        save_btn = Button(text='Save Level', on_press=self.save_level)
        cancel_btn = Button(text='Cancel', on_press=self.cancel)
        toolbar.add_widget(save_btn)
        toolbar.add_widget(cancel_btn)
        
        main_layout.add_widget(toolbar)
        
        # Board grid
        self.grid = GridLayout(cols=7, spacing=dp(2))
        self.cells = []
        
        for i in range(7):
            row = []
            for j in range(7):
                cell = Button(
                    background_normal='',
                    background_color=(0.8, 0.8, 0.8, 1)
                )
                cell.bind(on_press=lambda btn, x=i, y=j: self.on_cell_press(x, y))
                self.grid.add_widget(cell)
                row.append(cell)
            self.cells.append(row)
            
        main_layout.add_widget(self.grid)
        
        # Status label
        self.status_label = Label(
            size_hint_y=None,
            height=dp(30),
            text='Select a tool and click cells to edit'
        )
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)
        self.current_tool = 0

    def select_tool(self, value):
        self.current_tool = value
        self._update_tool_buttons()

    def on_cell_press(self, x, y):
        self.board[x][y] = self.current_tool
        self._update_cell_colors()
        self._validate_board()

    def _update_tool_buttons(self):
        for button in self.tools.values():
            button.background_color = (0.8, 0.8, 0.8, 1)
        
        tool_map = {0: 'empty', 1: 'team_a', 2: 'team_b', 9: 'obstacle'}
        if self.current_tool in tool_map:
            self.tools[tool_map[self.current_tool]].background_color = (0.3, 0.7, 0.3, 1)

    def _update_cell_colors(self):
        for i in range(7):
            for j in range(7):
                value = self.board[i][j]
                if value == 0:
                    color = (0.8, 0.8, 0.8, 1)  # Empty
                elif value == 1:
                    color = (0.9, 0.1, 0.1, 1)  # Team A
                elif value == 2:
                    color = (0.1, 0.1, 0.9, 1)  # Team B
                else:  # 9
                    color = (0.3, 0.3, 0.3, 1)  # Obstacle
                self.cells[i][j].background_color = color

    def _validate_board(self):
        # Count pieces
        team_a = sum(row.count(1) for row in self.board)
        team_b = sum(row.count(2) for row in self.board)
        
        if team_a == team_b and team_a > 0:
            self.status_label.text = 'Valid board configuration'
            return True
        else:
            self.status_label.text = 'Invalid: Teams must have equal, non-zero pieces'
            return False

    def save_level(self, instance):
        if not self._validate_board():
            return
            
        try:
            with open('levels.txt', 'r') as f:
                levels = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            levels = []
            
        new_level = {
            "name": f"Custom Level {len(levels) + 1}",
            "size": [7, 7],
            "board": self.board
        }
        
        levels.append(new_level)
        
        with open('levels.txt', 'w') as f:
            json.dump(levels, f, indent=4)
            
        self.manager.current = 'start'

    def cancel(self, instance):
        self.manager.current = 'start'