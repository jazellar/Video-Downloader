import os
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk


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

    if mp3_only_var.get():
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
            "writethumbnail": True,
            "embedthumbnail": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
                {
                    "key": "FFmpegMetadata",
                    "add_metadata": True,
                },
                {
                    "key": "EmbedThumbnail",
                    "already_have_thumbnail": False,
                },
            ],
        }
    else:
        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
            "writethumbnail": True,
            "embedthumbnail": True,
            "postprocessors": [
                {
                    "key": "FFmpegMetadata",
                    "add_metadata": True,
                },
                {
                    "key": "EmbedThumbnail",
                    "already_have_thumbnail": False,
                },
            ],
        }

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
        toggle_canvas.itemconfig(toggle_track_left, fill="#3b8bff")
        toggle_canvas.itemconfig(toggle_track_right, fill="#3b8bff")
        toggle_canvas.itemconfig(toggle_track_middle, fill="#3b8bff")
    else:
        toggle_canvas.itemconfig(toggle_circle, fill="#ffffff")
        toggle_canvas.coords(toggle_circle, 6, 6, 30, 30)
        toggle_canvas.itemconfig(toggle_track_left, fill="#374c79")
        toggle_canvas.itemconfig(toggle_track_right, fill="#374c79")
        toggle_canvas.itemconfig(toggle_track_middle, fill="#374c79")


# GUI Setup
root = tk.Tk()
root.title("AnyStream Downloader")
root.geometry("800x600")
root.configure(bg="#071326")

# 1. Enable scalability and set constraints
root.resizable(True, True) 
root.minsize(800, 600) # Prevents the UI from breaking when scaled down

# 2. Load the AnyStream Background.png image
bg_path = os.path.join(os.path.dirname(__file__), "AnyStream Background.png")
try:
    original_bg = Image.open(bg_path)
except Exception as e:
    print(f"Error loading background: {e}")
    original_bg = None

# Canvas for the background image
bg_canvas = tk.Canvas(root, highlightthickness=0, bd=0)
bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

def resize_bg(event):
    if original_bg:
        # Scale the image to the new window size[cite: 1]
        resized = original_bg.resize((event.width, event.height), Image.Resampling.LANCZOS)
        root.bg_img = ImageTk.PhotoImage(resized)
        bg_canvas.delete("bg_img")
        bg_canvas.create_image(0, 0, image=root.bg_img, anchor="nw", tags="bg_img")
        bg_canvas.lower("bg_img")

root.bind("<Configure>", resize_bg)

# 3. Use 'place' for the main card to keep it centered during scaling
card = tk.Frame(root, bg="#071326", padx=30, pady=30)
card.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

logo_image = None
logo_display_image = None
logo_candidates = [
    "AnyStream Logo.png",
    #"logo.png",
    #"AnyStreamLogo.png",
    #"app_icon.png",
]
logo_path = None
for candidate in logo_candidates:
    candidate_path = os.path.join(os.path.dirname(__file__), candidate)
    if os.path.exists(candidate_path):
        logo_path = candidate_path
        break

