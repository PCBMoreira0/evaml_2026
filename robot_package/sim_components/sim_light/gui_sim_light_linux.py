from tkinter import *
import tkinter
from  tkinter import ttk # Using tables

import sys

import os

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
parent_dir = os.path.abspath(os.path.join(BASE_DIR, "../../.."))
sys.path.append(parent_dir)
parent_dir = os.path.abspath(os.path.join(BASE_DIR, "../.."))
sys.path.append(parent_dir)
parent_dir = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.append(parent_dir)


# Closing application
def on_closing(window):
    # if messagebox.askokcancel("Quit", "Do you want to quit?"):
    print("Bye bye!")
    window.destroy()
    

# Graphical user interface class
class Gui(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        parent.title("Smart Bulb (1)")
        self.w = 180
        self.h = 170
        parent.geometry(str(self.w) + "x" + str(self.h))

        # Define the closing app function
        parent.protocol("WM_DELETE_WINDOW", lambda: on_closing(parent)) 

        # Does not show the minimize button
        parent.resizable(0,0)

        # Font size 10 for buttons and texts in general
        self.font1 = ('Arial', 10)

        # Setting the default font for application
        parent.option_add( "*font", "Arial 9")

        # Define the top frame
        self.frame_top = tkinter.Frame(master=parent) #self.h

        self.frame_top.pack(side=tkinter.TOP)

        # Defining the image files
        self.bulb_image = PhotoImage(file = (BASE_DIR / "images/bulb.png").resolve())

        # Define the frame that will accommodate the canvas with the EVA image
        self.frame_robot = tkinter.Frame(master=self.frame_top, width= 360) #self.h

        self.frame_robot.pack(side=tkinter.LEFT)

        # Creating the graphic canvas
        self.canvas = Canvas(self.frame_robot, width = 430, height = 900) # Canvas is necessary to use images with transparency
        self.canvas.pack(side=tkinter.LEFT, pady= 5)
        
       
        


