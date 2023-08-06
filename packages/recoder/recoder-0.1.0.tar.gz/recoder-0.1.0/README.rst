recoder
=======

Установка
---------
::

    $ git clone https://bitbucket.org/dkuryakin/recoder.git
    $ cd recoder && python setup.py install

или
::

    $ pip install recoder

Полезные команды
----------------

Использование как консольная тулза.
::

    $ echo "Îñíîâíàÿ Îëèìïèéñêàÿ äåðåâíÿ â" | python -mrecoder [coding]

По умолчанию, coding=utf-8.

Использование в коде
--------------------

Чаще всего с кракозябрами справится такой базовый пример:

.. code-block:: python

    from recoder.cyrillic import Recoder
    rec = Recoder()
    broken_text = u'Îñíîâíàÿ Îëèìïèéñêàÿ äåðåâíÿ â'
    fixed_text = rec.fix_common(broken_text)
    print fixed_text.encode('utf-8')


Если базовый пример не справился, можно поиграться с настройками:

.. code-block:: python

    from recoder.cyrillic import Recoder
    rec = Recoder(depth=4)
    broken_text = u'...'
    fixed_text = rec.fix(broken_text)  # fix работает дольше и сложнее чем fix_common
    ...


Можно использовать частоупотребимые слова (и, на, к, в, ...) как индикатор успеха перекодировки. Но в этом случае текст починится только если в нём есть эти слова:

.. code-block:: python

    from recoder.cyrillic import Recoder
    rec = Recoder(use_plus_words=True)
    ...


Замечания
---------

В данный момент поддерживается только кириллица.

Расширение
----------

Если хочется расширить библиотеку не только кириллицей, предусмотренна удобная тулза:
::

    $ cat some_learning_text.txt | python -mrecoder.builder [coding]

По-умолчанию, coding=utf-8. На stdin подавать текстовку для обучения. На выходе получится 2 файлика: 3grams.json и plus_words.json. Далее всё делается по аналогии с recoder.cyrillic.

Тесты
-----

Тут всё просто:
::

    $ git clone https://bitbucket.org/dkuryakin/recoder.git
    $ cd recoder && python setup.py test
