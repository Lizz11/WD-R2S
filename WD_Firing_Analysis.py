import h5py
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

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
            channel_names = [f['channels'][i].attrs.get('name', f'Channel {i}') for i in channels]
            channel_combobox['values'] = channel_names
            channel_combobox.set("Select a channel")
            status_label.config(text="File loaded successfully.", fg="black")
            plot_button.config(state=tk.NORMAL)
        except Exception as e:
            status_label.config(text=f"Error loading file: {e}", fg="#d32f2f")

def plot_channel(selected_channel):
    try:
        time = f['channels'][selected_channel]['time'][:]
        data = f['channels'][selected_channel]['data'][:]
        name = f['channels'][selected_channel].attrs['name']
        units = f['channels'][selected_channel].attrs.get('units', 'Units')
        
        plt.figure(figsize=(10, 5))
        plt.plot(time, data, '.', label=f"Original {name} ({units})", markersize=5)
        
        plt.legend()
        plt.title(f"{name} Data")
        plt.xlabel('Time')
        plt.ylabel(units)
        plt.grid()
        plt.tight_layout()
        plt.show()
        
        print(f"Selected channel: {name}")
    except KeyError as e:
        status_label.config(text=f"Error plotting data: Missing {e}", fg="#d32f2f")

def calculate_of_ratio():
    try:
        start_time = float(start_time_entry.get())
        end_time = float(end_time_entry.get())

        if 'M850' not in f['channels'] or 'M730' not in f['channels']:
            raise ValueError("One or both channels not found in the file.")

        time_n2o = f['channels']['M850']['time'][:]
        data_n2o = f['channels']['M850']['data'][:]
        
        time_ipa = f['channels']['M730']['time'][:]
        data_ipa = f['channels']['M730']['data'][:]

        mask_n2o = (time_n2o >= start_time) & (time_n2o <= end_time)
        mask_ipa = (time_ipa >= start_time) & (time_ipa <= end_time)
        
        if not np.any(mask_n2o) or not np.any(mask_ipa):
            raise ValueError("No data found within the specified time range.")

        avg_n2o = np.mean(data_n2o[mask_n2o])
        avg_ipa = np.mean(data_ipa[mask_ipa])
        
        std_dev_n2o = np.std(data_n2o[mask_n2o])
        std_dev_ipa = np.std(data_ipa[mask_ipa])
        
        of_ratio = avg_n2o / avg_ipa
        of_ratio_error = of_ratio * np.sqrt((std_dev_n2o / avg_n2o) ** 2 + (std_dev_ipa / avg_ipa) ** 2)

        avg_n2o_rounded = round(avg_n2o, 4)
        avg_ipa_rounded = round(avg_ipa, 4)
        of_ratio_rounded = round(of_ratio, 4)
        of_ratio_error_rounded = round(of_ratio_error, 4)
        std_dev_n2o_rounded = round(std_dev_n2o, 4)
        std_dev_ipa_rounded = round(std_dev_ipa, 4)

        result_string = (f"Average N2O: {avg_n2o_rounded}\n"
                         f"Average IPA: {avg_ipa_rounded}\n"
                         f"OF Ratio: {of_ratio_rounded} ± {of_ratio_error_rounded}\n"
                         f"Standard Deviation N2O: {std_dev_n2o_rounded}\n"
                         f"Standard Deviation IPA: {std_dev_ipa_rounded}")

        result_window = tk.Toplevel(root)
        result_window.title("OF Ratio Results")
        result_text = tk.Text(result_window, wrap=tk.WORD)
        result_text.insert(tk.END, result_string)
        result_text.pack(padx=10, pady=10)
        result_text.config(state=tk.NORMAL)  # Make text editable for copying
        result_text.focus_set()
        result_text.tag_add("sel", "1.0", "end")  # Select all text for easy copying

    except ValueError as ve:
        messagebox.showerror("Error", str(ve))
    except Exception as e:
        messagebox.showerror("Error", f"Calculation error: {e}")

