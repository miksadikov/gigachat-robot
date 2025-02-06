import vosk, queue, json
import sounddevice as sd
import time
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

keyword_vars = ['привет робот', 'привет', 'робот']
command_vars = ['найди', 'комнате', 'подъедь']
auto_define_dev_id = 1

gigachat_creds = ''

payload = Chat(
    messages=[
        Messages(
            role=MessagesRole.SYSTEM,
            content="Ты ассистент робота, который помогает ему выполнять команды человека."
        )
    ],
    temperature=0.7,
    max_tokens=500,
)

q = queue.Queue()
devices = sd.query_devices()

## Define device id
if auto_define_dev_id:
    for id in str(devices).split("\n"):
        if "ReSpeaker 4 Mic Array" in id:
            dev_id = int(id.split()[1])
            break
else:
    print("Select device id: \n", devices)
    dev_id = 0 # default

    try:
        dev_id = int(input())
    except ValueError:
        print("Using default value: 0")

samplerate = int(sd.query_devices(dev_id, 'input')['default_samplerate'])

giga = GigaChat(credentials=gigachat_creds, verify_ssl_certs=False, model="GigaChat-Pro")

prompt = "Привет. Ты ведь знаешь, что сейчас в робототехнике начинают активно применяться большие языковые модели. Я хочу, чтобы ты помог мне управлять роботом. Робот понимает только простые команды типа go, stop, rotate_left и rotate_right, о которых я тебе расскажу, а я буду отдавать команды роботу на обычном естественном языке: 'найди предмет', 'подъедь к предмету'. Итак, робот понимает только простые команды (функции) вида go(centimeters), stop(), rotate_left() и rotate_right(). Данные функции содержатся в модуле robot.py, ты должен использовать этот модуль в своей функции по управлению роботом (импортируй этот модуль robot.py). Кроме этого ты должен импортировать модуль image_processing.py и использовать следующие функции из этого модуля: capture() - снимает фото и возвращает его, object_detection(image, object_class_name) - принимает на вход изображение, которое вернула функция capture() (изображение в списке параметров идет первым) и название класса объекта (object_class_name), который нужно найти, а возвращает две переменных: первая это 'found' типа boolean, принимающую значение = True, если объект найден или False если не найден, а вторая - это 'image', если объект найден на изображении, то возвращается это изображение, на котором объект обведен зеленой рамкой, если объект не найден на изображении, то возвращается это изображение без всяких рамок. find_green_bbox_width(image) - принимает на вход изображение, на котором искомый объект обведен зеленой рамкой, а возвращает tuple из трех значений: первые два - это координаты x и y центра искомого объекта, а третья - ширина в пикселях этой зеленой рамки. Тебе нужно развернуть робота так, чтобы он был нацелен на центр искомого объекта. Для этого у тебя в модуле image_processing.py есть функция object_center_offset(x), которая вычисляет текущее смещение центра объекта от цетра изображения, для этого функция object_center_offset(x) принимает на вход координату x центра искомого объекта, данную координату возвращает функция find_green_bbox_width(image). Итак, если функция object_center_offset(x) вернула False, то робот пока на направлен на центр искомого объекта и робота нужно еще немного повернуть с помощью функции rotate_left(). Если функция object_center_offset(x) вернула True, то вызывай функцию, вычисляющую расстояние до объекта - get_object_distance(object_class_name, object_width_px), она принимает на вход имя класса объекта и полученную от функции find_green_bbox_width() ширину объекта (его зеленой рамки) в пикселях, а возвращает расстояние до этого объекта в сантиметрах (centimeters). Помни, что функция find_green_bbox_width() возвращает tuple из трех значений, в функции get_object_distance() нужно использовать только третье значение из этого tuple! После этого нужно дать команду роботу подъехать к данному объекту: go(centimeters). Если объект не найден на изображении, то мы должны немного повернуть робота с помощью функции rotate_left(). Перед тем как повернуть робота делай паузу в 2 секунды! Для этого импортируй модуль time (import time) и вызови функцию time.sleep(2). После того как робот немного повернулся, мы снова снимаем фото и весь цикл снова повторяется. Таким образом функция, которую я прошу тебя написать, должна работать в цикле и искать нужный объект! Выходим из цикла, только если объект найден! Теперь представь, что робот находится в комнате, а в определенном месте этой комнаты находится интересующий меня объект - например стул, холодильник, телевизор и так далее, назовем его просто объектом. Допустим, что я даю команду роботу: 'найди стул в комнате и подъедь к нему' или 'найди холодильник в комнате и подъедь к нему'. Напиши пожалуйста функцию move_to_object() на языке Python, которая с помощью перечисленных выше функций (go, rotate_left, rotate_right, stop, capture, object_detection, find_green_bbox_width, get_object_distance) позволит роботу выполнить мою команду. Функция move_to_object() не принимает на вход параметры и ничего не возвращает. Важно: выводи только код на Python, никаких пояснений после кода не нужно! Написанную тобой функцию я сразу буду использовать в своей программе, поэтому в твоем выводе не должно быть никакого лишнего текста, а только код на Python! Класс (тип) объекта, который наш робот будет искать, ты должен определить из моей команды. Команда всегда выглядит примерно так: 'найди стул в комнате и подъедь к нему' или 'найди холодильник в комнате и подъедь к нему', т.е после слова 'найди' всегда следует название класса объекта: например 'стул', 'холодильник' или какой-либо другой объект. Ты должен перевести название искомого объекта из моей команды на английский язык и использовать внутри функции move_to_object() в функции object_detection(image, object_class_name). После того, как я произнесу команду, ты должен написать мне функцию move_to_object(), о которой я говорил тебе выше. Переменной с именем класса объекта присваивай название объекта из команды! Не нужно писать вот так: object_class_name = 'chair' if 'стул' in command else 'refrigerator' if 'холодильник' in command else None'. Пиши так: object_class_name = 'chair' (если в команде было сказано про стул) или так object_class_name = 'refrigerator' (если в команде было сказано про холодильник) и так далее. Тебе ничего не известнно про переменную command! Ты не должен использовать переменную command! Забудь переменную command! В функции move_to_object() ты сразу присваиваешь переменной object_class_name название объекта, который я назвал в своей команде! И еще: пиши мне только код функции move_to_object(), не нужно писать пример её использования и не нужно вызывать её! Мне нужен только код этой функции move_to_object()! Твоя ошибка в том, что в конце функции move_to_object() ты пишешь пример её выполнения! Повторяю, не нужно самим вызывать эту функцию и не нужно писать в конце пример её выполнения - это очень важно, запомни! Жди от меня команды! "


