# Проект: Foodgram

«Фудграм» — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.

## Функционал и возможности проекта:

1. Авторизация пользователей с использованием Djoser;
2. Подписки на других пользователей;
3. Создание и редактирование рецептов с изображениями;
4. К рецептам добавлять теги и ингредиенты (обязательно);
5. Добавлять рецепты в избранное или список покупок;
6. Выгрузка списка покупок в текстовый файл;
7. Просмотр рецептов других пользователей.

## Технические характеристики проекта:

1. Web-server: nginx 1.27.3;
2. Database: postgres 13;
3. Authorization: djoser;
4. Code: Python3.10
5. ORM: Django 5.1
6. API: DRF 3.15

## Данные для тестирования:

*http://tdeveloper.ru/* - Веб-сервер с полным функционалом  
*http://tdeveloper.ru/admin/* - Административная панель

<details>
<summary> <b>Учетная запись администратора:</b> </summary>
  username: test_admin   
  password: Qq123456
</details>

## Примеры запросов к API:

1. **Основные эндпоинты API.**

*http://tdeveloper.ru/api/users/* - POST - регистрация пользователя, GET - просмотр пользователей;

*http://tdeveloper.ru/api/tags/* - GET - просмотр тегов;

*http://tdeveloper.ru/api/ingredients/* - GET - просмотр ингредиентов;

*http://tdeveloper.ru/api/recipes/* - GET/POST - просмотр/добавление рецептов;

*http://tdeveloper.ru/api/recipes/{recipes_id}/shopping_cart/* - POST - добавление в список покупок;

*http://tdeveloper.ru/api/recipes/{recipes_id}/favorite/* - POST - добавление в избранное;

*http://tdeveloper.ru/api/users/{user_id}/subscriptions/* - POST/DELETE - создание/удаление подписки на пользователя;

2. **Регистрация и получение токена.**
Эндпоинт: */api/users/* принимает запросы GET и POST.
POST - Регистрация пользователя для регистрации:
*http://tdeveloper.ru/api/v1/users/* 
```json
{
    "email": "string",
    "username": "string",
    "first_name": "string (not required)",
    "last_name": "string (not required)",
    "password": "string (not required)",
}
```
POST - Получить токен указав почту и пароль:
*http://tdeveloper.ru/api/auth/token/login/* -
```json
{
    "email": "string",
    "password": "string"
}
```
Полученный токен необходимо использовать для любых операций к API, кроме GET.
