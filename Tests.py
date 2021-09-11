class Tests:
    pages0 = [
        'https://ru.wikipedia.org/wiki/Сергеев,_Александр_Михайлович_(физик)',
        'https://ria.ru/20200802/1575215918.html',
        'https://argumenti-ru.turbopages.org/argumenti.ru/s/society/2020/10/692115',
        'https://tass.ru/info/4594221',
        'http://новости-россии.ru-an.info/новости/президент-ран-сергеев-лжёт-от-страха-и-невежества/',
        'https://newsroom24.ru/news/details/233785/',
        'https://rus.team/people/aleksandr-mikhajlovich-sergeev',
        'http://www.kremlin.ru/catalog/persons/544/events/64103',
        'http://www.kremlin.ru/catalog/persons/544/events/62016',
        'http://www.kremlin.ru/catalog/persons/544/events/59648'
    ]
    pages1 = ['https://ru.wikipedia.org/wiki/Коралловые_рифы']
    pages2 = ['https://aprott.ru/']
    pages3 = []

    def test(func, str):
        if str == 0:
            func(Tests.pages0)
        elif str == 1:
            func(Tests.pages1)
        elif str == 2:
            func(Tests.pages2)
        elif str == 3:
            func(Tests.pages3)

    def run_all(func):
        func(Tests.pages0)
        func(Tests.pages1)
        func(Tests.pages2)
        func(Tests.pages3)
