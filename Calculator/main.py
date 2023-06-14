# download image files first
# arithmetric logic

import customtkinter as ctk
from buttons import Button, ImageButton, NumButton, MathButton, MathImageButton
import darkdetect
from PIL import Image
from settings import *

# As this a code for windows, this is to prevent mac users from getting error
try:
    from ctypes import windll, byref, sizeof, c_int
except:
    pass

class Calculator(ctk.CTk):
    def __init__(self, is_dark):

        # setup
        super().__init__(fg_color = (WHITE, BLACK))
        # 1. set appearance to dark or light depending on is_dark - bool
        ctk.set_appearance_mode(f'{"dark" if is_dark else "light"}')

        # 2. fg_color = White or Black
        # 3. get the start window size from the settings and disable window resizing
        self.geometry(f'{APP_SIZE[0]}x{APP_SIZE[1]}')
        self.resizable(False, False)

        # 4. hide the title and the icon
        self.title('')
        self.iconbitmap('empty.ico')
        self.title_bar_color(is_dark)

        # grid layout - 7 rows, 4 column
        self.rowconfigure(list(range(MAIN_ROWS)), weight = 1, uniform = 'a')
        self.columnconfigure(list(range(MAIN_COLUMNS)), weight = 1, uniform = 'a')

        # data
        self.result_string = ctk.StringVar(value = '0')
        self.formula_string = ctk.StringVar(value = '')
        self.display_nums = []
        self.full_operation = []

        # widgets
        self.create_widgets ()

        self.mainloop()

    def create_widgets(self):
        # fonts
        main_font = ctk.CTkFont(family = FONT, size = NORMAL_FONT_SIZE)
        result_font = ctk.CTkFont(family = FONT, size = OUTPUT_FONT_SIZE)


        #output labels
        OutputLabel(self, 0, 'SE', main_font, self.formula_string) #formula
        OutputLabel(self, 1, 'E', result_font, self.result_string) # result

        # clear (AC) button
        Button(
            parent = self, 
            func = self.clear, # do not call it yet, only pass
            text = OPERATORS['clear']['text'], 
            col = OPERATORS['clear']['col'],
            row = OPERATORS['clear']['row'],
            font = main_font,
            span = 1
            )
        
        # percentage button
        Button(
            parent = self, 
            func = self.percent, # do not call it yet, only pass
            text = OPERATORS['percent']['text'], 
            col = OPERATORS['percent']['col'],
            row = OPERATORS['percent']['row'],
            font = main_font,
            span = 1
            )
        
        # invert button
        invert_image = ctk.CTkImage(
            light_image= Image.open(OPERATORS['invert']['image path']['dark']),
            dark_image= Image.open(OPERATORS['invert']['image path']['light'])
            )
        ImageButton(
            parent = self, 
            func = self.invert, # do not call it yet, only pass
            col = OPERATORS['invert']['col'],
            row = OPERATORS['invert']['row'],
            image = invert_image
            )
        
        # num buttons
        for num, data in NUM_POSITIONS.items():
            NumButton(
                parent = self,
                text = num, 
                func = self.num_press, 
                col = data['col'], 
                row = data['row'], 
                font = main_font,
                span = data['span']
                )
            
        # maths buttons
        for operator, data in MATHS_POSITIONS.items(): # items() key value pairs
            if data['image path']:
                divide_image = ctk.CTkImage(
                    light_image= Image.open(data['image path']['dark']),
                    dark_image= Image.open(data['image path']['light']),
                    )
                
                MathImageButton(
                    parent = self,
                    operator = operator, 
                    func = self.math_press, 
                    col = data['col'], 
                    row = data['row'], 
                    image = divide_image)
            else:
                MathButton(
                    parent = self,
                    text = data['character'], 
                    operator = operator, 
                    func = self.math_press, 
                    col = data['col'], 
                    row = data['row'], 
                    font = main_font)
    
    # Functionalities of the buttons
    def num_press(self, value):
        self.display_nums.append(str(value))
        full_number = ''.join(self.display_nums)
        self.result_string.set(full_number)

    def math_press(self, value):
        current_number = ''.join(self.display_nums)

        if current_number:
            self.full_operation.append(current_number)

            if value != '=':
                # update data - value string
                self.full_operation.append(value)
                self.display_nums.clear()
                
                # update output (operation)
                self.result_string.set('')
                self.formula_string.set(' '.join(self.full_operation))

            else:
                formula = ' '.join(self.full_operation)
                result = eval(formula) # eval must be used very carefully as security risk - do not use it for a website


                # format the result - if result is the data type, load and return true or false
                    # problem - too many numbers after the decimal
                    # 2. an integer is formatted like a float after division
                if isinstance(result, float):
                    if result.is_integer(): # check if it is an integer or float point number
                        result = int(result) 
                    else:
                        result = round(result, 5)

                # update data + clear the full operation list + display nums should have the value of the result
                self.full_operation.clear()
                self.display_nums = [str(result)]

                # update output
                self.result_string.set(result)
                self.formula_string.set(formula)

    def clear(self):
        # clear the output
        self.result_string.set(0)
        self.formula_string.set('')

        # clear the data
        self.display_nums.clear()
        self.full_operation.clear()

    # divide current value by 100
    def percent(self):
        # cannot start with current number = ... as starting with 0 will create a ValueError
        if self.display_nums: # if list is not empty
            current_number = float(''.join(self.display_nums))
            percent_number = current_number / 100

            # update the data and output
            self.display_nums = list(str(percent_number))
            self.result_string.set(''.join(self.display_nums))

    def invert(self):

        current_number = ''.join(self.display_nums)
        if current_number:
            # if we have a number - checks positive/negative
            if float(current_number) > 0:
                self.display_nums.insert(0, '-') # insert value at index 0 and negative value
            else:
                del self.display_nums[0]

            self.result_string.set(''.join(self.display_nums))

    def title_bar_color(self, is_dark):
        try:
            HWND = windll.user32.GetParent(self.winfo_id())
            DWMWA_ATTRIBUTE = 35
            COLOR = TITLE_BAR_HEX_COLORS['dark'] if is_dark else TITLE_BAR_HEX_COLORS['light']
            windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_ATTRIBUTE, byref(c_int(COLOR), sizeof(c_int)))
        except:
            pass

# once for the formula and for the actual output
class OutputLabel(ctk.CTkLabel):
    def __init__(self, parent, row, anchor, font, string_var):
        super().__init__(master = parent, text = '123', font = font, textvariable = string_var)
        self.grid(column = 0, columnspan = 4, row = row, sticky = anchor, padx = 10)


if __name__ == '__main__':
    Calculator(darkdetect.isDark())