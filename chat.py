import os
import openai
import pickle
import subprocess
import pyautogui
import keyboard
import web


# message = {"role": "role",
#            "content": "content"}
class Messages:
    def __init__(self):
        with open("guide.txt", "r") as guide:
            self.data = [{"role": "system", "content": guide.read()}]

    def insert(self, role, content):
        self.data.append({"role": role,
                          "content": content})

    def latest(self):
        tar = len(self.data) - 1
        return self.data[tar]

    def all(self):
        return self.data

    def save(self):
        with open("messages.list", "wb") as file:
            pickle.dump(self.data, file)

    def load(self):
        with open("messages.list", "rb") as file:
            self.data = pickle.load(file)

    def clear(self):
        with open("guide.txt", "r") as guide:
            self.data = [{"role": "system", "content": guide.read()}]

    def remove(self, content):
        removed = None
        for message in self.data:
            if content.replace("user: ", "") in message["content"]:
                index = self.data.index(message)
                removed = self.data.pop(index)

        return removed

    def filter(self, size):
        for message in self.data:
            if len(message["content"]) > size:
                l = len(message["content"])
                message["content"] = f"Message removed due to length: {l}. Original sender: {message['role']}"
                message["role"] = "system"


def get_response(m, model, streaming=False):
    if not streaming:
        r = openai.ChatCompletion.create(
            model=model,  # gpt-3.5-turbo gpt-4
            messages=m.all()
        )
    else:
        stream = openai.ChatCompletion.create(
            model=model,  # gpt-3.5-turbo gpt-4
            messages=m.all(),
            stream=True
        )
        r = next(stream)
    return r


def print_message(message):
    print(f"{message['role']}: {message['content']}")


def decompile_message(message):
    return message["role"], message["content"]


def is_command(content):
    lines = content.split("\n")
    print(lines)
    for line in lines:
        if line.startswith("|"):
            return True
    return False


def run(content, messages):
    lines = content.split("\n")
    to_run = content
    for line in lines:
        if line.startswith("|"):
            to_run = line
    if to_run.startswith("|sys|"):
        cmd = to_run.replace("|sys|", "")
        if "start " not in cmd:
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            return p.stdout.read().decode('utf-8', errors='ignore')
        else:
            try:
                os.system(cmd)
            except Exception as e:
                return e
            return 0
    elif to_run.startswith("|save|"):
        messages.save()
        messages.insert("system", "Messages successfully saved.")
        print_message(messages.latest())
    elif to_run.startswith("|load|"):
        messages.load()
        messages.insert("system", "Messages successfully loaded.")
        print_message(messages.latest())
    elif to_run.startswith("|exec|"):
        try:
            exec(to_run.replace("|exec|", ""))
        except Exception as e:
            messages.insert("system", f"python: {e}")
        print_message(messages.latest())
    elif to_run.startswith("|write|"):
        parts = content.split("|write|")
        bundle = parts[1].split("|fn|")
        print(parts)
        print(bundle)
        to_write = bundle[0]
        filename = bundle[1]
        with open(filename, "w") as file:
            file.write(to_write.replace(r"\n", "\n"))
    elif to_run.startswith("|retrieve|"):
        to_return = ""
        with open("chat.py", "r") as file:
            to_return += "Logic Script:\n" + file.read() + "\n"
        with open("app.py", "r") as file:
            to_return += "GUI Script:\n" + file.read()

        return to_return
    elif to_run.startswith("|search|"):
        query = to_run.replace("|search|", "")
        results = web.search_web(query)

        return results


def message_loop():
    openai.api_key = retrieve_key()
    messages = Messages()
    print_message(messages.latest())
    while True:
        messages.insert("user", input("user: "))
        response = get_response(messages, "gpt-4")
        messages.insert(response["choices"][0]["message"]["role"], response["choices"][0]["message"]["content"])
        content = messages.latest()["content"]
        if is_command(content):
            stdout = run(content, messages)
            if stdout is not None and len(stdout) > 0:
                print(f"CMD: {stdout}")
        print_message(messages.latest())


def retrieve_key():
    with open("key.txt", "r") as file:
        return file.read()


if __name__ == "__main__":
    message_loop()
