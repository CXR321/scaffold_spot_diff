from PIL import Image, ImageDraw

# 图片的路径
image_path = "CrazyGames-SpottingDifferences/1.png"  # 替换为你的图片路径

# 加载图片
image = Image.open(image_path)
draw = ImageDraw.Draw(image)

# 圆心坐标和半径
x, y = 1600, 500  # 替换为你的坐标
radius = 50

# 在指定坐标处绘制圆
draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline="black")

# 显示图像
# image.show()

# 保存图像
save_path = "llm_spot_img/1.png"  # 替换为你想保存的路径
image.save(save_path)
