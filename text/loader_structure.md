# Структура хранения данных
Как было сказано в введении базы данных бывают разных типов. В нашей конкретной задаче было достаточно обычной реляционной базы данных. Так как объемы информации не настолько большие чтобы выделять под это отдельный сервер и частота запросов невелика, было решено остановиться на базе данных Sqlite.

Загрузка информации происходит в несколько этапов:

1. Собираем список нужных новостных изданий.
1. Запись списка URL в базу данных в таблицу с именем queue колонку url.
1. Дальше в несколько процессов запускается скрипт загрузчика.
1. Загрузчик берет каждую запись из очереди.
1. При помощи API CommonCrawl получает ссылки на архивы для скачивания.
1. Пакетами, которые позволяет хранящий ресурс, данные загружаются в таблицу content.
1. Текст отправляется в колонку raw_cont, а адрес страницы в колонку url

Проиллюстрировать работу программы по загрузке и обработке информации можно следующей диаграммой [Рис. 1]



![Caption](diagrams/Content_filling.png)

                Рис. 1: Иллюстрация работы загрузчика


## Структура таблиц
```SQL 
TABLE queue(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT,
    load_started DEFAULT NULL,
    load_complete DEFAULT NULL
);
TABLE content(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT,
    cont TEXT
);
```

Всего было выгружено 5Гб очищенных данных. Загрузка производилась в несколько процессов. Данные очищались на этапе получения от различных HTML тегов при помощи библиотеки BeautifulSoup и проекта readability в языке программирования Python.

## Математическая модель структуры данных
Основана на реляционной алгебре. Основным элементом являются мультимножества.

1. Отношение $-$ это таблица или ее подмножество.

1. Кортеж $-$ строка в талице.

1. Атрибут $-$ столбец в таблице.

1. Поле $-$ ячейка таблицы определенного типа.

1. Тип ячейки в таблице $-$ некоторое число $a \in \mathbb{N}$, где $\mathbb{N}$ $-$ множество натуральных чисел. 
    
    Соответствие типов:
    1. $t_1$ $-$ целое число
    1. $t_2$ $-$ текст (последовательность символов)
    1. $t_3$ $-$ булево значение (0 $-$ Ложь, 1 $-$ Истина)
    1. $t_4$ $-$ время


1. Множество уникальных элементов $U(name_1(t_1), ..., name_2(t_k))$ $-$ набор уникальных кортежей, где у каждого кортежа есть $k$ атрибутов с именами $name_1,..., name_2$ соответствующими типам $t_1, ..., t_k$. Обозначение выборки определенных кортежей с атрибутами $name_n, ..., name_k$, у некоторых из которых задано целевое значение (например $name_t\in [10,20]$, a $name_s\in \{ \textup{Саша}, \textup{Маша}, \textup{Женя}\}$), будет выглядеть так: $\pi (U(name_n, ..., name_k))_{\sigma(name_t\in [10,20], \quad name_s\in \{ \textup{Саша}, \textup{Маша}, \textup{Женя}\})}$

1. Мультимножество ($M(U(t_1, ..., t_k))$) построенное на множестве уникальных элементов $U(t_1, ..., t_k)$ $-$ это упорядоченная пара $(U, \varphi)$ такая, что
$\varphi: U \rightarrow \mathbb{N}$, где $\mathbb{N}$ $-$ множество натуральных чисел, отображение $\varphi$ : $\forall x \in U$  $\exists y \in \mathbb{N}: \varphi(x) = y$. (дальше множество уникальных элементов будет опускаться)


В нашем случае имеется 3 мультимножества: 
1. $queue(id(t_1), url(t_2), load\texttt{\_}started(t_4), load\texttt{\_}complete(t_4))$ $-$ содержит в себе набор из элементов. Служит для хранения очереди используемых в поиске новостных изданий. Каждый элемент представляет собой кортеж из $4$ полей:
    * $id$ $-$ уникальный номер для каждого элемента
    * $url$ $-$ URL новостного ресурса
    * $load\texttt{\_}started$ $-$ время начала загрузки записей новостного ресурса
    * $load\texttt{\_}complete$ $-$ время окончания загрузки записей новостного ресурса
