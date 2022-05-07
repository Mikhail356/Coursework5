# Введение 
Введение — общее описание проблемной области информационного поиска и поиска имен в частности и формулировка задачи.

В наше время интернет является огромным хранилищем различной информации. Не вся она полезна для конкретных задач. Поэтому люди придумали поисковые системы. Первым этапом в любом поиске является поверхностный сбор информации. Его осуществляют при помощи поисковых пауков [@abukausarWebCrawlerReview2013]. 

Поисковый паук это программа, которая автоматически обходит структурированный набор адресов (URL) и заносит полученные страницы в специальную базу данных. Из полученных текстов, в свою очередь, извлекаются новые URL и добавляются в конец исходного набора. Пауки различаются по типам [@wirelesscommunicationandcomputingstudentcsedepartmentg.h.raisoniinstituteofengineeringandtechnologyforwomennagpurindiaStudyWebCrawler2014], так существуют _периодические_ пауки широкого назначения [@choEvolutionWebImplications]. Они скачивают все указанные в списке URL, пока не наберут желаемое количество скаченных страниц и останавливаются. Эта процедура повторяется периодически, когда возникает необходимость в обновлении данных. Они не самые эффективные с точки зрения скорости исполнения, зато отсутствует возможность не обновления заранее заданной страницы. Также существуют _пошаговые_ пауки, продолжающие свою работу непрерывно. Их задача не заканчивать обходить страницы и заменять наименее полезные страницы на более полезные по некоторому правилу [@choEvolutionWebImplications]. В этом случае могут возникать различные осложнения из-за неясности как универсально определить полезность некоторой страницы. Если считать страницу важной по непрерывному количеству посещений ее, то можно удалить важную страницу на которой раз в месяц оплачиваются счета за важные услуги (например коммунальные). Или же считать полезными только те страницы на которые больше всего ежемесячная аудитория, что делает невозможным использование такого паука с некоторой узкой целью (поиска информации по своей узкой специальности). Следующим типом являются _распределенные_ пауки[@boldiUbiCrawlerScalableFully2004], состоящие из многих пауков широкого назначения, которые проверяют URL только в определенной области интернета ограниченной географически. При этом есть единый сервер, контролирующий и распределяющий URL между ними. Таким образом достигается большая отказоустойчивость всей системы, хоть и существует некоторое ограничение скорости в силу использования пауков широкого назначения. Эту проблему призваны были решать _параллельные_ пауки [@ParallelCrawlers]. В отличие от _распределенных_ они обрабатывают единый массив URL, которые разделены на несколько машин, обрабатывающих эти URL параллельно, а не последовательно. Такое улучшение позволило повысить скорость выгрузки страниц. Подтипом пауков широкого назначения являются _фокусированные_. Они обходят и добавляют в список дальнейшего обхода только те URL, страница которых соответствует некоторой теме (допустим теме поискового запроса), используя при этом различные методы подсчета обратных ссылок. В Google Inc. в 1998 году использовали для этой цели PageRank [@BRIN1998107]. Для определения формулы дадим следующие условия, пусть на странице А цитируются страницы $S_1, ..., S_n$ (присутствуют их URL), $d \in (0,1)$ параметр затухания (в работе брали $0.85$), $C(A)$ - общее количество цитируемых страниц на странице А. Тогда $PR(A) = (1-d) + d*(\frac{PR(S_1)}{C(S_1)}+\frac{PR(S_2)}{C(S_2)}+...+\frac{PR(S_n)}{C(S_n)})$, где $PR$ это PageRank. Существует множество вариантов, выбора параметров для построения фокусированных пауков. Поэтому они, в свою очередь, подразделяются на различные виды в зависимости от способа определения соответствия страницы теме и способа обработки страниц [@batsakisImprovingPerformanceFocused2009].

Дальше по абзацу на следующее:

1. Место хранения всех этих обкаченных данных (Разные виды бд реляционные не реляционные язык SQL)

2. Способы поиска в тексте конкретных слов (полнотекстовый)

3. Способы определения связности найденных слов (через графы знаний, мл, еще сказать про что вообще значит связность)
