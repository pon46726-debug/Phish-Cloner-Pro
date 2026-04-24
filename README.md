<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=28&duration=2000&pause=1000&color=36BCF7&center=true&vCenter=true&width=600&lines=Phish-Cloner+Pro+%F0%9F%8E%A3;Clone+%2B+Inject+%2B+Serve;Educational+Purpose+Only" alt="Typing SVG" />
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green"></a>
  <a href="#"><img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey"></a>
  <a href="#"><img src="https://img.shields.io/badge/Educational-Only-red"></a>
</p>

# 🎣 Phish-Cloner Pro

> **Учебный инструмент** для пентестеров, студентов ИБ и red team.
> Клонирует веб-страницу, сохраняет все ресурсы, внедряет кастомный JS-сниффер и **сразу хостит клон** для демонстрации.

После клонирования страница выглядит как настоящая, а JavaScript перехватывает учётные данные и отправляет их на сервер сбора.  
**Используйте только с явного разрешения владельца системы!**

---

## 📦 Возможности

- 🕸 **Клонирование страниц** — скачивает HTML, CSS, JS, изображения  
- 🔗 **Локализация ресурсов** — вся статика хранится локально, никаких внешних запросов  
- 💉 **Инъекция JS-сниффера** — перехватывает данные форм (логин/пароль)  
- 📡 **Сервер сбора** — принимает перехваченные учётные данные (Flask)  
- 🎨 **Стильный CLI** — ASCII-баннер, цветной вывод, одна команда для клонирования и хостинга  
- 🐳 **Docker support** — быстрый запуск без установки зависимостей (опционально)  

---

## 🚀 Быстрый старт

### Локальный запуск

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/pon46726-debug/phish-cloner-pro.git
cd phish-cloner-pro

# 2. Установите зависимости
pip install -r requirements.txt

# 3. Запустите сервер сбора (в отдельном терминале)
python server.py

# 4. Клонируйте страницу и сразу захостите её
python cloner.py clone https://example.com/login --serve 8080
