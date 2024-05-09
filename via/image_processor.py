import cv2
from cv2.gapi.wip import draw
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

grid_size_w, grid_size_h = 16, 10
# 5, 4 : 0.2125
# 6, 4
# 8, 5


def draw_bounding_box(image_path, save_path, x1, y1, x2, y2):
    image = cv2.imread(image_path)
    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)
    cv2.imwrite(save_path, image)


def draw_bounding_boxes(image_path, save_path, bboxes):
    image = cv2.imread(image_path)
    for x1, y1, w, h in bboxes:
        x2 = x1 + w
        y2 = y1 + h
        cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
    cv2.imwrite(save_path, image)


def draw_bounding_boxes_ratio(image_path, save_path, coordinates):
    image = cv2.imread(image_path)
    h, w = image.shape[0], image.shape[1]
    for x1, y1, x2, y2 in coordinates:
        x1 = int(x1 * w)
        x2 = int(x2 * w)
        y1 = int(y1 * h)
        y2 = int(y2 * h)
        cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)
    cv2.imwrite(save_path, image)


def local_masked(image_path, save_path, x1, y1, x2, y2):
    image = cv2.imread(image_path)
    mask = np.zeros_like(image)

    # Draw a white rectangle on the mask where you want to keep the image visible
    cv2.rectangle(mask, (x1, y1), (x2, y2), (255, 255, 255), -1)
    gray_mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    image[gray_mask == 0] = [255, 255, 255]  # Change to white
    cv2.imwrite(save_path, image)


def numbered_gridding(image_path, save_path, grid_size_w, grid_size_h):
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img, "RGBA")

        # Get image dimensions
        width, height = img.size

        # Calculate grid size
        cell_width = width / grid_size_w
        cell_height = height / grid_size_h

        # Draw the grid lines
        for i in range(1, grid_size_w):
            x = i * cell_width
            draw.line([(x, 0), (x, height)], fill=(128, 128, 128, 128), width=1)
        for i in range(1, grid_size_h):
            y = i * cell_height
            draw.line([(0, y), (width, y)], fill=(128, 128, 128, 128), width=1)

        # Draw and label intersection points
        # try:
        # Try to load a default font
        #     font = ImageFont.load_default()
        # except IOError:
        #     # If no font is found, use a simple font
        font = ImageFont.truetype("fonts/arial.ttf", 15)

        count = 1
        for j in range(grid_size_h + 1):
            for i in range(grid_size_w + 1):
                x = i * cell_width
                y = j * cell_height

                # Draw a small dot at the intersection
                circle_radius = 3
                draw.ellipse(
                    [
                        (x - circle_radius, y - circle_radius),
                        (x + circle_radius, y + circle_radius),
                    ],
                    fill="black",
                )

                text_x, text_y = x + 5, y
                if i == grid_size_w and j == grid_size_h:
                    text_x, text_y = x - 20, y - 15
                elif i == grid_size_w and j == 0:
                    text_x, text_y = x - 20, y
                elif j == grid_size_h:  # Bottom border
                    text_x, text_y = x + 5, y - 15
                elif i == grid_size_w:  # Right border
                    text_x, text_y = x - 20, y

                # Label the point
                draw.text((text_x, text_y), str(count), fill="black", font=font)
                count += 1

        img.save(save_path)


def coordinates_gridding(image_path, save_path, grid_size_w, grid_size_h):
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img, "RGBA")

        # Get image dimensions
        width, height = img.size

        # Calculate grid size
        cell_width = width / grid_size_w
        cell_height = height / grid_size_h

        # Draw the grid lines
        for i in range(1, grid_size_w):
            x = i * cell_width
            draw.line([(x, 0), (x, height)], fill=(128, 128, 128, 128), width=1)
        for i in range(1, grid_size_h):
            y = i * cell_height
            draw.line([(0, y), (width, y)], fill=(128, 128, 128, 128), width=1)

        font = ImageFont.truetype("fonts/arial.ttf", 10)

        count = 0
        for j in range(grid_size_h + 1):
            for i in range(grid_size_w + 1):
                x = i * cell_width
                y = j * cell_height

                # Draw a small dot at the intersection
                circle_radius = 3
                draw.ellipse(
                    [
                        (x - circle_radius, y - circle_radius),
                        (x + circle_radius, y + circle_radius),
                    ],
                    fill="black",
                )

                text_x, text_y = x + 5, y
                if i == grid_size_w and j == grid_size_h:
                    text_x, text_y = x - 20, y - 15
                elif i == grid_size_w and j == 0:
                    text_x, text_y = x - 20, y
                elif j == grid_size_h:  # Bottom border
                    text_x, text_y = x + 5, y - 15
                elif i == grid_size_w:  # Right border
                    text_x, text_y = x - 20, y

                # Label the point
                count_w = count % (grid_size_w + 1)
                count_h = count // (grid_size_w + 1)
                label_str = f"({count_w+1},{count_h+1})"
                draw.text((text_x, text_y), label_str, fill="black", font=font)
                count += 1

        img.save(save_path)


