import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
from tqdm import tqdm
import re
import random

grid_size_w, grid_size_h = 16, 10


def dot_matrix_two_dimensional_black_or_white(
    image_path, save_path, dots_size_w, dots_size_h
):
    print(image_path)
    print(save_path)
    print(dots_size_h)
    print(dots_size_w)
    with Image.open(image_path) as img:
        draw_mode = img.mode  # Use the same mode as your image
        draw = ImageDraw.Draw(img, draw_mode)

        # Ensure the image is in RGB mode for color inversion
        if draw_mode != "RGB":
            img = img.convert("RGB")
            print("no RGB")

        # Get image dimensions
        width, height = img.size
        print(width)
        print(height)

        # Calculate grid size
        grid_size_w = dots_size_w + 1
        grid_size_h = dots_size_h + 1
        cell_width = width / grid_size_w
        cell_height = height / grid_size_h

        font = ImageFont.truetype(
            "arial.ttf", width // 40
        )  # Adjust font path as needed

        count = 0
        for j in range(1, grid_size_h):
            for i in range(1, grid_size_w):
                x = int(i * cell_width)
                y = int(j * cell_height)

                # Get pixel color at (x, y)
                pixel_color = img.getpixel((x, y))

                # MODIFIED: Calculate opposite color from [black, white]
                if pixel_color[0] + pixel_color[1] + pixel_color[2] >= 255 * 3 / 2:
                    opposite_color = (0, 0, 0)
                else:
                    opposite_color = (255, 255, 255)

                # Draw a small dot at the intersection with the opposite color
                circle_radius = width // 240  # Adjust size as needed
                draw.ellipse(
                    [
                        (x - circle_radius, y - circle_radius),
                        (x + circle_radius, y + circle_radius),
                    ],
                    fill=opposite_color,
                    # fill="black",
                )

                text_x, text_y = x + 3, y

                # Label the point with the opposite color
                count_w = count // dots_size_w
                count_h = count % dots_size_w
                label_str = f"({count_w+1},{count_h+1})"
                draw.text((text_x, text_y), label_str, fill=opposite_color)
                count += 1

        print(count)
        img.save(save_path)


def find_img_dirs(target_directory):
    import fnmatch

    jsonl_files = []
    for dirpath, _, filenames in os.walk(target_directory):
        for filename in fnmatch.filter(filenames, "annotations.json"):
            jsonl_files.append(os.path.join(dirpath, filename))
    jsonl_files = [file.replace("annotations.json", "images") for file in jsonl_files]
    return jsonl_files


def get_img_files(dir_):
    json_files = []
    for root, dirs, files in os.walk(dir_):
        for file in files:
            if file.endswith(".png"):
                json_files.append(os.path.join(root, file))
    return json_files


def extract_answer(answer):
    pattern = r"\[\[(.*?)\]\]"
    matches = re.findall(pattern, answer)
    if matches:
        extracted_text = matches[-1]
        extracted_ls = eval("[" + extracted_text + "]")
        return extracted_ls
    return None


if __name__ == "__main__":
    dir_ = "CrazyGames-SpottingDifferences/"
    # for dir_ in find_img_dirs("repo/EgoThink/data"):
    imgs = [dir_ + str(img_id) + ".png" for img_id in range(1, 2)]
    for img_path in imgs:
        save_path = img_path.replace(".png", "_dots.png")
        save_path = save_path.replace("CrazyGames-SpottingDifferences/", "dot_img/")
        try:
            dot_matrix_two_dimensional_black_or_white(
                img_path, save_path, grid_size_w, grid_size_h
            )
        except:
            print(img_path)
            continue
