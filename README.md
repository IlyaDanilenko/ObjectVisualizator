# Визуализатор Объектов
Визуализатор выполнен на Open Source фреймворке для 3D рендеринга и игр [Panda3D](https://www.panda3d.org/)
## Установка
1. Клонируем репозиторий
```
git clone https://github.com/IlyaDanilenko/KiberdromVisualizator.git
```
2. Устанавливаем необходимые библиотеки Python
```
cd KiberdromVisualizator
pip install -r requirements.txt
```

## Настройка
Все настройки можно найти в `settings/settings.json`

### Описание настроек
#### Блок workspace
* background - цвет фона в формате RGB
* camera - настройка камеры
* camera>position - координаты камеры в формате XYZ
* camera>angle - угол наклона в формате Yaw Pitch Roll
#### Блок polygon
* image_name - путь до изображения полигона
* scale - размеры поля в формате XYZ
#### Блок objects
* path - путь до папки с файлами моделей .egg
* color - цвет объектов в формате RGB
* scale - размеры объектов в формате XYZ
#### Блок server
* ip - IP адресс сокета
* port - порт сокета

## Запуск визуализатора
```
python main.py
```

## Формат принимаемый визуализатором
Визуализатор работает с JSON представлением данных.
На вход визуализатор ожидает список JSON объектов
### Пример передаваемой структуры
```
[
    {
        "id": 0, // уникальный номер, недолжен повторяться
        "type": "type_name", // type_name - совпадает с названием 3D модели
        "position": {
            "x": 0.0, // координата X
            "y": 0.0, // координата Y
            "z": 0.0 // координата Z
        },
        "yaw": 0.0 // угол поворота вдоль оси Z
    }
]
```
:heavy_exclamation_mark: __ВАЖНО__: Объекты должны быть упорядоченны по ID внутри массива, также ID не должны повторяться или прерываться.

## Управление
Для перемещения камеры используются клавишы:
* `W` и `Правая кнопка мыши, курсор вверх` - перемешение вперед по координате Y
* `S` и `Правая кнопка мыши, курсор вниз` - перемещение назад по координате Y
* `A` и `Правая кнопка мыши, курсор вправо` - перемещение вперед по координате X
* `D` и `Правая кнопка мыши, курсор влево` - перемещение назад по координате X
* `Q` и `Зажатое колесико мыши, курсор вверх`- перемещение вперед по координате Z
* `E` и `Зажатое колесико мыши, курсор вниз` - перемещение назад по координате Z
* `UP` и `Левая кнопка мыши, курсор вверх` - повернуть камеру наверх
* `DOWN` и `Левая кнопка мыши, курсор вниз` - повернуть камеру вниз
* `LEFT` и `Левая кнопка мыши, курсор влево` - повернуть камеру налево
* `RIGHT` и `Левая кнопка мыши, курсор вправо` - повернуть камеру направо
* `Escape` - выход из программы

## Выход из программы
:heavy_exclamation_mark: __ВАЖНО__: При выходе может возникнуть ошибка - это нормально

## Прочее
### Пример отправки координат объектов
Пример `test_client.py`. Запуск:
```
python test_client.py
```

### Добавление новых моделей
Все модели храняться в objects. Модели должны быть в .egg формате. В Panda3D встроенны несколько [утилит](https://docs.panda3d.org/1.10/python/tools/model-export/index) конвертации в egg формат. Однако чтобы сконвертировать stl в egg воспользуйтесь [скриптом](http://codepad.org/dlG9cKKQ).

### Изменение изображения полигона
Изображение стандартного полигона хранится в `map\`.

:heavy_exclamation_mark: __ВАЖНО__: Высота и ширина изображения должны быть одинаковыми
