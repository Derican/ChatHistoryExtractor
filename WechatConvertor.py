import json, sys, os, re, cleantext, time
from wechat_emoji_config import WECHAT_EMOJI

root_path = r"C:\Users\Derican\Documents\WechatExported0809\隔壁班的江建岳"

def replace(matched):
    h_s = matched.group(1)
    h_i = int(h_s, base=16)
    return chr(h_i)

def uni_to_cn(s: str):
    result = re.sub(r"\\u([0-9a-fA-F]{4})", replace, s)
    return result

def process_chat_list(chat_list):
    # Remove None and Empty
    chat_list = [chat for chat in chat_list if chat[1] is not None and len(chat[1]) > 0]

    state = 0
    cached_instruction = []
    cached_output = []
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
                        "instruction": '\n'.join(reversed(cached_instruction[:3])),
                        "input": "",
                        "output": '\n'.join(reversed(cached_output))
                    })

                cached_instruction = []
                cached_output = []
                cached_output.append(chat[1])
                state = 0
    if len(cached_instruction) > 0 and len(cached_output) > 0:
        json_output.append({
            "instruction": '\n'.join(reversed(cached_instruction[:3])),
            "input": "",
            "output": '\n'.join(reversed(cached_output))
        })
    return json_output

def convert_wechat_to_json(wechat_path):
    output = []
    for filename in os.listdir(wechat_path):
        if filename.endswith(".txt"):
            with open(os.path.join(wechat_path, filename), "r", encoding="utf-8") as f:
                lines = f.readlines()
                title_line = lines[0]
                # Extract title like "10.19-20类脑大赛决赛志愿者 - 微信聊天记录"
                title = title_line.split(" - ")[0]
                print("Processing", title)
                lines = lines[2:]
                # Extract pattern lines like "R (2020-03-08 19:02:13):来了"
                pattern = re.compile(r"(.+?) \(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\):(.+)")
                instructions_output = []
                for line in lines:
                    match = pattern.match(line)
                    if match:
                        name, content = match.groups()
                        content = cleantext.clean(content, to_ascii=False, lower=False, no_emoji=True)
                        # Remove "[图片]", "[表情]", "[文件: ]", "[语音 1]"
                        content = re.sub(r"\[.+?\]", "", content)
                        # Remove \ue[0-9a-f]{3}
                        content = re.sub(r"\\ue[0-9a-f]{3}", "", content.encode("unicode_escape").decode("utf-8"))
                        # Replace \u[0-9a-f]{4} to unicode
                        content = uni_to_cn(content)
                        instructions_output.append(
                            (
                            'output' if name == '隔壁班的江建岳' else 'instruction',
                            content
                            )
                        )
                json_output = process_chat_list(instructions_output)
                output += json_output
    with open(f"output_{time.time()}.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    convert_wechat_to_json(root_path)
