import os
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Function to generate text overlay with custom font
def generate_text_image(text, font_path, font_size, text_color="white", bg_color="black", size=(1280, 720)):
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)

    # Load custom font
    font = ImageFont.truetype(font_path, font_size)
    
    # Get text bounding box and calculate text size
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Position text in the center of the image
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # Add text to the image
    draw.text(position, text, font=font, fill=text_color)
    
    # Convert to numpy array (required for moviepy)
    return np.array(img)

# Define transition effects
def crossfade(clip1, clip2, duration=1):
    return concatenate_videoclips([clip1.crossfadeout(duration), clip2.crossfadein(duration)])

# Additional transitions for completeness
def slide_from_right(clip1, clip2, duration=1):
    w, h = clip1.size
    slide = lambda t: ('center', h * (1 - t / duration))
    return concatenate_videoclips([clip1.set_position(slide), clip2.set_position(('center', 'center'))])

def zoom_in(clip1, clip2, duration=1):
    zoom1 = clip1.resize(lambda t: 1 + 0.5 * t / duration)
    return concatenate_videoclips([zoom1, clip2])

def spin_transition(clip1, clip2, duration=1):
    spin1 = clip1.rotate(lambda t: 360 * t / duration)
    return concatenate_videoclips([spin1, clip2])

# Function to create video with transitions and text
def create_video_with_transitions(image_dir, font_path, output_file, duration_per_image=2, transition_duration=1):
    # Load all images from the directory
    image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg'))]
    
    # DEBUG: Print loaded image files
    print(f"Image files loaded: {image_files}")
    
    # Check if there are any images
    if len(image_files) == 0:
        print("No images found in the directory!")
        return

    image_clips = []
    
    # Create a list of ImageClip objects with forced resizing and RGB conversion
    for img_path in image_files:
        print(f"Loading image: {img_path}")
        try:
            # Load image with PIL, ensure it's in RGB mode
            img = Image.open(img_path).convert('RGB')
            img = img.resize((1280, 720))  # Force resize to video resolution
            img_array = np.array(img)

            # Create ImageClip with resized image
            clip = ImageClip(img_array).set_duration(duration_per_image)
            image_clips.append(clip)
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
    
    # Ensure that the image clips are loaded correctly
    if not image_clips:
        print("No images were loaded. Please check the image directory path.")
        return

    print(f"Loaded {len(image_clips)} image clips.")

    # Check that there are enough clips to apply transitions
    if len(image_clips) < 2:
        print("Not enough clips for transitions. Creating video with only the available images.")
        final_video = concatenate_videoclips(image_clips, method="compose")
    else:
        final_clips = []
        for i in range(len(image_clips) - 1):
            clip1 = image_clips[i]
            clip2 = image_clips[i + 1]

            # Apply the transition between valid clips
            try:
                print(f"Applying transition between clip {i} and clip {i+1}")
                transition = crossfade(clip1, clip2, transition_duration)
                final_clips.append(transition)
            except Exception as e:
                print(f"Error applying transition at index {i}: {e}")
                final_clips.append(clip1)
                final_clips.append(clip2)

        # Add the last clip without a transition
        final_clips.append(image_clips[-1])  # Add the last clip without transition
        
        # Concatenate all clips together
        final_video = concatenate_videoclips(final_clips, method="compose")

    # Debug: Save a frame from each image to check if images are loaded properly
    for i, clip in enumerate(image_clips):
        frame = clip.get_frame(0)  # Get the first frame of each image clip
        Image.fromarray(frame).save(f"image_frame_{i}.jpg")
        print(f"Saved image_frame_{i}.jpg for inspection.")

    # Add a text overlay (optional)
    text_img = generate_text_image("Dear Client, welcome to Your Video!", font_path, 70, text_color="white")
    text_clip = ImageClip(text_img).set_duration(3)

    # Combine the text clip and the video
    final_video = concatenate_videoclips([text_clip, final_video])

    # Write the video file
    try:
        print("Writing final video...")
        final_video.write_videofile(output_file, codec='libx264', fps=24)
    except Exception as e:
        print(f"Error during video writing: {e}")

# Set paths based on your directory structure
image_dir = "/home/abenlinux/upwork-projects/video-transitions-project/images"
font_path = "/home/abenlinux/upwork-projects/video-transitions-project/Fonts/four.ttf"  # Change to the desired font
output_file = "/home/abenlinux/upwork-projects/video-transitions-project/output_video.mp4"

# Create the video with transitions and text
create_video_with_transitions(image_dir, font_path, output_file)
