# https://www.crazygames.com/game/find-the-difference

from PIL import Image
import sys

# Load the image
image_path = f'{sys.argv[1]}.png'
image = Image.open(image_path)

# Calculate the dimensions for the split
width, height = image.size
left_half = (0, 0, width // 2 - 3, height)
right_half = (width // 2 + 3, 0, width, height)

# Crop the image into two halves
left_image = image.crop(left_half)
right_image = image.crop(right_half)

# Save the two halves
left_image.save(f'{sys.argv[1]}-left.png')
right_image.save(f'{sys.argv[1]}-right.png')

print("Done")
