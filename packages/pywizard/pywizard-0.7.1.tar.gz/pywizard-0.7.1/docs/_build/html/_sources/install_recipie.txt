

To set property::

    pywizard set foo 123
    pywizard list
    pywizard rm 132

To add magic book::

    pywizard book-list
    > default

    pwyizard use mysql


    pywizard book mysql /some/path

    pywizard book-create other github://ribozz:somth@boo/some/book.index
    pywizard book-create mysql

    pywizard book-add-spell mysql db-create github://ribozz:somth@boo/some/book.py
    pywizard book-list-spells mysql
    pywizard book-remove-spell mysql

    > mysql
      * create-db
      * drop-db
    pywizard spell-list mysql
    pywizard magic mysql root 123123 | pywizard --apply




pywizard account-list

[]

pywizard add-account --type mysql --user admin

pywizard account-list --type mysql
pywizard account-update admin
pywizard account-remove admin

pywizard account-set-default --type mysql --user admin



pywizard book-install mysql


