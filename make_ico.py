from PIL import Image

# Open your source high-res PNG file
img = Image.open("AnyStream Logo.png")

# Windows icons look best when packed with multiple standard scaling resolutions
icon_sizes = [(16, 16), (32, 32), (48, 48), (256, 256)]
img.save("AnyStreamLogo.ico", sizes=icon_sizes)
print("[+] Created AnyStreamLogo.ico successfully!")