# Проект YaTube
Проект доступен по адресу http://tetrapack55.pythonanywhere.com/
YaTube - платформа для публикации микроблогов. Проект создан на основе MVT-архитектуры. Пользователи могут создавать учетную запись, публиковать сообщения, подписываться на любимых авторов, оставлять комментарии.
Проект покрыт тестами (unit-testing)

### Технологии, использованные при разработке
[![Python](https://img.shields.io/badge/Python-3776AB?style=plastic&logo=python&logoColor=092E20&labelColor=white
)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-092E20?style=plastic&logo=django&logoColor=092E20&labelColor=white
)](https://www.djangoproject.com/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=plastic&logo=sqlite&logoColor=003B57&labelColor=white
)](https://www3.sqlite.org/index.html)
[![HTML5](https://img.shields.io/badge/HTML-E34F26?style=plastic&logo=html5&logoColor=E34F26&labelColor=white
)](https://html.com/html5/)
[![CSS](https://img.shields.io/badge/CSS-1572B6?style=plastic&logo=css3&logoColor=1572B6&labelColor=white
)](https://www.w3.org/Style/CSS/Overview.en.html)

### Запуск проекта
1) Клонируйте репозиторий на свой компьютер и перейдите в него в командной строке
```
git clone git@github.com:tetrapack55/YaTube_project.git
cd YaTube_project
```
2) Создайте и активируйте виртуальное окружение
```
python -m venv venv
source venv/Scripts/activate
```
3) Установите зависимости из файла requirements.txt
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
4) Выполните миграции
```
python manage.py migrate
```
5) Создайте суперпользователя
```
python manage.py createsuperuser
```
6) Запустите проект
```
python manage.py runserver
```