import tkinter as tk
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk
from ffpyplayer.player import MediaPlayer  

dir_path = Path("C:/Users/PutYourUSerHere/Downloads/File_Searcher-main/File_Searcher-main/Documents/File_Searcher/General_jihad_stuff")


video_player_instance = None
video_loop_id = None
current_playing_file = None

def update(event):
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
        
    search_term = search_entry.get().lower()
    items_to_show = data_source if not search_term else [item for item in data_source if search_term in item.lower()]
    
    for item in items_to_show:
        item_label = tk.Label(
            scrollable_frame, text=item, font=("Arial", 12), anchor="w", 
            bg="white", fg="black", padx=10, pady=5, cursor="hand2"
        )
        item_label.pack(fill="x", padx=5, pady=2)
        item_label.bind("<Button-1>", lambda e, text=item: select_item(text))
        
    canvas.configure(scrollregion=canvas.bbox("all"))

def stop_media():

    global video_player_instance, video_loop_id, current_playing_file
    if video_loop_id is not None:
        root.after_cancel(video_loop_id)
        video_loop_id = None
    if video_player_instance is not None:
        video_player_instance.close_player()
        video_player_instance = None
    current_playing_file = None

def select_item(text):
    search_entry.delete(0, tk.END)
    search_entry.insert(0, text)
    
    file_path = dir_path / text
    ext = file_path.suffix.lower()
    
    stop_media()
    
    valid_images = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.HEIC'}
    valid_videos = {'.mov', '.mp4', '.avi', '.mkv'}
    
    if ext in valid_images:
        show_image_preview(file_path)
    elif ext in valid_videos:
        show_video_preview(file_path)
    else:
        preview_label.config(image="", text="Unsupported file preview format.")

def show_image_preview(file_path):

    try:
        img = Image.open(file_path)
        img.thumbnail((350, 350))
        tk_img = ImageTk.PhotoImage(img)
        preview_label.config(image=tk_img, text="")
        preview_label.image = tk_img
    except Exception as e:
        preview_label.config(image="", text=f"Error loading image:\n{e}")

def show_video_preview(file_path):

    global video_player_instance, current_playing_file
    try:
        current_playing_file = file_path

        video_player_instance = MediaPlayer(str(file_path), ff_opts={'pix_fmt': 'rgb24'})
        stream_video_with_audio()
    except Exception as e:
        preview_label.config(image="", text=f"Error playing video:\n{e}")

def stream_video_with_audio():
    """Decodes sequential audiovisual packets and keeps them perfectly synchronized."""
    global video_player_instance, video_loop_id, current_playing_file
    if video_player_instance is None:
        return


    frame, val = video_player_instance.get_frame()
    
    if val == 'eof':

        loop_target = current_playing_file
        stop_media()
        if loop_target:
            show_video_preview(loop_target)
        return
        
    if val == 'paused' or frame is None:

        video_loop_id = root.after(5, stream_video_with_audio)
        return


    img_data, pts = frame
    size = img_data.get_size()
    
    try:

        raw_planes = img_data.to_bytearray()
        if isinstance(raw_planes, list):
            raw_bytes = b"".join(raw_planes)
        else:
            raw_bytes = raw_planes

        img = Image.frombytes("RGB", size, raw_bytes)
        img.thumbnail((350, 350))
        
        tk_img = ImageTk.PhotoImage(img)
        preview_label.config(image=tk_img, text="")
        preview_label.image = tk_img
    except Exception as e:
        print(f"Frame decoding warning: {e}")
    
    video_loop_id = root.after(10, stream_video_with_audio)

def on_close():
    stop_media()
    root.destroy()

root = tk.Tk()
root.title("File-search")
root.geometry("850x600")
root.protocol("WM_DELETE_WINDOW", on_close)

data_source = [f.name for f in dir_path.iterdir() if f.is_file()]


left_panel = tk.Frame(root)
left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

right_panel = tk.Frame(root, bg="gray95", width=400)
right_panel.pack(side="right", fill="both", expand=False, padx=10, pady=10)
right_panel.pack_propagate(False)


label = tk.Label(left_panel, text="Search Menu:", font=("Arial", 12))
label.pack(pady=5)

search_entry = tk.Entry(left_panel, font=("Arial", 12), width=25)
search_entry.pack(pady=5)
search_entry.bind("<KeyRelease>", update)

container = tk.Frame(left_panel)
container.pack(fill="both", expand=True, padx=10, pady=10)

canvas = tk.Canvas(container, highlightthickness=0)
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


preview_title = tk.Label(right_panel, text="File Preview", font=("Arial", 12, "bold"), bg="gray95")
preview_title.pack(pady=10)

preview_label = tk.Label(right_panel, text="Click a file\nto see preview", font=("Arial", 11), bg="gray95", fg="gray50")
preview_label.pack(fill="both", expand=True, padx=10, pady=10)


update(None)

root.mainloop()
