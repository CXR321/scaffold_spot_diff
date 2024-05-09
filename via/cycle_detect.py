import cv2
import numpy as np
from PIL import Image, ImageDraw


def detect_green_circles(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Convert to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the range of green color in HSV
    # These values can be changed depending on the shade of green
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([70, 255, 255])

    # Create a mask for green color
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    # Bitwise-AND mask and original image
    green_only = cv2.bitwise_and(image, image, mask=green_mask)

    # Convert masked image to grayscale
    gray = cv2.cvtColor(green_only, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise and improve circle detection
    gray_blurred = cv2.GaussianBlur(gray, (9, 9), 0)

    # Apply HoughCircles to detect circles
    circles = cv2.HoughCircles(
        gray_blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=60,
        param1=50,
        param2=30,
        minRadius=35,
        maxRadius=45,
    )

    # Check if circles have been detected and initialize a list to store circles
    detected_circles = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            center_x, center_y, radius = circle[0], circle[1], circle[2]
            # detected_circles.append((center_x, center_y, radius))
            detected_circles.append([[center_x, center_y], radius])

    return detected_circles


def get_cycle(image_name):
    radius_upper = 42
    radius_lower = 37

    def circle_wash(circles):
        def search_same_point(circles, coordinate):
            for i in range(len(circles)):
                if (
                    abs(circles[i][0][0] - coordinate[0]) <= 2
                    and abs(circles[i][0][1] - coordinate[1]) <= 2
                ):
                    return i
            return -1

        washed_circles = []
        double_circle_index = []
        for circle in circles:
            # 圆心坐标和半径
            x, y = circle[0][0], circle[0][1]  # 替换为你的坐标
            radius = circle[1]

            is_same_id = search_same_point(washed_circles, circle[0])
            if is_same_id == -1:
                washed_circles.append(circle)
            else:
                double_circle_index.append(is_same_id)
        if len(washed_circles) == 20:
            return washed_circles
        elif len(washed_circles) > 20:
            [washed_circles[i] for i in double_circle_index]
            return [washed_circles[i] for i in double_circle_index]

    # # image_name = "3-res.png"

    # # 载入图片
    image_path = "CrazyGames-SpottingDifferences/" + image_name
    # image = cv2.imread(image_path)

    # # 将图片从BGR颜色空间转换到HSV颜色空间
    # hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # # 绿色在HSV颜色空间中的范围
    # # 这些值可能需要根据你的图片进行调整
    # lower_green = np.array([40, 40, 40])
    # upper_green = np.array([60, 255, 255])

    # # 创建一个绿色的掩码
    # mask = cv2.inRange(hsv, lower_green, upper_green)

    # # 寻找掩码中的轮廓
    # contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # # 用于存储中心点和半径的列表
    # circles = []

    # # 对于每个轮廓，计算其最小闭圆
    # for cnt in contours:
    #     # 计算轮廓的中心点和半径
    #     (x, y), radius = cv2.minEnclosingCircle(cnt)
    #     center = (int(x), int(y))
    #     radius = int(radius)

    #     if radius > radius_upper or radius < radius_lower:
    #         continue
    #     # 将中心点和半径添加到列表中
    #     circles.append((center, radius))

    #     # 确定圆上一个点的坐标（以圆心向右半径长度的点为例）
    #     edge_x = int(x + radius)
    #     edge_y = int(y)  # 圆上这点的y坐标与圆心的y坐标相同
    #     # 获取圆边缘上该点的HSV颜色值
    #     try:
    #         hsv_color_value_edge = hsv[edge_y][edge_x]
    #         # 输出颜色值
    #         print("HSV Color value at (x, y):", hsv_color_value_edge)
    #     except:
    #         pass

    # circles = circle_wash(circles)
    # circles_num = len(circles)
    # if circles_num != 20:
    #     print(f"now detect cycle: {circles_num}")
    # return circles

    return detect_green_circles(image_path)


if __name__ == "__main__":
    image_name = "6-res.png"
    circles = get_cycle(image_name)
    # 输出检测到的圆圈的中心点和半径
    print(circles)
    print(f"get cycle nums : {len(circles)}")

    # 图片的路径
    image_path = "CrazyGames-SpottingDifferences/" + image_name  # 替换为你的图片路径

    # 加载图片
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    for circle in circles:
        # 圆心坐标和半径
        x, y = circle[0][0], circle[0][1]  # 替换为你的坐标
        radius = circle[1]

        # 在指定坐标处绘制圆
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline="black")

    # 显示图像
    # image.show()

    # 保存图像
    save_path = "llm_spot_img/" + image_name  # 替换为你想保存的路径
    image.save(save_path)