1. $content(id(t_1), url(t_2), cont(t_2))$ $-$ содержит набор полученных из новостных изданий очищенных текстов новостей, где каждая запись является кортежем из $3$ полей:
    * $id$ $-$ уникальный номер для каждого элемента
    * $url$ $-$ URL новости
    * $cont$ $-$ чистый текст новости содержащийся по этому URL

Алгоритм сбора данных в этой модели будет определяться следующими соотношениями. Операция выбора из таблицы $queue$ записи с $id = 1$ выглядит так $\pi(queue)_{\sigma(id=1)}$. Общее количество элементов в мультимножестве $set$ с атрибутом $id$ можно определить функцией $len: set \rightarrow \mathbb{N}$. Она определяется так $len(set) = \# \{(id\neq NULL) \in set\}$. Первым шагом алгоритма будет выбор следующего новостного ресурса $(current\text{\_}id, current\text{\_}url) = \pi(queue(id, url))_{\sigma(id \in \min\limits_{id}(\pi(queue(id))_{\sigma(load\text{\_}started = NULL)}))}$. По окончании обработки по исходному $id$ будет записана дата окончания обработки новостного ресурса 
$$\pi(queue(load\text{\_}complete))_{\sigma(id = current\text{\_}id)} = current\text{\_}date.$$
Полученный $current\text{\_}url$ же передается при помощи Интернет соединения на специальный интерфейс CommonCrawl, который возвращает последовательность URL для обхода $url_1, url_2, ... url_m$. Для каждого элемента этой последовательности загружаются сжатые архивы, в которых хранятся нужные страницы. В итоге получается последовательность страниц с HTML-тегами $p_1, p_2, ... p_f$. Полученная последовательность отправляется на обработку специальной программе которая отдает пары $(url_1, cont_1), (url_2, cont_2), ..., (url_n, cont_n)$. То есть можно написать отображения 
$$get\text{\_}url(current\text{\_}url) := (url_1, url_2, ..., url_n)$$ 
и 
$$get\text{\_}text(current\text{\_}url) := (cont_1, cont_2, ..., cont_n).$$
Полученные записи заносятся в мультимножество $content$ следующим образом
$$\pi(content(id, url, cont))_{\sigma(id=NULL)} = $$
$$=((last\text{\_}id+1, last\text{\_}id+2, ..., last\text{\_}id+n), get\text{\_}url(current\text{\_}url), get\text{\_}text(current\text{\_}url)),$$
где $last\text{\_}id = len(content)$.


## Замечания о реализации

Скорость работы загрузчика в один процесс составляет около 50 новостей в минуту. Ее можно было повысить до 200 записей в минуту за счет работы 4 fetcher скриптов совместно. Дальнейшее увеличение количества работающих задач не приносило успеха, так как СУБД SQLite не позволяет одновременно писать в таблицу больше чем одному процессу. До 4 включительно так как из-за сетевых задержек это не оказывало влияния и также из-за ограниченности в вычислительных мощностях. Для дальнейшего повышения скорости загрузки, если таковая потребуется, нужно будет перейти на более промышленную базу данных и переписать fetcher на асинхронное выполнение. Были загружены базы данных на 100, 200 тысяч и 1 миллион записей, это соответствует 356 мегабайтам, 1 гигабайту и 5 гигабайтам занятого дискового пространства. При этом из исходной очереди обработки новостных изданий длиной в 200 записей проходилось только 10 для 100 000 записей и примерно столько же для 1 гигабайта. Для базы на 1 000 000 записей было решено обходить по странице с каждого новостного издания, чтобы получать новости с 200 новостных изданий. Сырые тексты, которые загружались с открытых быз данных CommonCrawl, обрабатывались открытым проектом readability, который к сожалению помимо плюсов $-$ очистка текста, убирание рекламы, имел и неприятный минус $-$ пропуск заголовка новости. В новостях по нему обычно можно сделать вывод о большей части содержания статьи, поэтому его исправление желательно в дальнейшей работе.

