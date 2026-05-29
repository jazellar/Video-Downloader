import os
import shutil
import yt_dlp
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageOps, ImageDraw

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_folder_var.set(folder)

def download_video():
    status_label.config(text="")
    url = url_entry.get().strip()
    output_folder = output_folder_var.get().strip()

    if not url:
        messagebox.showerror("Error", "Please enter a video URL.")
        return

    if not output_folder:
        messagebox.showerror("Error", "Please choose a download folder.")
        return

    # Cross-platform environment checks
    ffmpeg_found = bool(shutil.which("ffmpeg") or shutil.which("ffmpeg.exe"))
    default_ffmpeg = r"C:\ffmpeg\bin"
    ffmpeg_dir = default_ffmpeg if os.path.isdir(default_ffmpeg) else ""
    
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
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
                {"key": "FFmpegMetadata", "add_metadata": True},
                {"key": "EmbedThumbnail", "already_have_thumbnail": False},
            ],
        }
    else:
        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
            "writethumbnail": True,
            "embedthumbnail": True,
            "postprocessors": [
                {"key": "FFmpegMetadata", "add_metadata": True},
                {"key": "EmbedThumbnail", "already_have_thumbnail": False},
            ],
        }

    needs_ffmpeg = mp3_only_var.get() or ("+" in ydl_opts.get("format", ""))
    if needs_ffmpeg and not ffmpeg_found:
        messagebox.showerror("FFmpeg Required",
                             "FFmpeg not found. Please install FFmpeg and add it to your system PATH.")
        return

    if ffmpeg_found and ffmpeg_dir:
        ydl_opts["ffmpeg_location"] = ffmpeg_dir

    if getattr(download_video, "running", False):
        messagebox.showinfo("In Progress", "A download is already running.")
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
        toggle_canvas.coords(toggle_circle, 46, 8, 72, 36)
        for part in [toggle_track_left, toggle_track_right, toggle_track_middle]:
            toggle_canvas.itemconfig(part, fill="#3b8bff")
    else:
        toggle_canvas.itemconfig(toggle_circle, fill="#ffffff")
        toggle_canvas.coords(toggle_circle, 8, 8, 34, 36)
        for part in [toggle_track_left, toggle_track_right, toggle_track_middle]:
            toggle_canvas.itemconfig(part, fill="#374c79")

# Fast Pillow-based Gradient Image Factory 
def create_gradient_image_pil(width, height, start_color, end_color, radius=18):
    def hex_to_rgb(h):
        return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    c1 = hex_to_rgb(start_color)
    c2 = hex_to_rgb(end_color)
    
    # Generate linear gradient base
    base = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(base)
    for x in range(width):
        r = int(c1[0] + (c2[0] - c1[0]) * (x / max(width - 1, 1)))
        g = int(c1[1] + (c2[1] - c1[1]) * (x / max(width - 1, 1)))
        b = int(c1[2] + (c2[2] - c1[2]) * (x / max(width - 1, 1)))
        draw.line([(x, 0), (x, height)], fill=(r, g, b, 255))
        
    # Mask rounded corners
    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, width, height], radius=radius, fill=255)
    
    final_image = Image.new("RGBA", (width, height), (7, 19, 38, 0))
    final_image.paste(base, (0, 0), mask=mask)
    return ImageTk.PhotoImage(final_image)

# GUI Initialization
root = tk.Tk()
root.title("AnyStream Downloader")
root.geometry("950x900")
root.configure(bg="#071326")
root.resizable(True, True)
root.minsize(840, 640)

# Background Management
bg_path = os.path.join(os.path.dirname(__file__), "AnyStream Background.png")
original_bg = None
if os.path.exists(bg_path):
    try:
        original_bg = Image.open(bg_path)
    except Exception as e:
        print(f"Error loading background visual assets: {e}")

bg_canvas = tk.Canvas(root, highlightthickness=0, bd=0)
bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

def resize_bg(event):
    if event.widget is root and original_bg and event.width > 10 and event.height > 10:
        bg_canvas.place(x=0, y=0, width=event.width, height=event.height)
        bg = ImageOps.fit(original_bg, (event.width, event.height), Image.Resampling.LANCZOS)
        root.bg_img = ImageTk.PhotoImage(bg)
        bg_canvas.delete("bg_img")
        bg_canvas.create_image(0, 0, image=root.bg_img, anchor="nw", tags="bg_img")
        bg_canvas.lower("bg_img")

root.bind("<Configure>", resize_bg)

