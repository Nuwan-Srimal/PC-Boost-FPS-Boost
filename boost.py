# This Script 75% compeleted... this file have some problems. dont angry with me because its currently under maintaining


import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import subprocess

# Function Definitions for Button Actions
def cleanup(): # not compelete 
    try:
        # Execute the cleanup commands
        subprocess.run(['cmd', '/c', 'color f'], check=True)
        subprocess.run(['cmd', '/c', 'del /s /f /q c:\\windows\\temp\\*.*'], check=True)
        subprocess.run(['cmd', '/c', 'rd /s /q c:\\windows\\temp'], check=True)
        subprocess.run(['cmd', '/c', 'md c:\\windows\\temp'], check=True)
        subprocess.run(['cmd', '/c', 'del /s /f /q C:\\WINDOWS\\Prefetch\\*.*'], check=True)
        subprocess.run(['cmd', '/c', 'del /s /f /q %temp%\\*.*'], check=True)

        messagebox.showinfo("Action", "Cleanup action completed successfully.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# need to add
def visual_tweaks():
    messagebox.showinfo("Action", "Visual Tweaks action triggered")

def fps_boost():
    messagebox.showinfo("Action", "FPS Boost action triggered")

def services():
    messagebox.showinfo("Action", "Services action triggered")

def cpu_optimization():
    messagebox.showinfo("Action", "CPU Optimization action triggered")

def uninstall_microsoft_edge():
    messagebox.showinfo("Action", "Uninstall Microsoft EDGE action triggered")

def uninstall_onedrive():
    messagebox.showinfo("Action", "Uninstall OneDrive action triggered")

def disable_defender():
    messagebox.showinfo("Action", "Disable Defender action triggered")

def ultimate_performance():
    messagebox.showinfo("Action", "Ultimate Performance action triggered")

def restart_explorer():
    messagebox.showinfo("Action", "Restart Explorer.exe action triggered")

def about():
    messagebox.showinfo("About", "Prof.LoKi Boost OS\nVersion 1.0")

# Create the main window
root = tk.Tk()
root.title("Prof.LoKi Boost OS")
root.geometry("800x600")

# Icon for the Application
root.iconbitmap('dsa.ico')  # Replace with the path to your .ico file

# Set the background image
bg_image = Image.open("123.jpg")  # Replace with your background image
bg_image = bg_image.resize((1920, 1080), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# Use a custom font for the gaming theme (ensure the font file is in the correct path)
custom_font = ("Impact", 14)

# Create a title label with custom font and color
title_label = tk.Label(root, text="Prof.LoKi Boost OS", font=("Impact", 30), fg="#00ff00", bg="#000000")
title_label.pack(pady=20)

# Define button styles for gaming theme
button_style = {
    "width": 20,
    "height": 2,
    "bg": "#262626",
    "fg": "#00ff00",
    "activebackground": "#404040",
    "font": custom_font,
    "relief": "flat",  # Flat style for a more modern look
}

# Create and place buttons with a gaming look
buttons = [
    ("Cleanup", cleanup),
    ("Visual Tweaks", visual_tweaks),
    ("FPS Boost", fps_boost),
    ("Services", services),
    ("CPU Optimization", cpu_optimization),
    ("Uninstall Microsoft EDGE", uninstall_microsoft_edge),
    ("Uninstall OneDrive", uninstall_onedrive),
    ("Disable Defender", disable_defender),
    ("Ultimate Performance", ultimate_performance),
    ("Restart Explorer.exe", restart_explorer),
    ("About", about),
]

for text, command in buttons:
    button = tk.Button(root, text=text, command=command, **button_style)
    button.pack(pady=10)

# Run the application
root.mainloop()



# @license Prof.LoKi
