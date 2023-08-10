import sys, os, json
import random

root_dir = "output_json"
MAX_LENGTH = 512

def pack_output_json(root_dir):
    output = []
    for filename in os.listdir(root_dir):
        if filename.endswith(".json"):
            with open(os.path.join(root_dir, filename), "r", encoding="utf-8") as f:
                l = json.load(f)
                for i in range(len(l)):
                    l[i]["instruction"] = l[i]["instruction"][:MAX_LENGTH]
                    l[i]["input"] = l[i]["input"][:MAX_LENGTH]
                    l[i]["output"] = l[i]["output"][:MAX_LENGTH]
                output += l
    # Shuffle output and divide into 0.8-0.2
    random.shuffle(output)
    train_output = output[:int(len(output) * 0.8)]
    test_output = output[int(len(output) * 0.8):]
    print("Train:", len(train_output), "Test:", len(test_output))
    with open("train.jsonl", "w", encoding="utf-8") as f:
        json.dump(train_output, f, indent=4, ensure_ascii=False)
    with open("dev.jsonl", "w", encoding="utf-8") as f:
        json.dump(test_output, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    pack_output_json(root_dir)