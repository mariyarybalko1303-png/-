#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==========================================================================
        УЛЬТИМАТИВНИЙ ПРОВІДНИК ФАЙЛІВ У СТИЛІ WINDOWS EXPLORER (v3.0)
==========================================================================
Цей скрипт є повнофункціональним файловим менеджером, який повністю відтворює
зовнішній вигляд, структуру та поведінку класичного провідника Windows:
1. Візуальний стиль Windows: світла тема, характерна кольорова палітра, м'яке 
   синє виділення елементів, рамки та шрифти.
2. Windows Sidebar: панель швидкого доступу з класичними папками (Робочий стіл,
   Завантаження, Документи, Зображення, Музика, Відео, Локальний диск C: / Root).
3. Повноцінний адресний рядок із кнопками "Назад", "Вгору", "Оновити" (🔄) та 
   інтегрованим вікном пошуку у верхньому правому куті папки.
4. Контекстне меню правої кнопки миші (Popup Menu): "Відкрити", "Редагувати в 
   Блокноті", "Перейменувати", "Видалити", "Створити папку", "Створити файл" та 
   "Властивості".
5. Вбудований Блокнот (Notepad) з можливістю редагування та збереження файлів.
6. Вікно "Властивості" (Properties) у класичному стилі Windows із відображенням 
   детальних метаданих, прав доступу, обсягу та дат.
