# Сдача лабораторной через GitHub

По методичке нужно отправить преподавателю две ссылки — на публичный репозиторий `fdf-python` и на релиз `v1.0`. Файл `fdf-python.bundle` содержит историю Git и подготовленные ветки.

## Репозиторий

1. Войдите на GitHub и создайте публичный репозиторий `fdf-python`. Оставьте его пустым. README, лицензию и .gitignore добавлять при создании не нужно, они уже есть в истории.
2. Откройте PowerShell в папке, где лежит `fdf-python.bundle`. Выполните команды ниже. Замените `USERNAME` своим логином на GitHub. При первом push Git может открыть окно входа.

```powershell
git clone -b main .\fdf-python.bundle fdf-github
cd fdf-github
git remote add github https://github.com/USERNAME/fdf-python.git
$firstCommit = git rev-list --max-parents=0 main
git push github "${firstCommit}:refs/heads/main"
git push github origin/feature/parser:refs/heads/feature/parser origin/feature/render:refs/heads/feature/render origin/bonus/zoom:refs/heads/bonus/zoom origin/bonus/ci:refs/heads/bonus/ci
```

## Pull request

Создавайте и вливайте PR по одному в указанном порядке. В каждом PR выбирайте `base: main`, а в поле `compare` — нужную ветку. Для слияния на GitHub используйте **Create a merge commit**, чтобы следующая ветка сравнивалась с уже влитым кодом.

| Ветка | Заголовок PR | Что написать в описании |
| --- | --- | --- |
| `feature/parser` | Добавить модель и парсер карт FdF | Чтение карты, разбор цветов, диагностика, тесты модели и парсера. Проверка: `pytest -q`. |
| `feature/render` | Добавить изометрическую отрисовку | Расчёт проекции, масштабирование по окну, завершение по Esc. Проверка: `python main.py maps/elem.fdf`. |
| `bonus/zoom` | Добавить управление камерой и градиенты | Колесо, стрелки, масштаб высот, смена вида, угол, цвет рёбер. Проверка: `pytest -q` и `python main.py maps/peak.fdf`. |
| `bonus/ci` | Добавить проверки GitHub Actions | Ruff, строгий mypy и pytest запускаются при push и PR. Проверка: вкладка Actions. |

Бейдж проверок можно получить на вкладке **Actions** после первого запуска. Выберите workflow **Проверки**, откройте меню с тремя точками, нажмите **Create status badge** и скопируйте Markdown в раздел «Тесты» файла README.

## Релиз

После слияния веток откройте **Releases → Draft a new release**. Введите тег `v1.0`, выберите создание нового тега и укажите `main` в поле **Target**. Название релиза — `FdF v1.0`. Нажмите **Publish release**, затем скопируйте ссылки на репозиторий и релиз.
