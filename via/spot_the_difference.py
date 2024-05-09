import ast
import base64
import os
import requests
import json
import re
from PIL import Image, ImageDraw
from requests.auth import HTTPBasicAuth
from datetime import datetime
from tqdm import tqdm
from tenacity import retry, wait_random_exponential, stop_after_attempt
from cycle_detect import get_cycle
from image_processor import grid_size_h, grid_size_w
import math

valid_radius = 50


def trans_dot_to_coordinate(dots):
    coordinates = []
    try:
        for dot in dots:
            coordinates.append(
                [
                    dot[0],
                    952 * dot[1] / (grid_size_w + 1),
                    594 * dot[2] / (grid_size_h + 1),
                ]
            )
        return coordinates
    except:
        return []


def point_in_cycle_num(coordinates, circles):
    def distance(coordinate, center):
        return math.sqrt(
            (coordinate[1] - center[0]) ** 2 + (coordinate[2] - center[1]) ** 2
        )

    num = 0
    circles_copy = circles[:]
    hit_circles = []
    for coordinate in coordinates:
        for circle in circles_copy:
            if distance(coordinate, circle[0]) < valid_radius:
                num += 1
                print(
                    f"num: {num}\ncircle in x:({circle[0][0]})     y:({circle[0][1]})"
                )
                hit_circles.append(circle)
                circles_copy.remove(circle)
                break
    return num, hit_circles


def parse_coordinate(response):
    answer_index = response.find("ANSWER:")
    if answer_index != -1:
        # 截取"ANSWER:"之后的部分
        answer_text = response[answer_index + len("ANSWER:") :]
    else:
        print("not find ANSWER:")
        answer_text = response
        # return []
    matches = re.findall(r"\[(.*?)\]", answer_text)
    print(type(matches))
    lists = []
    if matches:
        num = 0
        for match in matches:
            num += 1
            try:
                # 将每个匹配的字符串解析为列表
                parsed_list = ast.literal_eval(f"[{match}]")
                # print(parsed_list)
                if len(parsed_list) == 2:
                    tmp_list = []
                    tmp_list.append(num)
                    tmp_list.extend(parsed_list)
                    parsed_list = tmp_list
                # print(parsed_list)
                lists.append(parsed_list)
                # print(lists)
                # print(str(match))
            except Exception as e:
                print(f"解析错误: {e}")
                # 使用正则表达式找到所有的数字
                numbers = re.findall(r"\d+", str(match))

                # 将找到的数字字符串转换为整数
                result = [int(num) for num in numbers]
                if len(result) == 3:
                    lists.append(result)
                else:
                    print(f"bad parse :{str(match)}")
        return lists
    else:
        print("not find []")
        return []


def llm_spot_img(coordinates, circles, hit_circles, img_name, is_dot):
    # 图片的路径
    image_path = "CrazyGames-SpottingDifferences/" + img_name  # 替换为你的图片路径

    # 加载图片
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    for coordinate in coordinates:
        # 圆心坐标和半径
        x, y = coordinate[1], coordinate[2]  # 替换为你的坐标
        radius = 50

        # 在指定坐标处绘制圆
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline="black")

    for circle in circles:
        # 圆心坐标和半径
        x, y = circle[0][0], circle[0][1]  # 替换为你的坐标
        radius = circle[1]

        # 在指定坐标处绘制圆
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius), outline="red", width=5
        )

    for circle in hit_circles:

        # 圆心坐标和半径
        x, y = circle[0][0], circle[0][1]  # 替换为你的坐标

        radius = circle[1]

        # 在指定坐标处绘制圆
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius), outline="blue", width=5
        )

    # 显示图像
    # image.show()

    # 保存图像
    if is_dot:
        save_path = "llm_spot_img/" + img_name  # 替换为你想保存的路径
    else:
        save_path = "llm_spot_naive_img/" + img_name
    image.save(save_path)


# ip: 183.172.201.80
# Function to encode the image
def encode_image(image_path):
    if not os.path.exists(image_path):
        print("not exist: ", image_path)
        exit(1)
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