# Style Overrides
style = ttk.Style(root)
style.theme_use("clam")
style.configure("Card.TFrame", background="#071326", borderwidth=0)
style.configure("Logo.TLabel", background="#071326", foreground="#ffffff", font=("Segoe UI", 34, "bold"))
style.configure("Subtitle.TLabel", background="#071326", foreground="#7fa7ff", font=("Segoe UI", 16))
style.configure("Label.TLabel", background="#071326", foreground="#d8e2ff", font=("Segoe UI", 12))
style.configure("Card.TEntry", fieldbackground="#15254f", foreground="#f0f4ff", background="#15254f", bordercolor="#3266ff")
style.configure("Card.Horizontal.TProgressbar", troughcolor="#15254f", background="#7de8a1")
style.configure("Header.TLabel", background="#0f2142", foreground="#ffffff", font=("Segoe UI", 34, "bold"))
style.configure("Subheader.TLabel", background="#0f2142", foreground="#cfd9f7", font=("Segoe UI", 11))
style.configure("SectionTitle.TLabel", background="#11254e", foreground="#f4f7ff", font=("Segoe UI", 11, "bold"))
style.configure("SectionDesc.TLabel", background="#11254e", foreground="#99b3d6", font=("Segoe UI", 9))
style.configure("Sidebar.TLabel", background="#0b1732", foreground="#8fafff", font=("Segoe UI", 10))
style.configure("SidebarActive.TLabel", background="#0b1732", foreground="#ffffff", font=("Segoe UI", 11, "bold"))
style.configure("SectionIcon.TLabel", background="#11254e", foreground="#7fa7ff", font=("Segoe UI", 12))

# Generate Optimized UI Images via PIL
browse_button_image = create_gradient_image_pil(140, 42, "#3d9cff", "#7668ff", radius=18)
download_button_image = create_gradient_image_pil(420, 72, "#3dc5ff", "#8a5bff", radius=26)

# Layout Setup
sidebar_frame = tk.Frame(root, bg="#0b1732", width=280, highlightthickness=0, bd=0)
sidebar_frame.grid(row=0, column=0, sticky="ns")

main_frame = tk.Frame(root, bg="#071326", highlightthickness=0, bd=0)
main_frame.grid(row=0, column=1, sticky="nsew")
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# App branding sidebar
sidebar_logo = tk.Frame(sidebar_frame, bg="#0b1732")
sidebar_logo.pack(fill="x", pady=(24, 20), padx=24)

logo_name = ttk.Label(sidebar_logo, text="AnyStream\nDownloader", style="Sidebar.TLabel", justify="left")
logo_name.pack(side="left")

nav_frame = tk.Frame(sidebar_frame, bg="#0b1732")
nav_frame.pack(fill="x", pady=(10, 30), padx=16)

for text, active in [("Downloader", True), ("History", False), ("Settings", False)]:
    item_bg = "#10214a" if active else "#0b1732"
    item = tk.Frame(nav_frame, bg=item_bg, pady=12, padx=16)
    item.pack(fill="x", pady=8)
    lbl_style = "SidebarActive.TLabel" if active else "Sidebar.TLabel"
    ttk.Label(item, text=text, style=lbl_style).pack(side="left")

# Primary Interface Cards
content_card = tk.Frame(main_frame, bg="#0f2142", highlightthickness=1, highlightbackground="#233963")
content_card.pack(fill="both", expand=True, padx=24, pady=24)

header_area = tk.Frame(content_card, bg=content_card["bg"])
header_area.pack(fill="x", padx=28, pady=(30, 16))
ttk.Label(header_area, text="Downloader", style="Header.TLabel").pack(anchor="w")
ttk.Label(header_area, text="Download videos from your favorite sites quickly and easily.", style="Subheader.TLabel").pack(anchor="w", pady=(12, 0))

scroll_frame = tk.Frame(content_card, bg=content_card["bg"])
scroll_frame.pack(fill="both", expand=True, padx=28, pady=(0, 12))

scroll_canvas = tk.Canvas(scroll_frame, bg=content_card["bg"], highlightthickness=0, bd=0)
scroll_canvas.pack(side="left", fill="both", expand=True)

section_container = tk.Frame(scroll_canvas, bg=content_card["bg"])
section_container_id = scroll_canvas.create_window((0, 0), window=section_container, anchor="nw")

section_container.bind("<Configure>", lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))
scroll_canvas.bind("<Configure>", lambda e: scroll_canvas.itemconfig(section_container_id, width=e.width))

# Context-specific local scrolling optimization
def _on_mousewheel(event):
    scroll_canvas.yview_scroll(-1 * int(event.delta / 120), "units")
scroll_canvas.bind("<Enter>", lambda e: scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel))
scroll_canvas.bind("<Leave>", lambda e: scroll_canvas.unbind_all("<MouseWheel>"))

# Inputs Block
add_url_section = tk.Frame(section_container, bg="#11254e", bd=0, highlightthickness=1, highlightbackground="#1e3d7b")
add_url_section.pack(fill="x", pady=(0, 18))
url_title_frame = tk.Frame(add_url_section, bg=add_url_section["bg"])
url_title_frame.pack(fill="x", padx=18, pady=(18, 6))
ttk.Label(url_title_frame, text="Video URL", style="SectionTitle.TLabel").pack(side="left")
url_entry = ttk.Entry(add_url_section, style="Card.TEntry")
url_entry.pack(fill="x", padx=18, pady=(12, 24))