def area_numbered_gridding(image_path, save_path, grid_size_w, grid_size_h):
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img, "RGBA")

        # Get image dimensions
        width, height = img.size

        # Calculate grid size
        cell_width = width / grid_size_w
        cell_height = height / grid_size_h

        # Draw the grid lines
        for i in range(1, grid_size_w):
            x = i * cell_width
            draw.line([(x, 0), (x, height)], fill=(128, 128, 128, 128), width=1)
        for i in range(1, grid_size_h):
            y = i * cell_height
            draw.line([(0, y), (width, y)], fill=(128, 128, 128, 128), width=1)

        font = ImageFont.truetype("fonts/arial.ttf", 40)

        count = 1
        for j in range(grid_size_h):
            for i in range(grid_size_w):
                # Calculate the center of each cell
                x_center = (i * cell_width) + (cell_width / 2)
                y_center = (j * cell_height) + (cell_height / 2)

                # Get text size to adjust text position
                text_width, text_height = draw.textsize(str(count), font=font)

                # Calculate text position (centered in the cell)
                text_x = x_center - (text_width / 2)
                text_y = y_center - (text_height / 2)

                # Label the center of the cell
                draw.text((text_x, text_y), str(count), fill="black", font=font)
                count += 1

        img.save(save_path)


def dot_matrix_two_dimensional(image_path, save_path, dots_size_w, dots_size_h):
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img, "RGBA")

        # Get image dimensions
        width, height = img.size

        # Calculate grid size
        grid_size_w = dots_size_w + 1
        grid_size_h = dots_size_h + 1
        cell_width = width / grid_size_w / 2
        cell_height = height / grid_size_h

        font = ImageFont.truetype("arial.ttf", 15)  ### TODO
        # font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 15)

        count = 0
        for j in range(1, grid_size_h):
            for i in range(1, grid_size_w):
                x = i * cell_width
                y = j * cell_height

                # Get pixel color at (x, y)
                pixel_color = img.getpixel((x, y))

                # MODIFIED: Calculate opposite color from [black, white]
                if pixel_color[0] + pixel_color[1] + pixel_color[2] >= 255 * 3 / 2:
                    opposite_color = (0, 0, 0)
                else:
                    opposite_color = (255, 255, 255)
                # Draw a small dot at the intersection
                circle_radius = 2  ### TODO 2
                draw.ellipse(
                    [
                        (x - circle_radius, y - circle_radius),
                        (x + circle_radius, y + circle_radius),
                    ],
                    # fill="black",
                    fill=opposite_color,
                )

                text_x, text_y = x + 2, y

                # Label the point
                count_w = count // dots_size_w
                count_h = count % dots_size_w
                label_str = f"[{count_w+1},{count_h+1}]"
                label_str = f"[{count_h+1},{count_w+1}]"
                draw.text((text_x, text_y), label_str, fill=opposite_color, font=font)
                # draw.text((text_x, text_y), label_str, fill="black")
                count += 1
        count = 0
        for j in range(1, grid_size_h):
            for i in range(1, grid_size_w):
                x = i * cell_width + width / 2
                y = j * cell_height

                # Get pixel color at (x, y)
                pixel_color = img.getpixel((x, y))

                # MODIFIED: Calculate opposite color from [black, white]
                if pixel_color[0] + pixel_color[1] + pixel_color[2] >= 255 * 3 / 2:
                    opposite_color = (0, 0, 0)
                else:
                    opposite_color = (255, 255, 255)

                # Draw a small dot at the intersection
                circle_radius = 2  ### TODO 2
                draw.ellipse(
                    [
                        (x - circle_radius, y - circle_radius),
                        (x + circle_radius, y + circle_radius),
                    ],
                    fill=opposite_color,
                )

                text_x, text_y = x + 2, y

                # Label the point
                count_w = count // dots_size_w
                count_h = count % dots_size_w
                label_str = f"[{count_w+1},{count_h+1}]"
                label_str = f"[{count_h+1},{count_w+1}]"
                draw.text((text_x, text_y), label_str, fill=opposite_color, font=font)
                # draw.text((text_x, text_y), label_str, fill="black")
                count += 1
        img.save(save_path)


def dot_matrix_two_dimensional_spot_the_difference(
    image_path, save_path, dots_size_w, dots_size_h
):
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img, "RGBA")

        # Get image dimensions
        width, height = img.size

        # left half
        width = width // 2

        # Calculate grid size
        grid_size_w = dots_size_w + 1
        grid_size_h = dots_size_h + 1
        cell_width = width / grid_size_w
        cell_height = height / grid_size_h

        font = ImageFont.truetype("arial.ttf", 20)

        count = 0
        for j in range(1, grid_size_h):
            for i in range(1, grid_size_w):
                # left half
                x = i * cell_width
                y = j * cell_height

                # Draw a small dot at the intersection
                circle_radius = 3
                draw.ellipse(
                    [
                        (x - circle_radius, y - circle_radius),
                        (x + circle_radius, y + circle_radius),
                    ],
                    fill="black",
                )

                text_x, text_y = x + 5, y

                # Label the point
                count_w = count % dots_size_w
                count_h = count // dots_size_w
                label_str = f"({count_w+1},{count_h+1})"
                draw.text((text_x, text_y), label_str, fill="black", font=font)
                # count += 1

                # right half
                x = i * cell_width + width
                y = j * cell_height

                # Draw a small dot at the intersection
                circle_radius = 3
                draw.ellipse(
                    [
                        (x - circle_radius, y - circle_radius),
                        (x + circle_radius, y + circle_radius),
                    ],
                    fill="black",
                )

                text_x, text_y = x + 5, y

                # Label the point
                count_w = count % dots_size_w
                count_h = count // dots_size_w
                label_str = f"({count_w+1},{count_h+1})"
                draw.text((text_x, text_y), label_str, fill="black", font=font)
                count += 1

        img.save(save_path)