@retry(wait=wait_random_exponential(min=2, max=10), stop=stop_after_attempt(5))
def query_single_turn(
    image_paths,
    question,
    history=None,
    model="gpt-4-vision-preview",
    temperature=0,
    max_tokens=8192,
    is_dot=False,
):
    content = [{"type": "text", "text": question}]
    # content = [{"type": "text", "text": "hello"}]
    for image_path in image_paths:
        # print(image_path)
        image_format = image_path.split(".")[-1]
        encoded_image = encode_image(image_path)
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{image_format};base64,{encoded_image}",
                    "detail": "high",
                },
            }
        )
    if not is_dot:
        messages = [{"role": "user", "content": content}]
    # for dotted
    else:
        messages = get_system_prompt_intro_dots_single_img(grid_size_h, grid_size_w)
        messages.append({"role": "user", "content": content})

    if history is not None:
        messages = history + messages

    # print("system")
    # print(messages[0]["content"][0])
    # print("uesr:")
    # print(messages[1]["content"][0])

    # print(messages[0]["role"])
    # print(messages[1]["role"])
    url = "http://43.163.219.59:8001/delta"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    # print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    # print(payload)

    data = json.dumps(payload)
    response = requests.post(
        url=url,
        data=data,
        auth=HTTPBasicAuth(username="lxy", password="Thumt4@2023"),
        timeout=120,
    )

    response_json = response.json()
    response_text = response_json["choices"][0]["message"]["content"]
    print(">>> response: ", response_text)
    return response_json


def query_single_turn_and_save(
    exp_name,
    image_paths,
    question,
    history=None,
    model="gpt-4-vision-preview",
    temperature=0,
    max_tokens=4096,
    additional_save=None,
    is_dot=False,
):
    def get_today_str():
        current_datetime = datetime.now()
        date_string = current_datetime.strftime("%Y-%m-%d")
        return date_string

    response = query_single_turn(
        image_paths, question, history, model, temperature, max_tokens, is_dot
    )
    # print("*********************************************")
    # print(f"response is {response}")
    overall = {
        "exp": exp_name,
        "image_paths": image_paths,
        "history": history,
        "question": question,
        "model": model,
        "temperature": temperature,
        "response": response,
    }

    if additional_save is not None:
        overall.update(additional_save)
    save_dir = os.path.join("log", get_today_str())
    save_file = os.path.join(save_dir, f"{exp_name}.json")
    os.makedirs(os.path.dirname(save_file), exist_ok=True)
    with open(save_file, "w") as f:
        f.write(json.dumps(overall, indent=2, ensure_ascii=False))
        f.close()
    return response["choices"][0]["message"]["content"]


def get_system_prompt_intro_dots_double_imgs(h, w):
    return [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": f'''I will provide you with two images of the same scene. The second image is overlaid with a dot matrix of a shape of {h} * {w} to help you with your task, and each dot is labeled with two-dimensional coordinates (x,y).\n 1. When you mention any key objects in the image, first output their nearest coordinates then identify them.\n 2. You use the coordinates to determine the spatial relationships of the objects. within each column, the x-coordinate increases from top to bottom, and Within each row, the y-coordinate increases from left to right.\n 3. You can search and reason region by region with the help of the dots.\n 4. Conclude a direct and brief answer to the question in the end, with format "ANSWER: "''',
                }
            ],
        }
    ]


def get_system_prompt_intro_dots_single_img(h, w):
    return [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    # "text": f"""The image consist of a left image and a right image. Left image and right image are overlaid with the same black dot matrix of a shape of {w} * {h} to help you with your task, and each dot is labeled with two-dimensional dot position [x, y]. The same dot position in the left and right images represent the same position.\n 1. When you mention any key object in the image, first find the dot closest to the object, and then ouput the dot's labeled dot position, and then identify the object. After identifying the object re-find the dot closest to the object to confirm if you find the correct closest dot, and output dot's labeled position\n 2. You use the dot positions to determine the spatial relationships of the objects. In the left image or right image,  within each row, the x-position increases from left to right, and Within each column, the y-position increases from top to bottom.\n 3. You can search and reason region by region with the help of the dots.\n4. Dots with the same dot position in the left and right images have the same relative position on the respective images. \n5. Conclude a direct and brief answer to the question in the end, with format "ANSWER: ".""",
                    "text": f"""The image consist of a left image and a right image. Left image and right image are overlaid with the same black dot matrix of a shape of {w} * {h} to help you with your task, and each dot is labeled with two-dimensional dot position [x, y]. The same dot position in the left and right images represent the same position.\n 1. When you mention any key area in the image, identify the area. Then find out the dot that is the closest to the center of the area, and base the partial region of the image where the dot is located indentify the area again.\n 2. You use the dot positions to determine the spatial relationships of the objects. In the left image or right image,  within each row, the x-position increases from left to right, and Within each column, the y-position increases from top to bottom.\n 3. You can search and reason region by region with the help of the dots.\n4. Conclude a direct and brief answer to the question in the end, with format "ANSWER: ".""",
                }
            ],
        }
    ]