# Output Destination Selector Block
folder_section = tk.Frame(section_container, bg="#11254e", bd=0, highlightthickness=1, highlightbackground="#1e3d7b")
folder_section.pack(fill="x", pady=(0, 18))
folder_title_frame = tk.Frame(folder_section, bg=folder_section["bg"])
folder_title_frame.pack(fill="x", padx=18, pady=(18, 6))
ttk.Label(folder_title_frame, text="Download Folder", style="SectionTitle.TLabel").pack(side="left")

folder_inner = tk.Frame(folder_section, bg="#0f224f")
folder_inner.pack(fill="x", padx=18, pady=(12, 18))
output_folder_var = tk.StringVar()
folder_entry = ttk.Entry(folder_inner, textvariable=output_folder_var, style="Card.TEntry")
folder_entry.pack(fill="x", side="left", expand=True, ipady=6)

browse_button_canvas = tk.Canvas(folder_inner, width=140, height=42, bg="#0f224f", highlightthickness=0, bd=0, cursor="hand2")
browse_button_canvas.create_image(0, 0, image=browse_button_image, anchor="nw")
browse_button_canvas.create_text(70, 21, text="Browse", fill="#ffffff", font=("Segoe UI", 11, "bold"))
browse_button_canvas.bind("<Button-1>", lambda e: choose_folder())
browse_button_canvas.pack(side="right", padx=(12, 0))

# Options Block
mp3_only_var = tk.BooleanVar(value=False)
options_section = tk.Frame(section_container, bg="#11254e", bd=0, highlightthickness=1, highlightbackground="#1e3d7b")
options_section.pack(fill="x", pady=(0, 18))
options_title_frame = tk.Frame(options_section, bg=options_section["bg"])
options_title_frame.pack(fill="x", padx=18, pady=(18, 6))
ttk.Label(options_title_frame, text="Download Options", style="SectionTitle.TLabel").pack(side="left")

toggle_frame = tk.Frame(options_section, bg=options_section["bg"])
toggle_frame.pack(fill="x", padx=18, pady=(6, 18))
toggle_canvas = tk.Canvas(toggle_frame, width=80, height=44, bg=options_section["bg"], highlightthickness=0, bd=0)
toggle_canvas.pack(side="left")
toggle_track_left = toggle_canvas.create_oval(6, 6, 42, 38, fill="#374c79", outline="")
toggle_track_right = toggle_canvas.create_oval(38, 6, 74, 38, fill="#374c79", outline="")
toggle_track_middle = toggle_canvas.create_rectangle(24, 6, 56, 38, fill="#374c79", outline="")
toggle_circle = toggle_canvas.create_oval(8, 8, 34, 36, fill="#ffffff", outline="")

toggle_text_label = ttk.Label(toggle_frame, text="Download audio only (MP3)", style="Subheader.TLabel")
toggle_text_label.pack(side="left", padx=(16, 0))
toggle_canvas.bind("<Button-1>", lambda e: toggle_mp3())
toggle_text_label.bind("<Button-1>", lambda e: toggle_mp3())

# Status / Progress Tracker Frame
status_section = tk.Frame(section_container, bg="#11254e", bd=0, highlightthickness=1, highlightbackground="#1e3d7b")
status_section.pack(fill="x", pady=(0, 18))
status_top = tk.Frame(status_section, bg=status_section["bg"])
status_top.pack(fill="x", padx=18, pady=(18, 8))
status_label = ttk.Label(status_top, text="Status Pending", style="SectionTitle.TLabel")
status_label.pack(side="left")

progress_var = tk.DoubleVar(value=0)
progressbar = ttk.Progressbar(status_section, variable=progress_var, maximum=100, style="Card.Horizontal.TProgressbar", mode="determinate")
progressbar.pack(fill="x", padx=18, pady=(0, 10), ipady=8)
progress_text = ttk.Label(status_section, text="", style="Subheader.TLabel")
progress_text.pack(anchor="e", padx=18, pady=(0, 16))

# Submit Operation Control Button Area
button_area = tk.Frame(content_card, bg=content_card["bg"])
button_area.pack(fill="x", padx=28, pady=(12, 28))
download_button_canvas = tk.Canvas(button_area, width=420, height=72, bg=content_card["bg"], highlightthickness=0, bd=0, cursor="hand2")
download_button_canvas.create_image(0, 0, image=download_button_image, anchor="nw")
download_button_canvas.create_text(210, 36, text="Download Video", fill="#ffffff", font=("Segoe UI", 16, "bold"))
download_button_canvas.bind("<Button-1>", lambda e: download_video())
download_button_canvas.pack(anchor="center")

root.mainloop()