if logo_path is not None:
    try:
        logo_image = tk.PhotoImage(file=logo_path)
        if logo_image.width() > 128 or logo_image.height() > 128:
            subsample_x = max(1, logo_image.width() // 128)
            subsample_y = max(1, logo_image.height() // 128)
            logo_display_image = logo_image.subsample(subsample_x, subsample_y)
        else:
            logo_display_image = logo_image
        root.iconphoto(False, logo_display_image)
    except Exception:
        logo_image = None
        logo_display_image = None

style = ttk.Style(root)
style.theme_use("clam")
style.configure("Card.TFrame", background="#071326", borderwidth=0)
style.configure("Logo.TLabel", background="#071326", foreground="#ffffff", font=("Segoe UI", 28, "bold"))
style.configure("Card.TLabel", background="#071326", borderwidth=0, relief="flat")
style.configure("Subtitle.TLabel", background="#071326", foreground="#7fa7ff", font=("Segoe UI", 14))
style.configure("Label.TLabel", background="#071326", foreground="#d8e2ff", font=("Segoe UI", 11))
style.configure("Card.TEntry", fieldbackground="#15254f", foreground="#f0f4ff", background="#15254f", bordercolor="#3266ff")
style.configure("Card.TButton", background="#3b8bff", foreground="#ffffff", font=("Segoe UI", 12, "bold"), borderwidth=0)
style.map("Card.TButton", background=[("active", "#5a9cff")])


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_gradient_image(width, height, start_color, end_color, radius=18, background="#0f1d3f"):
    image = tk.PhotoImage(width=width, height=height)
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)
    bg_rgb = hex_to_rgb(background)
    for y in range(height):
        y_ratio = y / max(height - 1, 1)
        if y < height * 0.18:
            vertical_brightness = 1.12 - (y / max(height * 0.18, 1)) * 0.12
        elif y > height * 0.82:
            vertical_brightness = 0.92 + (1 - (y - height * 0.82) / max(height * 0.18, 1)) * 0.08
        else:
            vertical_brightness = 1.0
        for x in range(width):
            left = x < radius
            right = x >= width - radius
            top = y < radius
            bottom = y >= height - radius
            inside = True
            if (left and top) or (right and top) or (left and bottom) or (right and bottom):
                cx = radius - x if left else x - (width - radius - 1)
                cy = radius - y if top else y - (height - radius - 1)
                if cx * cx + cy * cy > radius * radius:
                    inside = False
            if not inside:
                color = f"#{bg_rgb[0]:02x}{bg_rgb[1]:02x}{bg_rgb[2]:02x}"
            else:
                ratio = x / max(width - 1, 1)
                r = int((start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio) * vertical_brightness)
                g = int((start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio) * vertical_brightness)
                b = int((start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio) * vertical_brightness)
                r = min(255, max(0, r))
                g = min(255, max(0, g))
                b = min(255, max(0, b))
                color = f"#{r:02x}{g:02x}{b:02x}"
            image.put(color, to=(x, y))
    return image


bg_canvas = tk.Canvas(root, highlightthickness=0, bd=0)
bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)


def draw_background(event=None):
    width = root.winfo_width()
    height = root.winfo_height()
    bg_canvas.delete("bg")
    for i in range(height):
        ratio = i / max(height - 1, 1)
        r = int(7 + (17 - 7) * ratio)
        g = int(19 + (34 - 19) * ratio)
        b = int(38 + (66 - 38) * ratio)
        bg_canvas.create_line(0, i, width, i, fill=f"#{r:02x}{g:02x}{b:02x}", tags="bg")
    bg_canvas.create_oval(width * 0.05, -height * 0.3, width * 0.9, height * 0.7,
                          fill="#13346c", outline="", tags="bg")
    bg_canvas.create_oval(width * 0.25, -height * 0.15, width * 0.95, height * 0.65,
                          fill="#0b2148", outline="", tags="bg")
    bg_canvas.lower("bg")


root.bind("<Configure>", draw_background)


browse_button_image = create_gradient_image(130, 40, "#30d4ff", "#8f5bff", radius=16, background="#071326")
download_button_image = create_gradient_image(260, 60, "#28d7ff", "#7b4cff", radius=20, background="#071326")


def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

card_border_canvas = tk.Canvas(root, width=780, height=520, bg=root["bg"], highlightthickness=0, bd=0)
card_border_canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Rounded glow border behind the card
corner = 28
card_border_canvas.create_oval(4, 4, 160, 160, fill="#112a55", outline="", tags="glow")
card_border_canvas.create_oval(580, 12, 760, 210, fill="#0c2350", outline="", tags="glow")
card_border_canvas.create_oval(44, 320, 200, 520, fill="#092040", outline="", tags="glow")

# The rounded card background is intentionally omitted so the window background shows through.
card = tk.Frame(card_border_canvas, bg=root["bg"], highlightthickness=0, bd=0)
card_border_canvas.create_window(390, 260, window=card)

header_frame = tk.Frame(card, bg=root["bg"], highlightthickness=0, bd=0)
header_frame.config(height=200)
header_frame.pack(fill=tk.X, pady=(0, 32), padx=28)

