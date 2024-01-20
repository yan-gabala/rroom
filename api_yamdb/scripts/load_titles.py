"""
При разворачивании проекта из "коробки" не требуется выполнение пунктов 1 и 2.

1) pip install django-extensions;

2) Добавьте строку 'django_extensions'в список INSTALLED_APPS в settings.py;

3) python manage.py migrate - для создания таблиц в базе данных;

4) python manage.py check - найдите ошибки и, при необходимости, исправьте их;

5) python manage.py runscript load_titles - eсли все пойдет хорошо, вы увидите
импортированные строки, напечатанные в консоли;

6) python manage.py runserver

7) http://127.0.0.1:8000/api/v1/titles/ - проверьте, как импортированные
произведения теперь отображаются на этой странице.

"""


import csv

from reviews.models import Categories, Genres, Title, TitleGenres


def run():
    with open('static/data/category.csv') as file:
        reader = csv.reader(file)
        next(reader)

        Categories.objects.all().delete()

        for row in reader:
            print(row)

            category = Categories(id=row[0],
                                  name=row[1],
                                  slug=row[2],
                                  )
            category.save()

    with open('static/data/genre.csv') as file:
        reader = csv.reader(file)
        next(reader)

        Genres.objects.all().delete()

        for row in reader:
            print(row)

            genre = Genres(id=row[0],
                           name=row[1],
                           slug=row[2],)
            genre.save()

    with open('static/data/titles.csv') as file:
        reader = csv.reader(file)
        next(reader)

        Title.objects.all().delete()

        for row in reader:
            print(row)

            title = Title(id=row[0],
                          name=row[1],
                          year=row[2],)
            title.save()

    with open('static/data/genre_title.csv') as file:
        """id,title_id,genre_id"""
        reader = csv.reader(file)
        next(reader)

        TitleGenres.objects.all().delete()

        for row in reader:
            print(row)

            title_genres = TitleGenres(id=row[0],
                                       title_id=row[1],
                                       genre_id=row[2],)
            title_genres.save()
