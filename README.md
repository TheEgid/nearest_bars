# nearest_bars

Проект предназначен для отображения на html-карте ближайших 5 (пяти) баров/питейных заведений.
Для работы требуется база данных баров Москвы.
На вход подается адрес, ближайшие бары к которому будут подписанными маркерами отмечены на карте.

### Как установить

Скачиваем файлы и переходим в папку nearest_bars. Сюда же сохраняем json файл с базой данных баров Москвы - [скачать тут](https://drive.google.com/open?id=1Fc9d8qsyoUsE7UaHczpxLdGNmiS3If8z)

Python 3.7 должен быть уже установлен. Затем используйте pip (или pip3, если есть конфликт с Python2) для установки зависимостей:

```
pip install -r requirements.txt
```

### Использование

Переходим в каталог с программой. Используя консольный ввод, аргументом передаем адрес. Программа будет выводить в консоль лог своей работы.
Результатом работы будет запущенный веб-сервер Flask и выведенная в консоли html ссылка на сгенерированную карту с адресом и отметками 5 ближайших баров.

```
python3 main.py Москва Кленовый бульвар 9
```

### Тестовый режим

В работе программы в целях отладки и ускорения работы используется временный файл .json. По умолчанию он очищается. 
Если требуется протестировать программу для проверки работы с одинаковым адресом, то первым аргументом 
передаем этот адрес, а дополнительным вторым аргументом после пробела передаем ключ **--test**.

```
python3 main.py Москва Кленовый бульвар 9 --test
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).


