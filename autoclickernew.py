import tkinter as tk
from tkinter import messagebox
from pynput.mouse import Button, Controller
from pynput import keyboard
import threading
import time
import os

# Initialize mouse controller 
mouse = Controller()

# Globals to control the clicker
clicking = False
clicks_per_second = 1.0
click_button = Button.left
settings_file = "settings.txt"
toggle_key = keyboard.Key.shift
waiting_for_key = False

# Function to save settings
def save_settings():
    with open(settings_file, "w") as file:
        file.write(f"clicks_per_second={clicks_per_second}\n")
        file.write(f"toggle_key={toggle_key}\n")

# Function to load settings
def load_settings():
    global clicks_per_second, toggle_key
    if os.path.exists(settings_file):
        with open(settings_file, "r") as file:
            for line in file:
                if line.startswith("clicks_per_second="):
                    try:
                        clicks_per_second = float(line.strip().split("=")[1])
                    except ValueError:
                        clicks_per_second = 1.0
                elif line.startswith("toggle_key="):
                    try:
                        toggle_key = eval(line.strip().split("=")[1])
                    except Exception:
                        toggle_key = keyboard.Key.shift

# Function to perform mouse clicking
def start_clicking():
    global clicking
    while clicking:
        mouse.click(click_button, 1)
        time.sleep(1 / clicks_per_second)

# Function to start the clicker thread
def start_thread():
    global clicking
    if not clicking:
        clicking = True
        update_ui_state()  # Update UI state when starting
        thread = threading.Thread(target=start_clicking)
        thread.daemon = True  # Ensure thread exits when the program does
        thread.start()

# Function to stop clicking
def stop_clicking():
    global clicking
    clicking = False
    update_ui_state()  # Update UI state when stopping

# Key listener for hotkeys
def on_press(key):
    global clicking, toggle_key, waiting_for_key
    if waiting_for_key:
        set_new_toggle_key(key)
        return

    if key == toggle_key:
        if clicking:
            stop_clicking()
        else:
            start_thread()

listener = keyboard.Listener(on_press=on_press)
listener.start()

# Function to update clicks per second
def update_clicks_per_second(new_value):
    global clicks_per_second
    try:
        clicks_per_second = float(new_value)
        if clicks_per_second <= 0:
            raise ValueError("Clicks per second must be positive.")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid positive number for clicks per second.")
    save_settings()

def update_click_button(new_button):
    global click_button 
    if new_button == "Left":
        click_button = Button.left
    elif new_button == "Right":
        click_button = Button.right
    elif new_button == "Middle":
        click_button = Button.middle

def set_new_toggle_key(key):
    global toggle_key, waiting_for_key
    toggle_key = key
    waiting_for_key = False
    key_entry.config(state="normal")
    key_entry.delete(0, tk.END)
    key_entry.insert(0, key.name if hasattr(key, 'name') else str(key))
    key_entry.config(state="readonly")
    save_settings()
    messagebox.showinfo("Keybind Set", f"Toggle key set to: {key}")

# Function to update UI state
def update_ui_state():
    if clicking:
        status_label.config(text="Status: ON", bg="green", fg="white")
    else:
        status_label.config(text="Status: OFF", bg="red", fg="white")

# Build the Tkinter application
app = tk.Tk()
app.title("Automatic Mouse Clicker")
app.geometry("300x400")

# Load settings
load_settings()

# Clicks Per Second Label and Entry
cps_label = tk.Label(app, text="Clicks Per Second:")
cps_label.pack(pady=5)

# User Input
cps_entry = tk.Entry(app, relief="ridge")
cps_entry.insert(0, str(clicks_per_second))  # Load saved value
cps_entry.pack(pady=5)

# Update clicks per second button
update_button = tk.Button(app, text="Update Clicks Per Second", command=lambda: update_clicks_per_second(cps_entry.get()))
update_button.pack(pady=5)

# Button Selection Dropdown
button_label = tk.Label(app, text="Selected Mouse Button:")
button_label.pack(pady=5)

button_options = ["Left", "Right", "Middle"]
button_var = tk.StringVar(value="Left")
button_menu = tk.OptionMenu(app, button_var, *button_options, command=update_click_button)
button_menu.pack(pady=5)

# Toggle Key Selection
key_label = tk.Label(app, text="Toggle Key (current: shift):")
key_label.pack(pady=5)

key_entry = tk.Entry(app, relief="ridge", state="readonly")
key_entry.insert(0, toggle_key.name if hasattr(toggle_key, 'name') else str(toggle_key))
key_entry.pack(pady=5)

update_key_button = tk.Button(app, text="Set New Toggle Key", command=lambda: start_keybinding())
update_key_button.pack(pady=5)

def start_keybinding():
    global waiting_for_key
    waiting_for_key = True
    key_entry.config(state="normal")
    key_entry.delete(0, tk.END)
    key_entry.insert(0, "Press any key...")
    key_entry.config(state="readonly")

# Instructions Label
instructions_label = tk.Label(app, text="Press the selected key to toggle clicking on/off", justify="center")
instructions_label.pack(pady=10)

# Status Label
status_frame = tk.Frame(app, bg="black", padx=3, pady=3)
status_label = tk.Label(status_frame, text="Status: OFF", bg="red", fg="white", width=20, height=2)
status_label.pack()
status_frame.pack(pady=10)

# Quit Button
quit_button = tk.Button(app, text="Quit", command=lambda: (save_settings(), app.quit()))
quit_button.pack(pady=10)

app.mainloop()
