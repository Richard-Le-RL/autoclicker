import tkinter as tk
from tkinter import messagebox
from pynput.mouse import Button, Controller
from pynput import keyboard
import threading
import time

# Initialize mouse controller 
mouse = Controller()

# Globals to control the clicker
clicking = False
clicks_per_second = 1.0

# Function to perform mouse clicking
def start_clicking():
    global clicking
    while clicking:
        mouse.click(Button.left, 1)
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
    global clicking
    if key == keyboard.Key.shift:
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

# Function to update UI state
def update_ui_state():
    if clicking:
        status_label.config(text="Status: ON", bg="green", fg="white")
    else:
        status_label.config(text="Status: OFF", bg="red", fg="white")

# Build the Tkinter application
app = tk.Tk()
app.title("Automatic Mouse Clicker")
app.geometry("300x250")

# Clicks Per Second Label and Entry
cps_label = tk.Label(app, text="Clicks Per Second:")
cps_label.pack(pady=5)

cps_entry = tk.Entry(app)
cps_entry.insert(0, "1.0")  # Default value
cps_entry.pack(pady=5)

update_button = tk.Button(app, text="Update Clicks Per Second", command=lambda: update_clicks_per_second(cps_entry.get()))
update_button.pack(pady=5)

# Instructions Label
instructions_label = tk.Label(app, text="Press SHIFT to toggle clicking on/off", justify="center")
instructions_label.pack(pady=10)

# Status Label
status_label = tk.Label(app, text="Status: OFF", bg="red", fg="white", width=20, height=2)
status_label.pack(pady=10)

# Quit Button
quit_button = tk.Button(app, text="Quit", command=app.quit)
quit_button.pack(pady=10)

app.mainloop()
