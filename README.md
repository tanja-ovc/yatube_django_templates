# Yatube
## Социальная сеть/блог/онлайн-дневник

Социальная сеть "Yatube" даёт пользователям возможность публиковать записи в свой блог, подписываться на любимых авторов и добавлять понравившиеся записи в избранное.

### Технологии

Проект написан на Python3.7 и фреймворке Django с использованием HTML-шаблонов.

### Как запустить проект локально

Клонируйте репозиторий:

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

```python3 manage.py migrate```

Запустить проект:

```python3 manage.py runserver```


### Авторство

Автор: Татьяна Овчинникова

Тесты в корне проекта (_yatube_django_templates/tests/_) написаны командой Яндекс.Практикума.
