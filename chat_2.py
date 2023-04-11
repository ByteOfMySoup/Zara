import os
import openai
import pickle
import subprocess


# Holds the conversation history
class Messages:
    def __init__(self):
        with open("guide.txt", "r") as guide:
            self.data = [{"role": "system", "content": guide.read()}]

    def insert(self, role, content):
        self.data.append({"role": role, "content": content})

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


# Retrieve OpenAI API response
def get_response(m):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=m.all()
    )
    return response.choices[0].message


# Manage the commands received
def run_command(content, messages):
    if content.startswith("|sys|"):
        cmd = content.replace("|sys|", "")
        if "start " not in cmd:
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            return p.stdout.read().decode()
        else:
            try:
                os.system(cmd)
            except Exception as e:
                return str(e)
            return "0"

    elif content.startswith("|save|"):
        messages.save()
        return "Messages successfully saved."

    elif content.startswith("|load|"):
        messages.load()
        return "Messages successfully loaded."

    elif content.startswith("|exec|"):
        try:
            exec(content.replace("|exec|", ""))
        except Exception as e:
            return f"Python: {str(e)}"
        return ""

    elif content.startswith("|write|"):
        bundle = content.replace("|write|", "").split("|fn|")
        to_write = bundle[0]
        filename = bundle[1]
        with open(filename, "w") as file:
            file.write(to_write)
        return ""

    elif content.startswith("|retrieve|"):
        return load_logic_and_gui_scripts()

    return None


# Load the logic and the GUI Python scripts
def load_logic_and_gui_scripts():
    scripts = ""
    with open("chat_2.py", "r") as file:
        scripts += "Logic Script:\n" + file.read() + "\n"
    with open("app_og.py", "r") as file:
        scripts += "GUI Script:\n" + file.read()
    return scripts


# Check if the message received is a command
def is_command(message):
    return message.startswith("|")


# The main chat loop for command line interface
def message_loop():
    openai.api_key = retrieve_key()
    messages = Messages()
    print(messages.latest()["content"])

    while True:
        messages.insert("user", input("user: "))
        ai_message = get_response(messages)

        if is_command(ai_message.content):
            result = run_command(ai_message.content, messages)
            if result:
                ai_message.content = result

        messages.insert(ai_message.role, ai_message.content)
        print(f"{ai_message.role}: {ai_message.content}")


# Retrieve OpenAI API key
def retrieve_key():
    with open("key.txt", "r") as file:
        return file.read()


if __name__ == "__main__":
    message_loop()