model = vosk.Model(r"/path/to/vosk-model-ru")
chat = False
command = ''

with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=dev_id, dtype='int16', \
                            channels=1, callback=(lambda i, f, t, s: q.put(bytes(i)))):
    rec = vosk.KaldiRecognizer(model, samplerate)

    while True:
        # Получаем информацию с микрофона
        data = q.get()
        if rec.AcceptWaveform(data):
            # Если речь была распознана, записываем ее в переменную data
            data = json.loads(rec.Result())["text"]
            # Выводим то, что было распознано (пустую строку, если ничего не распознано):
            print("Recognized: " + data)
            if chat == False:
                if any(keyword in data for keyword in keyword_vars):
                    chat = True
            else:
                if any(keyword in data for keyword in command_vars):
                    command = "Твоя команда: " + data + " - выполняй её!"
                    print(command)
                    break

message = prompt + command
response = giga.chat(message)
response = response.choices[0].message.content
response = response.replace('```python', '')
response = response.replace('```', '')

print(response)

f = open("robot_script.py", "w+")
f.write(response)
f.close()

f = open("robot_script.py", "r+")
lines = f.readlines()
f.close()
f = open("robot_script.py", 'w')
for line in lines[:-1]:
    f.writelines(line)
f.close()

import robot_script

robot_script.move_to_object()