def find_img_dirs(target_directory):
    import fnmatch

    jsonl_files = []
    for dirpath, _, filenames in os.walk(target_directory):
        for filename in fnmatch.filter(filenames, "annotations.json"):
            jsonl_files.append(os.path.join(dirpath, filename))
    jsonl_files = [file.replace("annotations.json", "images") for file in jsonl_files]
    return jsonl_files


if __name__ == "__main__":
    ### localize
    # img_path = "images/math/equations/1.png"
    # save_path = "images/math/equations/1_localized_adjusted_3.png"
    # # coordinates = [(0.05, 0.05, 0.95, 0.25), (0.05, 0.30, 0.95, 0.45), (0.05, 0.50, 0.95, 0.65), (0.05, 0.70, 0.95, 0.85)]
    # # coordinates = [(0.05, 0.05, 0.95, 0.20), (0.05, 0.25, 0.95, 0.40), (0.05, 0.45, 0.95, 0.60), (0.05, 0.65, 0.95, 0.80)]
    # # coordinates = [(0.05, 0.02, 0.95, 0.18), (0.05, 0.22, 0.95, 0.38), (0.05, 0.42, 0.95, 0.58), (0.05, 0.62, 0.95, 0.78)]
    # coordinates = [(0.05, 0.00, 0.95, 0.15), (0.05, 0.18, 0.95, 0.32), (0.05, 0.35, 0.95, 0.50), (0.05, 0.53, 0.95, 0.68)]
    # draw_bounding_boxes_ratio(img_path, save_path, coordinates)

    ## guide
    # imgs = os.listdir("images/MME/count")
    # imgs = [os.path.join("images/MME/count", file) for file in imgs if file.endswith("jpg")]
    # for img_path in imgs:
    #     # img_path = "images/MME_failures/count/imgs/000000450303.jpg"
    #     # save_path = "images/MME_failures/count/imgs/000000450303_dots.jpg"
    #     save_path = img_path.replace(".jpg", "_dots.jpg")
    #     grid_size_w, grid_size_h = 6, 4
    #     dot_matrix_two_dimensional(img_path, save_path, grid_size_w, grid_size_h)

    # imgs = os.listdir("images/Spot_the_Difference")
    # imgs = [os.path.join("images/Spot_the_Difference", file) for file in imgs if file.endswith("-1.png")]
    # for img_path in imgs:
    #     save_path = img_path.replace(".png", "_dots.png")
    #     grid_size_w, grid_size_h = 6, 4
    #     dot_matrix_two_dimensional_spot_the_difference(img_path, save_path, grid_size_w, grid_size_h)

    dir_ = "CrazyGames-SpottingDifferences/"
    # for dir_ in find_img_dirs("repo/EgoThink/data"):
    imgs = [dir_ + str(img_id) + ".png" for img_id in range(1, 51)]
    for img_path in imgs:
        save_path = img_path.replace(".png", "_dots.png")
        save_path = save_path.replace("CrazyGames-SpottingDifferences/", "dot_img/")
        try:
            dot_matrix_two_dimensional(img_path, save_path, grid_size_w, grid_size_h)
        except:
            print(img_path)
            continue

    # draw_bounding_boxes_ratio(img_path, save_path, [
    #     (0.12, 0.65, 0.36, 0.93),
    #     (0.62, 0.68, 0.88, 0.95)
    # ])

    # bboxes = [[203, 236, 34, 41.5], [304, 263, 38, 52.5], [203, 164, 24.5, 34.5], [148, 125, 23, 28.5], [129, 133, 29.5, 34.5], [155, 151, 21, 22], [182, 92, 18.5, 28.5], [234, 141, 27, 39.5], [213, 212, 23.5, 30], [226, 164, 18.5, 34], [552, 54, 34.5, 30.5], [180, 434, 28, 29], [124, 380, 22.5, 21.5], [157, 318, 16, 22], [152, 306, 16.5, 18.5], [176, 18, 23, 30], [587, 33, 29.5, 34.5], [563, 371, 17.5, 28.5], [327, 526, 10.5, 14.5]]
    # draw_bounding_boxes("images/CountAnythingV1_clean/agriculture/agru_mer-1/test/IMG_2006_JPG.rf.01f4cf1a034e67f5137a6264620ef4b9.jpg", "test.jpg", bboxes)