if logo_display_image:
    logo_width = logo_display_image.width()
    logo_height = logo_display_image.height()
    logo_holder = tk.Canvas(header_frame,
                             width=logo_width + 8,
                             height=logo_height + 8,
                             bg=root["bg"],
                             highlightthickness=0,
                             bd=0)
    logo_holder.create_image(4, 4, image=logo_display_image, anchor="nw")
    logo_holder.image = logo_display_image
    logo_holder.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

logo_label = ttk.Label(header_frame, text="AnyStream", style="Logo.TLabel")
logo_label.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

subtitle_label = ttk.Label(header_frame, text="Downloader", style="Subtitle.TLabel")
subtitle_label.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

form_frame = tk.Frame(card, bg=root["bg"], highlightthickness=0, bd=0)
form_frame.pack(fill=tk.BOTH, expand=True, padx=28, pady=(0, 28))

url_label = ttk.Label(form_frame, text="Video URL:", style="Label.TLabel")
url_label.grid(row=0, column=0, sticky="w", pady=(0, 8))
url_entry = ttk.Entry(form_frame, style="Card.TEntry", width=60)
url_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 18))

folder_label = ttk.Label(form_frame, text="Download Folder:", style="Label.TLabel")
folder_label.grid(row=2, column=0, sticky="w", pady=(0, 8))

output_folder_var = tk.StringVar()
folder_entry = ttk.Entry(form_frame, textvariable=output_folder_var, style="Card.TEntry", width=46)
folder_entry.grid(row=3, column=0, sticky="ew")

browse_button_canvas = tk.Canvas(form_frame, width=130, height=40, bg="#071326", highlightthickness=0, bd=0, cursor="hand2")
browse_button_canvas.create_image(0, 0, image=browse_button_image, anchor="nw")
browse_button_canvas.create_text(65, 20, text="Browse", fill="#ffffff", font=("Segoe UI", 10, "bold"))
browse_button_canvas.image = browse_button_image
browse_button_canvas.bind("<Button-1>", lambda e: choose_folder())
browse_button_canvas.grid(row=3, column=1, sticky="e", padx=(12, 0))

mp3_only_var = tk.BooleanVar(value=False)

toggle_frame = tk.Frame(form_frame, bg=root["bg"], highlightthickness=0, bd=0)
toggle_frame.grid(row=4, column=0, columnspan=2, sticky="w", pady=(20, 0))

toggle_canvas = tk.Canvas(toggle_frame, width=64, height=34, bg="#071326", highlightthickness=0, bd=0)
toggle_canvas.pack(side=tk.LEFT)

toggle_track_left = toggle_canvas.create_oval(4, 4, 34, 30, fill="#374c79", outline="")
toggle_track_right = toggle_canvas.create_oval(30, 4, 60, 30, fill="#374c79", outline="")
toggle_track_middle = toggle_canvas.create_rectangle(17, 4, 47, 30, fill="#374c79", outline="")
toggle_circle = toggle_canvas.create_oval(6, 6, 30, 30, fill="#ffffff", outline="")

toggle_text_label = ttk.Label(toggle_frame, text="Download audio only (MP3)", style="Label.TLabel")
toggle_text_label.pack(side=tk.LEFT)

toggle_canvas.bind("<Button-1>", lambda e: toggle_mp3())
toggle_text_label.bind("<Button-1>", lambda e: toggle_mp3())

status_label = ttk.Label(form_frame, text="", style="Label.TLabel")
status_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=(18, 0))

download_button_canvas = tk.Canvas(form_frame, width=260, height=60, bg="#071326", highlightthickness=0, bd=0, cursor="hand2")
download_button_canvas.create_image(0, 0, image=download_button_image, anchor="nw")
download_button_canvas.create_text(130, 30, text="Download Video", fill="#ffffff", font=("Segoe UI", 15, "bold"))
download_button_canvas.image = download_button_image
download_button_canvas.bind("<Button-1>", lambda e: download_video())
download_button_canvas.grid(row=6, column=0, columnspan=2, pady=(5, 0))

form_frame.columnconfigure(0, weight=1)
form_frame.columnconfigure(1, weight=0)

root.mainloop()