7. Інтерактивне сортування стовпців (Ім'я, Дата змінення, Тип, Розмір) за кліком.
==========================================================================
"""

import os
import sys
import shutil
import datetime
import fnmatch
import argparse
import platform
import subprocess

# Глобальні змінні для ANSI кольорів у TUI (якщо GUI не запуститься)
CLR_HEADER = '\033[95m'
CLR_FOLDER = '\033[94m'
CLR_FILE = '\033[92m'
CLR_WARN = '\033[93m'
CLR_FAIL = '\033[91m'
CLR_RESET = '\033[0m'
CLR_BOLD = '\033[1m'


def get_readable_size(size_in_bytes):
    """Конвертує розмір у байтах у зручний для читання формат Windows (KB, MB, GB)."""
    if size_in_bytes == 0 or size_in_bytes == "":
        return ""
    for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
        if size_in_bytes < 1024.0:
            # Округлюємо до більшого цілого для КБ, як у Windows
            if unit == 'КБ':
                return f"{int(os.path.ceil(size_in_bytes))} {unit}"
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f} ПБ"


# ====================================================================
# 1. МОДУЛЬ TUI (FALLBACK TERMINAL MODE)
# ====================================================================

class TerminalExplorer:
    def __init__(self, start_dir=None):
        self.current_dir = os.path.abspath(start_dir or os.getcwd())

    def run(self):
        print(f"\n{CLR_WARN}⚠️ Запущено консольний Fallback-режим (TUI). Для запуску віконного інтерфейсу використовуйте графічну систему.{CLR_RESET}")
        self.print_welcome()
        while True:
            try:
                self.list_directory()
                cmd_input = input(f"\n{CLR_BOLD}[{os.path.basename(self.current_dir) or self.current_dir}]{CLR_RESET} > ").strip()
                if not cmd_input:
                    continue
                
                parts = cmd_input.split()
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd in ['exit', 'quit', 'вихід']:
                    break
                elif cmd in ['help', 'допомога']:
                    self.print_help()
                elif cmd == 'cd':
                    self.change_directory(args)
                elif cmd in ['view', 'перегляд']:
                    self.view_file(args)
                elif cmd in ['mkdir', 'папка']:
                    self.create_directory(args)
                elif cmd in ['create', 'файл']:
                    self.create_file(args)
                elif cmd in ['delete', 'видалити']:
                    self.delete_item(args)
                elif cmd in ['search', 'пошук']:
                    self.search_items(args)
                elif cmd in ['info', 'інфо']:
                    self.show_info(args)
                else:
                    print(f"{CLR_FAIL}❌ Невідома команда. Наберіть 'help' для переліку команд.{CLR_RESET}")
            except KeyboardInterrupt:
                print(f"\n{CLR_WARN}Перервано користувачем. Наберіть 'exit' для виходу.{CLR_RESET}")
            except Exception as e:
                print(f"{CLR_FAIL}💥 Помилка: {e}{CLR_RESET}")

    def print_welcome(self):
        print("="*70)
        print(f"{CLR_HEADER}{CLR_BOLD}       ІНТЕРАКТИВНИЙ КОНСОЛЬНИЙ ПРОВІДНИК ФАЙЛІВ (Windows Style TUI){CLR_RESET}")
        print("="*70)

    def print_help(self):
        print(f"\n{CLR_BOLD}Доступні команди:{CLR_RESET}")
        print(f"  • {CLR_BOLD}cd <папка>{CLR_RESET}     - Перейти у вказану директорію")
        print(f"  • {CLR_BOLD}view <файл>{CLR_RESET}    - Переглянути текстовий файл")
        print(f"  • {CLR_BOLD}mkdir <ім'я>{CLR_RESET}   - Створити нову папку")
        print(f"  • {CLR_BOLD}create <ім'я>{CLR_RESET}  - Створити порожній файл")
        print(f"  • {CLR_BOLD}delete <ім'я>{CLR_RESET}  - Видалити елемент")
        print(f"  • {CLR_BOLD}search <маска>{CLR_RESET} - Пошук файлів за шаблоном (наприклад: *.txt)")
        print(f"  • {CLR_BOLD}info <ім'я>{CLR_RESET}    - Метадані елемента")
        print(f"  • {CLR_BOLD}exit{CLR_RESET}           - Вийти з програми")

    def list_directory(self):
        print(f"\n{CLR_HEADER}Шлях: {CLR_BOLD}{self.current_dir}{CLR_RESET}")
        print("-" * 70)
        try:
            items = os.listdir(self.current_dir)
        except Exception as e:
            print(f"{CLR_FAIL}❌ Доступ обмежено: {e}{CLR_RESET}")
            self.current_dir = os.path.dirname(self.current_dir)
            return

        folders = []
        files = []
        for item in items:
            p = os.path.join(self.current_dir, item)
            if os.path.isdir(p):
                folders.append(item)
            else:
                files.append(item)
        folders.sort()
        files.sort()

        for folder in folders:
            print(f"  📁 {CLR_FOLDER}{CLR_BOLD}{folder}/{CLR_RESET}")
        for file in files:
            size = os.path.getsize(os.path.join(self.current_dir, file))
            print(f"  📄 {CLR_FILE}{file}{CLR_RESET} ({get_readable_size(size)})")

    def change_directory(self, args):
        if not args: return
        target = " ".join(args)
        new_path = os.path.abspath(os.path.join(self.current_dir, target))
        if os.path.isdir(new_path):
            self.current_dir = new_path
        else:
            print(f"{CLR_FAIL}❌ Папки не існує.{CLR_RESET}")

    def view_file(self, args):
        if not args: return
        filename = " ".join(args)
        full_path = os.path.join(self.current_dir, filename)
        if os.path.isfile(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    print(f.read(2000))
            except Exception as e:
                print(f"{CLR_FAIL}Помилка зчитування: {e}{CLR_RESET}")

    def create_directory(self, args):
        if not args: return
        os.makedirs(os.path.join(self.current_dir, " ".join(args)), exist_ok=True)
        print("✅ Створено.")

    def create_file(self, args):
        if not args: return
        with open(os.path.join(self.current_dir, " ".join(args)), 'w', encoding='utf-8') as f:
            f.write("")
        print("✅ Створено.")

    def delete_item(self, args):
        if not args: return
        name = " ".join(args)
        p = os.path.join(self.current_dir, name)
        if os.path.exists(p):
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
            print("✅ Видалено.")

    def search_items(self, args):
        if not args: return
        pattern = " ".join(args)
        for root, dirs, files in os.walk(self.current_dir):
            for name in dirs + files:
                if fnmatch.fnmatch(name, pattern):
                    print(f"  • {os.path.relpath(os.path.join(root, name), self.current_dir)}")

    def show_info(self, args):
        if not args: return
        p = os.path.join(self.current_dir, " ".join(args))
        if os.path.exists(p):
            stat = os.stat(p)
            print(f"Розмір: {get_readable_size(stat.st_size)}")
            print(f"Змінено: {datetime.datetime.fromtimestamp(stat.st_mtime)}")


# ====================================================================
# 2. МОДУЛЬ GUI (ПОЛНОЦІННИЙ WINDOWS-ПРОВІДНИК НА TKINTER)
# ====================================================================

def get_file_emoji(name, is_dir):
    """Повертає відповідну Windows-іконку (емодзі) на основі розширення файлу."""
    if is_dir:
        return "📁"
    
    ext = os.path.splitext(name)[1].lower()
    if ext in ['.txt', '.log', '.md', '.ini', '.cfg', '.json', '.yaml', '.yml']:
        return "📝"  # Текстовий файл
    elif ext in ['.py', '.jl', '.cpp', '.h', '.cs', '.java', '.js', '.html', '.css', '.sh', '.bat']:
        return "⚙️"  # Код / Налаштування / Скрипт
    elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.webp']:
        return "🖼️"  # Зображення
    elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']:
        return "📦"  # Архів
    elif ext in ['.mp3', '.wav', '.flac', '.ogg', '.m4a']:
        return "🎵"  # Аудіо
    elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv']:
        return "🎬"  # Відео
    elif ext in ['.pdf']:
        return "📕"  # PDF
    elif ext in ['.doc', '.docx', '.odt']:
        return "📘"  # Документ Word
    elif ext in ['.xls', '.xlsx', '.csv', '.ods']:
        return "📊"  # Спредшит
    elif ext in ['.exe', '.msi', '.app', '.dmg']:
        return "🚀"  # Виконуваний файл
    return "📄"  # Звичайний файл


def run_gui_mode(start_path):
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, simpledialog
    except ImportError:
        # Автоматичний перехід на TUI за відсутності GUI
        tui = TerminalExplorer(start_path)
        tui.run()
        return

    class WindowsExplorerGUI(tk.Tk):
        def __init__(self, initial_dir):
            super().__init__()
            self.title("Провідник Windows 📂")
            self.geometry("980x640")
            self.minsize(800, 500)
            
            # Встановлюємо початковий шлях
            self.current_dir = os.path.abspath(initial_dir)
            self.history = [self.current_dir]
            self.history_index = 0
            
            # Сортування за замовчуванням: за іменем, за зростанням
            self.sort_column = "name"
            self.sort_descending = False

            # Побудова інтерфейсу та стилізація
            self.setup_windows_styles()
            self.build_ui_layout()
            self.load_directory(self.current_dir)

        def setup_windows_styles(self):
            """Задає чисті кольори, характерні для Windows Explorer (світла тема)."""
            self.style = ttk.Style(self)
            self.style.theme_use("clam")
            
            # Кольори Windows 10/11
            self.bg_window = "#ffffff"       # Фон списку файлів (білий)
            self.bg_panels = "#f3f3f3"       # Фон панелей та сайдбару (світло-сірий)
            self.border_color = "#d0d0d0"    # Колір меж (нейтральний сірий)
            self.accent_blue = "#0078d7"     # Синій колір Windows
            self.selected_bg = "#e5f3ff"     # М'яке синє виділення під час фокусу
            self.selected_fg = "#000000"     # Чорний текст при виділенні
            
            self.configure(background=self.bg_panels)

            # Налаштування стилів елементів
            self.style.configure(".", background=self.bg_panels, foreground="#000000", font=("Segoe UI", 10))
            self.style.configure("TFrame", background=self.bg_panels)
            
            # Кнопки навігації
            self.style.configure("Nav.TButton", background="#fcfcfc", borderwidth=1, relief="flat", font=("Segoe UI", 10))
            self.style.map("Nav.TButton", 
                           background=[("active", "#e5e5e5"), ("pressed", "#cccccc")],
                           relief=[("pressed", "sunken")])
            
            # Сайдбар кнопки швидкого доступу
            self.style.configure("Sidebar.TButton", anchor="w", padding=(15, 4), background=self.bg_panels, borderwidth=0, relief="flat", font=("Segoe UI", 10))
            self.style.map("Sidebar.TButton",
                           background=[("active", "#e5f3ff"), ("pressed", "#cce8ff")],
                           foreground=[("active", "#000000")])

            # Стилізація таблиці Treeview
            self.style.configure("Treeview", 
                                 background=self.bg_window, 
                                 fieldbackground=self.bg_window, 
                                 rowheight=26, 
                                 borderwidth=1, 
                                 borderColor=self.border_color,
                                 font=("Segoe UI", 10))
            
            self.style.configure("Treeview.Heading", 
                                 background="#fafafa", 
                                 foreground="#000000", 
                                 font=("Segoe UI", 9, "bold"), 
                                 relief="flat", 
                                 padding=(6, 4))
            
            self.style.map("Treeview.Heading",
                           background=[("active", "#e5f3ff")])
            
            # Створюємо чисте виділення без затінення тексту чорним кольором
            self.style.map("Treeview", 
                           background=[("selected", self.selected_bg)], 
                           foreground=[("selected", self.selected_fg)])

        def build_ui_layout(self):
            # 1. Головне меню дій (Панель інструментів у стилі Стрічки Windows)
            ribbon_frame = ttk.Frame(self, padding=(10, 5), borderwidth=1, relief="solid")
            ribbon_frame.pack(fill=tk.X, side=tk.TOP, ipady=2)
            
            # Колір рамки стрічки
            ribbon_frame.config()

            # Кнопки швидких дій на стрічці
            self.btn_ribbon_newfolder = ttk.Button(ribbon_frame, text="📁 Нова папка", style="Nav.TButton", command=self.gui_mkdir)
            self.btn_ribbon_newfolder.pack(side=tk.LEFT, padx=3)

            self.btn_ribbon_newfile = ttk.Button(ribbon_frame, text="📄 Новий файл", style="Nav.TButton", command=self.gui_touch)
            self.btn_ribbon_newfile.pack(side=tk.LEFT, padx=3)

            self.btn_ribbon_edit = ttk.Button(ribbon_frame, text="📝 Редагувати", style="Nav.TButton", command=self.gui_edit_selected)
            self.btn_ribbon_edit.pack(side=tk.LEFT, padx=3)

            self.btn_ribbon_rename = ttk.Button(ribbon_frame, text="🏷️ Перейменувати", style="Nav.TButton", command=self.gui_rename)
            self.btn_ribbon_rename.pack(side=tk.LEFT, padx=3)

            self.btn_ribbon_delete = ttk.Button(ribbon_frame, text="❌ Видалити", style="Nav.TButton", command=self.gui_delete)
            self.btn_ribbon_delete.pack(side=tk.LEFT, padx=3)

            self.btn_ribbon_props = ttk.Button(ribbon_frame, text="ℹ️ Властивості", style="Nav.TButton", command=self.gui_show_properties)
            self.btn_ribbon_props.pack(side=tk.LEFT, padx=3)

            # 2. Панель адреси (Навігація) та вікно Пошуку
            nav_frame = ttk.Frame(self, padding=(10, 5))
            nav_frame.pack(fill=tk.X, side=tk.TOP)

            # Кнопка Назад
            self.btn_back = ttk.Button(nav_frame, text="⬅", width=3, style="Nav.TButton", command=self.go_back)
            self.btn_back.pack(side=tk.LEFT, padx=1)

            # Кнопка Вперед
            self.btn_forward = ttk.Button(nav_frame, text="➡", width=3, style="Nav.TButton", command=self.go_forward)
            self.btn_forward.pack(side=tk.LEFT, padx=1)

            # Кнопка Вгору
            self.btn_up = ttk.Button(nav_frame, text="⬆", width=3, style="Nav.TButton", command=self.go_up)
            self.btn_up.pack(side=tk.LEFT, padx=1)

            # Кнопка Оновити
            self.btn_refresh = ttk.Button(nav_frame, text="🔄", width=3, style="Nav.TButton", command=lambda: self.load_directory(self.current_dir))
            self.btn_refresh.pack(side=tk.LEFT, padx=2)

            # Поле введення поточної адреси (Адресна строка)
            self.entry_path = ttk.Entry(nav_frame, font=("Segoe UI", 10))
            self.entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
            self.entry_path.bind("<Return>", lambda e: self.go_to_entered_path())

            # Поле швидкого Пошуку (Windows Search Box) у правому кутку
            self.search_var = tk.StringVar()
            self.search_var.set("🔍 Пошук у цій папці...")
            self.entry_search = ttk.Entry(nav_frame, textvariable=self.search_var, font=("Segoe UI", 9, "italic"), width=25)
            self.entry_search.pack(side=tk.RIGHT, padx=2)
            
            # Ефекти фокусу для поля пошуку
            self.entry_search.bind("<FocusIn>", self.on_search_focus_in)
            self.entry_search.bind("<FocusOut>", self.on_search_focus_out)
            self.entry_search.bind("<KeyRelease>", lambda e: self.on_search_key_release())

            # 3. Розділювальна панель (Сайдбар Швидкого доступу ліворуч, Дерево файлів праворуч)
            paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
            paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 5))

            # Бічна панель (Sidebar) у стилі "Цей ПК"
            sidebar = ttk.Frame(paned_window, width=200, padding=(5, 10), borderwidth=1, relief="solid")
            sidebar.pack_propagate(False)
            paned_window.add(sidebar, weight=1)

            lbl_quick_access = ttk.Label(sidebar, text="⭐ Швидкий доступ", font=("Segoe UI", 9, "bold"))
            lbl_quick_access.pack(anchor=tk.W, pady=(0, 5), padx=5)

            # Кнопки швидкого доступу з емодзі
            user_home = os.path.expanduser("~")
            shortcuts = [
                ("🖥️ Робочий стіл", os.path.join(user_home, "Desktop")),
                ("📥 Завантаження", os.path.join(user_home, "Downloads")),
                ("📄 Документи", os.path.join(user_home, "Documents")),
                ("🖼️ Зображення", os.path.join(user_home, "Pictures")),
                ("🎵 Музика", os.path.join(user_home, "Music")),
                ("🎬 Відео", os.path.join(user_home, "Videos"))
            ]

            # Додаємо робочі папки, якщо вони існують
            for label, path in shortcuts:
                if os.path.exists(path):
                    btn = ttk.Button(sidebar, text=label, style="Sidebar.TButton", command=lambda p=path: self.load_directory(p))
                    btn.pack(fill=tk.X, anchor=tk.W, pady=1)

            # Секція "Цей ПК"
            lbl_this_pc = ttk.Label(sidebar, text="💻 Цей ПК", font=("Segoe UI", 9, "bold"))
            lbl_this_pc.pack(anchor=tk.W, pady=(15, 5), padx=5)

            # Головний диск C: (або Root / на UNIX)
            root_path = "C:\\" if platform.system() == "Windows" else "/"
            btn_root = ttk.Button(sidebar, text=f"💾 Локальний диск ({root_path})", style="Sidebar.TButton", command=lambda: self.load_directory(root_path))
            btn_root.pack(fill=tk.X, anchor=tk.W, pady=1)

            # Робочий каталог нашого проекту
            btn_project = ttk.Button(sidebar, text="📂 Поточний проект", style="Sidebar.TButton", command=lambda: self.load_directory(os.getcwd()))
            btn_project.pack(fill=tk.X, anchor=tk.W, pady=1)

            # Головний список файлів (Таблиця Treeview з 4 стовпцями як у Windows)
            main_list_frame = ttk.Frame(paned_window, padding=2)
            paned_window.add(main_list_frame, weight=4)

            # Скролбари
            scroll_y = ttk.Scrollbar(main_list_frame, orient=tk.VERTICAL)
            scroll_x = ttk.Scrollbar(main_list_frame, orient=tk.HORIZONTAL)

            self.tree = ttk.Treeview(
                main_list_frame, 
                columns=("name", "mtime", "type", "size"), 
                show="headings",
                yscrollcommand=scroll_y.set,
                xscrollcommand=scroll_x.set
            )
            
            scroll_y.config(command=self.tree.yview)
            scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
            scroll_x.config(command=self.tree.xview)
            scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
            self.tree.pack(fill=tk.BOTH, expand=True)

            # Заголовки стовпців з підтримкою сортування
            self.tree.heading("name", text="Ім'я", anchor=tk.W, command=lambda: self.sort_by_column("name"))
            self.tree.heading("mtime", text="Дата змінення", anchor=tk.W, command=lambda: self.sort_by_column("mtime"))
            self.tree.heading("type", text="Тип", anchor=tk.W, command=lambda: self.sort_by_column("type"))
            self.tree.heading("size", text="Розмір", anchor=tk.E, command=lambda: self.sort_by_column("size"))

            # Пропорції ширини стовпців
            self.tree.column("name", width=340, minwidth=150, anchor=tk.W)
            self.tree.column("mtime", width=140, minwidth=100, anchor=tk.W)
            self.tree.column("type", width=140, minwidth=80, anchor=tk.W)
            self.tree.column("size", width=100, minwidth=80, anchor=tk.E)

            # Події подвійного кліку та правої кнопки миші
            self.tree.bind("<Double-1>", lambda e: self.on_double_click_item())
            self.tree.bind("<Button-3>", self.show_context_menu) # Windows права кнопка
            self.tree.bind("<Button-2>", self.show_context_menu) # для macOS

            # Створення контекстного меню
            self.context_menu = tk.Menu(self, tearoff=0, font=("Segoe UI", 10))
            self.context_menu.add_command(label="📂 Відкрити", command=self.on_double_click_item)
            self.context_menu.add_command(label="📝 Редагувати в Блокноті", command=self.gui_edit_selected)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="📁 Створити папку", command=self.gui_mkdir)
            self.context_menu.add_command(label="📄 Створити файл", command=self.gui_touch)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="🏷️ Перейменувати", command=self.gui_rename)
            self.context_menu.add_command(label="❌ Видалити", command=self.gui_delete)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="ℹ️ Властивості", command=self.gui_show_properties)

            # 4. Нижня статусна панель (Status Bar)
            status_frame = ttk.Frame(self, padding=(10, 3), borderwidth=1, relief="solid")
            status_frame.pack(fill=tk.X, side=tk.BOTTOM)
            
            self.lbl_status = ttk.Label(status_frame, text="Кількість елементів: 0", font=("Segoe UI", 9))
            self.lbl_status.pack(side=tk.LEFT)

            self.lbl_selected_status = ttk.Label(status_frame, text="", font=("Segoe UI", 9))
            self.lbl_selected_status.pack(side=tk.RIGHT, padx=15)

            # Зв'язуємо клік по виділенню зі статусною панеллю
            self.tree.bind("<<TreeviewSelect>>", self.on_selection_change)

        # --- КЕРУВАННЯ ПОШУКОМ ---
        def on_search_focus_in(self, event):
            if self.search_var.get() == "🔍 Пошук у цій папці...":
                self.search_var.set("")
                self.entry_search.config(font=("Segoe UI", 10, "normal"))

        def on_search_focus_out(self, event):
            if not self.search_var.get().strip():
                self.search_var.set("🔍 Пошук у цій папці...")
                self.entry_search.config(font=("Segoe UI", 9, "italic"))

        def on_search_key_release(self):
            query = self.search_var.get().strip()
            if not query or query == "🔍 Пошук у цій папці...":
                self.load_directory(self.current_dir)
                return
            
            # Виконуємо пошук «на льоту» у поточній папці
            self.filter_directory_view(query)

        def filter_directory_view(self, pattern):
            """Фільтрує відображувані елементи відповідно до запиту пошуку."""
            for row in self.tree.get_children():
                self.tree.delete(row)

            try:
                items = os.listdir(self.current_dir)
            except Exception:
                return

            folders = []
            files = []
            pattern_lower = pattern.lower()
            
            for item in items:
                if pattern_lower not in item.lower():
                    continue
                p = os.path.join(self.current_dir, item)
                try:
                    is_dir = os.path.isdir(p)
                    stat = os.stat(p)
                    mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                    emoji = get_file_emoji(item, is_dir)
                    
                    if is_dir:
                        folders.append((f"{emoji} {item}", "Папка", "", mtime, item))
                    else:
                        ext_desc = f"Файл {os.path.splitext(item)[1].upper()}" if os.path.splitext(item)[1] else "Файл"
                        folders.append((f"{emoji} {item}", ext_desc, get_readable_size(stat.st_size), mtime, item))
                except Exception:
                    continue

            # Сортування
            folders.sort(key=lambda x: x[4].lower())
            
            for item_view in folders:
                self.tree.insert("", tk.END, values=(item_view[0], item_view[3], item_view[1], item_view[2]))

        # --- СОРТУВАННЯ СТОВПЦІВ ---
        def sort_by_column(self, col):
            """Сортує таблицю за кліком на заголовок стовпця (як у Windows)."""
            if self.sort_column == col:
                # Змінюємо напрямок
                self.sort_descending = not self.sort_descending
            else:
                self.sort_column = col
                self.sort_descending = False
            
            self.load_directory(self.current_dir)

        # --- НАВІГАЦІЯ ТА ВІДКРИТТЯ ---
        def load_directory(self, target_dir):
            """Зчитує та відображає файли і папки з сортуванням."""
            target_dir = os.path.abspath(target_dir)
            if not os.path.isdir(target_dir):
                messagebox.showerror("Помилка навігації", f"Папки не існує:\n{target_dir}")
                return

            try:
                items = os.listdir(target_dir)
            except PermissionError:
                messagebox.showerror("Доступ обмежено", f"Немає прав доступу до цієї директорії:\n{target_dir}")
                return
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося відкрити папку:\n{e}")
                return

            self.current_dir = target_dir
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, self.current_dir)

            # Запис в історію переходів
            if not self.history or self.history[self.history_index] != self.current_dir:
                self.history = self.history[:self.history_index + 1]
                self.history.append(self.current_dir)
                self.history_index = len(self.history) - 1

            # Очищення таблиці
            for row in self.tree.get_children():
                self.tree.delete(row)

            folders_list = []
            files_list = []
            
            for item in items:
                p = os.path.join(self.current_dir, item)
                try:
                    is_dir = os.path.isdir(p)
                    stat = os.stat(p)
                    mtime_raw = stat.st_mtime
                    mtime_str = datetime.datetime.fromtimestamp(mtime_raw).strftime('%Y-%m-%d %H:%M')
                    emoji = get_file_emoji(item, is_dir)
                    
                    if is_dir:
                        folders_list.append({
                            "display_name": f"{emoji} {item}",
                            "raw_name": item,
                            "type": "Папка з файлами",
                            "size": -1, # для папок розмір не пишем
                            "size_str": "",
                            "mtime": mtime_str,
                            "mtime_raw": mtime_raw
                        })
                    else:
                        ext = os.path.splitext(item)[1].upper()
                        ext_desc = f"Файл {ext}" if ext else "Файл"
                        files_list.append({
                            "display_name": f"{emoji} {item}",
                            "raw_name": item,
                            "type": ext_desc,
                            "size": stat.st_size,
                            "size_str": get_readable_size(stat.st_size),
                            "mtime": mtime_str,
                            "mtime_raw": mtime_raw
                        })
                except Exception:
                    continue

            # Сортування відповідно до обраного стовпця та правил Windows (Папки завжди перші!)
            def get_sort_key(el):
                if self.sort_column == "name":
                    return el["raw_name"].lower()
                elif self.sort_column == "mtime":
                    return el["mtime_raw"]
                elif self.sort_column == "type":
                    return el["type"].lower()
                elif self.sort_column == "size":
                    return el["size"]
                return el["raw_name"].lower()

            rev = self.sort_descending
            folders_list.sort(key=get_sort_key, reverse=rev)
            files_list.sort(key=get_sort_key, reverse=rev)

            # Виводимо спочатку папки, потім файли
            all_elements = folders_list + files_list if not rev else files_list + folders_list
            for el in all_elements:
                self.tree.insert("", tk.END, values=(el["display_name"], el["mtime"], el["type"], el["size_str"]))

            # Оновлюємо нижній статус-бар
            self.lbl_status.config(text=f"Елементів: {len(items)} | Папок: {len(folders_list)} | Файлів: {len(files_list)}")
            self.lbl_selected_status.config(text="")

        def on_selection_change(self, event):
            selected = self.tree.selection()
            if not selected:
                self.lbl_selected_status.config(text="")
                return
            
            # Підрахунок сумарного розміру обраних елементів
            sizes = []
            for sel in selected:
                vals = self.tree.item(sel, "values")
                name = vals[0][2:] # видаляємо емодзі
                p = os.path.join(self.current_dir, name)
                if os.path.isfile(p):
                    sizes.append(os.path.getsize(p))
            
            if len(selected) == 1:
                vals = self.tree.item(selected[0], "values")
                self.lbl_selected_status.config(text=f"Виділено 1 елемент: {vals[0][2:]}")
            else:
                total_sz = get_readable_size(sum(sizes))
                self.lbl_selected_status.config(text=f"Виділено елементів: {len(selected)} (Розмір файлів: {total_sz})")

        def on_double_click_item(self):
            selected = self.tree.selection()
            if not selected: return
            
            vals = self.tree.item(selected[0], "values")
            raw_name = vals[0][2:]
            item_type = vals[2]
            full_path = os.path.join(self.current_dir, raw_name)

            if item_type == "Папка з файлами":
                self.load_directory(full_path)
            else:
                # Намагаємося розпізнати текстові кодові файли і відкрити їх у Блокноті
                ext = os.path.splitext(raw_name)[1].lower()
                if ext in ['.txt', '.py', '.jl', '.log', '.md', '.ini', '.cfg', '.json', '.yaml', '.yml', '.sh', '.bat']:
                    self.gui_view_file(full_path, raw_name)
                else:
                    # Запуск системним додатком за замовчуванням
                    try:
                        if platform.system() == "Windows":
                            os.startfile(full_path)
                        elif platform.system() == "Darwin": # macOS
                            subprocess.run(["open", full_path], check=True)
                        else: # Linux
                            subprocess.run(["xdg-open", full_path], check=True)
                    except Exception as e:
                        # Якщо не вдалося, показуємо Блокнот як fallback
                        self.gui_view_file(full_path, raw_name)

        def show_context_menu(self, event):
            # Виділяємо рядок під мишкою
            row_id = self.tree.identify_row(event.y)
            if row_id:
                self.tree.selection_set(row_id)
                self.context_menu.post(event.x_root, event.y_row if hasattr(event, "y_row") else event.y_root)

        # --- НАВІГАЦІЯ ІСТОРІЇ ---
        def go_back(self):
            if self.history_index > 0:
                self.history_index -= 1
                self.load_directory(self.history[self.history_index])

        def go_forward(self):
            if self.history_index < len(self.history) - 1:
                self.history_index += 1
                self.load_directory(self.history[self.history_index])

        def go_up(self):
            parent = os.path.dirname(self.current_dir)
            if parent != self.current_dir:
                self.load_directory(parent)

        def go_to_entered_path(self):
            entered = self.entry_path.get().strip()
            if os.path.isdir(entered):
                self.load_directory(entered)
            else:
                messagebox.showerror("Помилка шляху", f"Провідник не може знайти вказану папку:\n{entered}")

        # --- ОПЕРАЦІЇ З ФАЙЛАМИ (ДІЇ WINDOWS) ---
        def gui_mkdir(self):
            name = simpledialog.askstring("Створення папки", "Введіть ім'я нової папки:")
            if name:
                p = os.path.join(self.current_dir, name)
                try:
                    os.makedirs(p)
                    self.load_directory(self.current_dir)
                except Exception as e:
                    messagebox.showerror("Помилка", f"Не вдалося створити папку:\n{e}")

        def gui_touch(self):
            name = simpledialog.askstring("Створення файлу", "Введіть ім'я нового файлу:")
            if name:
                p = os.path.join(self.current_dir, name)
                try:
                    with open(p, 'w', encoding='utf-8') as f:
                        f.write("")
                    self.load_directory(self.current_dir)
                    # Відкриваємо файл у Блокноті відразу після створення
                    self.gui_view_file(p, name)
                except Exception as e:
                    messagebox.showerror("Помилка", f"Не вдалося створити файл:\n{e}")

        def gui_rename(self):
            selected = self.tree.selection()
            if not selected: return
            
            vals = self.tree.item(selected[0], "values")
            old_name = vals[0][2:]
            
            new_name = simpledialog.askstring("Перейменування", f"Введіть нове ім'я для '{old_name}':", initialvalue=old_name)
            if new_name and new_name != old_name:
                old_p = os.path.join(self.current_dir, old_name)
                new_p = os.path.join(self.current_dir, new_name)
                try:
                    os.rename(old_p, new_p)
                    self.load_directory(self.current_dir)
                except Exception as e:
                    messagebox.showerror("Помилка перейменування", f"Не вдалося перейменувати елемент:\n{e}")

        def gui_delete(self):
            selected = self.tree.selection()
            if not selected: return

            vals = self.tree.item(selected[0], "values")
            raw_name = vals[0][2:]
            item_type = vals[2]
            full_path = os.path.join(self.current_dir, raw_name)

            confirm = messagebox.askyesno("Видалення", f"Ви впевнені, що хочете видалити {item_type.lower()} '{raw_name}'?")
            if confirm:
                try:
                    if os.path.isdir(full_path):
                        try:
                            os.rmdir(full_path)
                        except OSError:
                            shutil.rmtree(full_path)
                    else:
                        os.remove(full_path)
                    self.load_directory(self.current_dir)
                except Exception as e:
                    messagebox.showerror("Помилка видалення", f"Не вдалося видалити елемент:\n{e}")

        def gui_edit_selected(self):
            selected = self.tree.selection()
            if not selected: return
            vals = self.tree.item(selected[0], "values")
            raw_name = vals[0][2:]
            full_path = os.path.join(self.current_dir, raw_name)
            if os.path.isfile(full_path):
                self.gui_view_file(full_path, raw_name)

        # --- ВБУДОВАНИЙ БЛОКНОТ (WINDOWS NOTEPAD WITH EDIT & SAVE) ---
        def gui_view_file(self, full_path, raw_name):
            notepad = tk.Toplevel(self)
            notepad.title(f"{raw_name} — Блокнот")
            notepad.geometry("700x500")
            
            # Створюємо меню блокнота
            menu_bar = tk.Menu(notepad)
            notepad.config(menu=menu_bar)
            
            # Меню Файл
            file_menu = tk.Menu(menu_bar, tearoff=0)
            menu_bar.add_cascade(label="Файл", menu=file_menu)
            
            # Скролбари та текстове поле
            text_frame = ttk.Frame(notepad, padding=2)
            text_frame.pack(fill=tk.BOTH, expand=True)

            scroll_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
            scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
            
            scroll_x = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
            scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

            text_area = tk.Text(text_frame, wrap=tk.NONE, font=("Consolas", 11), 
                                yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                                background="#ffffff", foreground="#000000")
            text_area.pack(fill=tk.BOTH, expand=True)
            
            scroll_y.config(command=text_area.yview)
            scroll_x.config(command=text_area.xview)

            # Завантажуємо текст
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    text_area.insert(tk.END, content)
            except Exception as e:
                text_area.insert(tk.END, f"Помилка зчитування файлу:\n{e}")

            # Збереження змін
            def save_notepad_changes():
                try:
                    updated_content = text_area.get("1.0", tk.END)
                    # Останній символ перенесення рядка Tkinter видаляємо
                    if updated_content.endswith('\n'):
                        updated_content = updated_content[:-1]
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    messagebox.showinfo("Блокнот", "Зміни успішно збережено!")
                    self.load_directory(self.current_dir) # оновити список
                except Exception as ex:
                    messagebox.showerror("Помилка збереження", f"Не вдалося зберегти зміни:\n{ex}")

            file_menu.add_command(label="💾 Зберегти", command=save_notepad_changes)
            file_menu.add_separator()
            file_menu.add_command(label="❌ Вийти", command=notepad.destroy)

            # Статус-бар блокнота
            lbl_not_status = ttk.Label(notepad, text=f" Кодування: UTF-8 | Шлях: {full_path}", font=("Segoe UI", 9, "italic"))
            lbl_not_status.pack(side=tk.BOTTOM, anchor=tk.W, pady=3)

        # --- ВІКНО ВЛАСТИВОСТЕЙ WINDOWS (PROPERTIES DIALOG) ---
        def gui_show_properties(self):
            selected = self.tree.selection()
            if not selected: return

            vals = self.tree.item(selected[0], "values")
            raw_name = vals[0][2:]
            item_type = vals[2]
            full_path = os.path.join(self.current_dir, raw_name)

            if not os.path.exists(full_path): return

            stat = os.stat(full_path)
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%d %B %Y р., %H:%M:%S')
            ctime = datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%d %B %Y р., %H:%M:%S')
            atime = datetime.datetime.fromtimestamp(stat.st_atime).strftime('%d %B %Y р., %H:%M:%S')

            # Створення діалогу властивостей у стилі Windows
            prop_dialog = tk.Toplevel(self)
            prop_dialog.title(f"Властивості: {raw_name}")
            prop_dialog.geometry("380x480")
            prop_dialog.resizable(False, False)
            prop_dialog.configure(background="#f0f0f0")

            # Вкладки властивостей
            notebook = ttk.Notebook(prop_dialog)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            tab_general = ttk.Frame(notebook, padding=15)
            notebook.add(tab_general, text="Загальні")

            # Рядок 1: Назва та велика іконка
            emoji = get_file_emoji(raw_name, os.path.isdir(full_path))
            header_frame = ttk.Frame(tab_general)
            header_frame.pack(fill=tk.X, pady=(0, 15))
            
            lbl_big_icon = ttk.Label(header_frame, text=emoji, font=("Segoe UI", 36))
            lbl_big_icon.pack(side=tk.LEFT, padx=(5, 15))

            name_var = tk.StringVar(value=raw_name)
            entry_rename_prop = ttk.Entry(header_frame, textvariable=name_var, font=("Segoe UI", 11, "bold"))
            entry_rename_prop.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=10)

            # Розділювач
            ttk.Separator(tab_general, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

            # Деталі
            details_frame = ttk.Frame(tab_general)
            details_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            def add_prop_row(label, val):
                row = ttk.Frame(details_frame)
                row.pack(fill=tk.X, pady=3)
                ttk.Label(row, text=label, font=("Segoe UI", 9, "bold"), width=15, anchor=tk.W).pack(side=tk.LEFT)
                ttk.Label(row, text=val, font=("Segoe UI", 9), justify=tk.LEFT).pack(side=tk.LEFT, fill=tk.X, expand=True)

            add_prop_row("Тип елемента:", item_type)
            add_prop_row("Розташування:", os.path.dirname(full_path))
            
            if os.path.isdir(full_path):
                # Підраховуємо елементи всередині папки
                try:
                    sub_items = os.listdir(full_path)
                    add_prop_row("Вміст:", f"Папок/файлів: {len(sub_items)}")
                except Exception:
                    add_prop_row("Вміст:", "Немає доступу")
            else:
                add_prop_row("Розмір:", f"{stat.st_size} байт ({get_readable_size(stat.st_size)})")

            # Розділювач
            ttk.Separator(tab_general, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

            # Дати створення/зміни
            add_prop_row("Створено:", ctime)
            add_prop_row("Змінено:", mtime)
            add_prop_row("Доступ:", atime)

            # Кнопка збереження нової назви
            def save_props():
                new_name = name_var.get().strip()
                if new_name and new_name != raw_name:
                    try:
                        os.rename(full_path, os.path.join(self.current_dir, new_name))
                        self.load_directory(self.current_dir)
                    except Exception as e:
                        messagebox.showerror("Помилка", f"Не вдалося перейменувати:\n{e}")
                prop_dialog.destroy()

            # Панель кнопок Ок / Скасувати у нижній частині
            btn_frame = ttk.Frame(prop_dialog, padding=5)
            btn_frame.pack(fill=tk.X, side=tk.BOTTOM)

            btn_ok = ttk.Button(btn_frame, text="OK", width=10, command=save_props)
            btn_ok.pack(side=tk.RIGHT, padx=5, pady=5)

            btn_cancel = ttk.Button(btn_frame, text="Скасувати", width=10, command=prop_dialog.destroy)
            btn_cancel.pack(side=tk.RIGHT, padx=5, pady=5)


    # Ініціалізуємо графічний додаток
    app = WindowsExplorerGUI(start_path)
    app.mainloop()


# ====================================================================
# 3. ТОЧКА ВХОДУ В ПРОГРАМУ
# ====================================================================

def main():
    parser = argparse.ArgumentParser(description="Провідник Файлів на Python у стилі Windows Explorer (v3.0)")
    parser.add_argument("--tui", action="store_true", help="Примусово запустити в консольному TUI-режимі")
    parser.add_argument("path", nargs="?", default=os.getcwd(), help="Стартова директорія для огляду")
    
    args = parser.parse_args()

    # Спроба запуску у віконному GUI режимі (якщо не передано прапорець --tui)
    if not args.tui:
        try:
            run_gui_mode(args.path)
        except Exception as e:
            # Fallback на TUI
            print(f"Помилка ініціалізації GUI ({e}). Перехід у консольний режим...")
            explorer = TerminalExplorer(args.path)
            explorer.run()
    else:
        explorer = TerminalExplorer(args.path)
        explorer.run()


if __name__ == '__main__':
    main()
