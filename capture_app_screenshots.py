import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageGrab
import time
import os
import sys

# Add local path to import app_gui
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app_gui import EasyPushGUI

def capture_gui_screenshots():
    print("[*] Launching EasyPushGUI to capture interface screenshots...")

    # We will initialize GUI, update geometry, switch tabs, and take screenshots using ImageGrab
    root = EasyPushGUI()
    root.geometry("1100x720")
    root.update()

    screenshots_dir = r"c:\Users\prakh\OneDrive\Desktop\researchs"

    # Helper function to capture window bounding box
    def snap(name, tab_index=0):
        # Select tab
        root.notebook.select(tab_index)
        root.update_idletasks()
        root.update()
        time.sleep(0.3)

        x = root.winfo_rootx()
        y = root.winfo_rooty()
        w = root.winfo_width()
        h = root.winfo_height()

        save_path = os.path.join(screenshots_dir, name)

        try:
            # Grab screenshot of window region
            bbox = (x, y, x + w, y + h)
            img = ImageGrab.grab(bbox)
            img.save(save_path)
            print(f"[OK] Captured screenshot: {save_path} ({w}x{h})")
        except Exception as e:
            print(f"[!] ImageGrab error for {name}: {e}")

    # Capture Tab 0: Dashboard
    snap("screenshot_dashboard.png", 0)

    # Capture Tab 1: Self Analysis
    snap("screenshot_self_analysis.png", 1)

    # Capture Tab 2: Automatic Push
    snap("screenshot_auto_push.png", 2)

    # Capture Tab 3: Manual Push & Versioning
    snap("screenshot_manual_push.png", 3)

    # Capture Tab 4: History & Undo
    snap("screenshot_history_undo.png", 4)

    # Capture Tab 5: Developer Tools
    snap("screenshot_dev_tools.png", 5)

    root.destroy()
    print("[OK] All screenshots captured successfully!")

if __name__ == "__main__":
    capture_gui_screenshots()
