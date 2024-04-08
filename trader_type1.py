import pyautogui
import keyboard
import pyperclip
from time import sleep
from keyboard import press_and_release
import cv2
import numpy as np
import pytesseract
import json
import os
from pytesseract import Output
from datetime import datetime
import multiprocessing

# Установка пути к исполняемому файлу Tesseract (если необходимо)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def write_to_json(data):
    try:
        filename = os.path.join(os.path.dirname(__file__), "history.json")
        purchase_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "item": data["item"],
            "price": data["price"],
        }
        with open(
            filename, "a", encoding="utf-8"
        ) as json_file:  # Используем режим добавления 'a'
            json_file.write(json.dumps(purchase_data, indent=4, ensure_ascii=False))
            json_file.write("\n")  # Добавляем новую строку для разделения записей
        return True
    except Exception as e:
        print(f"Произошла ошибка при записи в JSON файл: {e}")
        return False


def wait_key(queue):
    print("Процесс 1 ожидает нажатия кнопки 'q'...")
    keyboard.wait("q")
    print("Процесс 1 передает команду второму процессу...")
    queue.put("break")


def recognize_digits(left, top, width, height, product_name, product_price, queue):
    try:
        keyboard.wait("enter")
        keyboard.release("enter")  # Освобождаем клавишу Enter после ее нажатия
        while True:
            # Считывание изображения с монитора в указанной области
            sleep(2)
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            inverted_frame = cv2.bitwise_not(frame)
            # Преобразование изображения в оттенки серого
            gray = cv2.cvtColor(inverted_frame, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enchanced_gray = clahe.apply(gray)

            # Применение порогового фильтра для улучшения распознавания
            _, thresh = cv2.threshold(
                enchanced_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )
            cv2.imwrite("adfsf.png", thresh)
            # Применение распознавания текста с помощью Tesseract
            data = pytesseract.image_to_data(thresh, output_type=Output.DICT)

            # Создаем список индексов пустых элементов в 'text'
            empty_indices = [i for i, text in enumerate(data["text"]) if text == ""]
            letter_indices = [
                i
                for i, text in enumerate(data["text"])
                if any(c.isalpha() for c in text)
            ]

            # Удаляем пустые элементы в 'text'
            data["text"] = [text for text in data["text"] if text != ""]

            # Удаляем элементы, содержащие буквы, из 'text'
            data["text"] = [
                text for text in data["text"] if not any(c.isalpha() for c in text)
            ]

            # Удаляем соответствующие элементы из других ключей
            for key in data.keys():
                if key != "text":
                    data[key] = [
                        value
                        for i, value in enumerate(data[key])
                        if i not in empty_indices and i not in letter_indices
                    ]

            merged_data = {"text": [], "left": [], "top": [], "width": [], "height": []}

            i = 0
            while i < len(data["text"]):
                # Если следующий элемент имеет тот же top
                if (
                    i + 1 < len(data["text"])
                    and abs(data["top"][i] - data["top"][i + 1]) <= 1
                ):
                    # Объединяем text
                    merged_data["text"].append(
                        data["text"][i] + "" + data["text"][i + 1]
                    )
                    # Берем данные от второго элемента
                    merged_data["left"].append(data["left"][i + 1])
                    merged_data["top"].append(data["top"][i + 1])
                    merged_data["width"].append(data["width"][i + 1])
                    merged_data["height"].append(data["height"][i + 1])
                    # Пропускаем следующий элемент
                    i += 2
                else:
                    # В противном случае, просто копируем элемент
                    merged_data["text"].append(data["text"][i])
                    merged_data["left"].append(data["left"][i])
                    merged_data["top"].append(data["top"][i])
                    merged_data["width"].append(data["width"][i])
                    merged_data["height"].append(data["height"][i])
                    i += 1

            # for i in range(len(merged_data["text"])):
            #     if data["text"][i]:  # Пороговое значение уверенности можно изменить
            #         # Выведите текст и его координаты
            #         print(
            #             f"Текст: {merged_data['text'][i]}, Координаты: left {merged_data['left'][i]}, top {merged_data['top'][i]}, width {merged_data['width'][i]}, height {merged_data['height'][i]}"
            #         )

            for i, text in enumerate(merged_data["text"]):
                if text.isdigit():  # Проверяем, является ли текст числом
                    number = int(text)
                    if number <= product_price and number > 1000:
                        print(">price", number)
                        pyautogui.moveTo(
                            x=left + merged_data["left"][i],
                            y=top + merged_data["top"][i],
                            duration=0.01,
                        )
                        pyautogui.click(
                            x=left + merged_data["left"][i],
                            y=top + merged_data["top"][i],
                        )
                        pyautogui.moveTo(
                            x=left + merged_data["left"][i] + 50,
                            y=top + merged_data["top"][i] + 50,
                            duration=0.01,
                        )
                        pyautogui.click(
                            x=left + merged_data["left"][i] + 50,
                            y=top + merged_data["top"][i] + 50,
                        )
                        pyautogui.moveTo(x=1260, y=760, duration=0.15)
                        pyautogui.click(x=1260, y=760)
                        write_to_json({"item": product_name, "price": number})
                        break

                    else:
                        print("Recognized digits:", number)
                else:
                    print("Not a number:", text)
            pyautogui.click(x=1800, y=450, duration=0.15)

            if not queue.empty():
                command = queue.get()
                if command == "break":
                    break

            cv2.imshow("Digit Recognition", frame)

        cv2.destroyAllWindows()

    except Exception as e:
        next
        print("An error occurred in recognize_digits:", e)


# Задержка перед выполнением следующего действия (в секундах)
DELAY = 0.3

# Стек строк
stack = ["Квант"]


def paste(text: str):
    pyperclip.copy(text)
    press_and_release("ctrl + v")


# Функция для вставки строки и ожидания нажатия кнопкиКвантКвантКвант
# def insert_and_wait(string):
#     try:
#         # pyautogui.moveTo(x=1860, y=1020, duration=DELAY)
#         # for a in range(26):
#         #     pyautogui.click(x=1860, y=1020)

#         # pyautogui.moveTo(x=1700, y=450, duration=DELAY)
#         # pyautogui.click(x=1700, y=450)
#         # # Вставить строку
#         # paste(string)
#         # pyautogui.moveTo(x=1800, y=450, duration=DELAY)
#         # pyautogui.click(x=1800, y=450)

#         # pyautogui.moveTo(x=1800, y=500, duration=DELAY)
#         # pyautogui.click(x=1800, y=500)

#         # pyautogui.moveTo(x=1800, y=500, duration=DELAY)
#         # pyautogui.click(x=1800, y=500)

#         # pyautogui.moveTo(x=1860, y=500, duration=DELAY)
#         # pyautogui.moveTo(x=1800, y=550, duration=DELAY)
#         # pyautogui.scroll(-1)
#         # pyautogui.mouseDown()
#         # pyautogui.moveRel(0, 20, duration=DELAY)
#         # pyautogui.mouseUp()
#         # pyautogui.moveTo(x=1800, y=550, duration=DELAY)
#         # queue = multiprocessing.Queue()
#         # p1 = multiprocessing.Process(target=wait_key, args=(queue,))
#         # p2 = multiprocessing.Process(
#         #     target=recognize_digits,
#         #     args=(left, top, width, height, productName, productPrice, queue),
#         # )
#         # p1.start()
#         # p2.start()
#         # p1.join()
#         # p2.join()
#         # recognize_digits(left, top, width, height, productName, productPrice)

#     except Exception as e:
#         print("An error occurred in insert_and_wait:", e)
#         return


# Главная функция
def main(productName, productPrice):
    try:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_directory, "ar_data.json")

        try:
            with open(file_path, "r") as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            print("Error: JSON file not found.")

        # Пример использования
        left = data["x"]  # Левая координата области
        top = data["y"]  # Верхняя координата области
        width = data["width"]  # Ширина области
        height = data["height"]  # Высота области
        productName = "Бета"
        productPrice = 200000
        queue = multiprocessing.Queue()
        p1 = multiprocessing.Process(target=wait_key, args=(queue,))
        p2 = multiprocessing.Process(
            target=recognize_digits,
            args=(left, top, width, height, productName, productPrice, queue),
        )
        p1.start()
        p2.start()
        p1.join()
        p2.join()

        # while True:
        #     keyboard.wait("enter")
        #     keyboard.release("enter")  # Освобождаем клавишу Enter после ее нажатия

        #     string = stack[
        #         index % len(stack)
        #     ]  # Получаем текущую строку, зацикливая индекс, если стек закончился
        #     insert_and_wait(productName)

        #     index += 1  # Увеличиваем индекс для следующей строки

        #     if keyboard.is_pressed("q"):
        #         break  # Завершаем выполнение программы, если нажата клавиша 'q'

    except Exception as e:
        print("An error occurred in main:", e)
        return
