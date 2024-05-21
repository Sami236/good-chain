import msvcrt
import os
clear = lambda: os.system('cls')

class Menu:
    def __init__(self, title, options):  
        self.options = options
        self.title = title

    def display(self):
        selected_index = 0
        while True:
            # Clear the console
            clear()
            # Print the menu with the selected option highlighted
            print(self.title)
            for i, option in enumerate(self.options):
                if i == selected_index:
                    print(f"> {option}")
                else:
                    print(f"  {option}")
            # Wait for a key press
            key_code = ord(msvcrt.getch())
            # Move the selection up or down based on the arrow keys
            if key_code == 72:  # Up arrow
                selected_index = max(selected_index - 1, 0)
            elif key_code == 80:  # Down arrow
                selected_index = min(selected_index + 1, len(self.options) - 1)
            # Select the option and return its index when the user presses enter
            elif key_code == 13:  # Enter                
                return selected_index
            elif key_code == 27: #esc
                return -1
