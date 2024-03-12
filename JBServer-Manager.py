# i dont comment my code :clueless:
import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from urllib.parse import urljoin
import requests
from PIL import Image, ImageTk
from io import BytesIO
import zipfile
import getpass
import time
import shutil

def check_and_install_dependencies():
    try:
        import requests
        import PIL
        import tkinter

    except ImportError as e:
        module_name = str(e).split("'")[1]
        print(f"Installing {module_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
        print(f"{module_name} installed successfully.")

def get_user_home_directory():
    return os.path.expanduser("~")

SRCDS_FILE_PATH = os.path.join(get_user_home_directory(), 'srcds.txt')

API_URL = "https://fiallaspares.com/api/jbsm"
ICON_URL = "https://jbased-group.github.io/wiki/icon.png"

def fetch_files():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        files_list = response.json()
        return files_list
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch files: {e}")
        return []

def on_download_jbmod_button_click(destination_entry):
    download_jbmod_srcds(destination_entry)

def download_jbmod_srcds(destination_entry):
    try:
        srcds_location = destination_entry.get()

        if not srcds_location:
            messagebox.showerror("Error", "Please specify the SRCDS location.")
            return

        user_name = getpass.getuser()
        steamcmd_path = os.path.join(get_user_home_directory(), 'steamcmd')
        os.makedirs(steamcmd_path, exist_ok=True)
        os.chdir(steamcmd_path)

        steamcmd_url = "https://fiallaspares.com/steamcmd.exe"
        steamcmd_path_full = os.path.join(steamcmd_path, 'steamcmd.exe')
        print("The Application will freeze!! Please dont close it!!")
        #print("Starting SteamCMD with path:", steamcmd_path_full)  
        #print("Force Install Directory:", srcds_location)  

        response = requests.get(steamcmd_url)
        response.raise_for_status()

        with open(steamcmd_path_full, 'wb') as steamcmd_file:
            steamcmd_file.write(response.content)

        subprocess.run([steamcmd_path_full, "+login", "anonymous", "+force_install_dir", srcds_location, "+app_update", "2181210", "+quit"])

        time.sleep(0)
        
        server_cfg_path = os.path.join(srcds_location, 'jbmod', 'cfg', 'server.cfg')
        with open(server_cfg_path, 'w') as server_cfg_file:
            server_cfg_file.write("sv_airaccelerate 1000000")
        
        motd_txt_path = os.path.join(srcds_location, 'jbmod', 'cfg', 'motd.txt')
        with open(motd_txt_path, 'w') as motd_file:
            motd_file.write("Downloaded and Configured with JBServer Manager")

        messagebox.showinfo("Download Complete", "JBMod SRCDS downloaded and updated successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download JBMod SRCDS: {e}")

def list_plugins(srcds_location):
    plugins_directory = os.path.join(srcds_location, 'jbmod', 'addons', 'sourcemod', 'plugins')
    if not os.path.exists(plugins_directory):
        messagebox.showerror("Error", "Plugins directory does not exist.")
        return []

    plugin_files = os.listdir(plugins_directory)
    enabled_plugins = [file for file in plugin_files if not os.path.isdir(os.path.join(plugins_directory, file))]
    return enabled_plugins

def list_disabled_plugins(srcds_location):
    disabled_plugins_directory = os.path.join(srcds_location, 'jbmod', 'addons', 'sourcemod', 'plugins', 'disabled')
    if not os.path.exists(disabled_plugins_directory):
        messagebox.showerror("Error", "Disabled plugins directory does not exist.")
        return []

    disabled_plugin_files = os.listdir(disabled_plugins_directory)
    return disabled_plugin_files

def move_plugin(plugin_name, srcds_location, from_directory, to_directory):
    try:
        source_path = os.path.join(srcds_location, 'jbmod', 'addons', 'sourcemod', 'plugins', from_directory, plugin_name)
        destination_path = os.path.join(srcds_location, 'jbmod', 'addons', 'sourcemod', 'plugins', to_directory, plugin_name)
        shutil.move(source_path, destination_path)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to move plugin: {e}")
        return False

def show_plugin_list(srcds_location):
    enabled_plugin_files = list_plugins(srcds_location)
    disabled_plugin_files = list_disabled_plugins(srcds_location)

    plugin_window = tk.Toplevel()
    plugin_window.title("Sourcemod Plugin List")
    plugin_window.geometry("600x300")

    enabled_frame = tk.Frame(plugin_window)
    enabled_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    enabled_label = tk.Label(enabled_frame, text="Enabled Plugins")
    enabled_label.pack(pady=10)

    enabled_listbox = tk.Listbox(enabled_frame, font=("Arial", 12), height=10)
    enabled_listbox.pack(expand=True, fill="both", padx=10, pady=10)

    for plugin_file in enabled_plugin_files:
        enabled_listbox.insert(tk.END, plugin_file)

    disabled_frame = tk.Frame(plugin_window)
    disabled_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    disabled_label = tk.Label(disabled_frame, text="Disabled Plugins")
    disabled_label.pack(pady=10)

    disabled_listbox = tk.Listbox(disabled_frame, font=("Arial", 12), height=10)
    disabled_listbox.pack(expand=True, fill="both", padx=10, pady=10)

    for plugin_file in disabled_plugin_files:
        disabled_listbox.insert(tk.END, plugin_file)

    def move_to_enabled():
        selected_item = disabled_listbox.curselection()
        if selected_item:
            plugin_name = disabled_listbox.get(selected_item)
            if move_plugin(plugin_name, srcds_location, "disabled", ""):
                disabled_listbox.delete(selected_item)
                enabled_listbox.insert(tk.END, plugin_name)

    def move_to_disabled():
        selected_item = enabled_listbox.curselection()
        if selected_item:
            plugin_name = enabled_listbox.get(selected_item)
            if move_plugin(plugin_name, srcds_location, "", "disabled"):
                enabled_listbox.delete(selected_item)
                disabled_listbox.insert(tk.END, plugin_name)

    move_to_disabled_button = tk.Button(plugin_window, text="Disable", command=move_to_disabled)
    move_to_disabled_button.pack(side=tk.RIGHT, padx=10, pady=10)
    
    move_to_enabled_button = tk.Button(plugin_window, text="Enable", command=move_to_enabled)
    move_to_enabled_button.pack(side=tk.LEFT, padx=10, pady=10)



def launch_server(srcds_location):
    try:
        command = f'"{os.path.join(srcds_location, "srcds.exe")}" -game jbmod +port 27015 +map jb_buildingblocks +hostname "JBMod 0.5.4 Built with JBServer Manager " +maxplayers 10 -console'
        subprocess.run(command, shell=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch server: {e}")

def on_launch_button_click(destination_entry):
    srcds_location = destination_entry.get()

    if not os.path.exists(srcds_location):
        messagebox.showerror("Error", "Invalid SRCDS location.")
        return

    launch_server(srcds_location)

def download_sourcemod(destination_path):
    try:
        sourcemod_url = "https://fiallaspares.com/source.zip"

        response_sourcemod = requests.get(sourcemod_url)
        response_sourcemod.raise_for_status()

        sourcemod_file_destination = os.path.join(destination_path, 'source.zip')
        with open(sourcemod_file_destination, 'wb') as sourcemod_file:
            sourcemod_file.write(response_sourcemod.content)

        sourcemod_extract_path = os.path.join(destination_path, 'jbmod')
        with zipfile.ZipFile(sourcemod_file_destination, 'r') as zip_ref:
            zip_ref.extractall(sourcemod_extract_path)

        messagebox.showinfo("Download Complete", "Sourcemod downloaded and extracted successfully.")
        print("Sourcemod Downloaded!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download Sourcemod: {e}")

def on_sourcemod_button_click(destination_entry):
    destination_path = destination_entry.get()
    print("The Application will freeze!! Please dont close it!! It IS downloading Sourcemod!!")

    if not os.path.exists(destination_path):
        messagebox.showerror("Error", "Invalid destination path.")
        return

    download_sourcemod(destination_path)

def download_file(file_name, destination_path):
    try:
        file_url = urljoin("https://fiallaspares.com/jbsm/", file_name)
        file_destination = os.path.join(destination_path, 'jbmod', 'addons', 'sourcemod', 'plugins', file_name)

        response = requests.get(file_url)
        response.raise_for_status()

        with open(file_destination, 'wb') as downloaded_file:
            downloaded_file.write(response.content)

        messagebox.showinfo("Download Complete", f"{file_name} downloaded successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download {file_name}: {e}")

def update_listbox(listbox, files_list):
    listbox.delete(0, tk.END)
    for file_name in files_list:
        listbox.insert(tk.END, file_name)

def on_download_button_click(listbox, destination_entry, download_all=False):
    destination_path = destination_entry.get()

    if not os.path.exists(destination_path):
        messagebox.showerror("Error", "Invalid destination path.")
        return

    if download_all:
        files_list = fetch_files()
        for file_name in files_list:
            download_file(file_name, destination_path)
        messagebox.showinfo("Download Complete", "All files downloaded successfully.")
    else:
        selected_item = listbox.curselection()
        if selected_item:
            file_name = listbox.get(selected_item)
            download_file(file_name, destination_path)
            messagebox.showinfo("Download Complete", f"{file_name} downloaded successfully.")
        else:
            messagebox.showwarning("No File Selected", "Please select a file to download.")

def browse_destination(entry):
    folder_selected = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(tk.END, folder_selected)

def on_search(entry, listbox, files_list):
    query = entry.get().lower()
    filtered_files = [file for file in files_list if query in file.lower()]
    update_listbox(listbox, filtered_files)

def load_icon(icon_url):
    try:
        response = requests.get(icon_url)
        response.raise_for_status()
        icon_data = BytesIO(response.content)
        icon_image = Image.open(icon_data)
        return ImageTk.PhotoImage(icon_image)
    except Exception as e:
        messagebox.showwarning("Icon Error", f"Failed to load icon: {e}")
        return None

def save_srcds_location(srcds_location):
    try:
        with open(SRCDS_FILE_PATH, 'w') as file:
            file.write(srcds_location)
        messagebox.showinfo("Saved", f"SRCDS location saved to {SRCDS_FILE_PATH}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save SRCDS location: {e}")

def modify_file(file_type):
    global SERVER_CFG_PATH, MOTD_TXT_PATH

    file_location = filedialog.askopenfilename(title=f"Select {file_type} file", filetypes=[(f"{file_type} files", f"*.{file_type}")])

    if not file_location:
        return

    if file_type == "cfg":
        SERVER_CFG_PATH = file_location
    elif file_type == "txt":
        MOTD_TXT_PATH = file_location

    open_text_editor(file_type, file_location)

def open_text_editor(file_type, file_location):
    try:
        subprocess.run(["notepad" if os.name == 'nt' else "open", file_location])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open text editor: {e}")


def modify_server_cfg(srcds_location):
    try:
        server_cfg_path = os.path.join(srcds_location, 'jbmod', 'cfg', 'server.cfg')
        if not os.path.exists(server_cfg_path):
            messagebox.showerror("Error", "server.cfg file not found.")
            return

        open_text_editor("cfg", server_cfg_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to modify server.cfg: {e}")

def modify_motd_txt(srcds_location):
    try:
        motd_txt_path = os.path.join(srcds_location, 'jbmod', 'cfg', 'motd.txt')
        if not os.path.exists(motd_txt_path):
            messagebox.showerror("Error", "motd.txt file not found.")
            return

        open_text_editor("txt", motd_txt_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to modify motd.txt: {e}")

API_KEY_PATH = os.path.join(os.path.expanduser("~"), 'apikey.txt')

def get_api_key():
    if os.path.exists(API_KEY_PATH) and os.path.getsize(API_KEY_PATH) > 0:
        with open(API_KEY_PATH, 'r') as f:
            return f.read().strip()
    else:
        return None

def prompt_api_key():
    root = tk.Tk()
    root.withdraw()

    api_key_window = tk.Toplevel(root)
    api_key_window.title("Enter API Key")

    label = tk.Label(api_key_window, text="Enter your API key:")
    label.pack(padx=10, pady=5)

    api_key_entry = tk.Entry(api_key_window)
    api_key_entry.pack(padx=10, pady=5)

    def submit_api_key():
        api_key = api_key_entry.get().strip()
        if api_key:
            with open(API_KEY_PATH, 'w') as f:
                f.write(api_key)
            api_key_window.destroy()
    submit_button = tk.Button(api_key_window, text="Submit", command=submit_api_key)
    submit_button.pack(padx=10, pady=5)

    api_key_window.focus_set()
    api_key_window.grab_set()
    api_key_window.wait_window()

def fetch_active_servers():
    api_key = get_api_key()
    if not api_key:
        if messagebox.askyesno("API Key", "Do you want to add an API key?"):
            prompt_api_key()
        api_key = get_api_key()

    if api_key:
        try:
            url = "https://api.steampowered.com/IGameServersService/GetServerList/v1/"
            params = {
                "key": api_key,
                "filter": "appid\\2158860"
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()["response"]["servers"]
        except Exception as e:
            print(f"Failed to fetch active servers: {e}")
            return []
    else:
        print("No API key provided.")
        return []


def fetch_and_display_jbmod_servers():
    active_servers = fetch_active_servers()
    if active_servers:
        server_window = tk.Toplevel()
        server_window.title("Active JBMod Servers")
        server_window.geometry("600x400")

        server_list_frame = tk.Frame(server_window)
        server_list_frame.pack(fill=tk.BOTH, expand=True)

        server_list_label = tk.Label(server_list_frame, text="Active JBMod Servers")
        server_list_label.pack(pady=10)

        server_listbox = tk.Listbox(server_list_frame, font=("Arial", 12), height=10)
        server_listbox.pack(expand=True, fill="both", padx=10, pady=10)

        for server in active_servers:
            server_info = f"Name: {server['name']} | Address: {server['addr']} | Map: {server['map']} | Players: {server['players']}/{server['max_players']}"
            server_listbox.insert(tk.END, server_info)
        
        def refresh_servers():
            server_listbox.delete(0, tk.END)
            new_active_servers = fetch_active_servers()
            if new_active_servers:
                for server in new_active_servers:
                    server_info = f"Name: {server['name']} | Address: {server['addr']} | Map: {server['map']} | Players: {server['players']}/{server['max_players']}"
                    server_listbox.insert(tk.END, server_info)
            else:
                messagebox.showinfo("No Servers", "No active JBMod servers found.")

        refresh_button = tk.Button(server_list_frame, text="Refresh", command=refresh_servers)
        refresh_button.pack(side=tk.BOTTOM, padx=10, pady=10)
    else:
        messagebox.showinfo("No Servers", "No active JBMod servers found.")

def main():
    app = tk.Tk()
    app.title("JBServer Manager")
    app.geometry("500x400")
    active_servers = fetch_active_servers()

    icon = load_icon(ICON_URL)
    if icon:
        app.iconphoto(True, icon)

    frame = tk.Frame(app, padx=10, pady=10)
    frame.pack(expand=True, fill="both")

    destination_label = tk.Label(frame, text="SRCDS Location:")
    destination_label.grid(row=0, column=0, pady=10, sticky="e")

    destination_entry = tk.Entry(frame, font=("Arial", 12))
    destination_entry.grid(row=0, column=1, columnspan=2, pady=10, padx=10, sticky="ew")

    if os.path.exists(SRCDS_FILE_PATH):
        with open(SRCDS_FILE_PATH, 'r') as file:
            default_srcds_location = file.read()
            destination_entry.insert(tk.END, default_srcds_location)

    destination_browse_button = tk.Button(frame, text="Browse", command=lambda: browse_destination(destination_entry))
    destination_browse_button.grid(row=0, column=3, pady=10, padx=5)

    search_entry = tk.Entry(frame, font=("Arial", 12))
    search_entry.grid(row=1, column=0, columnspan=3, pady=10, padx=10, sticky="ew")

    files_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, font=("Arial", 12), height=10)
    files_listbox.grid(row=2, column=0, columnspan=4, pady=10, padx=10, sticky="nsew")

    refresh_button = tk.Button(frame, text="Refresh List", command=lambda: update_listbox(files_listbox, fetch_files()))
    refresh_button.grid(row=3, column=0, pady=5)

    download_button = tk.Button(frame, text="Download Selected File", command=lambda: on_download_button_click(files_listbox, destination_entry))
    download_button.grid(row=3, column=1, pady=5)

    save_button = tk.Button(frame, text="Save SRCDS Location", command=lambda: save_srcds_location(destination_entry.get()))
    save_button.grid(row=3, column=2, pady=5)

    search_button = tk.Button(frame, text="Search", command=lambda: on_search(search_entry, files_listbox, fetch_files()))
    search_button.grid(row=1, column=3, pady=10, padx=10)

    frame.rowconfigure(2, weight=1)
    frame.columnconfigure(0, weight=1)
    
    download_all_button = tk.Button(frame, text="Download All Files", command=lambda: on_download_button_click(files_listbox, destination_entry, download_all=True))
    download_all_button.grid(row=3, column=3, pady=5)
    
    download_jbmod_button = tk.Button(frame, text="Download JBMod", command=lambda: on_download_jbmod_button_click(destination_entry))
    download_jbmod_button.grid(row=4, column=0, columnspan=4, pady=10)
    
    sourcemod_button = tk.Button(frame, text="Download Sourcemod", command=lambda: on_sourcemod_button_click(destination_entry))
    sourcemod_button.grid(row=4, column=2, columnspan=4, pady=5)
    
    launch_button = tk.Button(frame, text="Launch Server", command=lambda: on_launch_button_click(destination_entry))
    launch_button.grid(row=5, column=3, pady=10)
    
    modify_window = tk.Toplevel()
    modify_window.title("Modify Files")
    modify_window.geometry("300x100")

    modify_motd_button = tk.Button(modify_window, text="Modify motd.txt", command=lambda: modify_motd_txt(destination_entry.get()))
    modify_motd_button.pack(pady=10)

    modify_server_cfg_button = tk.Button(modify_window, text="Modify server.cfg", command=lambda: modify_server_cfg(destination_entry.get()))
    modify_server_cfg_button.pack(pady=10)
    
    show_plugins_button = tk.Button(frame, text="Show Installed Plugins", command=lambda: show_plugin_list(destination_entry.get()))
    show_plugins_button.grid(row=5, column=0, columnspan=4, pady=10)
    
    fetch_servers_button = tk.Button(frame, text="Fetch JBMod Servers", command=fetch_and_display_jbmod_servers)
    fetch_servers_button.grid(row=5, column=0, columnspan=1, pady=10)


    update_listbox(files_listbox, fetch_files())

    app.mainloop()

if __name__ == "__main__":
    main()
