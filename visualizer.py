import os
import math
from PIL import Image, ImageDraw

def generate_collatz_image(sequence, starting_number, max_value, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    
    width, height = 800, 800
    cx, cy = width / 2, height / 2
    img = Image.new("RGB", (width, height), (12, 12, 20))
    draw = ImageDraw.Draw(img)
    
    x, y = 0.0, 0.0
    angle = 0.0
    step_length = 22
    mirrors = 6  # Creates a 6-sided snowflake/mandala effect
    
    for i, val in enumerate(sequence):
        angle += -0.45 if val % 2 == 0 else 0.75
        next_x = x + math.cos(angle) * step_length
        next_y = y + math.sin(angle) * step_length
        
        ratio = i / max(1, len(sequence))
        color = (int(60 + 195 * ratio), int(230 * (1 - ratio)), 255)
        
        # Draw the line 6 times rotated around the center
        for m in range(mirrors):
            rot = (2 * math.pi / mirrors) * m
            cos_r, sin_r = math.cos(rot), math.sin(rot)
            
            p1 = (cx + x * cos_r - y * sin_r, cy + x * sin_r + y * cos_r)
            p2 = (cx + next_x * cos_r - next_y * sin_r, cy + next_x * sin_r + next_y * cos_r)
            
            draw.line([p1, p2], fill=color, width=3)
            # Add a small dot on odd jumps for extra detail
            if val % 2 != 0:
                draw.ellipse([p2[0]-3, p2[1]-3, p2[0]+3, p2[1]+3], fill=(255, 255, 255))
                
        x, y = next_x, next_y

    filename = f"collatz_{starting_number}.png"
    img.save(os.path.join(output_folder, filename))
    return f"/static/images/{filename}"