def get_yes_or_no_postfix():
    return [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": f"""Finally, conclude your answer in format [[ANSWER]], such as [[yes]] or [[no]].""",
                }
            ],
        }
    ]


def extract_final_answer(answer):
    if not isinstance(answer, str):
        return None
    try:
        pattern = r"\[\[(.*?)\]\]"
        matches = re.findall(pattern, answer)
        if matches:
            extracted_text = matches[-1]
            return extracted_text.strip()
        else:
            pattern = r"\((.)\)"
            matches = re.findall(pattern, answer)
            last_match = matches[-1] if matches else None
            if last_match in ["a", "b", "A", "B"]:
                return last_match
    except:
        print("extract error ...")
        return None
    return None


def get_spot_the_difference_inst():
    return f"""Search the regions sequentially with the help of the dot matrix and the two-dimensional coordinates, finally spot ten differences between two images."""


if __name__ == "__main__":
    for is_dot in [True, False]:
        test_image_num = 3
        circle_success_num = 0
        test_fail_ids = []
        refuse_answer_num = 0
        print(f"now test is_dot={is_dot}")
        # is_dot = True

        for img_id in range(2, test_image_num + 1):
            ### for single query
            exp_name = f"Spot_the_difference/Spot_the_difference_example_1_direct"
            # for question image
            if is_dot:
                img_name = str(img_id) + "_dots" + ".png"
            else:
                img_name = str(img_id) + ".png"

            if is_dot:
                image_paths = [
                    # ("CrazyGames-SpottingDifferences/" + img_name),
                    ("dot_img/" + img_name),
                ]
            else:
                image_paths = [
                    ("CrazyGames-SpottingDifferences/" + img_name),
                    # ("dot_img/" + img_name),
                ]
            # base_dot_info = " Please use the dot position to assist you and give the pixel coordinate based on resolution as the answer of question."
            # base_dot_info = "When using dot position (x, y), it can be transform to pixel coordinate. For example, if the dot metric is 4(height) x 4(width) and the left image is 952(width) * 594(height), then dot position (2, 3) equals [3/5 * 952, 2/5 * 594] in pixel coordinate in the left image. Left image and right image have the same dot position.\nPlease note that dot position can guide you, but the actual pixel coordinate of the difference has nothing to do with the dot position."

            history = None

            if is_dot:
                question = "Spot ten differences of the images"
                # addition_info = " and give pixel coordinate of every difference to make I can locate on the image by my program. The pixel coordinate can be that the left edge of the left image is x=0, the right edge of the right image is x=1904 (based on the resolution of the image), and the top and bottom edges of the images are y=0 and y=594. Please note that you need to indicate the pixel coordinate use [spot index, x, y]. After discovering the difference between the left and right images, you only need to point out its pixel coordinates in the left image(it means that the x-coordinate is less than 952)"
                # addition_info = " and give pixel coordinate of every difference to make I can locate on the image by my program. The pixel coordinate can be that the left edge of the left image is x=0, the right edge of the right image is x=1904 (based on the resolution of the image), and the top and bottom edges of the images are y=0 and y=594. Please note that you need to indicate the pixel coordinate use [spot index, x, y]. After discovering the difference between the left and right images, you only need to point out nearest dot position and then calculate the dot's pixel coordinate."
                # base_dot_info = "Left image and right image have the same dot metric. You can use the dot position to help you get the correct pixel coordinate. If the dot metric is 8(width) * 5(height) and the left image's resolution is 952 * 594, the dot position (x, y) equals to pixel coordinate [952 * x / (8 + 1), 594 * y / (5 + 1)]. Please notice that in answer you only need to give the final result and the dot's pixel coordinate do not equals to the difference's pixel coordinate but it can guide you find the correct pixel coordinate of difference you need find."
                # base_dot_info = f"Left image and right image have the same dot metric. You can use the dot position to help you get the correct pixel coordinate. for example if the dot metric is {grid_size_w}(width) * {grid_size_h}(height) and the left image's resolution is 952 * 594, the dot position (2, 3) equals to pixel coordinate [(952 * 2 / ({grid_size_w} + 1)), (594 * 3 / ({grid_size_h} + 1))]. Please notice that in answer you only need to give the calculation result rather than the calculation process."

                # addition_info = " and give the nearest dot position of every difference in the format: [spot index, x, y]."
                # addition_info = " and when you spot a difference, output the position of the dot closest to the difference in the format: [spot index, x, y]."
                addition_info = " and use dot and dot's lebeled position to locate the difference. Please note that your answer is the closest dot's labeled position of every difference in the format: [spot index, x, y]."
                addition_info = " and answer dot position closest to every difference in the format: [spot index, x, y]."
                # addition_info = ""
                # base_dot_info = "You can use dot position to compare because same dot position [x, y] means the same position in left and right image."
                base_dot_info = "When you are spotting the difference, you can confirm it by comparing local images near the same dot position of the left and right images. For example if you think [2, 3] is different then compare local images near [2, 3] in left and right images."
                # base_dot_info = "When you are looking for differences, if you find a difference and assume that the difference is near dot position [x, y], you can compare the images near the dot position [x, y] of the left and right images to confirm whether they are different."
                base_dot_info = ""
                trick_for_answer = " I am going to tip $100 for a better answer."
                cot_prompt = " Let's think step by step."
            else:
                # # for no dot
                # # for basic
                question = "Spot ten differences of the images"
                # to make llm print coordinate by give an example
                addition_info = " and give mathematic coordinate of every difference to make I can locate on the image by my program. The coordinate can be that the left edge of the left image is x=0, the right edge of the right image is x=1904 (based on the resolution of the image), and the top and bottom edges of the images are y=0 and y=594. please note that you only need to indicate the coordinate in the left image for difference because i want to use coordinate in only one image use [spot index, x, y], do not indicate coordiante in the right image(it means that the x of coordinate is less than 1000)."
                # to make llm answer more actively because llm always return can not give an answer
                trick_for_answer = " I am going to tip $100 for a good solution"

            question = question + addition_info + trick_for_answer
            # print(question)
            print(question)
            print(image_paths)
            try:
                response = query_single_turn_and_save(
                    exp_name, image_paths, question, history=history, is_dot=is_dot
                )
                print("get respones")
            except:
                test_fail_ids.append(img_id)
                print(f"test {img_id} failed!!!")
                continue

            # print("my response")
            # print(response)
            # for check image
            img_name = str(img_id) + "-res.png"

            # response = "ANSWER: [1,1], [3,2], [6,3], [6,2], [8,1], [9,3], [3,3], [10,5], [2,5], [7,1]."

            coordinates = parse_coordinate(response)
            print(coordinates)
            if is_dot == True:
                coordinates = trans_dot_to_coordinate(coordinates)
            if coordinates == []:
                test_fail_ids.append(img_id)
                print(f"test {img_id} failed!!!")
                refuse_answer_num += 1
                continue
            cycles = get_cycle(img_name)
            print(coordinates)
            # print(point_in_cycle_num(coordinates, cycles))
            test_success_num, hit_circles = point_in_cycle_num(coordinates, cycles)
            llm_spot_img(coordinates, cycles, hit_circles, img_name, is_dot)
            print(f"test {img_id}: {test_success_num}")
            circle_success_num += test_success_num
        if is_dot:
            with open("dot-res.txt", "w") as f:
                f.write(f"success test num: {test_image_num - len(test_fail_ids)}\n")
                f.write(f"llm refuse answer num: {refuse_answer_num}\n")
                f.write(f"all hit circles num: {circle_success_num}\n")
                f.write(
                    f"all accuracy: {circle_success_num / ((test_image_num - len(test_fail_ids)) * 10)}\n"
                )
        else:
            with open("dot-NONE-res.txt", "w") as f:
                f.write(f"success test num: {test_image_num - len(test_fail_ids)}\n")
                f.write(f"llm refuse answer num: {refuse_answer_num}\n")
                f.write(f"all hit circles num: {circle_success_num}\n")
                f.write(
                    f"all accuracy: {circle_success_num / ((test_image_num - len(test_fail_ids)) * 10)}\n"
                )
        print(f"success test num: {test_image_num - len(test_fail_ids)}")
        print(f"llm refuse answer num: {refuse_answer_num}")
        print(f"all hit circles num: {circle_success_num}")
        print(
            f"all accuracy: {circle_success_num / ((test_image_num - len(test_fail_ids)) * 10)}"
        )
