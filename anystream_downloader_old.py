import os
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk  # Ensure you have run: pip install pillow

# --- Functional Logic ---

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_folder_var.set(folder)

def download_video():
    url = url_entry.get().strip()
    output_folder = output_folder_var.get().strip()

    if not url:
        messagebox.showerror("Error", "Please enter a video URL.")
        return

    if not output_folder:
        messagebox.showerror("Error", "Please choose a download folder.")
        return

    ydl_opts = {
        "format": "bestaudio/best" if mp3_only_var.get() else "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
        "writethumbnail": True,
        "embedthumbnail": True,
        "postprocessors": [
            {"key": "FFmpegMetadata", "add_metadata": True},
            {"key": "EmbedThumbnail", "already_have_thumbnail": False},
        ],
    }

    if mp3_only_var.get():
        ydl_opts["postprocessors"].insert(0, {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        status_label.config(text="Download complete!", foreground="#7de8a1")
    except Exception as e:
        status_label.config(text=f"Download failed: {e}", foreground="#ff6b6b")

def toggle_mp3():
    mp3_only_var.set(not mp3_only_var.get())
    if mp3_only_var.get():
        toggle_canvas.itemconfig(toggle_circle, fill="#7de8a1")
        toggle_canvas.coords(toggle_circle, 34, 6, 58, 30)
        toggle_canvas.itemconfig(toggle_track_middle, fill="#3b8bff")
    else:
        toggle_canvas.itemconfig(toggle_circle, fill="#ffffff")
        toggle_canvas.coords(toggle_circle, 6, 6, 30, 30)
        toggle_canvas.itemconfig(toggle_track_middle, fill="#374c79")

# --- GUI Setup ---

root = tk.Tk()
root.title("AnyStream Downloader")
root.geometry("800x600")
root.configure(bg="#071326")

# Scalability & Constraints
root.resizable(True, True)
root.minsize(800, 600)
TARGET_RATIO = 800 / 600 

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_gradient_image(width, height, start_color, end_color, radius=18, background="#0f1d3f"):
    if width <= 0 or height <= 0:
        raise ValueError("Gradient size must be positive")
    image = tk.PhotoImage(width=width, height=height)
    ...
    """Generates original high-quality button gradients"""
    image = tk.PhotoImage(width=width, height=height)
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)
    for y in range(height):
        for x in range(width):
            ratio = x / max(width - 1, 1)
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
            image.put(f"#{r:02x}{g:02x}{b:02x}", to=(x, y))
    return image

# Asset Paths (Using the names verbatim)
bg_path = os.path.join(os.path.dirname(__file__), "AnyStream Background.png")
logo_path = os.path.join(os.path.dirname(__file__), "AnyStream Logo.png")

# Set the Window/App Icon
if os.path.exists(logo_path):
    try:
        icon_img = Image.open(logo_path)
        icon_photo = ImageTk.PhotoImage(icon_img)
        root.iconphoto(False, icon_photo)
    except: pass

bg_canvas = tk.Canvas(root, highlightthickness=0, bd=0)
bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

def handle_resize(event):
    if event.widget == root:
        new_w, new_h = event.width, event.height
        
        # Enforce Aspect Ratio Snap
        if (new_w / new_h) > TARGET_RATIO:
            fw, fh = int(new_h * TARGET_RATIO), new_h
        else:
            fw, fh = new_w, int(new_w / TARGET_RATIO)
        
        if abs(new_w - fw) > 2 or abs(new_h - fh) > 2:
            root.geometry(f"{fw}x{fh}")

        try:
            if os.path.exists(bg_path):
                with Image.open(bg_path) as img:
                    resized = img.resize((fw, fh), Image.Resampling.LANCZOS)
                    root.bg_img = ImageTk.PhotoImage(resized)
                    bg_canvas.delete("bg_img")
                    bg_canvas.create_image(0, 0, image=root.bg_img, anchor="nw", tags="bg_img")
                    bg_canvas.lower("bg_img")
        except: pass

root.bind("<Configure>", handle_resize)

# --- Styling ---

style = ttk.Style(root)
style.theme_use("clam")
style.configure("Logo.TLabel", background="#071326", foreground="#ffffff", font=("Segoe UI", 28, "bold"))
style.configure("Subtitle.TLabel", background="#071326", foreground="#7fa7ff", font=("Segoe UI", 14))
style.configure("Label.TLabel", background="#071326", foreground="#d8e2ff", font=("Segoe UI", 11))
style.configure("Card.TEntry", fieldbackground="#15254f", foreground="#f0f4ff")

# Content Card
card = tk.Frame(root, bg="#071326", padx=30, pady=30)
card.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Logo Display
if os.path.exists(logo_path):
    try:
        l_img = Image.open(logo_path)
        l_img.thumbnail((120, 120))
        root.logo_photo = ImageTk.PhotoImage(l_img)
        tk.Label(card, image=root.logo_photo, bg="#071326").pack(pady=(0, 10))
    except: pass

ttk.Label(card, text="AnyStream", style="Logo.TLabel").pack()
ttk.Label(card, text="Downloader", style="Subtitle.TLabel").pack(pady=(0, 20))

# Form
form_frame = tk.Frame(card, bg="#071326")
form_frame.pack()

ttk.Label(form_frame, text="Video URL:", style="Label.TLabel").grid(row=0, column=0, sticky="w")
url_entry = ttk.Entry(form_frame, style="Card.TEntry", width=60)
url_entry.grid(row=1, column=0, columnspan=2, pady=(5, 15))

ttk.Label(form_frame, text="Download Folder:", style="Label.TLabel").grid(row=2, column=0, sticky="w")
output_folder_var = tk.StringVar()
folder_entry = ttk.Entry(form_frame, textvariable=output_folder_var, style="Card.TEntry", width=45)
folder_entry.grid(row=3, column=0, sticky="ew")

# Browse Button (Gradient)
browse_grad = create_gradient_image(100, 35, "#30d4ff", "#8f5bff")
btn_br = tk.Canvas(form_frame, width=100, height=35, bg="#071326", highlightthickness=0, cursor="hand2")
btn_br.create_image(0, 0, image=browse_grad, anchor="nw")
btn_br.create_text(50, 17, text="Browse", fill="white", font=("Segoe UI", 10, "bold"))
btn_br.bind("<Button-1>", lambda e: choose_folder())
btn_br.grid(row=3, column=1, padx=(12, 0))

# MP3 Toggle
mp3_only_var = tk.BooleanVar(value=False)
toggle_f = tk.Frame(card, bg="#071326")
toggle_f.pack(anchor="w", pady=20)
toggle_canvas = tk.Canvas(toggle_f, width=64, height=34, bg="#071326", highlightthickness=0)
toggle_canvas.pack(side="left")
toggle_track_middle = toggle_canvas.create_rectangle(4, 4, 60, 30, fill="#374c79", outline="")
toggle_circle = toggle_canvas.create_oval(6, 6, 30, 30, fill="#ffffff", outline="")
toggle_canvas.bind("<Button-1>", lambda e: toggle_mp3())
ttk.Label(toggle_f, text="Download audio only (MP3)", style="Label.TLabel").pack(side="left", padx=10)

status_label = ttk.Label(card, text="", style="Label.TLabel")
status_label.pack(pady=10)

# Download Button (Gradient)
dl_grad = create_gradient_image(260, 50, "#28d7ff", "#7b4cff")
btn_dl = tk.Canvas(card, width=260, height=50, bg="#071326", highlightthickness=0, cursor="hand2")
btn_dl.create_image(0, 0, image=dl_grad, anchor="nw")
btn_dl.create_text(130, 25, text="Download Video", fill="white", font=("Segoe UI", 14, "bold"))
btn_dl.bind("<Button-1>", lambda e: download_video())
btn_dl.pack()

root.mainloop()