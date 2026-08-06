import sys
import os

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageDraw, ImageFont

def create_placeholder():
    # Create a 200x200 transparent image
    img = Image.new("RGBA", (200, 200), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple circle as the "pet"
    draw.ellipse((20, 20, 180, 180), fill=(100, 200, 255, 255), outline=(50, 150, 200, 255), width=5)
    
    # Draw eyes
    draw.ellipse((60, 60, 90, 90), fill=(255, 255, 255, 255))
    draw.ellipse((110, 60, 140, 90), fill=(255, 255, 255, 255))
    draw.ellipse((70, 70, 80, 80), fill=(0, 0, 0, 255))
    draw.ellipse((120, 70, 130, 80), fill=(0, 0, 0, 255))
    
    # Draw mouth
    draw.arc((70, 100, 130, 140), start=0, end=180, fill=(0, 0, 0, 255), width=5)
    
    img.save("pet_placeholder.png")
    print("Placeholder created successfully.")

if __name__ == "__main__":
    create_placeholder()
