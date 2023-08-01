from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.common.base import AppiumOptions
import asyncio, appium
import re, time, string, json, cleantext
from selenium.common.exceptions import NoSuchElementException

appium_server_url = 'http://localhost:4723'

def extract_qq_chat():

    # Extract left from bounds ([left, top][right, bottom])
    def extract_left(bounds: str):
        return int(bounds[1:bounds.index(',')])

    # Extract root's label (instruction/ouput) and text
    def check_root(element):
        # check whether the resource-id with "com.tencent.mobileqq:id/s4y" is before the resource-id with "com.tencent.mobileqq:id/nlp"
        try:
            if extract_left(
                    element.find_element(by=AppiumBy.ID,
                                        value="com.tencent.mobileqq:id/s4y").
                    get_attribute("bounds")) < extract_left(
                        element.find_element(by=AppiumBy.ID,
                                            value="com.tencent.mobileqq:id/nlp").
                        get_attribute("bounds")):
                label = "instruction"
            else:
                label = "output"
        except Exception as e:
            return None, None
        try:
            text_el = element.find_element(by=AppiumBy.ID, value="com.tencent.mobileqq:id/ex1")
            text = text_el.text
            # Remove \x14 emoji
            try:
                while True:
                    emoji_index = text.index('\x14')
                    text = text[:emoji_index] + text[emoji_index + 2:]
            except ValueError as e:
                pass
            # Remove other emoji
            text = cleantext.clean(text, to_ascii=False, lower=False, no_emoji=True)
        except NoSuchElementException as e:
            text = ""
        return label, text

    # Process chat list
    def process_chat_list(chat_list):
        # Remove None and Empty
        chat_list = [chat for chat in chat_list if chat[1] is not None and len(chat[1]) > 0]

        state = 0
        cached_instruction = []
        cached_output = []
        last_i = len(chat_list)
        json_output = []
        for chat in reversed(chat_list):
            if state == 0:
                if chat[0] == "instruction":
                    cached_instruction.append(chat[1])
                    state = 1
                else:
                    cached_output.append(chat[1])
            elif state == 1:
                if chat[0] == "instruction":
                    cached_instruction.append(chat[1])
                else:
                    if len(cached_instruction) > 0 and len(cached_output) > 0:
                        json_output.append({
                            "instruction": '\n'.join(reversed(cached_instruction)),
                            "input": "",
                            "output": '\n'.join(reversed(cached_output))
                        })
                    last_i = chat_list.index(chat)

                    cached_instruction = []
                    cached_output = []
                    cached_output.append(chat[1])
                    state = 0
        if len(cached_instruction) > 0 and len(cached_output) > 0:
            json_output.append({
                "instruction": '\n'.join(reversed(cached_instruction)),
                "input": "",
                "output": '\n'.join(reversed(cached_output))
            })
            last_i = -1
        return chat_list[:last_i + 1], json_output

    options = AppiumOptions()
    options.set_capability("platformName", "Android")
    options.set_capability("platformVersion", "10")
    options.set_capability("automationName", "uiautomator2")
    options.set_capability("deviceName", "3EP0219423003283")
    options.set_capability("appPackage", "com.tencent.mobileqq")
    options.set_capability("noReset", True)

    driver = webdriver.Remote(appium_server_url, options=options)

    # Get the screen center
    screen_size = driver.get_window_size()
    screen_center_x = screen_size['width'] / 2
    screen_center_y = screen_size['height'] / 2
    # Get the RecyclerView height
    recycler_view = driver.find_element(by=AppiumBy.XPATH,
        value="//androidx.recyclerview.widget.RecyclerView")
    recycler_view_height = recycler_view.size['height']

    # Scroll to the top of the current chat while the first resource-id with "com.tencent.mobileqq:id/nlp" stays same
    current_first_nlp = driver.find_element(by=AppiumBy.ID, value="com.tencent.mobileqq:id/nlp")
    root_list = []
    chat_list = []
    prev_chat_list = []
    json_chat = []
    while True:
        # Get all the resource-id with "com.tencent.mobileqq:id/root"
        new_root_list = driver.find_elements(by=AppiumBy.ID, value="com.tencent.mobileqq:id/root")
        # Remove those already checked
        new_root_list = [
            root for root in new_root_list if root not in root_list
        ]
        for root in new_root_list:
            chat_list.append(check_root(root))
        # print(chat_list)
        prev_chat_list, json_output = process_chat_list(chat_list + prev_chat_list)
        json_chat += json_output
        # print(json_output, prev_chat_list)
        chat_list = []
        root_list = new_root_list


        # input()
        driver.swipe(screen_center_x,
                     screen_center_y - recycler_view_height * 6 / 15,
                     screen_center_x,
                     screen_center_y + recycler_view_height * 6 / 15, 1000)
        time.sleep(2)
        new_first_nlp = driver.find_element(by=AppiumBy.ID, value="com.tencent.mobileqq:id/nlp")
        if new_first_nlp == current_first_nlp:
            break
        current_first_nlp = new_first_nlp

    # print(json_chat)
    json.dump(list(reversed(json_chat)), open(f"output_{time.time()}.json", "w", encoding="utf-8"), ensure_ascii=False)


    driver.quit()

if __name__ == '__main__':
    extract_qq_chat()