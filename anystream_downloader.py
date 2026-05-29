import os
import shutil
import yt_dlp
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageOps


def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_folder_var.set(folder)


def download_video():
    # Clear any previous status when a new download is requested
    status_label.config(text="")

    url = url_entry.get().strip()
    output_folder = output_folder_var.get().strip()

    if not url:
        messagebox.showerror("Error", "Please enter a video URL.")
        return

    if not output_folder:
        messagebox.showerror("Error", "Please choose a download folder.")
        return

    # Determine ffmpeg availability: check PATH first, then a common install location
    default_ffmpeg = r"C:\ffmpeg\bin"
    ffmpeg_dir = default_ffmpeg if os.path.isdir(default_ffmpeg) else ""
    ffmpeg_found = bool(shutil.which("ffmpeg") or shutil.which("ffmpeg.exe"))
    if not ffmpeg_found and ffmpeg_dir:
        if os.path.exists(os.path.join(ffmpeg_dir, "ffmpeg.exe")) or os.path.exists(os.path.join(ffmpeg_dir, "ffmpeg")):
            ffmpeg_found = True

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

    # If merging multiple formats or doing FFmpeg postprocessing, ensure ffmpeg exists
    needs_ffmpeg = mp3_only_var.get() or ("+" in ydl_opts.get("format", ""))
    if needs_ffmpeg and not ffmpeg_found:
        messagebox.showerror("FFmpeg required",
                             "FFmpeg/ffprobe not found. Install FFmpeg and ensure it's on PATH (or install to C:\\ffmpeg\\bin).")
        return

    # If a local ffmpeg installation exists in the common folder, pass it to yt-dlp
    if ffmpeg_found and ffmpeg_dir:
        ydl_opts["ffmpeg_location"] = ffmpeg_dir

    # Prevent concurrent downloads
    if getattr(download_video, "running", False):
        messagebox.showinfo("Download in progress", "A download is already running. Please wait.")
        return

    progress_var.set(0)
    progress_text.config(text="Starting...")

    def download_task():
        download_video.running = True

        def progress_hook(d):
            status = d.get("status")
            if status == "downloading":
                downloaded = d.get("downloaded_bytes") or 0
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                if total:
                    percent = downloaded / total * 100
                    root.after(0, lambda: progress_var.set(percent))
                    root.after(0, lambda: progress_text.config(text=f"{percent:.1f}%"))
                else:
                    root.after(0, lambda: progress_text.config(text="Downloading..."))
            elif status == "finished":
                root.after(0, lambda: progress_var.set(100))
                root.after(0, lambda: progress_text.config(text="Processing..."))

        local_opts = dict(ydl_opts)
        local_opts["progress_hooks"] = [progress_hook]

        try:
            with yt_dlp.YoutubeDL(local_opts) as ydl:
                ydl.download([url])
            root.after(0, lambda: status_label.config(text="Download complete!", foreground="#7de8a1"))
        except Exception as e:
            root.after(0, lambda: status_label.config(text=f"Download failed: {e}", foreground="#ff6b6b"))
        finally:
            root.after(0, lambda: progress_text.config(text=""))
            download_video.running = False

    threading.Thread(target=download_task, daemon=True).start()


def toggle_mp3():
    mp3_only_var.set(not mp3_only_var.get())
    if mp3_only_var.get():
        toggle_canvas.itemconfig(toggle_circle, fill="#7de8a1")
        # move knob to right for 80x44 canvas
        toggle_canvas.coords(toggle_circle, 46, 8, 72, 36)
        toggle_canvas.itemconfig(toggle_track_left, fill="#3b8bff")
        toggle_canvas.itemconfig(toggle_track_right, fill="#3b8bff")
        toggle_canvas.itemconfig(toggle_track_middle, fill="#3b8bff")
    else:
        toggle_canvas.itemconfig(toggle_circle, fill="#ffffff")
        # move knob back to left
        toggle_canvas.coords(toggle_circle, 8, 8, 34, 36)
        toggle_canvas.itemconfig(toggle_track_left, fill="#374c79")
        toggle_canvas.itemconfig(toggle_track_right, fill="#374c79")
        toggle_canvas.itemconfig(toggle_track_middle, fill="#374c79")


# GUI Setup
root = tk.Tk()
root.title("AnyStream Downloader")
root.geometry("900x950")
root.configure(bg="#071326")

