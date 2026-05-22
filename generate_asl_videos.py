"""
ASL Video Generator for Odyssey of the Mind Performance
========================================================
Generates fingerspelling-based ASL videos for each scene of the story.
Uses the spoken-to-signed library for pose generation and renders
avatar-style videos showing hand/body movements.

Usage:
    python3 generate_asl_videos.py
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from spoken_to_signed.gloss_to_pose.lookup.fingerspelling_lookup import FingerspellingPoseLookup
from spoken_to_signed.gloss_to_pose import concatenate_poses
from pose_format import Pose
import imageio

# ============ Configuration ============
OUTPUT_DIR = "videos"
WIDTH = 640
HEIGHT = 480
BG_COLOR = (20, 25, 40)  # Dark blue background
BODY_COLOR = (100, 180, 255)  # Light blue for body
HAND_COLOR = (255, 200, 100)  # Gold for hands
FACE_COLOR = (180, 220, 255)  # Pale blue for face
LINE_WIDTH = 2
POINT_RADIUS = 4

# Hand connections (landmark indices within hand component)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),      # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),      # Index
    (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
    (0, 13), (13, 14), (14, 15), (15, 16),# Ring
    (0, 17), (17, 18), (18, 19), (19, 20),# Pinky
    (5, 9), (9, 13), (13, 17),            # Palm
]

# Body connections (indices within pose landmarks)
BODY_CONNECTIONS = [
    (0, 1),  # Shoulders
    (0, 2), (2, 4),  # Left arm
    (1, 3), (3, 5),  # Right arm
    (0, 6), (1, 7),  # Torso
    (6, 7),  # Hips
]


def get_component_data(pose, frame_idx, component_name):
    """Extract points for a specific component from the pose data."""
    offset = 0
    for comp in pose.header.components:
        n_points = len(comp.points)
        if comp.name == component_name:
            return pose.body.data[frame_idx, 0, offset:offset + n_points, :]
        offset += n_points
    return None


def draw_connections(draw, points, connections, color, line_width=2):
    """Draw lines between connected points."""
    for i, j in connections:
        if i < len(points) and j < len(points):
            x1, y1 = points[i]
            x2, y2 = points[j]
            if not (np.isnan(x1) or np.isnan(y1) or np.isnan(x2) or np.isnan(y2)):
                if 0 <= x1 <= WIDTH and 0 <= y1 <= HEIGHT and 0 <= x2 <= WIDTH and 0 <= y2 <= HEIGHT:
                    draw.line([(x1, y1), (x2, y2)], fill=color, width=line_width)


def draw_points(draw, points, color, radius=3):
    """Draw circles at each point."""
    for x, y in points:
        if not (np.isnan(x) or np.isnan(y)):
            if 0 <= x <= WIDTH and 0 <= y <= HEIGHT:
                draw.ellipse(
                    [(x - radius, y - radius), (x + radius, y + radius)],
                    fill=color
                )


def render_frame(pose, frame_idx):
    """Render a single frame of the pose as an image."""
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Get data for each component
    body = get_component_data(pose, frame_idx, 'POSE_LANDMARKS')
    left_hand = get_component_data(pose, frame_idx, 'LEFT_HAND_LANDMARKS')
    right_hand = get_component_data(pose, frame_idx, 'RIGHT_HAND_LANDMARKS')

    # Scale and center the pose data
    # The pose data coordinates are roughly in pixel space already
    # but we need to adjust to our frame size
    all_points = []
    for data in [body, left_hand, right_hand]:
        if data is not None:
            valid = data[~np.isnan(data[:, 0])]
            if len(valid) > 0:
                all_points.append(valid)

    if not all_points:
        return np.array(img)

    all_pts = np.concatenate(all_points, axis=0)
    min_x, min_y = np.nanmin(all_pts[:, 0]), np.nanmin(all_pts[:, 1])
    max_x, max_y = np.nanmax(all_pts[:, 0]), np.nanmax(all_pts[:, 1])

    # Scale to fit in frame with padding
    padding = 60
    scale_x = (WIDTH - 2 * padding) / max(max_x - min_x, 1)
    scale_y = (HEIGHT - 2 * padding) / max(max_y - min_y, 1)
    scale = min(scale_x, scale_y)

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    def transform(points):
        """Transform points to screen coordinates."""
        result = []
        for pt in points:
            x = (pt[0] - center_x) * scale + WIDTH / 2
            y = (pt[1] - center_y) * scale + HEIGHT / 2
            result.append((x, y))
        return result

    # Draw body
    if body is not None:
        body_pts = transform(body[:, :2])
        draw_connections(draw, body_pts, BODY_CONNECTIONS, BODY_COLOR, LINE_WIDTH + 1)
        draw_points(draw, body_pts, BODY_COLOR, POINT_RADIUS + 1)

    # Draw left hand
    if left_hand is not None:
        lh_pts = transform(left_hand[:, :2])
        draw_connections(draw, lh_pts, HAND_CONNECTIONS, HAND_COLOR, LINE_WIDTH)
        draw_points(draw, lh_pts, HAND_COLOR, POINT_RADIUS)

    # Draw right hand
    if right_hand is not None:
        rh_pts = transform(right_hand[:, :2])
        draw_connections(draw, rh_pts, HAND_CONNECTIONS, HAND_COLOR, LINE_WIDTH)
        draw_points(draw, rh_pts, HAND_COLOR, POINT_RADIUS)

    return np.array(img)


def text_to_fingerspelling_pose(text, fs_lookup):
    """Convert text to fingerspelling poses, word by word."""
    words = text.strip().split()
    poses = []

    for word in words:
        # Clean word - keep only letters
        clean_word = ''.join(c for c in word.lower() if c.isalpha())
        if not clean_word:
            continue

        try:
            pose = fs_lookup.lookup(clean_word, clean_word, 'en', 'ase')
            poses.append(pose)
        except (FileNotFoundError, Exception) as e:
            print(f"  Skipping word '{clean_word}': {e}")
            continue

    if not poses:
        return None

    if len(poses) == 1:
        return poses[0]

    return concatenate_poses(poses, trim=False)


def render_pose_to_video(pose, output_path, text_overlay=""):
    """Render a full pose sequence to video."""
    n_frames = len(pose.body.data)
    fps = int(pose.body.fps)

    print(f"    Rendering {n_frames} frames at {fps} FPS...")

    import av

    container = av.open(output_path, mode='w')
    stream = container.add_stream('libx264', rate=fps)
    stream.width = WIDTH
    stream.height = HEIGHT
    stream.pix_fmt = 'yuv420p'
    stream.options = {'crf': '23', 'preset': 'fast'}

    for i in range(n_frames):
        frame_data = render_frame(pose, i)

        # Add text overlay showing the current word context
        if text_overlay:
            img = Image.fromarray(frame_data)
            draw = ImageDraw.Draw(img)
            # Add a bar at the bottom
            bar_height = 40
            draw.rectangle(
                [(0, HEIGHT - bar_height), (WIDTH, HEIGHT)],
                fill=(10, 10, 30)
            )
            # Truncate text if too long
            display_text = text_overlay[:80] + "..." if len(text_overlay) > 80 else text_overlay
            draw.text((10, HEIGHT - bar_height + 10), display_text, fill=(200, 220, 255))
            frame_data = np.array(img)

        av_frame = av.VideoFrame.from_ndarray(frame_data, format='rgb24')
        for packet in stream.encode(av_frame):
            container.mux(packet)

    # Flush
    for packet in stream.encode():
        container.mux(packet)
    container.close()
    print(f"    Saved: {output_path}")


def generate_scene_video(scene_num, text, fs_lookup, max_words=15):
    """Generate ASL video for a scene by fingerspelling key words."""
    output_path = os.path.join(OUTPUT_DIR, f"scene{scene_num}.mp4")

    print(f"\n  Scene {scene_num}: Generating ASL fingerspelling...")

    # For each scene, take the most important words (nouns, verbs)
    # and fingerspell them to create a comprehensible video
    words = text.split()

    # Take first N words to keep video manageable
    segment = ' '.join(words[:max_words])
    print(f"    Text segment: '{segment}'")

    pose = text_to_fingerspelling_pose(segment, fs_lookup)
    if pose is None:
        print(f"    ERROR: Could not generate pose for scene {scene_num}")
        return False

    render_pose_to_video(pose, output_path, text_overlay=segment)
    return True


# ============ Scene Texts (simplified for fingerspelling) ============
SCENE_TEXTS = [
    # Scene 1: Introduction
    "Lost in Omerland welcome to our story from planet Carnivosia",
    # Scene 2: Crash Landing
    "Captain Super and Duper crash land on planet search for crystal",
    # Scene 3: Cyberpunk City
    "They find robot in Cyberpunk City recover missing gear",
    # Scene 4: Robot Betrayal
    "Robot betrays group in forest freezes them with trap",
    # Scene 5: Crystal Cave
    "Crystal Cave robot raps her story heroes forgive her",
    # Scene 6: Triumphant Return
    "Crystal found under ship heroes return home celebrate victory",
]


def main():
    print("=" * 60)
    print("ASL Video Generator - Odyssey of the Mind")
    print("Generating fingerspelling ASL videos for each scene")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\nInitializing ASL fingerspelling lookup...")
    fs_lookup = FingerspellingPoseLookup()
    print("Ready!")

    for i, text in enumerate(SCENE_TEXTS, 1):
        generate_scene_video(i, text, fs_lookup, max_words=12)

    print("\n" + "=" * 60)
    print("DONE! Videos generated in the 'videos/' folder.")
    print("=" * 60)


if __name__ == "__main__":
    main()
