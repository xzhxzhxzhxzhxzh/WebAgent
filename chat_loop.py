import sys
import select
import os
import shutil
import requests
import json
import base64
import subprocess
import logging
import numpy as np
from PIL import Image, ImageDraw
from typing import List, Dict
from src.logger import logger_setup

logger_setup()
logger = logging.getLogger(__name__)
BASE_URL = "http://127.0.0.1:8000"


def create_chat_completion(
    model: str,
    messages: List[Dict[str, str]],
    curr_url: str,
    img_hist: int,
    temperature: float = 0.8,
    max_tokens: int = 2048,
    top_p: float = 0.8,
    use_stream: bool = False,
):
    move_forward = False
    data = {
        "model": model,
        "messages": messages[-3:],
        "stream": use_stream,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }

    response = requests.post(
        f"{BASE_URL}/v1/chat/completions", json=data, stream=use_stream
    )
    if response.status_code == 200:
        if use_stream:
            raise NotImplementedError
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")[6:]
                    try:
                        response_json = json.loads(decoded_line)
                        content = (
                            response_json.get("choices", [{}])[0]
                            .get("delta", {})
                            .get("content", "")
                        )
                        print(content)
                    except:
                        print("Special Token:", decoded_line)
        else:
            decoded_line = response.json()
            content = (
                decoded_line.get("choices", [{}])[0]
                .get("message", "")
                .get("content", "")
            )
            msg_response = {
                "role": "assistant",
                "content": content,
            }

            logger.info(f"Raw content: {content}")
            content = parse_message(content)
            logger.info(f"Parsed content: {content}")

            if content["next_act"]:
                print(
                    f"[AGENT]: I suggest: {content['plan']}\nThe next step is: {content['next_act']}"
                )
            else:
                print(f"[AGENT]: I suggest: {content['plan']}")

            if content["operation"]:
                visual_atten_area(
                    f"screenshot/screenshot_{img_hist - 1}.jpg",
                    content["operation"]["position"],
                )
                result = subprocess.run(
                    [
                        "node",
                        "browser_procesing.js",
                        curr_url,
                        str(img_hist),
                        json.dumps(content["operation"]),
                    ],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    logger.debug("Error in js script:", result.stderr)
                    assert result.returncode == 0
                curr_url = result.stdout.strip()
                move_forward = not interrupt_act()

            return msg_response, curr_url, move_forward, img_hist
    else:
        print("[SYSTEM]: Error:", response.status_code)
        return None


def parse_message(message: str):
    message_list = message.split("\n")
    try:
        plan = message_list[0][6:]
    except IndexError:
        logger.debug(f"No plan was detected: {message_list}")
        raise ValueError

    try:
        next_act = message_list[1][13:]
    except IndexError:
        next_act = ""
        logger.debug(f"No action was detected: {message_list}")

    try:
        operation = message_list[-1][19:]
        operation = parse_action(operation)
    except IndexError:
        operation = ""
        logger.debug(f"No operation was detected: {message_list}")

    output = {
        "plan": plan,
        "next_act": next_act,
        "operation": operation,
    }
    return output


def parse_action(message: str):
    try:
        _, operation = message.split(" -> ")
    except ValueError:
        logger.debug(f"Unknown operation: {message}")
        raise NotImplementedError

    if "CLICK" in operation:
        action = "CLICK"
        _, pos = operation.split(" at the box ")
        pos = pos[2:-2].replace(" ", "").split(",")
        pos_x = (0.5 * (int(pos[2]) - int(pos[0])) + int(pos[0])) / 1000
        pos_y = (0.5 * (int(pos[3]) - int(pos[1])) + int(pos[1])) / 1000
        pos = [
            pos_x,
            pos_y,
            int(pos[0]) / 1000,
            int(pos[1]) / 1000,
            int(pos[2]) / 1000,
            int(pos[3]) / 1000,
        ]
        content = ""
    elif "TYPE" in operation:
        action = "TYPE"
        content, pos = operation.split(" at the box ")
        pos = pos[2:-2].replace(" ", "").split(",")
        pos_x = (0.5 * (int(pos[2]) - int(pos[0])) + int(pos[0])) / 1000
        pos_y = (0.5 * (int(pos[3]) - int(pos[1])) + int(pos[1])) / 1000
        pos = [
            pos_x,
            pos_y,
            int(pos[0]) / 1000,
            int(pos[1]) / 1000,
            int(pos[2]) / 1000,
            int(pos[3]) / 1000,
        ]
        content = content[6:]
    else:
        logger.debug(f"Unknown operation: {operation}")
        raise NotImplementedError

    return {"action": action, "position": pos, "content": content}


def visual_atten_area(image_path, pos):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    ellipse_pos = np.array([pos[0], pos[1], pos[0], pos[1]]) * 1120
    ellipse_pos[:2] = ellipse_pos[:2] - 3
    ellipse_pos[2:] = ellipse_pos[2:] + 3
    rectangle_pos = np.array([pos[2], pos[3], pos[4], pos[5]]) * 1120

    draw.ellipse(ellipse_pos.tolist(), outline="red", fill="red")
    draw.rectangle(rectangle_pos.tolist(), outline="red")

    img.save(image_path)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def interrupt_act():
    print("[SYSTEM]: ENTER to stop (3s)")
    sys.stdout.flush()
    ready, _, _ = select.select([sys.stdin], [], [], 3)
    if ready:
        sys.stdin.readline().strip()
        return True
    else:
        return False


if __name__ == "__main__":
    if os.path.exists("screenshot"):
        shutil.rmtree("screenshot")
    os.makedirs("screenshot")

    msg_hist = []
    img_hist = 0
    move_forward = False
    curr_url = "https://www.amazon.com/" # Change this to your interested webpage

    while True:
        if img_hist == 0:
            result = subprocess.run(
                ["node", "browser_procesing.js", curr_url, str(img_hist)],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logger.debug("Error in js script:", result.stderr)
                assert result.returncode == 0
            curr_url = result.stdout.strip()
            logger.info(f"URL: {curr_url}")

        if not move_forward:
            query = input("[USER]: ")
            if query == "stop" or query == "q" or query == "exit":
                break
            query += "(with grounding)"
            logger.info(f"User input: {query}")
        else:
            assert msg_hist[-2]["role"] == "user"
            query = msg_hist[-2]["content"][0]["text"]
            logger.info(f"Auto input: {query}")

        img_url = f"data:image/jpeg;base64, {encode_image(os.path.join('screenshot', f'screenshot_{img_hist}.jpg'))}"
        img_hist += 1

        message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": query,
                },
                {
                    "type": "image_url",
                    "image_url": {"url": img_url},
                },
            ],
        }
        msg_hist.append(message)
        msg_response, curr_url, move_forward, img_hist = create_chat_completion(
            model="cogagent-chat-hf",
            messages=msg_hist,
            curr_url=curr_url,
            img_hist=img_hist,
            use_stream=False,
        )
        msg_hist.append(msg_response)
        logger.info(f"URL: {curr_url}")