# 1. Enable scalability and set constraints
root.resizable(True, True)
root.minsize(840, 640) # Prevents the UI from breaking when scaled down

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
    if event.widget is root and original_bg and event.width > 10 and event.height > 10:
        bg_canvas.place(x=0, y=0, width=event.width, height=event.height)
        bg = ImageOps.fit(original_bg, (event.width, event.height),
                           Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        root.bg_img = ImageTk.PhotoImage(bg)
        bg_canvas.delete("bg_img")
        bg_canvas.create_image(0, 0, image=root.bg_img, anchor="nw", tags="bg_img")
        bg_canvas.lower("bg_img")

root.bind("<Configure>", resize_bg)

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
        img = Image.open(logo_path).convert("RGBA")
        desired_logo_size = (50, 50)  # change to whatever (width, height) you want
        img.thumbnail(desired_logo_size, Image.Resampling.LANCZOS)
        logo_display_image = ImageTk.PhotoImage(img)
        root.iconphoto(False, logo_display_image)
    except Exception as e:
        logo_display_image = None

style = ttk.Style(root)
style.theme_use("clam")
style.configure("Card.TFrame", background="#071326", borderwidth=0)
style.configure("Logo.TLabel", background="#071326", foreground="#ffffff", font=("Segoe UI", 34, "bold"))
style.configure("Card.TLabel", background="#071326", borderwidth=0, relief="flat")
style.configure("Subtitle.TLabel", background="#071326", foreground="#7fa7ff", font=("Segoe UI", 16))
style.configure("Label.TLabel", background="#071326", foreground="#d8e2ff", font=("Segoe UI", 12))
style.configure("Card.TEntry", fieldbackground="#15254f", foreground="#f0f4ff", background="#15254f", bordercolor="#3266ff")
style.configure("Card.TButton", background="#3b8bff", foreground="#ffffff", font=("Segoe UI", 12, "bold"), borderwidth=0)
style.map("Card.TButton", background=[("active", "#5a9cff")])
# Progressbar style: empty/trough color match entry field, filled color green
style.configure("Card.Horizontal.TProgressbar", troughcolor="#15254f", background="#7de8a1")
progress_var = tk.DoubleVar(value=0)
style.configure("Header.TLabel", background="#071326", foreground="#ffffff", font=("Segoe UI", 34, "bold"))
style.configure("Subheader.TLabel", background="#071326", foreground="#cfd9f7", font=("Segoe UI", 11))
style.configure("SectionTitle.TLabel", background="#11254e", foreground="#f4f7ff", font=("Segoe UI", 11, "bold"))
style.configure("SectionDesc.TLabel", background="#11254e", foreground="#99b3d6", font=("Segoe UI", 9))
style.configure("Sidebar.TLabel", background="#0b1732", foreground="#8fafff", font=("Segoe UI", 10))
style.configure("SidebarActive.TLabel", background="#0b1732", foreground="#ffffff", font=("Segoe UI", 11, "bold"))
style.configure("SectionIcon.TLabel", background="#11254e", foreground="#7fa7ff", font=("Segoe UI", 12))
style.configure("Dark.Vertical.TScrollbar",
                gripcount=0,
                background="#0f224f",
                troughcolor="#071326",
                bordercolor="#071326",
                arrowcolor="#7fa7ff",
                lightcolor="#071326",
                darkcolor="#071326",
                troughrelief="flat",
                relief="flat")
style.map("Dark.Vertical.TScrollbar",
          background=[("active", "#133a78")],
          arrowcolor=[("active", "#c3ddff")])


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_gradient_image(width, height, start_color, end_color, radius=18, background="#0f1d3f"):
    if width <= 0 or height <= 0:
        raise ValueError("Gradient size must be positive")
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

browse_button_image = create_gradient_image(140, 42, "#3d9cff", "#7668ff", radius=18, background="#11254e")
download_button_image = create_gradient_image(420, 72, "#3dc5ff", "#8a5bff", radius=26, background="#071326")

sidebar_frame = tk.Frame(root, bg="#0b1732", width=280, highlightthickness=0, bd=0)
sidebar_frame.grid(row=0, column=0, sticky="ns")

main_frame = tk.Frame(root, bg="#071326", highlightthickness=0, bd=0)
main_frame.grid(row=0, column=1, sticky="nsew")

root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# Sidebar content
sidebar_logo = tk.Frame(sidebar_frame, bg="#0b1732")
sidebar_logo.pack(fill="x", pady=(24, 20), padx=24)
if logo_display_image:
    logo_side = tk.Canvas(sidebar_logo, width=38, height=38, bg="#0b1732", highlightthickness=0, bd=0)
    logo_side.create_image(4, 4, image=logo_display_image, anchor="nw")
    logo_side.image = logo_display_image
    logo_side.pack(side="left", padx=(0, 8))
logo_name = ttk.Label(sidebar_logo, text="AnyStream\nDownloader", style="Sidebar.TLabel", justify="left")
logo_name.pack(side="left")

nav_frame = tk.Frame(sidebar_frame, bg="#0b1732")
nav_frame.pack(fill="x", pady=(10, 30), padx=16)
for text, active in [("Downloader", True), ("History", False), ("Settings", False)]:
    item_bg = "#10214a" if active else "#0b1732"
    item = tk.Frame(nav_frame, bg=item_bg, pady=12, padx=16)
    item.pack(fill="x", pady=8)
    label_style = "SidebarActive.TLabel" if active else "Sidebar.TLabel"
    ttk.Label(item, text=text, style=label_style).pack(side="left")

bottom_frame = tk.Frame(sidebar_frame, bg="#0b1732")
bottom_frame.pack(side="bottom", fill="x", pady=24, padx=24)
theme_label = ttk.Label(bottom_frame, text="Theme", style="Sidebar.TLabel")
theme_label.pack(anchor="w", pady=(0, 12))
theme_select = ttk.Label(bottom_frame, text="▾ System Default", style="Sidebar.TLabel")
theme_select.pack(fill="x", pady=(0, 20), ipady=8, padx=2)
status_box = tk.Frame(bottom_frame, bg="#10214a", padx=12, pady=12)
status_box.pack(fill="x")
status_header = ttk.Label(status_box, text="Ready", style="SidebarActive.TLabel")
status_header.pack(anchor="w")
status_line = ttk.Label(status_box, text="All systems operational", style="Sidebar.TLabel")
status_line.pack(anchor="w", pady=(4, 0))

# Main content card
content_card = tk.Frame(main_frame, bg="#0f2142", highlightthickness=1, highlightbackground="#233963")
content_card.pack(fill="both", expand=True, padx=24, pady=24)

header_area = tk.Frame(content_card, bg=content_card["bg"])
header_area.pack(fill="x", padx=28, pady=(30, 16))
header_title = ttk.Label(header_area, text="Downloader", style="Header.TLabel")
header_title.pack(anchor="w")
header_subtitle = ttk.Label(header_area, text="Download videos from your favorite sites quickly and easily.", style="Subheader.TLabel")
header_subtitle.pack(anchor="w", pady=(12, 0))

scroll_frame = tk.Frame(content_card, bg=content_card["bg"])
scroll_frame.pack(fill="both", expand=True, padx=28, pady=(0, 12))

scroll_canvas = tk.Canvas(scroll_frame, bg=content_card["bg"], highlightthickness=0, bd=0)
scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=scroll_canvas.yview, style="Dark.Vertical.TScrollbar")
scroll_canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y", pady=(0, 0), padx=(0, 12))
scroll_canvas.pack(side="left", fill="both", expand=True)

