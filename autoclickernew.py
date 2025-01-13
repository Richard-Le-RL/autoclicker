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
# toggle_keys = set([keyboard.Key.shift]) # When we initially used just the shift key for triggering the clicker
waiting_for_keys = False
current_keys = set() # Start as an empty set 

# Helper function to get key symbol
def get_key_symbol(key):
    # Handle special keys
    if isinstance(key, keyboard.Key):
        if key == keyboard.Key.shift:
            return "⇧-left"  
        elif key == keyboard.Key.ctrl:
            return "⌃"
        elif key == keyboard.Key.alt:
            return "⌥"
        elif key == keyboard.Key.caps_lock:
            return "⇪"
        elif key == keyboard.Key.shift_l:
            return "⇧-left"
        elif key == keyboard.Key.shift_r:
            return "⇧-right"  # Right shift
        elif key == keyboard.Key.cmd:
            return "⌘-left"
        elif key == keyboard.Key.cmd_r:
            return "⌘-right"
        else:
            return str(key).split('.')[-1]
    # Handle character keys
    elif hasattr(key, 'char') and key.char is not None:
        return key.char
    # Handle other cases (such as function keys)
    return str(key)

# Function to save settings
def save_settings():
    with open(settings_file, "w") as file:
        file.write(f"clicks_per_second={clicks_per_second}\n")
        file.write(f"toggle_keys={[get_key_symbol(key) for key in toggle_keys]}\n")

# Function to load settings
def load_settings():
    global clicks_per_second, toggle_keys
    if os.path.exists(settings_file):
        with open(settings_file, "r") as file:
            for line in file:
                if line.startswith("clicks_per_second="):
                    try:
                        clicks_per_second = float(line.strip().split("=")[1])
                    except ValueError:
                        clicks_per_second = 1.0
                elif line.startswith("toggle_keys="):
                    try:
                        keys = eval(line.strip().split("=")[1])
                        toggle_keys.clear()
                        for key in keys:
                            if hasattr(keyboard.Key, key):
                                toggle_keys.add(getattr(keyboard.Key, key))
                            else:
                                toggle_keys.add(keyboard.KeyCode.from_char(key))
                    except Exception:
                        toggle_keys = set([keyboard.Key.shift])

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
    global clicking, waiting_for_keys, current_keys, toggle_keys
    if waiting_for_keys:
        current_keys.add(key)
        update_key_display()
        return

    current_keys.add(key)
    
    print(f"Pressed: {key}, Current Keys: {current_keys}, Toggle Keys: {toggle_keys}")  # Debugging line
    
    # Check if all keys in toggle_keys are pressed (not just one key)
    if set(toggle_keys).issubset(current_keys):
        if clicking:
            stop_clicking()
        else:
            start_thread()

def on_release(key):
    global current_keys, waiting_for_keys
    if waiting_for_keys:
        return
    if key in current_keys:
        current_keys.remove(key)

    print(f"Released: {key}, Current Keys: {current_keys}")  # Debugging line
    
    # Ensure that the autoclicker is not triggered unless all keys are pressed
    if set(toggle_keys).issubset(current_keys):
        if clicking:
            stop_clicking()
        else:
            start_thread()



listener = keyboard.Listener(on_press=on_press, on_release=on_release)
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

def set_new_toggle_keys():
    global toggle_keys, waiting_for_keys, current_keys
    if not current_keys:
        messagebox.showerror("Error", "No keys selected for toggle. Please press some keys.")
        return
    toggle_keys = current_keys.copy()
    
    # Reset current_keys to ensure it doesn't trigger with incomplete key combinations
    current_keys = set()  # Reset to ensure that only the full combination can trigger

    waiting_for_keys = False
    key_entry.config(state="normal")
    key_entry.delete(0, tk.END)
    key_entry.insert(0, "+".join([get_key_symbol(key) for key in toggle_keys]))
    key_entry.config(state="readonly")
    key_label.config(text=f"Toggle Keys (current: {', '.join([get_key_symbol(key) for key in toggle_keys])}):")
    
    save_settings()
    messagebox.showinfo("Keybind Set", f"Toggle keys set to: {', '.join([get_key_symbol(key) for key in toggle_keys])}")


def start_keybinding():
    global waiting_for_keys, current_keys
    waiting_for_keys = True
    current_keys = set()
    key_entry.config(state="normal")
    key_entry.delete(0, tk.END)
    key_entry.insert(0, "Press keys...")
    key_entry.config(state="readonly")

def update_key_display():
    key_entry.config(state="normal")
    key_entry.delete(0, tk.END)
    key_entry.insert(0, " + ".join([get_key_symbol(key) for key in current_keys]))
    key_entry.config(state="readonly")

# Function to update UI state
def update_ui_state():
    if clicking:
        status_label.config(text="Status: ON", bg="green", fg="white")
    else:
        status_label.config(text="Status: OFF", bg="red", fg="white")

# Build the Tkinter application
app = tk.Tk()
app.title("Automatic Mouse Clicker")
app.geometry("450x500")

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
key_label = tk.Label(app, text=f"Toggle Keys (current: {', '.join([get_key_symbol(key) for key in toggle_keys])}):")
key_label.pack(pady=5)

key_entry = tk.Entry(app, relief="ridge", state="readonly")
key_entry.insert(0, " + ".join([get_key_symbol(key) for key in toggle_keys]))
key_entry.pack(pady=5)

update_key_button = tk.Button(app, text="Set New Toggle Keys", command=start_keybinding)
update_key_button.pack(pady=5)

confirm_key_button = tk.Button(app, text="Confirm Toggle Keys", command=set_new_toggle_keys)
confirm_key_button.pack(pady=5)

# Instructions Label
instructions_label = tk.Label(app, text="Press the selected key combination to toggle clicking on/off", justify="center")
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