import os
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox

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
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }
    else:
        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Success", "Download complete!")
    except Exception as e:
        messagebox.showerror("Error", f"Download failed:\n{e}")

# GUI Setup
root = tk.Tk()
root.title("Video Downloader")

tk.Label(root, text="Video URL:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

output_folder_var = tk.StringVar()

tk.Label(root, text="Download Folder:").pack(pady=5)
folder_frame = tk.Frame(root)
folder_frame.pack()

folder_entry = tk.Entry(folder_frame, textvariable=output_folder_var, width=40)
folder_entry.pack(side=tk.LEFT, padx=5)

mp3_only_var = tk.BooleanVar()

mp3_checkbox = tk.Checkbutton(root, text="Download audio only (MP3)", variable=mp3_only_var)
mp3_checkbox.pack(pady=5)

browse_button = tk.Button(folder_frame, text="Browse", command=choose_folder)
browse_button.pack(side=tk.LEFT)

download_button = tk.Button(root, text="Download Video", command=download_video)
download_button.pack(pady=20)

root.mainloop()