section_container = tk.Frame(scroll_canvas, bg=content_card["bg"])
section_container_id = scroll_canvas.create_window((0, 0), window=section_container, anchor="nw")

def update_scroll_region(event):
    scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

section_container.bind("<Configure>", update_scroll_region)

scroll_canvas.bind("<Configure>", lambda e: scroll_canvas.itemconfig(section_container_id, width=e.width))

# Smooth scrolling while hovering over the content area
scroll_canvas.bind("<Enter>", lambda e: scroll_canvas.focus_set())
scroll_canvas.bind_all("<MouseWheel>", lambda e: scroll_canvas.yview_scroll(-1 * int(e.delta / 120), "units"))
scroll_canvas.bind_all("<Button-4>", lambda e: scroll_canvas.yview_scroll(-1, "units"))
scroll_canvas.bind_all("<Button-5>", lambda e: scroll_canvas.yview_scroll(1, "units"))

# Add URL section
add_url_section = tk.Frame(section_container, bg="#11254e", bd=0, highlightthickness=1, highlightbackground="#1e3d7b")
add_url_section.pack(fill="x", pady=(0, 18))
add_url_title = tk.Frame(add_url_section, bg=add_url_section["bg"])
add_url_title.pack(fill="x", padx=18, pady=(18, 6))
add_url_icon = ttk.Label(add_url_title, text="🔗", style="SectionIcon.TLabel")
add_url_icon.pack(side="left")
add_url_label = ttk.Label(add_url_title, text="Add URL", style="SectionTitle.TLabel")
add_url_label.pack(side="left", padx=(10, 0))
add_url_desc = ttk.Label(add_url_section, text="Paste the video link to download", style="SectionDesc.TLabel")
add_url_desc.pack(fill="x", padx=18)
url_entry = ttk.Entry(add_url_section, style="Card.TEntry")
url_entry.pack(fill="x", padx=18, pady=(12, 24))

# Browse section
folder_section = tk.Frame(section_container, bg="#11254e", bd=0, highlightthickness=1, highlightbackground="#1e3d7b")
folder_section.pack(fill="x", pady=(0, 18))
folder_title = tk.Frame(folder_section, bg=folder_section["bg"])
folder_title.pack(fill="x", padx=18, pady=(18, 6))
folder_icon = ttk.Label(folder_title, text="📁", style="SectionIcon.TLabel")
folder_icon.pack(side="left")
folder_label = ttk.Label(folder_title, text="Browse Folder", style="SectionTitle.TLabel")
folder_label.pack(side="left", padx=(10, 0))
folder_desc = ttk.Label(folder_section, text="Choose where to save your downloaded files", style="SectionDesc.TLabel")
folder_desc.pack(fill="x", padx=18)

