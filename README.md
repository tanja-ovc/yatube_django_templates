# Yatube
## Социальная сеть/блог/онлайн-дневник

Социальная сеть "Yatube" даёт пользователям возможность публиковать записи в свой блог, подписываться на любимых авторов и добавлять понравившиеся записи в избранное.

### Технологии

Проект написан на Python3.7 и фреймворке Django с использованием HTML-шаблонов.

### Как выглядит сайт

<img width="1139" alt="Screenshot 2023-10-06 at 22 53 39" src="https://github.com/tanja-ovc/yatube_django_templates/assets/85249138/b3b183ad-d813-4c4d-902a-3ec0620886fd">

<img width="1140" alt="Screenshot 2023-10-06 at 22 54 52" src="https://github.com/tanja-ovc/yatube_django_templates/assets/85249138/1fd2a512-0967-4fb4-8bea-f39f2f7cce73">

### Как запустить проект локально

Клонируйте репозиторий:

```git@github.com:tanja-ovc/yatube_django_templates.git```

либо

```git clone https://github.com/tanja-ovc/yatube_django_templates.git```

Убедитесь, что находитесь в директории _yatube_django_templates/_ либо перейдите в неё:

```cd yatube_django_templates/```

Cоздайте виртуальное окружение:

```python3 -m venv venv```

Активируйте виртуальное окружение:

* Для Linux/Mac:
 
    ```source venv/bin/activate```

* Для Windows:

    ```source venv/Scripts/activate```

При необходимости обновите pip:

```pip install --upgrade pip```

Установите зависимости из файла requirements.txt:

```pip install -r requirements.txt```

Примените миграции:

```cd yatube/```

```python3 manage.py migrate```

Запустите проект:

```python3 manage.py runserver```

### Авторство

Автор: Татьяна Овчинникова

Тесты в корне проекта (_yatube_django_templates/tests/_) написаны командой Яндекс.Практикума.
