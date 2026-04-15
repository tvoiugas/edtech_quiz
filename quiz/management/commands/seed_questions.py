from django.core.management.base import BaseCommand
from quiz.models import Category, Question, Answer


QUESTIONS_DATA = {
    'python': {
        'name': 'Python',
        'icon': '🐍',
        'color': '#3b82f6',
        'description': 'Тестирование знаний Python — от основ до продвинутых концепций',
        'difficulty_label': 'Beginner → Expert',
        'questions': [
            {
                'text': 'Что выведет следующий код?\n\nx = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)',
                'difficulty': 'easy',
                'explanation': 'В Python списки передаются по ссылке. y и x указывают на один объект, поэтому изменение y влияет на x.',
                'answers': [('[1, 2, 3, 4]', True), ('[1, 2, 3]', False), ('Error', False), ('None', False)]
            },
            {
                'text': 'Какой из следующих способов создаёт генератор в Python?',
                'difficulty': 'medium',
                'explanation': 'Генераторная функция использует ключевое слово yield. Выражения в () также создают генераторы.',
                'answers': [('def f(): yield x', True), ('def f(): return x', False), ('[x for x in range(10)]', False), ('{x: x for x in range(10)}', False)]
            },
            {
                'text': 'Что такое GIL в Python?',
                'difficulty': 'hard',
                'explanation': 'GIL (Global Interpreter Lock) — мьютекс, позволяющий выполняться только одному потоку Python одновременно.',
                'answers': [('Global Interpreter Lock — механизм блокировки потоков', True), ('Global Input Library — библиотека ввода', False), ('General Interface Layer — слой интерфейса', False), ('Garbage In Logging — система логирования', False)]
            },
            {
                'text': 'Какой результат выполнения: bool("") and bool(0) or bool("hello")?',
                'difficulty': 'medium',
                'explanation': '"hello" — истинное значение. False and False or True = True.',
                'answers': [('True', True), ('False', False), ('"hello"', False), ('Error', False)]
            },
            {
                'text': 'Что делает декоратор @staticmethod?',
                'difficulty': 'easy',
                'explanation': '@staticmethod позволяет вызывать метод без создания экземпляра класса и без доступа к self или cls.',
                'answers': [('Определяет метод, не привязанный к экземпляру или классу', True), ('Кэширует результат функции', False), ('Делает метод приватным', False), ('Запрещает переопределение метода', False)]
            },
            {
                'text': 'Что выведет: print(type(lambda x: x))?',
                'difficulty': 'easy',
                'explanation': 'lambda создаёт функцию, тип которой <class function>.',
                'answers': [("<class 'function'>", True), ("<class 'lambda'>", False), ("<class 'method'>", False), ("<class 'object'>", False)]
            },
            {
                'text': 'Какой модуль Python используется для работы с JSON?',
                'difficulty': 'easy',
                'explanation': 'Модуль json встроен в Python и предоставляет функции dumps(), loads(), dump(), load().',
                'answers': [('json', True), ('pickle', False), ('yaml', False), ('struct', False)]
            },
            {
                'text': 'Что такое метакласс в Python?',
                'difficulty': 'hard',
                'explanation': 'Метакласс — это класс, экземплярами которого являются другие классы. type — дефолтный метакласс.',
                'answers': [('Класс, создающий другие классы', True), ('Абстрактный базовый класс', False), ('Класс с множественным наследованием', False), ('Класс без экземпляров', False)]
            },
            {
                'text': 'В чём разница между list и tuple?',
                'difficulty': 'easy',
                'explanation': 'list — изменяемый (mutable), tuple — неизменяемый (immutable). Tuple обычно быстрее и используется для фиксированных данных.',
                'answers': [('list изменяемый, tuple — нет', True), ('tuple изменяемый, list — нет', False), ('Нет разницы, это синонимы', False), ('list поддерживает только числа', False)]
            },
            {
                'text': 'Что делает функция zip() в Python?',
                'difficulty': 'easy',
                'explanation': 'zip() объединяет несколько итерируемых объектов в один, создавая кортежи из элементов с одинаковыми индексами.',
                'answers': [('Объединяет несколько итерируемых в один', True), ('Сжимает данные', False), ('Создаёт словарь из двух списков', False), ('Сортирует несколько списков одновременно', False)]
            },
        ]
    },
    'javascript': {
        'name': 'JavaScript',
        'icon': '⚡',
        'color': '#f59e0b',
        'description': 'ES6+, асинхронность, DOM, и современный JS',
        'difficulty_label': 'Junior → Senior',
        'questions': [
            {
                'text': 'Что такое замыкание (closure) в JavaScript?',
                'difficulty': 'medium',
                'explanation': 'Замыкание — функция, которая запоминает переменные из своей внешней области видимости даже после завершения внешней функции.',
                'answers': [('Функция, имеющая доступ к переменным внешней области', True), ('Способ скрыть данные в объекте', False), ('Метод копирования объектов', False), ('Функция без аргументов', False)]
            },
            {
                'text': 'Что выведет: console.log(typeof null)?',
                'difficulty': 'medium',
                'explanation': 'typeof null === "object" — это исторический баг JavaScript, сохранённый для обратной совместимости.',
                'answers': [('"object"', True), ('"null"', False), ('"undefined"', False), ('"boolean"', False)]
            },
            {
                'text': 'В чём разница между == и === в JavaScript?',
                'difficulty': 'easy',
                'explanation': '== сравнивает значения с приведением типов, === сравнивает значения И типы без приведения.',
                'answers': [('=== проверяет тип и значение, == только значение', True), ('Нет разницы, они идентичны', False), ('== строже, чем ===', False), ('=== работает только для чисел', False)]
            },
            {
                'text': 'Что такое Promise в JavaScript?',
                'difficulty': 'medium',
                'explanation': 'Promise — объект, представляющий результат асинхронной операции, которая может завершиться успешно (resolve) или с ошибкой (reject).',
                'answers': [('Объект для работы с асинхронными операциями', True), ('Синхронный способ вызова функций', False), ('Метод для работы с массивами', False), ('Способ объявить константу', False)]
            },
            {
                'text': 'Что делает оператор spread (...) в JavaScript?',
                'difficulty': 'easy',
                'explanation': 'Spread разворачивает итерируемый объект в отдельные элементы. Используется для копирования, объединения массивов и объектов.',
                'answers': [('Разворачивает итерируемый объект в элементы', True), ('Создаёт функцию с произвольным числом аргументов', False), ('Удаляет элемент из массива', False), ('Создаёт глубокую копию объекта', False)]
            },
            {
                'text': 'Что такое event loop в JavaScript?',
                'difficulty': 'hard',
                'explanation': 'Event loop — механизм, позволяющий JavaScript выполнять неблокирующие операции путём обработки колбэков из очереди задач.',
                'answers': [('Механизм обработки асинхронных задач и колбэков', True), ('Цикл for для обхода событий DOM', False), ('Встроенный планировщик потоков', False), ('Система управления памятью', False)]
            },
            {
                'text': 'Что выведет: [1,2,3].map(x => x * 2)?',
                'difficulty': 'easy',
                'explanation': 'map() применяет функцию к каждому элементу и возвращает новый массив.',
                'answers': [('[2, 4, 6]', True), ('[1, 2, 3]', False), ('6', False), ('undefined', False)]
            },
            {
                'text': 'Что такое прототипное наследование?',
                'difficulty': 'hard',
                'explanation': 'В JS каждый объект имеет прототип. При обращении к свойству JS ищет его в объекте, затем в цепочке прототипов до Object.prototype.',
                'answers': [('Объекты наследуют свойства через цепочку прототипов', True), ('Классы наследуют методы через extends', False), ('Копирование всех свойств одного объекта в другой', False), ('Механизм множественного наследования', False)]
            },
            {
                'text': 'Какой метод используется для создания копии массива?',
                'difficulty': 'easy',
                'explanation': 'slice() без аргументов создаёт поверхностную копию массива. Spread [...arr] тоже работает.',
                'answers': [('[...arr] или arr.slice()', True), ('arr.copy()', False), ('arr.clone()', False), ('Object.create(arr)', False)]
            },
            {
                'text': 'Что такое hoisting в JavaScript?',
                'difficulty': 'medium',
                'explanation': 'Hoisting — механизм подъёма объявлений переменных (var) и функций в начало их области видимости до выполнения кода.',
                'answers': [('Подъём объявлений переменных и функций наверх области', True), ('Оптимизация кода JavaScript-движком', False), ('Метод для работы с DOM элементами', False), ('Способ создания глобальных переменных', False)]
            },
        ]
    },
    'sql': {
        'name': 'SQL & Databases',
        'icon': '🗄️',
        'color': '#10b981',
        'description': 'SQL запросы, индексы, транзакции и проектирование БД',
        'difficulty_label': 'Junior → DBA',
        'questions': [
            {
                'text': 'Что делает оператор JOIN в SQL?',
                'difficulty': 'easy',
                'explanation': 'JOIN объединяет строки из двух или более таблиц на основе связанного столбца.',
                'answers': [('Объединяет строки из нескольких таблиц', True), ('Удаляет дублирующиеся строки', False), ('Сортирует результат запроса', False), ('Группирует данные по условию', False)]
            },
            {
                'text': 'В чём разница между INNER JOIN и LEFT JOIN?',
                'difficulty': 'medium',
                'explanation': 'INNER JOIN возвращает только совпадающие строки. LEFT JOIN возвращает все строки из левой таблицы, даже если нет совпадений.',
                'answers': [('LEFT JOIN включает все строки левой таблицы', True), ('INNER JOIN быстрее LEFT JOIN всегда', False), ('Нет разницы, это синонимы', False), ('LEFT JOIN работает только с одной таблицей', False)]
            },
            {
                'text': 'Что такое индекс в базе данных?',
                'difficulty': 'medium',
                'explanation': 'Индекс — структура данных, ускоряющая поиск и сортировку, но замедляющая операции INSERT/UPDATE/DELETE.',
                'answers': [('Структура для ускорения поиска данных', True), ('Уникальный идентификатор каждой строки', False), ('Копия таблицы для резервного хранения', False), ('Ограничение на тип данных в столбце', False)]
            },
            {
                'text': 'Что делает оператор GROUP BY?',
                'difficulty': 'easy',
                'explanation': 'GROUP BY группирует строки с одинаковыми значениями в сводные строки, используется с агрегатными функциями.',
                'answers': [('Группирует строки для агрегатных функций', True), ('Сортирует результат по группам', False), ('Фильтрует дублирующиеся строки', False), ('Объединяет несколько таблиц', False)]
            },
            {
                'text': 'Что такое транзакция в СУБД?',
                'difficulty': 'medium',
                'explanation': 'Транзакция — последовательность операций, выполняемых как единое целое. Поддерживает свойства ACID.',
                'answers': [('Набор операций, выполняемых как единое целое', True), ('Отдельный SQL запрос', False), ('Способ создания резервной копии', False), ('Механизм шифрования данных', False)]
            },
            {
                'text': 'Что означает аббревиатура ACID?',
                'difficulty': 'hard',
                'explanation': 'ACID: Atomicity (атомарность), Consistency (согласованность), Isolation (изолированность), Durability (долговечность).',
                'answers': [('Atomicity, Consistency, Isolation, Durability', True), ('Availability, Consistency, Integrity, Durability', False), ('Atomicity, Concurrency, Isolation, Data', False), ('Access, Control, Index, Duplication', False)]
            },
            {
                'text': 'Чем отличается WHERE от HAVING?',
                'difficulty': 'medium',
                'explanation': 'WHERE фильтрует строки до группировки, HAVING — после группировки (используется с GROUP BY).',
                'answers': [('WHERE до группировки, HAVING после', True), ('HAVING работает быстрее WHERE', False), ('WHERE только для числовых полей', False), ('Нет разницы, они взаимозаменяемы', False)]
            },
            {
                'text': 'Что такое PRIMARY KEY?',
                'difficulty': 'easy',
                'explanation': 'PRIMARY KEY — уникальный идентификатор каждой строки в таблице. Не может быть NULL и должен быть уникальным.',
                'answers': [('Уникальный идентификатор строки в таблице', True), ('Первый столбец в любой таблице', False), ('Индекс для ускорения поиска', False), ('Шифрование данных в столбце', False)]
            },
            {
                'text': 'Что делает оператор DISTINCT?',
                'difficulty': 'easy',
                'explanation': 'DISTINCT возвращает только уникальные значения, убирая дубликаты из результата запроса.',
                'answers': [('Возвращает только уникальные строки', True), ('Сортирует результат по возрастанию', False), ('Выбирает только первую строку', False), ('Создаёт индекс на столбец', False)]
            },
            {
                'text': 'Что такое нормализация базы данных?',
                'difficulty': 'hard',
                'explanation': 'Нормализация — процесс организации таблиц для уменьшения избыточности данных и аномалий обновления.',
                'answers': [('Организация таблиц для уменьшения избыточности', True), ('Оптимизация SQL запросов', False), ('Создание резервных копий данных', False), ('Шифрование конфиденциальных данных', False)]
            },
        ]
    },
    'algorithms': {
        'name': 'Алгоритмы',
        'icon': '🧠',
        'color': '#8b5cf6',
        'description': 'Сортировки, поиск, сложность, структуры данных',
        'difficulty_label': 'Junior → FAANG',
        'questions': [
            {
                'text': 'Какова временная сложность бинарного поиска?',
                'difficulty': 'easy',
                'explanation': 'Бинарный поиск делит массив пополам на каждом шаге, что даёт O(log n).',
                'answers': [('O(log n)', True), ('O(n)', False), ('O(n²)', False), ('O(1)', False)]
            },
            {
                'text': 'Что такое Big O нотация?',
                'difficulty': 'easy',
                'explanation': 'Big O описывает верхнюю границу роста времени выполнения алгоритма в зависимости от размера входных данных.',
                'answers': [('Описание верхней границы сложности алгоритма', True), ('Точное время выполнения алгоритма', False), ('Минимальная сложность алгоритма', False), ('Объём памяти, используемый алгоритмом', False)]
            },
            {
                'text': 'В чём разница между стеком (Stack) и очередью (Queue)?',
                'difficulty': 'easy',
                'explanation': 'Stack: LIFO (последний вошёл — первый вышел). Queue: FIFO (первый вошёл — первый вышел).',
                'answers': [('Stack — LIFO, Queue — FIFO', True), ('Stack — FIFO, Queue — LIFO', False), ('Они одинаковы, только разные названия', False), ('Queue хранит больше элементов', False)]
            },
            {
                'text': 'Какая сортировка имеет лучшую среднюю сложность?',
                'difficulty': 'medium',
                'explanation': 'Quicksort и Mergesort имеют O(n log n) в среднем. Это оптимально для сравнительных сортировок.',
                'answers': [('Quick Sort / Merge Sort — O(n log n)', True), ('Bubble Sort — O(n)', False), ('Insertion Sort — O(log n)', False), ('Selection Sort — O(n²)', False)]
            },
            {
                'text': 'Что такое рекурсия?',
                'difficulty': 'easy',
                'explanation': 'Рекурсия — когда функция вызывает саму себя. Важно иметь базовый случай для остановки рекурсии.',
                'answers': [('Функция, вызывающая саму себя', True), ('Цикл с условием выхода', False), ('Метод оптимизации кода', False), ('Тип данных в функциональном программировании', False)]
            },
            {
                'text': 'Что такое хэш-таблица?',
                'difficulty': 'medium',
                'explanation': 'Хэш-таблица использует хэш-функцию для маппинга ключей к индексам массива. Доступ O(1) в среднем случае.',
                'answers': [('Структура данных с O(1) доступом по ключу', True), ('Таблица с сортировкой по хэшу', False), ('Зашифрованный массив данных', False), ('Список с уникальными элементами', False)]
            },
            {
                'text': 'Что такое граф в программировании?',
                'difficulty': 'medium',
                'explanation': 'Граф — структура данных из вершин (nodes) и рёбер (edges). Бывает направленным и ненаправленным.',
                'answers': [('Набор вершин, соединённых рёбрами', True), ('Двумерный массив чисел', False), ('Специальный тип дерева', False), ('Визуализация данных', False)]
            },
            {
                'text': 'В чём идея динамического программирования?',
                'difficulty': 'hard',
                'explanation': 'DP разбивает задачу на подзадачи и сохраняет результаты (мемоизация), избегая повторных вычислений.',
                'answers': [('Сохранение результатов подзадач для избежания повторений', True), ('Использование динамической памяти', False), ('Параллельное выполнение алгоритмов', False), ('Оптимизация с помощью рандомизации', False)]
            },
            {
                'text': 'Какова сложность поиска в связном списке?',
                'difficulty': 'easy',
                'explanation': 'В связном списке нет прямого доступа по индексу — нужно перебирать элементы от начала, поэтому O(n).',
                'answers': [('O(n)', True), ('O(1)', False), ('O(log n)', False), ('O(n²)', False)]
            },
            {
                'text': 'Что такое BFS (Breadth-First Search)?',
                'difficulty': 'medium',
                'explanation': 'BFS обходит граф/дерево по уровням, используя очередь. Находит кратчайший путь в невзвешенном графе.',
                'answers': [('Обход графа по уровням с использованием очереди', True), ('Обход графа в глубину', False), ('Алгоритм сортировки деревьев', False), ('Поиск в хэш-таблице', False)]
            },
        ]
    },
    'devops': {
        'name': 'DevOps & Cloud',
        'icon': '☁️',
        'color': '#06b6d4',
        'description': 'Docker, Kubernetes, CI/CD, Linux и облачные технологии',
        'difficulty_label': 'Dev → Ops',
        'questions': [
            {
                'text': 'Что такое Docker контейнер?',
                'difficulty': 'easy',
                'explanation': 'Контейнер — изолированная среда с приложением и его зависимостями. Контейнеры используют ядро хоста, но изолируют процессы.',
                'answers': [('Изолированная среда для запуска приложения', True), ('Виртуальная машина с полной ОС', False), ('Архив с кодом приложения', False), ('Облачный сервер', False)]
            },
            {
                'text': 'В чём разница между Docker image и контейнером?',
                'difficulty': 'easy',
                'explanation': 'Image — неизменяемый шаблон (blueprint). Контейнер — запущенный экземпляр image.',
                'answers': [('Image — шаблон, контейнер — запущенный экземпляр', True), ('Они одинаковы', False), ('Контейнер хранится в registry', False), ('Image — это контейнер с данными', False)]
            },
            {
                'text': 'Что такое CI/CD?',
                'difficulty': 'easy',
                'explanation': 'CI (Continuous Integration) — автоматическая сборка и тестирование при каждом коммите. CD (Continuous Delivery/Deployment) — автоматический деплой.',
                'answers': [('Автоматизация сборки, тестирования и деплоя', True), ('Система контроля версий', False), ('Метод написания тестов', False), ('Облачный провайдер', False)]
            },
            {
                'text': 'Что делает команда docker-compose up?',
                'difficulty': 'easy',
                'explanation': 'docker-compose up запускает все сервисы, описанные в docker-compose.yml файле.',
                'answers': [('Запускает все сервисы из docker-compose.yml', True), ('Собирает Docker образы', False), ('Останавливает все контейнеры', False), ('Удаляет все контейнеры', False)]
            },
            {
                'text': 'Что такое Kubernetes?',
                'difficulty': 'medium',
                'explanation': 'Kubernetes (K8s) — система оркестрации контейнеров для автоматизации развёртывания, масштабирования и управления.',
                'answers': [('Система оркестрации контейнеров', True), ('Облачный провайдер от Google', False), ('Альтернатива Docker', False), ('Язык конфигурации для DevOps', False)]
            },
            {
                'text': 'Что такое Infrastructure as Code (IaC)?',
                'difficulty': 'medium',
                'explanation': 'IaC — управление инфраструктурой через код (файлы конфигурации), а не вручную. Примеры: Terraform, Ansible.',
                'answers': [('Управление инфраструктурой через код', True), ('Автоматическое написание кода', False), ('Хранение кода в облаке', False), ('Виртуализация серверов', False)]
            },
            {
                'text': 'Что такое reverse proxy?',
                'difficulty': 'medium',
                'explanation': 'Reverse proxy принимает запросы клиентов и перенаправляет их на внутренние серверы. Nginx часто используется как reverse proxy.',
                'answers': [('Сервер, перенаправляющий запросы на бэкенд', True), ('Инструмент для VPN соединений', False), ('Способ кэширования запросов', False), ('Балансировщик нагрузки базы данных', False)]
            },
            {
                'text': 'Что такое Pod в Kubernetes?',
                'difficulty': 'hard',
                'explanation': 'Pod — минимальная развёртываемая единица в K8s. Содержит один или несколько контейнеров, разделяющих сеть и хранилище.',
                'answers': [('Минимальная единица развёртывания с контейнерами', True), ('Тип виртуальной машины', False), ('Набор настроек кластера', False), ('Отдельный Docker контейнер', False)]
            },
            {
                'text': 'Что делает команда git rebase?',
                'difficulty': 'medium',
                'explanation': 'git rebase переносит коммиты ветки на новое основание, создавая линейную историю без merge commit.',
                'answers': [('Переносит коммиты на новое основание', True), ('Объединяет две ветки с merge commit', False), ('Удаляет последний коммит', False), ('Создаёт новую ветку', False)]
            },
            {
                'text': 'Для чего используется Dockerfile?',
                'difficulty': 'easy',
                'explanation': 'Dockerfile — текстовый файл с инструкциями для сборки Docker image.',
                'answers': [('Инструкции для сборки Docker image', True), ('Конфигурация docker-compose', False), ('Файл с переменными окружения', False), ('Скрипт запуска приложения', False)]
            },
        ]
    },
}


class Command(BaseCommand):
    help = 'Seed database with quiz categories and questions'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding questions...')

        for slug, data in QUESTIONS_DATA.items():
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': data['name'],
                    'icon': data['icon'],
                    'color': data['color'],
                    'description': data['description'],
                    'difficulty_label': data['difficulty_label'],
                }
            )

            if created:
                self.stdout.write(f'  Created category: {category.name}')
            else:
                self.stdout.write(f'  Category exists: {category.name}')

            if created:
                for i, q_data in enumerate(data['questions']):
                    question = Question.objects.create(
                        category=category,
                        text=q_data['text'],
                        difficulty=q_data['difficulty'],
                        explanation=q_data.get('explanation', ''),
                        order=i,
                    )
                    for j, (answer_text, is_correct) in enumerate(q_data['answers']):
                        Answer.objects.create(
                            question=question,
                            text=answer_text,
                            is_correct=is_correct,
                            order=j,
                        )
                self.stdout.write(f'    Added {len(data["questions"])} questions')

        self.stdout.write(self.style.SUCCESS('Done! Database seeded successfully.'))