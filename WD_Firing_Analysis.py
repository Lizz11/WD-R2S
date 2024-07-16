import h5py
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog

# Global variables to store the file and channels
f = None
channels = []
channel_names = []

def load_file():
    global f, channels, channel_names
    file_path = filedialog.askopenfilename(title="Select HDF5 File", filetypes=[("HDF5 files", "*.h5;*.hdf5")])
    if file_path:
        try:
            f = h5py.File(file_path, "r")
            channels = list(f['channels'])
            channel_names = [f['channels'][i].attrs['name'] for i in channels]
            channel_combobox['values'] = channel_names  # Update combobox values
            channel_combobox.set("Select a channel")  # Reset default text
            channel_combobox.grid(row=2, column=0, columnspan=2, padx=20, pady=10)  # Centered
            status_label.config(text="File loaded successfully.", fg="black")  # Changed color to black
        except Exception as e:
            status_label.config(text=f"Error loading file: {e}", fg="#d32f2f")  # Keep error text red

def plot_channel(selected_channel):
    # Retrieve channel data
    time = f['channels'][selected_channel]['time'][:]
    data = f['channels'][selected_channel]['data'][:]
    name = f['channels'][selected_channel].attrs['name']
    units = f['channels'][selected_channel].attrs['units']
    
    # Plotting the channel data
    plt.figure(figsize=(10, 5))
    plt.plot(time, data, '.', label=f"{name} ({units})", markersize=5)
    plt.legend()
    plt.title(name)
    plt.xlabel('Time')
    plt.ylabel(units)
    plt.grid()
    plt.tight_layout()
    plt.show()
    
    print(f"Selected channel: {name}")

def on_channel_select(event):
    if f is not None:
        selected_name = channel_combobox.get()
        selected_channel = channels[channel_names.index(selected_name)]
        plot_channel(selected_channel)  # Automatically plot after selection
    else:
        status_label.config(text="Please load a file first.", fg="#d32f2f")  # Error in red

# Creating the GUI
root = tk.Tk()
root.title("Channel Selector")
root.geometry("400x250")
root.configure(bg="#e0e0e0")

# Label for instructions
label = tk.Label(root, text="Select an HDF5 File:", bg="#e0e0e0", font=("Helvetica", 14, "bold"))
label.grid(row=0, column=0, columnspan=2, pady=(20, 10), sticky="nsew")

# Button to load file with size closely fitting the text
load_button = tk.Button(root, text="Load HDF5 File", command=load_file, bg="#4CAF50", fg="white", font=("Helvetica", 12))
load_button.grid(row=1, column=0, columnspan=2, pady=(0, 10), padx=(20,20), sticky="nsew")  # Centered

# Dropdown for channel selection
channel_combobox = ttk.Combobox(root, state='readonly', font=("Helvetica", 12))
channel_combobox.set("Select a channel")  # Set default text
channel_combobox.bind("<<ComboboxSelected>>", on_channel_select)

# Status label to show messages
status_label = tk.Label(root, text="", bg="#e0e0e0", font=("Helvetica", 10), fg="black")
status_label.grid(row=3, column=0, columnspan=2, pady=(10, 20), sticky="nsew")

# Configure grid weights for centering
for i in range(4):  # Adjust the number of rows
    root.grid_rowconfigure(i, weight=1)

for j in range(2):  # Adjust the number of columns
    root.grid_columnconfigure(j, weight=1)

# Run the application
root.mainloop()

# Closing the HDF5 file
if f is not None:
    f.close()