def calculate_thrust():
    try:
        if 'LC190' not in f['channels']:
            raise ValueError("Channel 'LC190' not found in the file.")
        
        data_lc190 = f['channels']['LC190']['data'][:]
        
        avg_lc190 = np.mean(data_lc190)
        std_dev_lc190 = np.std(data_lc190)

        avg_lc190_rounded = round(avg_lc190, 4)
        std_dev_lc190_rounded = round(std_dev_lc190, 4)

        result_string = (f"Average Thrust: {avg_lc190_rounded}\n"
                         f"Standard Deviation Thrust: {std_dev_lc190_rounded}")

        result_window = tk.Toplevel(root)
        result_window.title("Thrust Results")
        result_text = tk.Text(result_window, wrap=tk.WORD)
        result_text.insert(tk.END, result_string)
        result_text.pack(padx=10, pady=10)
        result_text.config(state=tk.NORMAL)  # Make text editable for copying
        result_text.focus_set()
        result_text.tag_add("sel", "1.0", "end")  # Select all text for easy copying

    except ValueError as ve:
        messagebox.showerror("Error", str(ve))
    except Exception as e:
        messagebox.showerror("Error", f"Calculation error: {e}")

def on_channel_select(event):
    if f is not None:
        selected_name = channel_combobox.get()
        if selected_name in channel_names:
            selected_channel = channels[channel_names.index(selected_name)]
        else:
            status_label.config(text="Invalid channel selection.", fg="#d32f2f")

# Creating the GUI
root = tk.Tk()
root.title("Channel Selector")
root.geometry("400x600")
root.configure(bg="#e0e0e0")

# Label for instructions
label = tk.Label(root, text="Select an HDF5 File:", bg="#e0e0e0", font=("Helvetica", 14, "bold"))
label.grid(row=0, column=0, columnspan=2, pady=(20, 10), sticky="nsew")

# Button to load file
load_button = tk.Button(root, text="Load HDF5 File", command=load_file, bg="#4CAF50", fg="white", font=("Helvetica", 12), width=20)
load_button.grid(row=1, column=0, columnspan=2, pady=(0, 5), padx=(20, 20), sticky="nsew")

# Status label for messages
status_label = tk.Label(root, text="", bg="#e0e0e0", font=("Helvetica", 10), fg="black")
status_label.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky="nsew")

# Dropdown for channel selection
channel_combobox = ttk.Combobox(root, state='readonly', font=("Helvetica", 10), width=18)
channel_combobox.set("Select a channel")
channel_combobox.bind("<<ComboboxSelected>>", on_channel_select)
channel_combobox.grid(row=3, column=0, columnspan=2, pady=(5, 10), sticky="nsew")

# Button to plot
plot_button = tk.Button(root, text="Plot", command=lambda: plot_channel(channels[channel_names.index(channel_combobox.get())]) if f else None, bg="#2196F3", fg="white", font=("Helvetica", 12), width=20, state=tk.DISABLED)
plot_button.grid(row=4, column=0, columnspan=2, pady=(10, 5), sticky="nsew")

# Time selection for OF Ratio
time_interval_label = tk.Label(root, text="Choose time interval:", bg="#e0e0e0", font=("Helvetica", 12))
time_interval_label.grid(row=5, column=0, columnspan=2, pady=(10, 5), sticky="nsew")

start_time_label = tk.Label(root, text="Start Time:", bg="#e0e0e0", font=("Helvetica", 12))
start_time_label.grid(row=6, column=0, sticky="e")
start_time_entry = tk.Entry(root, font=("Helvetica", 12))
start_time_entry.grid(row=6, column=1, pady=(5, 10), sticky="w")

end_time_label = tk.Label(root, text="End Time:", bg="#e0e0e0", font=("Helvetica", 12))
end_time_label.grid(row=7, column=0, sticky="e")
end_time_entry = tk.Entry(root, font=("Helvetica", 12))
end_time_entry.grid(row=7, column=1, pady=(5, 10), sticky="w")

# Calculate OF Ratio button
calculate_of_ratio_button = tk.Button(root, text="Calculate OF Ratio", command=calculate_of_ratio, bg="#2196F3", fg="white", font=("Helvetica", 12), width=20)
calculate_of_ratio_button.grid(row=8, column=0, columnspan=2, pady=(10, 5), sticky="nsew")

# Calculate thrust button
calculate_thrust_button = tk.Button(root, text="Calculate Thrust", command=calculate_thrust, bg="#2196F3", fg="white", font=("Helvetica", 12), width=20)
calculate_thrust_button.grid(row=9, column=0, columnspan=2, pady=(10, 20), sticky="nsew")

# Configure grid weights for centering
for i in range(10):
    root.grid_rowconfigure(i, weight=1)
for j in range(2):
    root.grid_columnconfigure(j, weight=1)

# Run the application
root.mainloop()

# Closing the HDF5 file
if f is not None:
    f.close()
