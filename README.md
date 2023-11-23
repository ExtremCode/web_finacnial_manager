# web_finacnial_manager
Описание: небольшое веб-приложение, которое может сохранять Ваши денежные операции с целью самостоятельного их анализа.
### Инструкция по запуску:
  #### - необходимо иметь развернутю базу данных PostgreSQL 15; 
  #### - изменить в файлах init_db, tests, repository переменные login и pswd на имя пользователя БД и пароль соответственно; 
  #### - перейти в директорию ./backend;
  #### - запустить сервер приложения командой: waitress-serve --listen=127.0.0.1:5000 app:app ; 
  #### - перейдя по локальному адресу, наслаждаться работой веб-приложения.
После запуска, программа сама создаст схему базы данных, наполнит необходимыми таблицами с помощью миграций.
