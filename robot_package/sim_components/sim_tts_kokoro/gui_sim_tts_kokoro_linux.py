from tkinter import *
import tkinter
from  tkinter import ttk # Using tables
import os
import sys


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent



# Adiciona o diretório pai ao path
# Caminho do diretório atual (onde está este script)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Sobe três níveis
parent_dir = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.append(parent_dir)
parent_dir = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.append(parent_dir)


# Closing application
def on_closing(window, self):
    # if messagebox.askokcancel("Quit", "Do you want to quit?"):
    print("Bye bye!")
    self.estado = "stopped"
    window.destroy()
    

# Graphical user interface class
class Gui(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        parent.title("Kokoro - TTS")
        self.w = 190
        self.h = 75
        self.estado = "running"
        parent.geometry(str(self.w) + "x" + str(self.h))

        # Define the closing app function
        parent.protocol("WM_DELETE_WINDOW", lambda: on_closing(parent, self)) 

        # Does not show the minimize button
        parent.resizable(0,0)

        # Font size 10 for buttons and texts in general
        self.font1 = ('Arial', 10)

        # Setting the default font for application
        parent.option_add( "*font", "Arial 9")

        # Define the top frame
        self.frame_top = tkinter.Frame(master=parent) #self.h

        self.frame_top.pack(side=tkinter.TOP)

        # Defining the image files /home/mrocha/MEGA/meus-codigos-2025/repositorios_git/evaml_2026/robot_package/sim_components/sim_tts_kokoro/images/tts_kokoro_0.png
        self.tts_kokoro_0 = PhotoImage(file = BASE_DIR / "images/tts_kokoro_0.png")
        self.tts_kokoro_1 = PhotoImage(file = BASE_DIR / "images/tts_kokoro_1.png")
        self.tts_kokoro_2 = PhotoImage(file = BASE_DIR / "images/tts_kokoro_2.png")
        self.tts_kokoro_3 = PhotoImage(file = BASE_DIR / "images/tts_kokoro_3.png")
        self.tts_kokoro_4 = PhotoImage(file = BASE_DIR / "images/tts_kokoro_4.png")

        # Define the frame that will accommodate the canvas with the EVA image
        self.frame_robot = tkinter.Frame(master=self.frame_top, width= 360) #self.h

        self.frame_robot.pack(side=tkinter.LEFT)

        # Creating the graphic canvas
        self.canvas = Canvas(self.frame_robot, width = 430, height = 900) # Canvas is necessary to use images with transparency
        self.canvas.pack(side=tkinter.LEFT)
        
       
        


