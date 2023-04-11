import pyautogui
import time


def dougie_dance():
    for _ in range(3):
        pyautogui.moveRel(50, 0, duration=0.5)
        pyautogui.moveRel(-50, 0, duration=0.5)
    pyautogui.moveRel(0, 50, duration=0.5)
    pyautogui.moveRel(0, -50, duration=0.5)


dougie_dance()