folder_inner = tk.Frame(folder_section, bg="#0f224f")
folder_inner.pack(fill="x", padx=18, pady=(12, 18))
output_folder_var = tk.StringVar()
folder_entry = ttk.Entry(folder_inner, textvariable=output_folder_var, style="Card.TEntry")
folder_entry.pack(fill="x", side="left", expand=True, ipady=6)

browse_button_canvas = tk.Canvas(folder_inner, width=140, height=42, bg="#0f224f", highlightthickness=0, bd=0, cursor="hand2")
browse_button_canvas.create_image(0, 0, image=browse_button_image, anchor="nw")
browse_button_canvas.create_text(70, 21, text="Browse", fill="#ffffff", font=("Segoe UI", 11, "bold"))
browse_button_canvas.image = browse_button_image
browse_button_canvas.bind("<Button-1>", lambda e: choose_folder())
browse_button_canvas.pack(side="right", padx=(12, 0))

mp3_only_var = tk.BooleanVar(value=False)

options_section = tk.Frame(section_container, bg="#11254e", bd=0, highlightthickness=1, highlightbackground="#1e3d7b")
options_section.pack(fill="x", pady=(0, 18))
options_title = tk.Frame(options_section, bg=options_section["bg"])
options_title.pack(fill="x", padx=18, pady=(18, 6))
options_icon = ttk.Label(options_title, text="⚙️", style="SectionIcon.TLabel")
options_icon.pack(side="left")
options_label = ttk.Label(options_title, text="Download Options", style="SectionTitle.TLabel")
options_label.pack(side="left", padx=(10, 0))

options_body = tk.Frame(options_section, bg=options_section["bg"])
options_body.pack(fill="x", padx=18, pady=(6, 18))
toggle_frame = tk.Frame(options_body, bg=options_section["bg"])
toggle_frame.pack(fill="x")
toggle_canvas = tk.Canvas(toggle_frame, width=80, height=44, bg=options_section["bg"], highlightthickness=0, bd=0)
toggle_canvas.pack(side="left")
toggle_track_left = toggle_canvas.create_oval(6, 6, 42, 38, fill="#374c79", outline="")
toggle_track_right = toggle_canvas.create_oval(38, 6, 74, 38, fill="#374c79", outline="")
toggle_track_middle = toggle_canvas.create_rectangle(24, 6, 56, 38, fill="#374c79", outline="")
toggle_circle = toggle_canvas.create_oval(8, 8, 34, 36, fill="#ffffff", outline="")

toggle_text_label = ttk.Label(toggle_frame, text="Download audio only (MP3)", style="Subheader.TLabel")
toggle_text_label.pack(side="left", padx=(16, 0), pady=10)

toggle_canvas.bind("<Button-1>", lambda e: toggle_mp3())
toggle_text_label.bind("<Button-1>", lambda e: toggle_mp3())

status_section = tk.Frame(section_container, bg="#11254e", bd=0, highlightthickness=1, highlightbackground="#1e3d7b")
status_section.pack(fill="x", pady=(0, 18))
status_top = tk.Frame(status_section, bg=status_section["bg"])
status_top.pack(fill="x", padx=18, pady=(18, 8))
status_icon = ttk.Label(status_top, text="✔️", style="SectionIcon.TLabel")
status_icon.pack(side="left")
status_label = ttk.Label(status_top, text="", style="SectionTitle.TLabel")
status_label.pack(side="left", padx=(10, 0))
progressbar = ttk.Progressbar(status_section, variable=progress_var, maximum=100, style="Card.Horizontal.TProgressbar", mode="determinate")
progressbar.pack(fill="x", padx=18, pady=(0, 10), ipady=8)
progress_text = ttk.Label(status_section, text="", style="Subheader.TLabel")
progress_text.pack(anchor="e", padx=18, pady=(0, 16))

button_area = tk.Frame(content_card, bg=content_card["bg"])
button_area.pack(fill="x", padx=28, pady=(12, 28))
download_button_canvas = tk.Canvas(button_area, width=420, height=72, bg=content_card["bg"], highlightthickness=0, bd=0, cursor="hand2")
download_button_canvas.create_image(0, 0, image=download_button_image, anchor="nw")
download_button_canvas.create_text(210, 36, text="Download Video", fill="#ffffff", font=("Segoe UI", 16, "bold"))
download_button_canvas.image = download_button_image
download_button_canvas.bind("<Button-1>", lambda e: download_video())
download_button_canvas.pack(anchor="center", pady=(0, 0))

root.mainloop()
