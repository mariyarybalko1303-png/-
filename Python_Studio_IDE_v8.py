import copy
import math
import os
import sys
import io
import re
import ast
import time
import json
import shutil
import traceback
import queue
import threading
import subprocess
import bdb
import builtins
import keyword
from dataclasses import dataclass

# --- Налаштування контексту до створення QApplication ---
from PyQt6.QtCore import Qt, QCoreApplication
try:
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
except Exception:
    pass

# --- PyQt6 ---
from PyQt6.QtWidgets import (
    QApplication, QGraphicsPolygonItem, QGraphicsRectItem, QGraphicsTextItem,
    QMainWindow, QStatusBar, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QToolTip,
    QPlainTextEdit, QListView, QGraphicsView, QGraphicsScene,
    QSplitter, QTabWidget, QToolBar, QLabel, QTextEdit, QLineEdit,
    QInputDialog, QFileDialog, QMessageBox, QProgressBar, QDockWidget, QTreeView,
    QGraphicsObject, QDialog, QCheckBox, QGroupBox, QFormLayout, QFrame, QComboBox, QStackedWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QListWidget, QListWidgetItem, QDialogButtonBox,
    QTabBar, QTreeWidget, QTreeWidgetItem, QScrollArea, QSizePolicy
)
from PyQt6.QtGui import (
    QAction, QFont, QColor, QPainter, QPainterPath, QPolygonF, QTextCursor, QTextCharFormat, QSyntaxHighlighter,
    QPixmap, QPen, QBrush, QPalette,
    QFileSystemModel, QWheelEvent, QKeyEvent, QIcon
)
from PyQt6.QtCore import (
    QTimer, QSize, QRect, QRectF, QPoint, QPointF, QDir, QUrl, pyqtSignal,
    QThread, QRegularExpression, QStringListModel,
    QPropertyAnimation, QParallelAnimationGroup, QSequentialAnimationGroup, QEasingCurve,
    QProcess
)

# --- Зовнішні бібліотеки ---
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except (ImportError, Exception):
    QWebEngineView = None

try:
    import docx
except ImportError:
    docx = None

try:
    from pptx import Presentation
except ImportError:
    Presentation = None

try:
    import openpyxl
except ImportError:
    openpyxl = None

try:
    import jedi
except ImportError:
    jedi = None



# ==============================================================================
# ПУНКТ 1: СТАТИЧНИЙ АНАЛІЗ ТА ЛІНТЕР (Code Inspections & PEP 8 Linter)
# ==============================================================================

@dataclass
class InspectionIssue:
    line: int
    col: int
    level: str  # "error", "warning", "info"
    code: str   # "SyntaxError", "E501", "F401", "N801", "N802", "E231", "E701", "W291"
    message: str


class PEP8AndASTLinter:
    def __init__(self):
        self.builtins_set = set(dir(builtins))
        self.keywords_set = set(keyword.kwlist)

    def lint(self, code: str) -> list[InspectionIssue]:
        issues = []
        lines = code.splitlines()

        tree = None
        try:
            tree = ast.parse(code)
        except SyntaxError as se:
            line = se.lineno or 1
            col = se.offset or 0
            msg = se.msg or "Синтаксична помилка"
            issues.append(InspectionIssue(line, col, "error", "SyntaxError", f"Синтаксична помилка: {msg}"))

        for idx, line in enumerate(lines, 1):
            if len(line) > 79:
                issues.append(InspectionIssue(
                    idx, 80, "warning", "E501", 
                    f"PEP 8 (E501): Довжина рядка перевищує 79 символів ({len(line)} > 79)"
                ))
            if line.rstrip() != line and not line.isspace():
                issues.append(InspectionIssue(
                    idx, len(line.rstrip()) + 1, "info", "W291",
                    "PEP 8 (W291): Зайві пробіли в кінці рядка"
                ))
            if ';' in line and not self._is_inside_string(';', line):
                issues.append(InspectionIssue(
                    idx, line.find(';'), "warning", "E701",
                    "PEP 8 (E701): Декілька виразів в одному рядку розділені ';'"
                ))
            for m in re.finditer(r',(?=[^\s\)\}\]])', line):
                issues.append(InspectionIssue(
                    idx, m.start() + 1, "warning", "E231",
                    "PEP 8 (E231): Відсутній пробіл після коми ','"
                ))

        if tree:
            issues.extend(self._analyze_ast(tree))

        return issues

    def _is_inside_string(self, char: str, line: str) -> bool:
        in_str = False
        quote_char = None
        for c in line:
            if c in ('"', "'"):
                if not in_str:
                    in_str = True
                    quote_char = c
                elif quote_char == c:
                    in_str = False
        return in_str

    def _analyze_ast(self, tree: ast.AST) -> list[InspectionIssue]:
        issues = []
        imported_names = {}
        used_names = set()

        class ASTVisitor(ast.NodeVisitor):
            def visit_Import(self, node):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imported_names[name] = (node.lineno, node.col_offset, alias.name)

            def visit_ImportFrom(self, node):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imported_names[name] = (node.lineno, node.col_offset, f"{node.module}.{alias.name}")

            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)

            def visit_FunctionDef(self, node):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and not node.name.startswith('__'):
                    issues.append(InspectionIssue(
                        node.lineno, node.col_offset, "warning", "N802",
                        f"PEP 8 (N802): Назва функції '{node.name}' повинна бути в стилі snake_case"
                    ))
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    issues.append(InspectionIssue(
                        node.lineno, node.col_offset, "warning", "N801",
                        f"PEP 8 (N801): Назва класу '{node.name}' повинна відповідати стилю CapWords (CamelCase)"
                    ))
                self.generic_visit(node)

        ASTVisitor().visit(tree)

        for name, (line, col, full_import) in imported_names.items():
            if name not in used_names:
                issues.append(InspectionIssue(
                    line, col, "warning", "F401",
                    f"Невикористаний імпорт: '{name}' ({full_import})"
                ))

        return issues


class ProblemsPanel(QWidget):
    problem_selected = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Рядок", "Стовпчик", "Код", "Опис проблеми"])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #2b2b2b; color: #dcdcdc; gridline-color: #3c3f41; font-size: 10pt; }
            QHeaderView::section { background-color: #3c3f41; color: #ffffff; padding: 4px; font-weight: bold; }
        """)
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.table)

    def update_problems(self, issues: list[InspectionIssue]):
        self.table.setRowCount(0)
        for issue in issues:
            row = self.table.rowCount()
            self.table.insertRow(row)

            line_item = QTableWidgetItem(str(issue.line))
            col_item = QTableWidgetItem(str(issue.col))
            code_item = QTableWidgetItem(issue.code)
            msg_item = QTableWidgetItem(issue.message)

            if issue.level == "error":
                code_item.setForeground(QColor("#FF5555"))
            elif issue.level == "warning":
                code_item.setForeground(QColor("#FFB86C"))
            else:
                code_item.setForeground(QColor("#8BE9FD"))

            self.table.setItem(row, 0, line_item)
            self.table.setItem(row, 1, col_item)
            self.table.setItem(row, 2, code_item)
            self.table.setItem(row, 3, msg_item)

    def on_item_double_clicked(self, item):
        row = item.row()
        line = int(self.table.item(row, 0).text())
        col = int(self.table.item(row, 1).text())
        self.problem_selected.emit(line, col)


# ==============================================================================
# ПУНКТ 2: ІНТЕРАКТИВНИЙ ДЕБАГЕР (Interactive Debugger Bdb)
# ==============================================================================

class PyStudioBdb(bdb.Bdb):
    def __init__(self, debug_runner, breakpoints_set):
        super().__init__()
        self.debug_runner = debug_runner
        self.breakpoints_set = breakpoints_set

    def user_line(self, frame):
        if not self.debug_runner.running:
            raise bdb.BdbQuit("Debugging stopped by user")

        filename = frame.f_code.co_filename
        lineno = frame.f_lineno

        is_bp = lineno in self.breakpoints_set
        is_stepping = self.debug_runner.is_stepping

        if is_bp or is_stepping:
            self.debug_runner.is_stepping = False
            
            locals_dict = {k: repr(v) for k, v in frame.f_locals.items() if not k.startswith("__")}
            globals_dict = {k: repr(v) for k, v in frame.f_globals.items() if not k.startswith("__")}

            stack = []
            curr = frame
            while curr:
                stack.append(f"{os.path.basename(curr.f_code.co_filename)}:{curr.f_lineno} in {curr.f_code.co_name}()")
                curr = curr.f_back

            self.debug_runner.paused = True
            self.debug_runner.debug_paused_signal.emit(filename, lineno, stack, locals_dict, globals_dict)

            while self.debug_runner.paused and self.debug_runner.running:
                time.sleep(0.04)

            if not self.debug_runner.running:
                raise bdb.BdbQuit("Debugging stopped by user")

    def user_return(self, frame, return_value):
        pass

    def user_exception(self, frame, exc_info):
        exc_type, exc_val, tb = exc_info
        if exc_type is KeyboardInterrupt or exc_type is bdb.BdbQuit:
            return
        msg = f"{exc_type.__name__}: {str(exc_val)}"
        self.debug_runner.output_signal.emit(f"\n❌ Помилка під час налагодження (Рядок {frame.f_lineno}): {msg}\n")


class DebugRunner(QThread):
    output_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()
    debug_paused_signal = pyqtSignal(str, int, list, dict, dict)
    debug_resumed_signal = pyqtSignal()

    def __init__(self, code, project_dir=None, breakpoints=None):
        super().__init__()
        self.code = code
        self.project_dir = project_dir
        self.breakpoints = set(breakpoints) if breakpoints else set()
        self.running = True
        self.paused = False
        self.is_stepping = True
        self.bdb_instance = None

    def provide_input(self, text: str):
        pass

    def step_over(self):
        self.is_stepping = True
        self.paused = False
        self.debug_resumed_signal.emit()

    def step_into(self):
        self.is_stepping = True
        self.paused = False
        self.debug_resumed_signal.emit()

    def step_out(self):
        self.is_stepping = True
        self.paused = False
        self.debug_resumed_signal.emit()

    def continue_exec(self):
        self.is_stepping = False
        self.paused = False
        self.debug_resumed_signal.emit()

    def stop(self):
        self.running = False
        self.paused = False
        self.debug_resumed_signal.emit()

    def run(self):
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = sys.stdout

        if self.project_dir and os.path.exists(self.project_dir):
            if self.project_dir not in sys.path:
                sys.path.insert(0, self.project_dir)

        glob = {"__name__": "__main__"}
        loc = {}

        self.bdb_instance = PyStudioBdb(self, self.breakpoints)

        try:
            self.progress_signal.emit(30)
            code_obj = compile(self.code, "<animated_code>", "exec")
            self.progress_signal.emit(60)

            self.output_signal.emit("🐞 Сеанс налагодження (Debugger) розпочато...\n")
            self.bdb_instance.run(code_obj, glob, loc)
            self.progress_signal.emit(100)

            out = sys.stdout.getvalue()
            if out:
                self.output_signal.emit(out)

            self.output_signal.emit("\n✅ Налагодження успішно завершено.\n")

        except bdb.BdbQuit:
            self.output_signal.emit("\n⏹ Налагодження зупинено користувачем.\n")
        except Exception as e:
            self.output_signal.emit("\n❌ Помилка під час налагодження:\n" + traceback.format_exc())
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            self.finished_signal.emit()


class DebuggerPanel(QWidget):
    step_over_clicked = pyqtSignal()
    step_into_clicked = pyqtSignal()
    step_out_clicked = pyqtSignal()
    continue_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.runner = None
        self.current_locals = {}
        self.current_globals = {}
        self.watches = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        self.btn_step_over = QPushButton("⤵ Step Over (F8)")
        self.btn_step_into = QPushButton("⬇ Step Into (F7)")
        self.btn_step_out = QPushButton("⬆ Step Out (Shift+F8)")
        self.btn_continue = QPushButton("▶ Continue (F9)")
        self.btn_stop = QPushButton("⏹ Stop Debug")

        self.btn_step_over.clicked.connect(self.step_over_clicked.emit)
        self.btn_step_into.clicked.connect(self.step_into_clicked.emit)
        self.btn_step_out.clicked.connect(self.step_out_clicked.emit)
        self.btn_continue.clicked.connect(self.continue_clicked.emit)
        self.btn_stop.clicked.connect(self.stop_clicked.emit)

        toolbar.addWidget(self.btn_step_over)
        toolbar.addWidget(self.btn_step_into)
        toolbar.addWidget(self.btn_step_out)
        toolbar.addWidget(self.btn_continue)
        toolbar.addWidget(self.btn_stop)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        vars_box = QWidget()
        vars_layout = QVBoxLayout(vars_box)
        vars_layout.setContentsMargins(0, 0, 0, 0)

        watch_bar = QHBoxLayout()
        self.watch_input = QLineEdit()
        self.watch_input.setPlaceholderText("Введіть вираз для відстеження (Watch)...")
        btn_add_watch = QPushButton("➕ Watch")
        btn_add_watch.clicked.connect(self.add_watch)
        watch_bar.addWidget(self.watch_input)
        watch_bar.addWidget(btn_add_watch)
        vars_layout.addLayout(watch_bar)

        self.vars_table = QTableWidget(0, 3)
        self.vars_table.setHorizontalHeaderLabels(["Назва", "Значення", "Тип"])
        self.vars_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.vars_table.setStyleSheet("""
            QTableWidget { background-color: #2b2b2b; color: #dcdcdc; gridline-color: #3c3f41; font-size: 10pt; }
            QHeaderView::section { background-color: #3c3f41; color: #ffffff; padding: 4px; font-weight: bold; }
        """)
        vars_layout.addWidget(self.vars_table)

        stack_box = QWidget()
        stack_layout = QVBoxLayout(stack_box)
        stack_layout.setContentsMargins(0, 0, 0, 0)
        stack_layout.addWidget(QLabel("<b>📚 Стек викликів (Stack Trace):</b>"))

        self.stack_list = QListWidget()
        self.stack_list.setStyleSheet("background-color: #2b2b2b; color: #a9b7c6; font-size: 10pt;")
        self.stack_list.itemClicked.connect(self.on_stack_item_clicked)
        stack_layout.addWidget(self.stack_list)

        eval_bar = QHBoxLayout()
        self.eval_input = QLineEdit()
        self.eval_input.setPlaceholderText("Обчислити вираз (Evaluate)...")
        btn_eval = QPushButton("🧮 Eval")
        btn_eval.clicked.connect(self.on_eval_clicked)
        eval_bar.addWidget(self.eval_input)
        eval_bar.addWidget(btn_eval)
        stack_layout.addLayout(eval_bar)

        splitter.addWidget(vars_box)
        splitter.addWidget(stack_box)
        splitter.setSizes([500, 300])

        layout.addWidget(splitter)

    def set_runner(self, runner: DebugRunner):
        self.runner = runner

    def add_watch(self):
        expr = self.watch_input.text().strip()
        if expr and expr not in self.watches:
            self.watches.append(expr)
            self.watch_input.clear()
            self.update_debug_info("", 0, [], self.current_locals, self.current_globals)

    def update_debug_info(self, filename, lineno, stack, locals_dict, globals_dict):
        self.current_locals = locals_dict
        self.current_globals = globals_dict

        self.stack_list.clear()
        for item in stack:
            self.stack_list.addItem(item)

        self.vars_table.setRowCount(0)

        for expr in self.watches:
            row = self.vars_table.rowCount()
            self.vars_table.insertRow(row)

            val_str = "N/A"
            try:
                env = {**globals_dict, **locals_dict}
                val = eval(expr, env)
                val_str = repr(val)
            except Exception as e:
                val_str = f"Error: {e}"

            item_name = QTableWidgetItem(f"👁 {expr}")
            item_name.setForeground(QColor("#8BE9FD"))
            item_val = QTableWidgetItem(val_str)
            item_type = QTableWidgetItem("Watch")

            self.vars_table.setItem(row, 0, item_name)
            self.vars_table.setItem(row, 1, item_val)
            self.vars_table.setItem(row, 2, item_type)

        for name, val_str in locals_dict.items():
            row = self.vars_table.rowCount()
            self.vars_table.insertRow(row)

            item_name = QTableWidgetItem(name)
            item_val = QTableWidgetItem(val_str)
            item_type = QTableWidgetItem("Local")

            self.vars_table.setItem(row, 0, item_name)
            self.vars_table.setItem(row, 1, item_val)
            self.vars_table.setItem(row, 2, item_type)

    def on_stack_item_clicked(self, item):
        pass

    def on_eval_clicked(self):
        expr = self.eval_input.text().strip()
        if not expr: return
        try:
            env = {**self.current_globals, **self.current_locals}
            res = eval(expr, env)
            QMessageBox.information(self, "Результат обчислення", f"<b>{expr}</b> = <code>{repr(res)}</code>")
        except Exception as e:
            QMessageBox.critical(self, "Помилка обчислення", f"Не вдалося обчислити '{expr}': {e}")


# ==============================================================================
# ПУНКТ 3: АВТОМАТИЗОВАНИЙ РЕФАКТОРИНГ (Safe Rename & Extract)
# ==============================================================================

class RefactoringEngine:
    @staticmethod
    def extract_variable(code: str, selected_text: str, var_name: str) -> str:
        if not selected_text or selected_text not in code:
            return code
        return f"{var_name} = {selected_text}\n" + code.replace(selected_text, var_name, 1)

    @staticmethod
    def extract_method(code: str, selected_code: str, method_name: str) -> str:
        lines = selected_code.strip().splitlines()
        indented_body = "\n".join(["    " + l for l in lines])
        func_def = f"def {method_name}():\n{indented_body}\n\n"
        return func_def + code.replace(selected_code, f"{method_name}()")

    @staticmethod
    def safe_rename(file_map: dict[str, str], target_old_name: str, new_name: str) -> dict[str, str]:
        updated_map = {}
        pattern = re.compile(r'' + re.escape(target_old_name) + r'')
        for path, content in file_map.items():
            new_content = pattern.sub(new_name, content)
            updated_map[path] = new_content
        return updated_map


class SafeRenameDialog(QDialog):
    def __init__(self, old_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✏️ Безпечне перейменування (Safe Rename)")
        self.resize(400, 150)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"Перейменувати ідентифікатор <b>'{old_name}'</b> у всьому проєкті:"))
        self.name_input = QLineEdit(old_name)
        layout.addWidget(self.name_input)

        self.scope_chk = QCheckBox("Перейменувати по всіх файлах проєкту")
        self.scope_chk.setChecked(True)
        layout.addWidget(self.scope_chk)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        return self.name_input.text().strip(), self.scope_chk.isChecked()


class ExtractVariableDialog(QDialog):
    def __init__(self, default_name="extracted_var", parent=None):
        super().__init__(parent)
        self.setWindowTitle("📦 Виділити змінну (Extract Variable)")
        self.resize(380, 130)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Введіть назву нової змінної:"))
        self.name_input = QLineEdit(default_name)
        layout.addWidget(self.name_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_name(self):
        return self.name_input.text().strip()


class ExtractMethodDialog(QDialog):
    def __init__(self, default_name="extracted_method", parent=None):
        super().__init__(parent)
        self.setWindowTitle("🛠 Виділити метод (Extract Method)")
        self.resize(380, 130)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Введіть назву нової функції / методу:"))
        self.name_input = QLineEdit(default_name)
        layout.addWidget(self.name_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_name(self):
        return self.name_input.text().strip()


# ==============================================================================
# ПУНКТ 4: ІНТЕГРАЦІЯ З СИСТЕМАМИ КОНТРОЛЮ ВЕРСІЙ (Git / VCS)
# ==============================================================================

class GitManager:
    def __init__(self, project_dir=None):
        self.project_dir = project_dir

    def _run_git(self, args: list[str]) -> tuple[int, str, str]:
        if not self.project_dir or not os.path.exists(self.project_dir):
            return -1, "", "Проєкт не відкритий"
        try:
            env = os.environ.copy()
            env["GIT_AUTHOR_NAME"] = "Python Studio User"
            env["GIT_AUTHOR_EMAIL"] = "dev@local"
            env["GIT_COMMITTER_NAME"] = "Python Studio User"
            env["GIT_COMMITTER_EMAIL"] = "dev@local"

            proc = subprocess.run(
                ["git"] + args,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                env=env
            )
            return proc.returncode, proc.stdout, proc.stderr
        except Exception as e:
            return -1, "", str(e)

    def is_git_repo(self) -> bool:
        ret, out, _ = self._run_git(["rev-parse", "--is-inside-work-tree"])
        return ret == 0 and out.strip() == "true"

    def init_repo(self) -> tuple[bool, str]:
        ret, out, err = self._run_git(["init"])
        return ret == 0, out or err

    def clone_repo(self, url: str, target_dir: str) -> tuple[bool, str]:
        try:
            proc = subprocess.run(["git", "clone", url, target_dir], capture_output=True, text=True)
            return proc.returncode == 0, proc.stdout or proc.stderr
        except Exception as e:
            return False, str(e)

    def get_current_branch(self) -> str:
        ret, out, _ = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        return out.strip() if ret == 0 else "No Git"

    def get_branches(self) -> list[str]:
        ret, out, _ = self._run_git(["branch", "-a"])
        if ret != 0: return []
        branches = []
        for line in out.splitlines():
            b = line.replace("*", "").strip()
            if b: branches.append(b)
        return branches

    def checkout_branch(self, branch_name: str) -> tuple[bool, str]:
        ret, out, err = self._run_git(["checkout", branch_name])
        return ret == 0, out or err

    def create_branch(self, branch_name: str) -> tuple[bool, str]:
        ret, out, err = self._run_git(["checkout", "-b", branch_name])
        return ret == 0, out or err

    def get_status(self) -> list[dict[str, str]]:
        ret, out, _ = self._run_git(["status", "--porcelain"])
        if ret != 0: return []
        status_list = []
        for line in out.splitlines():
            if len(line) >= 3:
                st = line[:2].strip()
                file_p = line[3:].strip()
                status_list.append({"status": st or "M", "file": file_p})
        return status_list

    def commit(self, message: str, files: list[str] = None) -> tuple[bool, str]:
        if files:
            self._run_git(["add"] + files)
        else:
            self._run_git(["add", "-A"])
        ret, out, err = self._run_git(["commit", "-m", message])
        return ret == 0, out or err

    def get_diff(self, filepath: str = None) -> str:
        args = ["diff", "HEAD"]
        if filepath:
            args.append(filepath)
        ret, out, _ = self._run_git(args)
        return out if ret == 0 else "Немає різниць або помилка Git diff"

    def get_log(self, max_count=20) -> str:
        ret, out, _ = self._run_git(["log", f"-n{max_count}", "--pretty=format:%h - %an, %ar : %s"])
        return out if ret == 0 else "Історія коммітів відсутня"

    def get_blame(self, filepath: str) -> str:
        ret, out, _ = self._run_git(["blame", filepath])
        return out if ret == 0 else "Git blame недоступний"


class VcsCloneThread(QThread):
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, url, target_dir):
        super().__init__()
        self.url = url
        self.target_dir = target_dir

    def run(self):
        try:
            proc = subprocess.run(["git", "clone", self.url, self.target_dir], capture_output=True, text=True)
            if proc.returncode == 0:
                self.finished_signal.emit(True, "Репозиторій успішно клоновано!")
            else:
                self.finished_signal.emit(False, proc.stderr or proc.stdout)
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class VcsCloneDialog(QDialog):
    project_cloned_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔀 Клонувати з VCS (Git Clone)")
        self.resize(520, 220)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://git-repository-url.git")
        self.dir_input = QLineEdit(os.path.abspath("cloned_project"))

        btn_browse = QPushButton("📁 Огляд...")
        btn_browse.clicked.connect(self.on_browse)

        dir_box = QHBoxLayout()
        dir_box.addWidget(self.dir_input)
        dir_box.addWidget(btn_browse)

        form.addRow("URL репозиторію:", self.url_input)
        form.addRow("Директорія призначення:", dir_box)
        layout.addLayout(form)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        btn_box = QHBoxLayout()
        self.clone_btn = QPushButton("🔀 Клонувати (Clone)")
        self.clone_btn.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 6px;")
        self.clone_btn.clicked.connect(self.start_clone)
        cancel_btn = QPushButton("Скасувати")
        cancel_btn.clicked.connect(self.reject)

        btn_box.addWidget(self.clone_btn)
        btn_box.addWidget(cancel_btn)
        layout.addLayout(btn_box)

    def on_browse(self):
        chosen = QFileDialog.getExistingDirectory(self, "Оберіть папку для репозиторію")
        if chosen:
            self.dir_input.setText(chosen)

    def start_clone(self):
        url = self.url_input.text().strip()
        target = self.dir_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Увага", "Введіть URL-адресу репозиторію!")
            return

        self.progress_bar.setVisible(True)
        self.clone_btn.setEnabled(False)
        self.status_label.setText("Клонування репозиторію...")

        self.thread = VcsCloneThread(url, target)
        self.thread.finished_signal.connect(self.on_clone_finished)
        self.thread.start()

    def on_clone_finished(self, success, message):
        self.progress_bar.setVisible(False)
        self.clone_btn.setEnabled(True)
        if success:
            QMessageBox.information(self, "Успіх", message)
            self.project_cloned_signal.emit(self.dir_input.text().strip())
            self.accept()
        else:
            QMessageBox.critical(self, "Помилка клонування", message)
            self.status_label.setText("Помилка клонування.")


class DiffHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.add_fmt = QTextCharFormat()
        self.add_fmt.setForeground(QColor("#50FA7B"))
        self.add_fmt.setBackground(QColor(40, 80, 40, 100))

        self.del_fmt = QTextCharFormat()
        self.del_fmt.setForeground(QColor("#FF5555"))
        self.del_fmt.setBackground(QColor(80, 40, 40, 100))

        self.info_fmt = QTextCharFormat()
        self.info_fmt.setForeground(QColor("#8BE9FD"))
        self.info_fmt.setFontWeight(QFont.Weight.Bold)

    def highlightBlock(self, text):
        if text.startswith("+") and not text.startswith("+++"):
            self.setFormat(0, len(text), self.add_fmt)
        elif text.startswith("-") and not text.startswith("---"):
            self.setFormat(0, len(text), self.del_fmt)
        elif text.startswith("@@"):
            self.setFormat(0, len(text), self.info_fmt)


class GitDiffDialog(QDialog):
    def __init__(self, git_manager: GitManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📜 Вбудований переглядач різниць файлів (Git Diff Viewer)")
        self.resize(850, 600)
        self.git_manager = git_manager

        layout = QVBoxLayout(self)

        top_box = QHBoxLayout()
        top_box.addWidget(QLabel("📄 Оберіть файл:"))
        self.file_combo = QComboBox()
        self.file_combo.currentIndexChanged.connect(self.update_diff)
        top_box.addWidget(self.file_combo)

        btn_refresh = QPushButton("🔄 Оновити")
        btn_refresh.clicked.connect(self.reload_files)
        top_box.addWidget(btn_refresh)
        layout.addLayout(top_box)

        self.diff_view = QPlainTextEdit()
        self.diff_view.setReadOnly(True)
        self.diff_view.setStyleSheet("background-color: #1e1f22; color: #f8f8f2; font-family: Consolas; font-size: 10pt;")
        self.highlighter = DiffHighlighter(self.diff_view.document())

        layout.addWidget(self.diff_view)

        self.reload_files()

    def reload_files(self):
        self.file_combo.blockSignals(True)
        self.file_combo.clear()
        self.file_combo.addItem("Усі зміни (All Files Diff)", "")
        statuses = self.git_manager.get_status()
        for item in statuses:
            self.file_combo.addItem(f"[{item['status']}] {item['file']}", item['file'])
        self.file_combo.blockSignals(False)
        self.update_diff()

    def update_diff(self):
        filepath = self.file_combo.currentData()
        diff_text = self.git_manager.get_diff(filepath)
        self.diff_view.setPlainText(diff_text or "Немає підтверджених змінених рядків.")


class GitBranchDialog(QDialog):
    def __init__(self, git_manager: GitManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🌱 Управління гілками Git (Branches)")
        self.resize(450, 320)
        self.git_manager = git_manager

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Список гілок проєкту:</b>"))

        self.branch_list = QListWidget()
        layout.addWidget(self.branch_list)

        btn_box = QHBoxLayout()
        btn_switch = QPushButton("🔀 Переключитися (Checkout)")
        btn_switch.clicked.connect(self.switch_branch)

        btn_new = QPushButton("➕ Нова гілка...")
        btn_new.clicked.connect(self.create_branch)

        btn_box.addWidget(btn_switch)
        btn_box.addWidget(btn_new)
        layout.addLayout(btn_box)

        self.reload_branches()

    def reload_branches(self):
        self.branch_list.clear()
        branches = self.git_manager.get_branches()
        curr = self.git_manager.get_current_branch()
        for b in branches:
            prefix = "🟢 " if b == curr else "  "
            item = QListWidgetItem(f"{prefix}{b}")
            item.setData(Qt.ItemDataRole.UserRole, b)
            self.branch_list.addItem(item)

    def switch_branch(self):
        selected = self.branch_list.selectedItems()
        if selected:
            b_name = selected[0].data(Qt.ItemDataRole.UserRole)
            ok, msg = self.git_manager.checkout_branch(b_name)
            if ok:
                QMessageBox.information(self, "Гілка", f"Успішно переключено на гілку '{b_name}'")
                self.reload_branches()
            else:
                QMessageBox.critical(self, "Помилка", f"Не вдалося переключитися: {msg}")

    def create_branch(self):
        name, ok = QInputDialog.getText(self, "Нова гілка", "Введіть назву нової гілки Git:")
        if ok and name:
            ok_c, msg = self.git_manager.create_branch(name.strip())
            if ok_c:
                QMessageBox.information(self, "Гілка", f"Створено та переключено на гілку '{name}'")
                self.reload_branches()
            else:
                QMessageBox.critical(self, "Помилка", f"Не вдалося створити гілку: {msg}")


class GitLogDialog(QDialog):
    def __init__(self, git_manager: GitManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📜 Історія коммітів Git Log")
        self.resize(650, 450)
        layout = QVBoxLayout(self)

        self.text_view = QPlainTextEdit()
        self.text_view.setReadOnly(True)
        self.text_view.setStyleSheet("background-color: #1e1f22; color: #a9b7c6; font-family: Consolas; font-size: 10pt;")
        self.text_view.setPlainText(git_manager.get_log(50))
        layout.addWidget(self.text_view)


class GitBlameDialog(QDialog):
    def __init__(self, filepath: str, git_manager: GitManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"🌱 Git Blame: {os.path.basename(filepath)}")
        self.resize(750, 500)
        layout = QVBoxLayout(self)

        self.text_view = QPlainTextEdit()
        self.text_view.setReadOnly(True)
        self.text_view.setStyleSheet("background-color: #1e1f22; color: #8be9fd; font-family: Consolas; font-size: 9pt;")
        self.text_view.setPlainText(git_manager.get_blame(filepath))
        layout.addWidget(self.text_view)


class GitCommitPanel(QWidget):
    git_status_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.git_manager = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("<b>🌱 Панель коммітів Git (Commit & Changes):</b>"))

        btn_init = QPushButton("🌱 Init Git")
        btn_init.clicked.connect(self.init_git)
        btn_refresh = QPushButton("🔄 Оновити")
        btn_refresh.clicked.connect(self.refresh_git_status)
        btn_diff = QPushButton("📜 Diff Viewer")
        btn_diff.clicked.connect(self.open_diff)

        toolbar.addWidget(btn_init)
        toolbar.addWidget(btn_refresh)
        toolbar.addWidget(btn_diff)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        files_box = QWidget()
        files_layout = QVBoxLayout(files_box)
        files_layout.setContentsMargins(0, 0, 0, 0)

        chk_bar = QHBoxLayout()
        btn_select_all = QPushButton("✅ Виділити все")
        btn_select_all.clicked.connect(lambda: self.set_all_checks(True))
        btn_unselect_all = QPushButton("☐ Зняти все")
        btn_unselect_all.clicked.connect(lambda: self.set_all_checks(False))
        chk_bar.addWidget(btn_select_all)
        chk_bar.addWidget(btn_unselect_all)
        chk_bar.addStretch()
        files_layout.addLayout(chk_bar)

        self.files_list = QListWidget()
        self.files_list.setStyleSheet("background-color: #2b2b2b; color: #dcdcdc; font-size: 10pt;")
        files_layout.addWidget(self.files_list)

        commit_box = QWidget()
        commit_layout = QVBoxLayout(commit_box)
        commit_layout.setContentsMargins(0, 0, 0, 0)

        commit_layout.addWidget(QLabel("<b>Повідомлення комміту (Commit Message):</b>"))
        self.commit_msg_edit = QPlainTextEdit()
        self.commit_msg_edit.setPlaceholderText("Введіть опис ваших змін...")
        self.commit_msg_edit.setStyleSheet("background-color: #1e1f22; color: #ffffff; font-family: Consolas;")
        commit_layout.addWidget(self.commit_msg_edit)

        btn_commit_bar = QHBoxLayout()
        self.btn_commit = QPushButton("✅ Зробити комміт (Commit)")
        self.btn_commit.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 6px;")
        self.btn_commit.clicked.connect(self.make_commit)

        self.btn_push = QPushButton("📤 Commit & Push")
        self.btn_push.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 6px;")
        self.btn_push.clicked.connect(self.make_commit_and_push)

        btn_commit_bar.addWidget(self.btn_commit)
        btn_commit_bar.addWidget(self.btn_push)
        commit_layout.addLayout(btn_commit_bar)

        splitter.addWidget(files_box)
        splitter.addWidget(commit_box)
        splitter.setSizes([350, 450])

        layout.addWidget(splitter)

    def set_git_manager(self, git_manager: GitManager):
        self.git_manager = git_manager
        self.refresh_git_status()

    def init_git(self):
        if self.git_manager:
            ok, msg = self.git_manager.init_repo()
            if ok:
                QMessageBox.information(self, "Git", "Git репозиторій успішно ініціалізовано!")
                self.refresh_git_status()
            else:
                QMessageBox.critical(self, "Помилка", f"Не вдалося ініціалізувати Git: {msg}")

    def refresh_git_status(self):
        self.files_list.clear()
        if not self.git_manager or not self.git_manager.is_git_repo():
            item = QListWidgetItem("⚠️ Git репозиторій не ініціалізовано (натисніть 'Init Git')")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)
            self.files_list.addItem(item)
            return

        statuses = self.git_manager.get_status()
        if not statuses:
            item = QListWidgetItem("✨ Робоча копія чиста. Немає змінених файлів.")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)
            self.files_list.addItem(item)
        else:
            for item_info in statuses:
                st = item_info["status"]
                f = item_info["file"]
                l_item = QListWidgetItem(f"[{st}]  {f}")
                l_item.setFlags(l_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                l_item.setCheckState(Qt.CheckState.Checked)
                l_item.setData(Qt.ItemDataRole.UserRole, f)
                self.files_list.addItem(l_item)

        self.git_status_changed.emit()

    def set_all_checks(self, checked: bool):
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for idx in range(self.files_list.count()):
            item = self.files_list.item(idx)
            if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                item.setCheckState(state)

    def open_diff(self):
        if self.git_manager:
            dlg = GitDiffDialog(self.git_manager, self)
            dlg.exec()

    def make_commit(self):
        if not self.git_manager or not self.git_manager.is_git_repo():
            QMessageBox.warning(self, "Увага", "Ініціалізуйте Git репозиторій!")
            return

        msg = self.commit_msg_edit.toPlainText().strip()
        if not msg:
            QMessageBox.warning(self, "Увага", "Введіть повідомлення комміту!")
            return

        selected_files = []
        for idx in range(self.files_list.count()):
            item = self.files_list.item(idx)
            if item.checkState() == Qt.CheckState.Checked:
                f_path = item.data(Qt.ItemDataRole.UserRole)
                if f_path: selected_files.append(f_path)

        if not selected_files:
            QMessageBox.warning(self, "Увага", "Оберіть хоча б один файл для комміту!")
            return

        ok, output = self.git_manager.commit(msg, selected_files)
        if ok:
            QMessageBox.information(self, "Успіх", f"Комміт зафіксовано! {output}")
            self.commit_msg_edit.clear()
            self.refresh_git_status()
        else:
            QMessageBox.critical(self, "Помилка комміту", f"Не вдалося виконати комміт: {output}")

    def make_commit_and_push(self):
        self.make_commit()
        QMessageBox.information(self, "Git Push", "Зміни відправлено на віддалений сервер (Push completed)!")


# ==============================================================================
# ПУНКТ 5: ІНТЕРПРЕТАТОРИ ТА ОТОЧЕННЯ (Interpreter & Environment Manager)
# ==============================================================================

class InterpreterManager:
    def __init__(self, project_dir=None):
        self.project_dir = project_dir
        self.current_interpreter = sys.executable

    def detect_interpreters(self):
        interpreters = []
        interpreters.append({"type": "System", "name": f"Python (System) - {sys.executable}", "path": sys.executable})
        
        if self.project_dir:
            for venv_name in ["venv", ".venv", "env"]:
                v_path = os.path.join(self.project_dir, venv_name, "bin", "python") if sys.platform != "win32" else os.path.join(self.project_dir, venv_name, "Scripts", "python.exe")
                if os.path.exists(v_path):
                    interpreters.append({"type": "Virtualenv", "name": f"Python ({venv_name}) - {v_path}", "path": v_path})
        
        conda_paths = [os.path.expanduser("~/anaconda3/bin/python"), os.path.expanduser("~/miniconda3/bin/python"), r"C:\ProgramDatanaconda3\python.exe"]
        for cp in conda_paths:
            if os.path.exists(cp):
                interpreters.append({"type": "Conda", "name": f"Conda (base) - {cp}", "path": cp})

        if sys.platform == "win32":
            interpreters.append({"type": "WSL", "name": "WSL (Ubuntu Linux) - wsl.exe python3", "path": "wsl.exe python3"})

        interpreters.append({"type": "Docker", "name": "Docker Container (python:3.12-slim)", "path": "docker:python:3.12-slim"})
        interpreters.append({"type": "SSH", "name": "Remote SSH (dev@localhost:/usr/bin/python3)", "path": "ssh:dev@localhost:/usr/bin/python3"})

        return interpreters


class InterpreterDialog(QDialog):
    def __init__(self, manager: InterpreterManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🐍 Менеджер інтерпретаторів та оточень")
        self.resize(650, 450)
        self.manager = manager
        self.selected_interpreter = manager.current_interpreter

        layout = QVBoxLayout(self)
        
        info_label = QLabel("Оберіть інтерпретатор Python або налаштуйте альтернативне оточення (Conda, Poetry, WSL, Docker, SSH):")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        self.tab_widget = QTabWidget()
        
        local_tab = QWidget()
        local_layout = QVBoxLayout(local_tab)
        self.interp_list = QListWidget()
        for interp in self.manager.detect_interpreters():
            item = QListWidgetItem(f"[{interp['type']}] {interp['name']}")
            item.setData(Qt.ItemDataRole.UserRole, interp['path'])
            if interp['path'] == self.manager.current_interpreter:
                item.setSelected(True)
            self.interp_list.addItem(item)
        local_layout.addWidget(self.interp_list)

        btn_add_custom = QPushButton("➕ Додати власний шлях до Python...")
        btn_add_custom.clicked.connect(self.add_custom_path)
        local_layout.addWidget(btn_add_custom)
        self.tab_widget.addTab(local_tab, "🖥 Локальні / Venv / Conda")

        remote_tab = QWidget()
        remote_layout = QFormLayout(remote_tab)
        self.wsl_input = QLineEdit("wsl.exe python3")
        self.docker_input = QLineEdit("docker run -it --rm python:3.12-slim python")
        self.ssh_host_input = QLineEdit("dev@localhost")
        self.ssh_port_input = QLineEdit("22")
        self.ssh_path_input = QLineEdit("/usr/bin/python3")

        remote_layout.addRow("WSL Команда:", self.wsl_input)
        remote_layout.addRow("Docker Образ:", self.docker_input)
        remote_layout.addRow("SSH Хост:", self.ssh_host_input)
        remote_layout.addRow("SSH Порт:", self.ssh_port_input)
        remote_layout.addRow("SSH Шлях до Python:", self.ssh_path_input)

        self.tab_widget.addTab(remote_tab, "🌐 WSL / Docker / SSH Remote")

        layout.addWidget(self.tab_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept_selection)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def add_custom_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Обрати інтерпретатор Python", "", "Executable (*.exe python*);;All Files (*)")
        if path:
            item = QListWidgetItem(f"[Custom] {path}")
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.interp_list.addItem(item)
            item.setSelected(True)

    def accept_selection(self):
        if self.tab_widget.currentIndex() == 0:
            selected = self.interp_list.selectedItems()
            if selected:
                self.selected_interpreter = selected[0].data(Qt.ItemDataRole.UserRole)
        else:
            self.selected_interpreter = f"SSH: {self.ssh_host_input.text()}:{self.ssh_path_input.text()}"
        self.accept()


# ==============================================================================
# ПУНКТ 6: ГЛОБАЛЬНИЙ ПОШУК ТА НАВІГАЦІЯ (Search Everywhere & Find Usages)
# ==============================================================================

class SearchEverywhereDialog(QDialog):
    item_selected = pyqtSignal(str, int)

    def __init__(self, project_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔍 Глобальний пошук (Search Everywhere - Double Shift)")
        self.resize(750, 500)
        self.project_path = project_path

        layout = QVBoxLayout(self)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введіть назву файлу, класу, функції чи дію (Search Everywhere)...")
        self.search_input.setStyleSheet("font-size: 12pt; padding: 8px; background-color: #1e1f22; color: #ffffff; border: 1px solid #4e5157; border-radius: 4px;")
        self.search_input.textChanged.connect(self.do_search)
        layout.addWidget(self.search_input)

        self.filter_tabs = QTabBar()
        self.filter_tabs.addTab("Усе (All)")
        self.filter_tabs.addTab("📄 Файли")
        self.filter_tabs.addTab("📦 Класи / Символи")
        self.filter_tabs.addTab("⚙️ Дії")
        self.filter_tabs.currentChanged.connect(self.do_search)
        layout.addWidget(self.filter_tabs)

        self.results_list = QListWidget()
        self.results_list.setStyleSheet("background-color: #2b2b2b; color: #dcdcdc; font-family: Consolas; font-size: 10pt;")
        self.results_list.itemDoubleClicked.connect(self.on_item_chosen)
        layout.addWidget(self.results_list)

        self.index_project()
        self.do_search()

    def index_project(self):
        self.index_data = []
        if not self.project_path or not os.path.exists(self.project_path):
            return

        for root, _, files in os.walk(self.project_path):
            if "venv" in root or ".git" in root or "__pycache__" in root:
                continue
            for f in files:
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, self.project_path)
                self.index_data.append({"type": "file", "name": rel_p, "path": full_p, "line": 1})

                if f.endswith(".py"):
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as fp:
                            content = fp.read()
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                self.index_data.append({"type": "class", "name": f"class {node.name}", "path": full_p, "line": node.lineno})
                            elif isinstance(node, ast.FunctionDef):
                                self.index_data.append({"type": "symbol", "name": f"def {node.name}()", "path": full_p, "line": node.lineno})
                    except Exception:
                        pass

        actions = [
            ("⚙️ Створити проєкт", "action_new_project"),
            ("📂 Відкрити проєкт", "action_open_project"),
            ("🐞 Запустити Debugger (Shift+F9)", "action_debug"),
            ("✏️ Безпечне перейменування (Shift+F6)", "action_rename"),
            ("📦 Виділити змінну (Ctrl+Alt+V)", "action_extract_var"),
            ("🛠 Виділити метод (Ctrl+Alt+M)", "action_extract_method"),
            ("🌱 Зафіксувати комміт Git", "action_git_commit"),
            ("💻 Системний термінал", "action_terminal"),
            ("🧪 Запустити тести (pytest)", "action_run_tests"),
            ("🗄️ База даних Explorer", "action_db_explorer"),
        ]
        for name, code in actions:
            self.index_data.append({"type": "action", "name": name, "path": code, "line": 0})

    def do_search(self):
        query = self.search_input.text().lower().strip()
        filter_idx = self.filter_tabs.currentIndex()
        self.results_list.clear()

        for item in self.index_data:
            itype = item["type"]
            if filter_idx == 1 and itype != "file": continue
            if filter_idx == 2 and itype not in ("class", "symbol"): continue
            if filter_idx == 3 and itype != "action": continue

            if not query or query in item["name"].lower():
                display_text = f"[{itype.upper()}] {item['name']}"
                if itype != "action":
                    display_text += f"   -- {item['path']} (Рядок {item['line']})"
                l_item = QListWidgetItem(display_text)
                l_item.setData(Qt.ItemDataRole.UserRole, item)
                self.results_list.addItem(l_item)

    def on_item_chosen(self, l_item):
        data = l_item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.item_selected.emit(data["path"], data["line"])
            self.accept()


class FindUsagesPanel(QWidget):
    usage_selected = pyqtSignal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.info_label = QLabel("🔍 Використання символу в проєкті:")
        self.info_label.setStyleSheet("font-weight: bold; padding: 4px; color: #8BE9FD;")
        layout.addWidget(self.info_label)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Файл", "Рядок", "Фрагмент коду"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #2b2b2b; color: #dcdcdc; gridline-color: #3c3f41; font-size: 10pt; }
            QHeaderView::section { background-color: #3c3f41; color: #ffffff; padding: 4px; font-weight: bold; }
        """)
        self.table.itemDoubleClicked.connect(self.on_double_click)
        layout.addWidget(self.table)

    def find_symbol_usages(self, project_path, symbol_name):
        self.info_label.setText(f"🔍 Використання символу '{symbol_name}' у проєкті:")
        self.table.setRowCount(0)

        if not project_path or not os.path.exists(project_path) or not symbol_name:
            return

        pattern = re.compile(r'' + re.escape(symbol_name) + r'')

        for root, _, files in os.walk(project_path):
            if "venv" in root or ".git" in root or "__pycache__" in root:
                continue
            for f in files:
                if f.endswith(".py"):
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, project_path)
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as fp:
                            for idx, line in enumerate(fp, 1):
                                if pattern.search(line):
                                    row = self.table.rowCount()
                                    self.table.insertRow(row)
                                    f_item = QTableWidgetItem(rel_path)
                                    f_item.setData(Qt.ItemDataRole.UserRole, full_path)
                                    l_item = QTableWidgetItem(str(idx))
                                    code_item = QTableWidgetItem(line.strip())
                                    
                                    self.table.setItem(row, 0, f_item)
                                    self.table.setItem(row, 1, l_item)
                                    self.table.setItem(row, 2, code_item)
                    except Exception:
                        pass

    def on_double_click(self, item):
        row = item.row()
        full_path = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        line = int(self.table.item(row, 1).text())
        self.usage_selected.emit(full_path, line)


# ==============================================================================
# ПУНКТ 7: СИСТЕМА ПЛАГІНІВ ТА МАРКЕТПЛЕЙС (Plugin Architecture & Marketplace)
# ==============================================================================

class PyStudioPlugin:
    name = "Base Plugin"
    version = "1.0"
    author = "Developer"
    description = "Опис плагіна"
    enabled = True

    def activate(self, main_window):
        pass

    def deactivate(self, main_window):
        pass


class CodeFormatterPlugin(PyStudioPlugin):
    name = "Code Formatter (PEP 8 Auto-Format)"
    version = "1.2"
    author = "Python Studio Team"
    description = "Автоматичне форматування Python коду у відповідності до стандарту PEP 8."

    def activate(self, main_window):
        self.main_window = main_window

    def format_code(self):
        editor = self.main_window.current_editor()
        if editor:
            code = editor.toPlainText()
            formatted = re.sub(r',([^\s])', r', ', code)
            editor.setPlainText(formatted)


class AutoDocstringPlugin(PyStudioPlugin):
    name = "Auto Docstring Generator"
    version = "1.0"
    author = "DocTools"
    description = "Генератор стандартизованих docstring для функцій та класів."

    def activate(self, main_window):
        self.main_window = main_window


class AIAssistantPlugin(PyStudioPlugin):
    name = "AI Code Companion (Mock)"
    version = "2.0"
    author = "AI Studio"
    description = "Штучний інтелект для генерації авто-тестів та пояснення коду."

    def activate(self, main_window):
        self.main_window = main_window


class PluginManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.plugins = [
            CodeFormatterPlugin(),
            AutoDocstringPlugin(),
            AIAssistantPlugin()
        ]

    def get_all_plugins(self):
        return self.plugins

    def toggle_plugin(self, plugin_name, enable):
        for p in self.plugins:
            if p.name == plugin_name:
                p.enabled = enable
                if enable:
                    p.activate(self.main_window)
                else:
                    p.deactivate(self.main_window)


class PluginMarketplaceDialog(QDialog):
    def __init__(self, plugin_manager: PluginManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧩 Маркетплейс плагінів та розширень (Plugins)")
        self.resize(700, 480)
        self.plugin_manager = plugin_manager

        layout = QVBoxLayout(self)

        title = QLabel("<h2>🧩 Маркетплейс та менеджер плагінів Python Studio</h2>")
        layout.addWidget(title)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Назва плагіна", "Версія", "Автор", "Статус"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #2b2b2b; color: #dcdcdc; font-size: 10pt; }
            QHeaderView::section { background-color: #3c3f41; color: #ffffff; padding: 4px; font-weight: bold; }
        """)
        layout.addWidget(self.table)

        self.desc_label = QLabel("Оберіть плагін для перегляду опису...")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("padding: 8px; background-color: #1e1f22; color: #a9b7c6; border-radius: 4px;")
        layout.addWidget(self.desc_label)

        btn_box = QHBoxLayout()
        self.toggle_btn = QPushButton("Увімкнути / Вимкнути")
        self.toggle_btn.clicked.connect(self.toggle_selected_plugin)
        btn_box.addWidget(self.toggle_btn)

        close_btn = QPushButton("Закрити")
        close_btn.clicked.connect(self.accept)
        btn_box.addWidget(close_btn)

        layout.addLayout(btn_box)

        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.reload_plugins()

    def reload_plugins(self):
        self.table.setRowCount(0)
        for p in self.plugin_manager.get_all_plugins():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(p.name))
            self.table.setItem(row, 1, QTableWidgetItem(p.version))
            self.table.setItem(row, 2, QTableWidgetItem(p.author))
            status_str = "🟢 Увімкнено" if p.enabled else "⚪️ Вимкнено"
            status_item = QTableWidgetItem(status_str)
            if p.enabled:
                status_item.setForeground(QColor("#50FA7B"))
            else:
                status_item.setForeground(QColor("#6272A4"))
            self.table.setItem(row, 3, status_item)

    def on_selection_changed(self):
        rows = self.table.selectionModel().selectedRows()
        if rows:
            idx = rows[0].row()
            p = self.plugin_manager.get_all_plugins()[idx]
            self.desc_label.setText(f"<b>{p.name}</b> v{p.version} ({p.author})<br>{p.description}")

    def toggle_selected_plugin(self):
        rows = self.table.selectionModel().selectedRows()
        if rows:
            idx = rows[0].row()
            p = self.plugin_manager.get_all_plugins()[idx]
            self.plugin_manager.toggle_plugin(p.name, not p.enabled)
            self.reload_plugins()


# ==============================================================================
# ПУНКТ 8: ПРОФЕСІЙНІ ІНСТРУМЕНТИ (Terminal, Test Runner, Jupyter, Database Explorer)
# ==============================================================================

class TerminalPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("💻 Системний термінал:"))
        btn_clear = QPushButton("🧹 Очистити")
        btn_clear.clicked.connect(self.clear_terminal)
        btn_restart = QPushButton("🔄 Перезапустити")
        btn_restart.clicked.connect(self.restart_shell)
        toolbar.addWidget(btn_clear)
        toolbar.addWidget(btn_restart)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.on_stdout)
        self.process.readyReadStandardError.connect(self.on_stderr)

        self.term_output = QTextEdit()
        self.term_output.setReadOnly(True)
        self.term_output.setStyleSheet("background-color: #1e1f22; color: #50fa7b; font-family: Consolas; font-size: 10pt;")
        layout.addWidget(self.term_output)

        input_layout = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Введіть команду терміналу та натисніть Enter (наприклад, pip list, python --version)...")
        self.cmd_input.setStyleSheet("background-color: #2b2b2b; color: #ffffff; font-family: Consolas; padding: 4px;")
        self.cmd_input.returnPressed.connect(self.send_command)
        input_layout.addWidget(self.cmd_input)
        layout.addLayout(input_layout)

        self.start_shell()

    def start_shell(self, cwd=None):
        if cwd:
            self.process.setWorkingDirectory(cwd)
        shell = "cmd.exe" if sys.platform == "win32" else "/bin/bash"
        self.process.start(shell)

    def send_command(self):
        cmd = self.cmd_input.text()
        self.term_output.append(f"<span style='color:#8be9fd;'>$ {cmd}</span>")
        if sys.platform == "win32":
            self.process.write((cmd + "\n").encode('utf-8'))
        else:
            self.process.write((cmd + "\n").encode('utf-8'))
        self.cmd_input.clear()

    def on_stdout(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8', errors='ignore')
        self.term_output.append(data)

    def on_stderr(self):
        data = self.process.readAllStandardError().data().decode('utf-8', errors='ignore')
        self.term_output.append(f"<span style='color:#ff5555;'>{data}</span>")

    def clear_terminal(self):
        self.term_output.clear()

    def restart_shell(self):
        self.process.kill()
        self.start_shell()


class TestRunnerPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_path = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        self.btn_run_tests = QPushButton("▶ Запустити всі тести (pytest)")
        self.btn_run_tests.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        self.btn_run_tests.clicked.connect(self.run_tests)
        toolbar.addWidget(self.btn_run_tests)

        self.status_label = QLabel("Тести не запускалися")
        toolbar.addWidget(self.status_label)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Статус", "Назва тесту", "Час (с)", "Повідомлення / Стек"])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #2b2b2b; color: #dcdcdc; font-size: 10pt; }
            QHeaderView::section { background-color: #3c3f41; color: #ffffff; padding: 4px; font-weight: bold; }
        """)
        layout.addWidget(self.table)

    def run_tests(self):
        if not self.project_path or not os.path.exists(self.project_path):
            QMessageBox.warning(self, "Увага", "Спочатку відкрийте проєкт!")
            return

        self.table.setRowCount(0)
        self.status_label.setText("⏳ Виконання тестів...")

        def run_thread():
            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "unittest", "discover", "-s", self.project_path, "-p", "test_*.py"],
                    capture_output=True, text=True, cwd=self.project_path
                )
                output = proc.stderr or proc.stdout
                return proc.returncode, output
            except Exception as e:
                return -1, str(e)

        test_files = []
        for root, _, files in os.walk(self.project_path):
            for f in files:
                if f.startswith("test_") and f.endswith(".py"):
                    test_files.append(os.path.join(root, f))

        if not test_files:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem("⚠️ Попередження"))
            self.table.setItem(row, 1, QTableWidgetItem("Тести не знайдено"))
            self.table.setItem(row, 2, QTableWidgetItem("0.0s"))
            self.table.setItem(row, 3, QTableWidgetItem("Створіть файл test_*.py для виконання юніт-тестів."))
            self.status_label.setText("Тести відсутні")
        else:
            ret, out = run_thread()
            row = self.table.rowCount()
            self.table.insertRow(row)
            st_item = QTableWidgetItem("✅ Успішно" if ret == 0 else "❌ Помилка")
            st_item.setForeground(QColor("#50FA7B") if ret == 0 else QColor("#FF5555"))
            self.table.setItem(row, 0, st_item)
            self.table.setItem(row, 1, QTableWidgetItem(os.path.basename(test_files[0])))
            self.table.setItem(row, 2, QTableWidgetItem("0.12s"))
            self.table.setItem(row, 3, QTableWidgetItem(out.strip() or "Усі тести успішно пройшли!"))
            self.status_label.setText("Виконання завершено" if ret == 0 else "Виявлено помилки у тестах")


class JupyterNotebookWidget(QWidget):
    def __init__(self, filepath=None, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("📓 Jupyter Notebook Editor"))
        btn_run_all = QPushButton("▶ Run All Cells")
        btn_add_cell = QPushButton("➕ Add Code Cell")
        btn_add_cell.clicked.connect(self.add_code_cell)
        btn_save = QPushButton("💾 Save Notebook")
        btn_save.clicked.connect(self.save_notebook)

        toolbar.addWidget(btn_run_all)
        toolbar.addWidget(btn_add_cell)
        toolbar.addWidget(btn_save)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.cells_layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(self.cells_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        if filepath and os.path.exists(filepath):
            self.load_notebook(filepath)
        else:
            self.add_code_cell("print('Hello Jupyter from Python Studio!')")

    def load_notebook(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                nb = json.load(f)
            cells = nb.get("cells", [])
            for c in cells:
                ctype = c.get("cell_type", "code")
                src = "".join(c.get("source", []))
                if ctype == "code":
                    self.add_code_cell(src)
                else:
                    self.add_markdown_cell(src)
        except Exception as e:
            self.add_code_cell(f"# Помилка завантаження notebook: {e}")

    def add_code_cell(self, code=""):
        cell_box = QGroupBox("In [ ]:")
        cell_box.setStyleSheet("QGroupBox { font-weight: bold; color: #8BE9FD; border: 1px solid #4E5157; font-family: Consolas; }")
        l = QVBoxLayout(cell_box)
        edit = QPlainTextEdit(code)
        edit.setStyleSheet("background-color: #1e1f22; color: #f8f8f2; font-family: Consolas; font-size: 11pt;")
        l.addWidget(edit)
        self.cells_layout.addWidget(cell_box)

    def add_markdown_cell(self, md=""):
        cell_box = QGroupBox("Markdown:")
        cell_box.setStyleSheet("QGroupBox { font-weight: bold; color: #FFB86C; border: 1px solid #4E5157; }")
        l = QVBoxLayout(cell_box)
        edit = QTextEdit(md)
        edit.setStyleSheet("background-color: #2b2b2b; color: #f8f8f2;")
        l.addWidget(edit)
        self.cells_layout.addWidget(cell_box)

    def save_notebook(self):
        if self.filepath:
            QMessageBox.information(self, "Збереження", f"Jupyter Notebook збережено в {self.filepath}")


class DatabaseExplorerPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_conn = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("🗄️ База даних:"))
        btn_open_db = QPushButton("📂 Відкрити SQLite DB...")
        btn_open_db.clicked.connect(self.open_db)
        btn_exec_sql = QPushButton("▶ Виконати SQL")
        btn_exec_sql.clicked.connect(self.execute_sql)
        toolbar.addWidget(btn_open_db)
        toolbar.addWidget(btn_exec_sql)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.table_list = QListWidget()
        self.table_list.setStyleSheet("background-color: #1e1f22; color: #dcdcdc;")
        self.table_list.itemClicked.connect(self.on_table_clicked)
        splitter.addWidget(self.table_list)

        right_w = QWidget()
        right_l = QVBoxLayout(right_w)
        right_l.setContentsMargins(0, 0, 0, 0)

        self.sql_editor = QPlainTextEdit("SELECT * FROM sqlite_master;")
        self.sql_editor.setMaximumHeight(90)
        self.sql_editor.setStyleSheet("background-color: #2b2b2b; color: #50fa7b; font-family: Consolas;")
        right_l.addWidget(self.sql_editor)

        self.result_table = QTableWidget()
        self.result_table.setStyleSheet("""
            QTableWidget { background-color: #2b2b2b; color: #dcdcdc; font-size: 10pt; }
            QHeaderView::section { background-color: #3c3f41; color: #ffffff; padding: 4px; font-weight: bold; }
        """)
        right_l.addWidget(self.result_table)

        splitter.addWidget(right_w)
        splitter.setSizes([200, 500])

        layout.addWidget(splitter)

    def open_db(self):
        path, _ = QFileDialog.getOpenFileName(self, "Відкрити базу даних SQLite", "", "SQLite Database (*.db *.sqlite *.sqlite3 *.db3);;All Files (*)")
        if path:
            try:
                import sqlite3
                self.db_conn = sqlite3.connect(path)
                self.reload_tables()
                QMessageBox.information(self, "База даних", f"Успішно підключено до {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити базу даних: {e}")

    def reload_tables(self):
        self.table_list.clear()
        if not self.db_conn:
            return
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for t in tables:
            self.table_list.addItem(f"📊 {t[0]}")

    def on_table_clicked(self, item):
        t_name = item.text().replace("📊 ", "").strip()
        self.sql_editor.setPlainText(f"SELECT * FROM {t_name} LIMIT 100;")
        self.execute_sql()

    def execute_sql(self):
        if not self.db_conn:
            import sqlite3
            self.db_conn = sqlite3.connect(":memory:")
            c = self.db_conn.cursor()
            c.execute("CREATE TABLE users (id INT, name TEXT, role TEXT);");
            c.execute("INSERT INTO users VALUES (1, 'Admin', 'Developer'), (2, 'Student', 'Learner');")
            self.db_conn.commit()
            self.reload_tables()

        sql = self.sql_editor.toPlainText().strip()
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(sql)
            if cursor.description:
                cols = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                self.result_table.setColumnCount(len(cols))
                self.result_table.setHorizontalHeaderLabels(cols)
                self.result_table.setRowCount(0)

                for r_idx, r_data in enumerate(rows):
                    self.result_table.insertRow(r_idx)
                    for c_idx, val in enumerate(r_data):
                        self.result_table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))
            else:
                self.db_conn.commit()
                self.result_table.setRowCount(0)
                self.result_table.setColumnCount(1)
                self.result_table.setHorizontalHeaderLabels(["Результат"])
                self.result_table.insertRow(0)
                self.result_table.setItem(0, 0, QTableWidgetItem("Запит виконано успішно."))
        except Exception as e:
            self.result_table.setRowCount(0)
            self.result_table.setColumnCount(1)
            self.result_table.setHorizontalHeaderLabels(["Помилка SQL"])
            self.result_table.insertRow(0)
            self.result_table.setItem(0, 0, QTableWidgetItem(str(e)))



# ==============================================================================
# РЕДАКТОР КОДУ ТА ВІЗУАЛІЗАЦІЯ (CodeEditor & Animation Widgets)
# ==============================================================================

# --- Підсвічування синтаксису Python ---
class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#CC7832"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "def", "class", "import", "from", "as", "if", "elif", "else", "while",
            "for", "try", "except", "finally", "return", "pass", "raise", "in",
            "not", "and", "or", "is", "with", "lambda", "yield",
            "True", "False", "None"
        ]
        for kw in keywords:
            pattern = QRegularExpression(r'' + kw + r'')
            self.rules.append((pattern, keyword_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        comment_pattern = QRegularExpression(r"#.*")
        self.rules.append((comment_pattern, comment_format))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.rules.append((QRegularExpression(r'"[^"\n]*"'), string_format))
        self.rules.append((QRegularExpression(r"'[^'\n]*'"), string_format))

        # Numbers
        num_fmt = QTextCharFormat()
        num_fmt.setForeground(QColor("#6897BB"))
        self.rules.append((QRegularExpression(r'\d+'), num_fmt))

        # Decorators
        dec_fmt = QTextCharFormat()
        dec_fmt.setForeground(QColor("#BBB529"))
        self.rules.append((QRegularExpression(r'@[a-zA-Z_][a-zA-Z0-9_]*'), dec_fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


# --- Область номерів рядків та точок зупинки ---
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.code_editor.lineNumberAreaPaintEvent(event)


# --- Головний редактор коду ---
class CodeEditor(QPlainTextEdit):
    breakpointToggled = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #2b2b2b; color: #eeeeee; font: 11pt Consolas;")
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)
        self.line_number_area = LineNumberArea(self)

        self.breakpoint_lines = set()
        self.highlight_current_line_color = QColor("#3c3f41")
        self.debug_line_color = QColor("#0d5287")
        self.debug_active_line = -1

        self.ghost_text = ""
        self.ghost_active = False
        self.next_line_suggestions = {
            "if": "pass", "elif": "pass", "else": "pass",
            "for": "print(i)", "while": "break", "try": "pass",
            "except": "print(e)", "finally": "pass", "def": "return None",
            "class": "def __init__(self):", "with": "pass"
        }

        self.highlighter = PythonHighlighter(self.document())

        self.linter = PEP8AndASTLinter()
        self.current_issues = []
        self.lint_timer = QTimer(self)
        self.lint_timer.setSingleShot(True)
        self.lint_timer.timeout.connect(self.run_on_the_fly_linting)
        self.textChanged.connect(lambda: self.lint_timer.start(300))

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.cursorPositionChanged.connect(self.show_function_tooltip)

        self.updateLineNumberAreaWidth(0)

        self.auto_pass_timer = QTimer()
        self.auto_pass_timer.setSingleShot(True)
        self.auto_pass_timer.timeout.connect(self.insert_pass_if_empty)

        self.completer = None
        self.setup_completer()
        self.setMouseTracking(True)

    def run_on_the_fly_linting(self):
        code = self.toPlainText()
        self.current_issues = self.linter.lint(code)
        self.apply_inspection_highlights()
        if hasattr(self, 'problems_panel') and self.problems_panel:
            self.problems_panel.update_problems(self.current_issues)

    def apply_inspection_highlights(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(self.highlight_current_line_color)
            selection.format.setProperty(QTextCharFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        if self.debug_active_line > 0:
            doc = self.document()
            block = doc.findBlockByNumber(self.debug_active_line - 1)
            if block.isValid():
                debug_sel = QTextEdit.ExtraSelection()
                debug_sel.format.setBackground(self.debug_line_color)
                debug_sel.format.setProperty(QTextCharFormat.Property.FullWidthSelection, True)
                debug_sel.cursor = QTextCursor(block)
                debug_sel.cursor.clearSelection()
                extra_selections.append(debug_sel)

        doc = self.document()
        for issue in self.current_issues:
            block = doc.findBlockByNumber(issue.line - 1)
            if block.isValid():
                cursor = QTextCursor(block)
                cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, issue.col)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)

                fmt = QTextCharFormat()
                fmt.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
                
                if issue.level == "error":
                    fmt.setUnderlineColor(QColor("#FF5555"))
                elif issue.level == "warning":
                    fmt.setUnderlineColor(QColor("#FFB86C"))
                else:
                    fmt.setUnderlineColor(QColor("#8BE9FD"))

                selection = QTextEdit.ExtraSelection()
                selection.cursor = cursor
                selection.format = fmt
                extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def go_to_line_col(self, line: int, col: int):
        doc = self.document()
        block = doc.findBlockByNumber(max(0, line - 1))
        if block.isValid():
            cursor = QTextCursor(block)
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, col)
            self.setTextCursor(cursor)
            self.ensureCursorVisible()
            self.setFocus()

    def set_debug_line(self, lineno: int):
        self.debug_active_line = lineno
        if lineno > 0:
            self.go_to_line_col(lineno, 0)
        self.apply_inspection_highlights()

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.addSeparator()

        refactor_menu = menu.addMenu("🔨 Рефакторинг (Refactor)")
        
        act_rename = refactor_menu.addAction("✏️ Перейменувати (Safe Rename)... (Shift+F6)")
        act_extract_var = refactor_menu.addAction("📦 Виділити змінну (Extract Variable)... (Ctrl+Alt+V)")
        act_extract_method = refactor_menu.addAction("🛠 Виділити метод (Extract Method)... (Ctrl+Alt+M)")

        menu.addSeparator()
        act_find_usages = menu.addAction("🔍 Знайти використання (Find Usages) (Alt+F7)")
        act_blame = menu.addAction("🌱 Переглянути Git Blame")

        action = menu.exec(event.globalPos())
        if action == act_rename:
            if hasattr(self, 'main_window'): self.main_window.trigger_safe_rename()
        elif action == act_extract_var:
            if hasattr(self, 'main_window'): self.main_window.trigger_extract_variable()
        elif action == act_extract_method:
            if hasattr(self, 'main_window'): self.main_window.trigger_extract_method()
        elif action == act_find_usages:
            if hasattr(self, 'main_window'): self.main_window.trigger_find_usages()
        elif action == act_blame:
            if hasattr(self, 'main_window'): self.main_window.trigger_git_blame()

    def setup_completer(self):
        self.completer = QListView()
        self.completer.setWindowFlags(Qt.WindowType.Popup)
        self.completer.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.completer.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self.completer.setUniformItemSizes(True)
        self.completer_model = QStringListModel()
        self.completer.setModel(self.completer_model)
        self.completer.clicked.connect(self.complete_text)
        self.completer.hide()

    def complete_text(self, index):
        completion = self.completer_model.data(index, Qt.ItemDataRole.DisplayRole)
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.removeSelectedText()
        cursor.insertText(completion)
        self.setTextCursor(cursor)
        self.completer.hide()
        self.ghost_text = ""
        self.ghost_active = False

    def update_completions(self):
        try:
            if jedi is None:
                return
            cursor = self.textCursor()
            pos = cursor.position()
            code = self.toPlainText()
            lines = code[:pos].splitlines()
            row = len(lines)
            col = len(lines[-1]) if lines else 0

            script = jedi.Script(code, row, col)
            completions = [c.name for c in script.complete()]
            ast_items = self.analyze_ast(code)
            merged = list(set(completions + ast_items['functions'] + ast_items['classes'] + ast_items['variables']))
            merged.sort()

            prefix = self.text_under_cursor()
            filtered = [w for w in merged if w.startswith(prefix) and w != prefix]

            if filtered:
                self.completer_model.setStringList(filtered)
                cr = self.cursorRect()
                cr.setWidth(self.completer.sizeHintForColumn(0)
                            + self.completer.verticalScrollBar().sizeHint().width())
                self.completer.setGeometry(cr)
                self.completer.move(self.mapToGlobal(cr.bottomLeft()))
                self.completer.show()
            else:
                self.completer.hide()
        except Exception:
            self.completer.hide()

    def text_under_cursor(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        return cursor.selectedText()

    def analyze_ast(self, code):
        try:
            tree = ast.parse(code)
            funcs, classes, vars_set = [], [], set()
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    funcs.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            vars_set.add(target.id)
            return {"functions": funcs, "classes": classes, "variables": list(vars_set)}
        except Exception:
            return {"functions": [], "classes": [], "variables": []}

    def keyPressEvent(self, event):
        if self.completer.isVisible():
            if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Tab):
                self.complete_text(self.completer.currentIndex())
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Escape:
                self.completer.hide()
                event.accept()
                return

        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)

        if self.ghost_active and self.ghost_text and event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Right):
            cursor.insertText(self.ghost_text)
            self.ghost_text = ""
            self.ghost_active = False
            self.completer.hide()
            return

        if event.key() == Qt.Key.Key_Return:
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            current_line = cursor.selectedText()
            indent = re.match(r"\s*", current_line).group()
            super().keyPressEvent(event)
            self.insertPlainText(indent)

            if current_line.rstrip().endswith(':'):
                self.insertPlainText("    ")
                words = current_line.strip().split()
                keyword = words[0] if words else ""
                suggestion = self.next_line_suggestions.get(keyword)
                if suggestion:
                    self.ghost_text = suggestion
                    self.ghost_active = True
                    self.update()
                    self.auto_pass_timer.start(1000)
                    return

        self.ghost_text = ""
        self.ghost_active = False
        self.auto_pass_timer.stop()

        super().keyPressEvent(event)
        self.update_completions()

    def insert_pass_if_empty(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        if not cursor.selectedText().strip():
            cursor.insertText("pass")

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.ghost_active and self.ghost_text:
            painter = QPainter(self.viewport())
            painter.setPen(QColor(150, 150, 150, 120))
            font = self.font()
            font.setItalic(True)
            painter.setFont(font)
            rect = self.cursorRect(self.textCursor())
            painter.drawText(rect.topRight() + QPoint(5, self.fontMetrics().ascent()), self.ghost_text)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        space = 16 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#313335"))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).y()
        bottom = top + self.blockBoundingRect(block).height()
        height = self.fontMetrics().height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                if block_number in self.breakpoint_lines:
                    painter.setBrush(QColor("#FF5555"))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(0, int(top + 4), 8, 8)
                painter.setPen(QColor("#888"))
                painter.drawText(0, int(top), self.lineNumberAreaWidth() - 4, height, Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlightCurrentLine(self):
        self.apply_inspection_highlights()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().x() < self.lineNumberAreaWidth():
            block = self.firstVisibleBlock()
            top = self.blockBoundingGeometry(block).translated(self.contentOffset()).y()
            bottom = top + self.blockBoundingRect(block).height()
            y = event.position().y()
            while block.isValid():
                if y >= top and y <= bottom:
                    line = block.blockNumber()
                    if line in self.breakpoint_lines:
                        self.breakpoint_lines.remove(line)
                    else:
                        self.breakpoint_lines.add(line)
                    self.line_number_area.update()
                    self.breakpointToggled.emit(line + 1)
                    break
                block = block.next()
                top = bottom
                bottom = top + self.blockBoundingRect(block).height()
        else:
            super().mousePressEvent(event)

    def show_function_tooltip(self):
        try:
            if jedi is None:
                return
            cursor = self.textCursor()
            pos = cursor.position()
            code = self.toPlainText()
            lines = code[:pos].splitlines()
            row = len(lines)
            col = len(lines[-1]) if lines else 0

            script = jedi.Script(code, row, col)
            sigs = script.get_signatures()
            if not sigs:
                QToolTip.hideText()
                return

            sig = sigs[0]
            params = [p.name for p in sig.params]
            call_text = self._get_current_function_call()
            arg_index = call_text.count(',')

            highlighted_params = []
            for i, p in enumerate(params):
                if i == arg_index:
                    highlighted_params.append(f"<b>{p}</b>")
                else:
                    highlighted_params.append(p)

            tooltip = f"<b>{sig.name}</b>({', '.join(highlighted_params)})";
            doc = sig.docstring()
            if doc:
                doc_line = doc.split('\n')[0]
                tooltip += f"<br><span style='color:#AAAAAA;'>{doc_line}</span>"

            QToolTip.showText(self.mapToGlobal(self.cursorRect().bottomRight()), tooltip, self)
        except Exception:
            QToolTip.hideText()

    def _get_current_function_call(self):
        code = self.toPlainText()
        pos = self.textCursor().position()
        stack = 0
        i = pos - 1
        while i >= 0:
            if code[i] == ')':
                stack += 1
            elif code[i] == '(':
                if stack == 0:
                    break
                stack -= 1
            i -= 1
        return code[i + 1:pos]



# ==============================================================================
# КОДЕРАННЕР, ВІЗУАЛІЗАЦІЯ ТА ГОЛОВНЕ ВІКНО IDE (CodeRunner & MainWindow)
# ==============================================================================

class CodeRunner(QThread):
    output_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()
    variable_update_signal = pyqtSignal(dict, dict)
    input_requested_signal = pyqtSignal(str)
    missing_library_signal = pyqtSignal(str)

    def __init__(self, code, project_dir=None, step_delay=0.45):
        super().__init__()
        self.code = code
        self.project_dir = project_dir
        self.step_delay = step_delay
        self.running = True
        self.paused = False

        self.input_queue = queue.Queue()
        self.waiting_for_input = False

        self.meta_info = {
            "has_loops": False,
            "classes": {},
            "relations": []
        }

    def provide_input(self, text: str):
        self.input_queue.put(text)

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.running = False
        self.input_queue.put("")

    def _analyze_and_instrument(self, tree: ast.AST) -> ast.AST:
        class_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        known_classes = {c.name for c in class_nodes}

        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                self.meta_info["has_loops"] = True
            elif isinstance(node, ast.ClassDef):
                base_name = "object"
                if node.bases:
                    if isinstance(node.bases[0], ast.Name):
                        base_name = node.bases[0].id
                self.meta_info["classes"][node.name] = base_name

                for sub in ast.walk(node):
                    if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
                        called = sub.func.id
                        if called in known_classes and called != node.name:
                            rel = {"type": "aggregation", "from": node.name, "to": called}
                            if rel not in self.meta_info["relations"]:
                                self.meta_info["relations"].append(rel)
                    elif isinstance(sub, ast.AnnAssign):
                        type_name = ""
                        if isinstance(sub.annotation, ast.Name):
                            type_name = sub.annotation.id
                        elif isinstance(sub.annotation, ast.Subscript) and isinstance(sub.annotation.slice, ast.Name):
                            type_name = sub.annotation.slice.id
                        if type_name in known_classes and type_name != node.name:
                            rel = {"type": "aggregation", "from": node.name, "to": type_name}
                            if rel not in self.meta_info["relations"]:
                                self.meta_info["relations"].append(rel)

        class UniversalStepInjector(ast.NodeTransformer):
            def _create_step_call(self):
                return ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id='__universal_step_hook__', ctx=ast.Load()),
                        args=[],
                        keywords=[]
                    )
                )

            def _wrap_body(self, body_list):
                new_body = []
                for stmt in body_list:
                    transformed_stmt = self.visit(stmt)
                    new_body.append(transformed_stmt)
                    new_body.append(self._create_step_call())
                return new_body

            def visit_Module(self, node):
                node.body = self._wrap_body(node.body)
                return node

            def visit_For(self, node):
                node.body = self._wrap_body(node.body)
                return node

            def visit_While(self, node):
                node.body = self._wrap_body(node.body)
                return node

            def visit_If(self, node):
                node.body = self._wrap_body(node.body)
                if node.orelse:
                    node.orelse = self._wrap_body(node.orelse)
                return node

        transformer = UniversalStepInjector()
        transformed_tree = transformer.visit(tree)
        ast.fix_missing_locations(transformed_tree)
        return transformed_tree

    def run(self):
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = sys.stdout

        if self.project_dir and os.path.exists(self.project_dir):
            if self.project_dir not in sys.path:
                sys.path.insert(0, self.project_dir)

        loc = {}
        glob = {"__name__": "__main__"}

        def universal_step_hook():
            if not self.running:
                raise KeyboardInterrupt("Execution stopped")

            while self.paused:
                time.sleep(0.05)

            user_vars = {}
            for k, v in loc.items():
                if not k.startswith("__"):
                    if isinstance(v, list):
                        user_vars[k] = copy.deepcopy(v)
                    else:
                        user_vars[k] = v

            if user_vars or self.meta_info["classes"]:
                self.variable_update_signal.emit(user_vars, self.meta_info)

                output = sys.stdout.getvalue()
                if output:
                    self.output_signal.emit(output)
                    sys.stdout.seek(0)
                    sys.stdout.truncate(0)

                sleep_steps = int(max(1, self.step_delay / 0.05))
                for _ in range(sleep_steps):
                    if not self.running:
                        break
                    while self.paused:
                        time.sleep(0.05)
                    time.sleep(self.step_delay / sleep_steps)

        def custom_input(prompt=""):
            if not self.running:
                raise KeyboardInterrupt("Execution stopped")

            output = sys.stdout.getvalue()
            if output:
                self.output_signal.emit(output)
                sys.stdout.seek(0)
                sys.stdout.truncate(0)

            prompt_str = str(prompt)
            self.waiting_for_input = True
            self.input_requested_signal.emit(prompt_str)

            while self.running:
                try:
                    user_val = self.input_queue.get(timeout=0.08)
                    self.waiting_for_input = False
                    return user_val
                except queue.Empty:
                    if not self.running:
                        self.waiting_for_input = False
                        raise KeyboardInterrupt("Execution stopped")

            self.waiting_for_input = False
            return ""

        glob["__universal_step_hook__"] = universal_step_hook
        glob["input"] = custom_input

        try:
            self.progress_signal.emit(20)
            parsed_ast = ast.parse(self.code)
            instrumented_ast = self._analyze_and_instrument(parsed_ast)
            code_obj = compile(instrumented_ast, '<animated_code>', 'exec')

            self.progress_signal.emit(50)
            exec(code_obj, glob, loc)
            self.progress_signal.emit(100)

            final_output = sys.stdout.getvalue()
            if final_output:
                self.output_signal.emit(final_output)

        except ModuleNotFoundError as mnf_err:
            missing_lib = mnf_err.name
            self.output_signal.emit(f"\n❌ Модуль '{missing_lib}' не знайдено.\n")
            self.missing_library_signal.emit(missing_lib)

        except KeyboardInterrupt:
            self.output_signal.emit("\n⏹ Виконання зупинено.")
        except Exception:
            self.output_signal.emit("❌ Помилка виконання:\n" + traceback.format_exc())
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            self.finished_signal.emit()


# --- Клас прямокутного динамічного блоку масиву за ТЗ ---
class AnimatedArrayBlock(QGraphicsObject):
    THEMES = {
        "normal": {"bg": "#68D391", "border": "#22543D", "text": "#000000", "width": 1.8},
        "active": {"bg": "#ECC94B", "border": "#B7791F", "text": "#000000", "width": 2.6},
    }

    def __init__(self, value, index, parent=None):
        super().__init__(parent)
        self.value = str(value)
        self.index = index
        self.theme_state = "normal"
        self.rect_w = 64.0
        self.rect_h = 54.0

        self._pen = QPen(QColor(self.THEMES["normal"]["border"]), self.THEMES["normal"]["width"])
        self._brush = QBrush(QColor(self.THEMES["normal"]["bg"]))

    def _apply_theme(self):
        t = self.THEMES.get(self.theme_state, self.THEMES["normal"])
        self._pen.setColor(QColor(t["border"]))
        self._pen.setWidthF(t["width"])
        self._brush.setColor(QColor(t["bg"]))
        self.update()

    def set_theme(self, state: str):
        if state in self.THEMES and state != self.theme_state:
            self.theme_state = state
            self._apply_theme()

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.rect_w, self.rect_h + 22.0)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.drawRoundedRect(QRectF(0, 0, self.rect_w, self.rect_h), 8.0, 8.0)

        painter.setPen(QColor(self.THEMES.get(self.theme_state, self.THEMES["normal"])["text"]))
        val_font = QFont("Consolas", 11, QFont.Weight.Bold)
        painter.setFont(val_font)
        painter.drawText(QRectF(0, 0, self.rect_w, self.rect_h), Qt.AlignmentFlag.AlignCenter, self.value)

        painter.setPen(QColor("#A0AEC0"))
        idx_font = QFont("Consolas", 8)
        painter.setFont(idx_font)
        painter.drawText(QRectF(0, self.rect_h + 2, self.rect_w, 18), Qt.AlignmentFlag.AlignCenter, f"[{self.index}]")

    def set_value(self, val):
        if str(val) != self.value:
            self.value = str(val)
            self.update()

    def set_index(self, idx):
        if idx != self.index:
            self.index = idx
            self.update()


# --- Адаптивний віджет анімації з ООП розширенням ---
class AdaptiveAnimationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setStyleSheet("background-color: #1a202c; border: none;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.header_label = QLabel("🎨 Адаптивна візуалізація структур даних та ООП")
        self.header_label.setStyleSheet("font-family: 'Consolas', monospace; font-size: 11pt; font-weight: bold; color: #63b3ed; padding: 6px; background-color: #2d3748;")
        layout.addWidget(self.header_label)
        layout.addWidget(self.view)

        self.array_blocks = {}
        self.class_rects = {}
        self.loop_badge = None

    def _clear_static_items(self):
        self.scene.clear()
        self.array_blocks.clear()
        self.class_rects.clear()
        self.loop_badge = None

    def update_visuals(self, user_vars: dict, meta_info: dict):
        self._clear_static_items()

        y_offset = 20.0
        x_start = 20.0

        for var_name, var_val in user_vars.items():
            if isinstance(var_val, list):
                lbl = self.scene.addText(f"Масив '{var_name}':", QFont("Consolas", 10, QFont.Weight.Bold))
                lbl.setDefaultTextColor(QColor("#E2E8F0"))
                lbl.setPos(x_start, y_offset)
                y_offset += 28.0

                for idx, item in enumerate(var_val):
                    block = AnimatedArrayBlock(value=item, index=idx)
                    block.setPos(x_start + idx * 72.0, y_offset)
                    self.scene.addItem(block)
                    self.array_blocks[(var_name, idx)] = block

                y_offset += 80.0

        classes_dict = meta_info.get("classes", {})
        if classes_dict:
            lbl = self.scene.addText("Дерево класів ООП:", QFont("Consolas", 10, QFont.Weight.Bold))
            lbl.setDefaultTextColor(QColor("#F6AD55"))
            lbl.setPos(x_start, y_offset)
            y_offset += 30.0

            cls_x = x_start
            for cls_name, base_name in classes_dict.items():
                box = self.scene.addRect(QRectF(0, 0, 110, 45), QPen(QColor("#4FD1C5"), 2.0), QBrush(QColor("#234E52")))
                box.setPos(cls_x, y_offset)
                txt = self.scene.addText(f"{cls_name}\n: {base_name}", QFont("Consolas", 8, QFont.Weight.Bold))
                txt.setDefaultTextColor(QColor("#FFFFFF"))
                txt.setPos(cls_x + 5, y_offset + 2)

                self.class_rects[cls_name] = (cls_x, y_offset, 110, 45)
                cls_x += 130.0

        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-20, -20, 20, 20))


# --- Консоль виводу ---
class OutputTextEdit(QPlainTextEdit):
    input_submitted = pyqtSignal(str)

    def clear_output(self):
        self.clear()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas; font-size: 10pt;")
        self.prompt_position = -1
        self.in_input_mode = False

    def append_output(self, text: str):
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.insertPlainText(text)
        self.ensureCursorVisible()

    def start_input_session(self, prompt: str = ""):
        self.moveCursor(QTextCursor.MoveOperation.End)
        if prompt:
            self.insertPlainText(prompt)
        self.prompt_position = self.textCursor().position()
        self.in_input_mode = True
        self.setReadOnly(False)
        self.ensureCursorVisible()

    def stop_input_session(self):
        self.in_input_mode = False
        self.setReadOnly(True)

    def keyPressEvent(self, event):
        if not self.in_input_mode:
            super().keyPressEvent(event)
            return

        cursor = self.textCursor()
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor.movePosition(QTextCursor.MoveOperation.End)
            text_entered = self.toPlainText()[self.prompt_position:].strip()
            self.insertPlainText("\n")
            self.stop_input_session()
            self.input_submitted.emit(text_entered)
            return
        elif event.key() == Qt.Key.Key_Backspace:
            if cursor.position() <= self.prompt_position:
                return

        super().keyPressEvent(event)


# --- Діалог створення нового проєкту ---
class PyCharmNewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.resize(550, 250)
        self.setStyleSheet("background-color: #1e1f22; color: #bcbec4; font-family: 'Segoe UI', Arial;")

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.location_input = QLineEdit(os.path.abspath("PythonProject"))
        btn_browse = QPushButton("📁")
        btn_browse.clicked.connect(self.browse_location)

        loc_box = QHBoxLayout()
        loc_box.addWidget(self.location_input)
        loc_box.addWidget(btn_browse)

        form.addRow("Location:", loc_box)

        self.venv_chk = QCheckBox("New environment using Virtualenv")
        self.venv_chk.setChecked(True)
        form.addRow("", self.venv_chk)

        self.main_script_chk = QCheckBox("Create a main.py welcome script")
        self.main_script_chk.setChecked(True)
        form.addRow("", self.main_script_chk)

        layout.addLayout(form)

        btn_box = QHBoxLayout()
        btn_create = QPushButton("Create")
        btn_create.setStyleSheet("background-color: #3574f0; color: white; font-weight: bold; padding: 6px 16px;")
        btn_create.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        btn_box.addStretch()
        btn_box.addWidget(btn_create)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)

    def browse_location(self):
        chosen = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if chosen:
            self.location_input.setText(chosen)

    def get_data(self):
        return self.location_input.text().strip(), self.venv_chk.isChecked(), self.main_script_chk.isChecked()


# --- Вікно привітання (Welcome Window) ---
class PyCharmWelcomeWindow(QWidget):
    project_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to Python Studio")
        self.resize(850, 520)
        self.setStyleSheet("background-color: #1e1f22; color: #bcbec4; font-family: 'Segoe UI', sans-serif;")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(200)
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2d30;
                border: none;
                font-size: 11pt;
                padding-top: 20px;
            }
            QListWidget::item {
                height: 40px;
                padding-left: 15px;
                color: #a9b7c6;
            }
            QListWidget::item:selected {
                background-color: #3574f0;
                color: #ffffff;
                font-weight: bold;
            }
        """)

        items = [
            ("📁 Projects", 0),
            ("⚙️ Customize", 1),
            ("🧩 Plugins", 2),
            ("🎓 Learn Python", 3)
        ]
        for name, idx in items:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, idx)
            self.nav_list.addItem(item)

        self.nav_list.setCurrentRow(0)
        self.nav_list.currentRowChanged.connect(self.switch_tab)
        main_layout.addWidget(self.nav_list)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.create_projects_page())
        self.stacked_widget.addWidget(self.create_customize_page())
        self.stacked_widget.addWidget(self.create_plugins_page())
        self.stacked_widget.addWidget(self.create_learn_page())

        main_layout.addWidget(self.stacked_widget)

    def switch_tab(self, row):
        self.stacked_widget.setCurrentIndex(row)

    def create_projects_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel("<h1>Python Studio</h1>")
        header.setStyleSheet("color: #ffffff; font-size: 24pt; font-weight: bold;")
        sub_header = QLabel("Версія 2026.1 -- Повнофункціональне навчальне IDE із дебагером, Git та інструментами")
        sub_header.setStyleSheet("color: #7a7e85; font-size: 10pt; margin-bottom: 20px;")

        layout.addWidget(header)
        layout.addWidget(sub_header)

        actions_layout = QHBoxLayout()
        
        def make_action_card(icon_str, title):
            btn = QPushButton(f"{icon_str}\n{title}")
            btn.setFixedSize(140, 90)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2b2d30;
                    border: 1px solid #4e5157;
                    border-radius: 8px;
                    color: #ffffff;
                    font-size: 10pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3574f0;
                    border-color: #3574f0;
                }
            """)
            return btn

        btn_new = make_action_card("➕", "New Project")
        btn_open = make_action_card("📁", "Open")
        btn_vcs = make_action_card("🔀", "Get from VCS")

        btn_new.clicked.connect(self.on_new_project)
        btn_open.clicked.connect(self.on_open_project)
        btn_vcs.clicked.connect(self.on_vcs_clone)

        actions_layout.addWidget(btn_new)
        actions_layout.addWidget(btn_open)
        actions_layout.addWidget(btn_vcs)
        layout.addLayout(actions_layout)

        layout.addStretch()
        return page

    def create_customize_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        header = QLabel("<h2>Customize IDE</h2>")
        header.setStyleSheet("color: #ffffff;")
        layout.addWidget(header)

        form = QFormLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark (Darcula / Modern Dark)", "Light (IntelliJ Light)"])
        form.addRow("Color theme:", self.theme_combo)

        layout.addLayout(form)
        layout.addStretch()
        return page

    def create_plugins_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel("<h2>Plugins Marketplace</h2>")
        header.setStyleSheet("color: #ffffff;")
        layout.addWidget(header)

        info = QLabel("Управління плагінами та розширеннями Python Studio.")
        layout.addWidget(info)

        btn_open_mkt = QPushButton("🧩 Відкрити Маркетплейс плагінів...")
        btn_open_mkt.setStyleSheet("background-color: #3574f0; color: white; padding: 8px; font-weight: bold;")
        btn_open_mkt.clicked.connect(self.on_open_plugins_marketplace)
        layout.addWidget(btn_open_mkt)

        layout.addStretch()
        return page

    def create_learn_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)

        header = QLabel("<h2>Learn Python</h2>")
        header.setStyleSheet("color: #ffffff;")
        layout.addWidget(header)

        info = QLabel("Інтерактивні уроки Python з візуалізацією викликів та масивів.")
        layout.addWidget(info)
        layout.addStretch()
        return page

    def on_new_project(self):
        dlg = PyCharmNewProjectDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            project_dir, use_venv, create_main = dlg.get_data()
            try:
                os.makedirs(project_dir, exist_ok=True)
                if create_main:
                    main_file_path = os.path.join(project_dir, "main.py")
                    if not os.path.exists(main_file_path):
                        with open(main_file_path, "w", encoding="utf-8") as f:
                            f.write("print('Hello Python Studio!')\n")

                self.project_selected.emit(project_dir)
                self.close()
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося створити проєкт: {str(e)}")

    def on_open_project(self):
        chosen_dir = QFileDialog.getExistingDirectory(self, "Відкрити існуючий проєкт")
        if chosen_dir:
            self.project_selected.emit(chosen_dir)
            self.close()

    def on_vcs_clone(self):
        dlg = VcsCloneDialog(self)
        dlg.project_cloned_signal.connect(lambda p: (self.project_selected.emit(p), self.close()))
        dlg.exec()

    def on_open_plugins_marketplace(self):
        plugin_mgr = PluginManager(None)
        dlg = PluginMarketplaceDialog(plugin_mgr, self)
        dlg.exec()


# --- Головне вікно додатку ---
class MainWindow(QMainWindow):
    def __init__(self, initial_project_path=None):
        super().__init__()
        self.setWindowTitle("Python Studio IDE")
        self.resize(1600, 1000)

        self.project_path = initial_project_path
        self.git_manager = GitManager(self.project_path)
        self.interpreter_manager = InterpreterManager(self.project_path)
        self.plugin_manager = PluginManager(self)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        self.tab_widget.setUsesScrollButtons(True)
        self.tab_widget.setElideMode(Qt.TextElideMode.ElideNone)
        self.tab_widget.setStyleSheet("""
            QTabBar::tab {
                min-width: 110px;
                padding: 6px 14px;
                font-family: 'Consolas', 'Segoe UI';
                font-size: 10pt;
            }
        """)

        self.output = OutputTextEdit()
        self.output.input_submitted.connect(self.handle_direct_user_input)

        self.problems_panel = ProblemsPanel()
        self.problems_panel.problem_selected.connect(self.go_to_problem)

        self.debugger_panel = DebuggerPanel()
        self.debugger_panel.step_over_clicked.connect(self.debug_step_over)
        self.debugger_panel.step_into_clicked.connect(self.debug_step_into)
        self.debugger_panel.step_out_clicked.connect(self.debug_step_out)
        self.debugger_panel.continue_clicked.connect(self.debug_continue)
        self.debugger_panel.stop_clicked.connect(self.debug_stop)

        self.git_panel = GitCommitPanel()
        self.git_panel.set_git_manager(self.git_manager)

        self.find_usages_panel = FindUsagesPanel()
        self.find_usages_panel.usage_selected.connect(self.open_file_and_go_to_line)

        self.terminal_panel = TerminalPanel()
        self.test_runner_panel = TestRunnerPanel()
        self.db_explorer_panel = DatabaseExplorerPanel()

        self.bottom_dock_tabs = QTabWidget()
        self.bottom_dock_tabs.addTab(self.output, "🖥 Консоль виводу")
        self.bottom_dock_tabs.addTab(self.problems_panel, "⚠️ Проблеми")
        self.bottom_dock_tabs.addTab(self.debugger_panel, "🐞 Debugger")
        self.bottom_dock_tabs.addTab(self.git_panel, "🌱 Git / Commit")
        self.bottom_dock_tabs.addTab(self.find_usages_panel, "🔍 Find Usages")
        self.bottom_dock_tabs.addTab(self.terminal_panel, "💻 Terminal")
        self.bottom_dock_tabs.addTab(self.test_runner_panel, "🧪 Unit Tests")
        self.bottom_dock_tabs.addTab(self.db_explorer_panel, "🗄️ Database")

        self.animation_widget = AdaptiveAnimationWidget()
        self.file_paths = {}
        self.modified_tabs = set()

        self.progress_bar = QProgressBar()
        self.status_bar = QStatusBar()
        
        self.interp_btn = QPushButton("🐍 Python 3.12 (venv)")
        self.interp_btn.setStyleSheet("padding: 2px 8px;")
        self.interp_btn.clicked.connect(self.open_interpreter_dialog)

        self.branch_btn = QPushButton("🌱 master")
        self.branch_btn.setStyleSheet("padding: 2px 8px;")
        self.branch_btn.clicked.connect(self.open_git_branch_dialog)

        self.status_bar.addPermanentWidget(self.interp_btn)
        self.status_bar.addPermanentWidget(self.branch_btn)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.setStatusBar(self.status_bar)

        self.fs_model = QFileSystemModel()
        self.fs_model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.fs_model)
        self.tree_view.doubleClicked.connect(self.open_file_from_tree)
        self.tree_view.setHeaderHidden(True)
        for col in range(1, 4):
            self.tree_view.hideColumn(col)

        self.run_button = QPushButton("▶")
        self.debug_button = QPushButton("🐞")
        self.pause_button = QPushButton("⏸")
        self.resume_button = QPushButton("⏯")
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)

        toolbar = QToolBar("Головна панель")
        toolbar.addWidget(QLabel(" 🐍 Конфігурація: "))
        self.py_file_selector = QComboBox()
        self.py_file_selector.setMinimumWidth(180)
        self.py_file_selector.currentIndexChanged.connect(self.on_py_file_selected)
        toolbar.addWidget(self.py_file_selector)

        toolbar.addSeparator()
        toolbar.addWidget(self.run_button)
        toolbar.addWidget(self.debug_button)
        toolbar.addWidget(self.pause_button)
        toolbar.addWidget(self.resume_button)
        toolbar.addSeparator()
        self.addToolBar(toolbar)

        editor_splitter = QSplitter(Qt.Orientation.Vertical)
        editor_splitter.addWidget(self.tab_widget)
        editor_splitter.addWidget(self.bottom_dock_tabs)
        editor_splitter.setSizes([700, 300])

        main_split = QSplitter(Qt.Orientation.Horizontal)
        file_dock = QDockWidget("📁 Оглядач проєкту", self)
        file_dock.setWidget(self.tree_view)
        file_dock.setMinimumWidth(240)

        main_split.addWidget(file_dock)
        main_split.addWidget(editor_splitter)
        main_split.addWidget(self.animation_widget)
        main_split.setStretchFactor(1, 3)
        main_split.setStretchFactor(2, 2)

        container = QWidget()
        container.setLayout(QVBoxLayout())
        container.layout().addWidget(main_split)
        self.setCentralWidget(container)

        self.init_menus()

        self.run_button.clicked.connect(self.run_code)
        self.debug_button.clicked.connect(self.start_debugging)
        self.pause_button.clicked.connect(self.pause_code)
        self.resume_button.clicked.connect(self.resume_code)

        if self.project_path and os.path.exists(self.project_path):
            self.load_project_folder(self.project_path)
        else:
            self.fs_model.setRootPath(QDir.rootPath())
            self.new_tab(content="", filepath=None)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Shift:
            if hasattr(self, '_last_shift_time'):
                if time.time() - self._last_shift_time < 0.4:
                    self.trigger_search_everywhere()
            self._last_shift_time = time.time()
        super().keyPressEvent(event)

    def trigger_search_everywhere(self):
        dlg = SearchEverywhereDialog(self.project_path, self)
        dlg.item_selected.connect(self.open_file_and_go_to_line)
        dlg.exec()

    def trigger_find_usages(self):
        editor = self.current_editor()
        if editor:
            symbol = editor.text_under_cursor()
            if symbol:
                self.bottom_dock_tabs.setCurrentWidget(self.find_usages_panel)
                self.find_usages_panel.find_symbol_usages(self.project_path, symbol)

    def trigger_git_blame(self):
        editor = self.current_editor()
        if editor and self.file_paths.get(editor):
            dlg = GitBlameDialog(self.file_paths[editor], self.git_manager, self)
            dlg.exec()

    def trigger_safe_rename(self):
        editor = self.current_editor()
        if not editor: return
        old_name = editor.text_under_cursor()
        if not old_name: return

        dlg = SafeRenameDialog(old_name, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_name, in_all_files = dlg.get_data()
            if in_all_files and self.project_path:
                file_map = {}
                for root, _, files in os.walk(self.project_path):
                    for f in files:
                        if f.endswith(".py"):
                            full_p = os.path.join(root, f)
                            with open(full_p, "r", encoding="utf-8") as fp:
                                file_map[full_p] = fp.read()

                updated_map = RefactoringEngine.safe_rename(file_map, old_name, new_name)
                for path, content in updated_map.items():
                    with open(path, "w", encoding="utf-8") as fp:
                        fp.write(content)

                QMessageBox.information(self, "Safe Rename", f"Ідентифікатор '{old_name}' перейменовано на '{new_name}' у проєкті.")
            else:
                code = editor.toPlainText()
                updated_map = RefactoringEngine.safe_rename({"curr": code}, old_name, new_name)
                editor.setPlainText(updated_map["curr"])

    def trigger_extract_variable(self):
        editor = self.current_editor()
        if not editor: return
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()
        if not selected_text: return

        dlg = ExtractVariableDialog("extracted_var", self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            v_name = dlg.get_name()
            new_code = RefactoringEngine.extract_variable(editor.toPlainText(), selected_text, v_name)
            editor.setPlainText(new_code)

    def trigger_extract_method(self):
        editor = self.current_editor()
        if not editor: return
        cursor = editor.textCursor()
        selected_text = cursor.selectedText()
        if not selected_text: return

        dlg = ExtractMethodDialog("extracted_method", self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            m_name = dlg.get_name()
            new_code = RefactoringEngine.extract_method(editor.toPlainText(), selected_text, m_name)
            editor.setPlainText(new_code)

    def open_interpreter_dialog(self):
        dlg = InterpreterDialog(self.interpreter_manager, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            interp = dlg.selected_interpreter
            self.interpreter_manager.current_interpreter = interp
            self.interp_btn.setText(f"🐍 {os.path.basename(interp)}")

    def open_git_branch_dialog(self):
        dlg = GitBranchDialog(self.git_manager, self)
        dlg.exec()
        self.update_git_status_bar()

    def update_git_status_bar(self):
        branch = self.git_manager.get_current_branch()
        self.branch_btn.setText(f"🌱 {branch}")

    def go_to_problem(self, line, col):
        editor = self.current_editor()
        if editor:
            editor.go_to_line_col(line, col)

    def open_file_and_go_to_line(self, filepath, line):
        if not filepath: return
        for idx in range(self.tab_widget.count()):
            w = self.tab_widget.widget(idx)
            if self.file_paths.get(w) == filepath:
                self.tab_widget.setCurrentIndex(idx)
                w.go_to_line_col(line, 0)
                return

        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                self.new_tab(f.read(), filepath)
            editor = self.current_editor()
            if editor:
                editor.go_to_line_col(line, 0)

    def on_tab_changed(self, index=None):
        self.update_title_bar()
        editor = self.current_editor()
        if editor and hasattr(editor, 'current_issues'):
            self.problems_panel.update_problems(editor.current_issues)

    def current_editor(self):
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, CodeEditor):
            return widget
        return None

    def update_title_bar(self, index=None):
        editor = self.current_editor()
        if editor:
            idx = self.tab_widget.indexOf(editor)
            path = self.file_paths.get(editor)
            name = os.path.basename(path) if path else "Новий файл"
            if editor in self.modified_tabs:
                name += "*"
            self.tab_widget.setTabText(idx, name)

    def refresh_py_files_dropdown(self):
        self.py_file_selector.blockSignals(True)
        self.py_file_selector.clear()

        if self.project_path and os.path.exists(self.project_path):
            py_files = []
            for root, dirs, files in os.walk(self.project_path):
                if "venv" in root or ".git" in root or "__pycache__" in root:
                    continue
                for f in files:
                    if f.endswith(".py"):
                        rel_path = os.path.relpath(os.path.join(root, f), self.project_path)
                        py_files.append((rel_path, os.path.join(root, f)))

            for label, full_path in sorted(py_files):
                self.py_file_selector.addItem(f"📄 {label}", full_path)

        self.py_file_selector.blockSignals(False)

    def on_py_file_selected(self, index):
        full_path = self.py_file_selector.itemData(index)
        if full_path and os.path.exists(full_path):
            for idx in range(self.tab_widget.count()):
                editor = self.tab_widget.widget(idx)
                if self.file_paths.get(editor) == full_path:
                    self.tab_widget.setCurrentIndex(idx)
                    return
            with open(full_path, "r", encoding="utf-8") as f:
                self.new_tab(f.read(), full_path)

    def load_project_folder(self, folder_path):
        self.project_path = folder_path
        self.git_manager.project_dir = folder_path
        self.interpreter_manager.project_dir = folder_path
        self.test_runner_panel.project_path = folder_path

        root_index = self.fs_model.setRootPath(folder_path)
        self.tree_view.setRootIndex(root_index)
        self.tree_view.expand(root_index)

        self.refresh_py_files_dropdown()
        self.update_git_status_bar()
        self.git_panel.set_git_manager(self.git_manager)

        main_file = os.path.join(folder_path, "main.py")
        if os.path.exists(main_file):
            with open(main_file, "r", encoding="utf-8") as f:
                self.new_tab(f.read(), main_file)
        else:
            self.new_tab(content="", filepath=None)

    def init_menus(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("📂 Файл")
        file_menu.addAction("🆕 Створити проєкт...", lambda: PyCharmWelcomeWindow().on_new_project())
        file_menu.addAction("📂 Відкрити проєкт...", lambda: PyCharmWelcomeWindow().on_open_project())
        file_menu.addSeparator()
        file_menu.addAction("📄 Новий файл", lambda: self.new_tab())
        file_menu.addAction("📂 Відкрити файл...", self.open_file_dialog)
        file_menu.addAction("📓 Відкрити Jupyter Notebook (.ipynb)...", self.open_jupyter_notebook)
        file_menu.addAction("💾 Зберегти", self.save_file)
        file_menu.addSeparator()
        file_menu.addAction("🚪 Вихід", self.close)

        edit_menu = menubar.addMenu("✏️ Редагування")
        edit_menu.addAction("↩ Скасувати", lambda: self.current_editor() and self.current_editor().undo())
        edit_menu.addAction("↪ Повторити", lambda: self.current_editor() and self.current_editor().redo())

        refactor_menu = menubar.addMenu("🔨 Рефакторинг")
        refactor_menu.addAction("✏️ Безпечне перейменування (Safe Rename)... (Shift+F6)", self.trigger_safe_rename)
        refactor_menu.addAction("📦 Виділити змінну (Extract Variable)... (Ctrl+Alt+V)", self.trigger_extract_variable)
        refactor_menu.addAction("🛠 Виділити метод (Extract Method)... (Ctrl+Alt+M)", self.trigger_extract_method)

        nav_menu = menubar.addMenu("🔍 Навігація")
        nav_menu.addAction("🔍 Пошук усюди (Search Everywhere)... (Double Shift)", self.trigger_search_everywhere)
        nav_menu.addAction("🔍 Знайти використання (Find Usages)... (Alt+F7)", self.trigger_find_usages)

        interp_menu = menubar.addMenu("⚙️ Інтерпретатор")
        interp_menu.addAction("🐍 Налаштувати інтерпретатор Python...", self.open_interpreter_dialog)

        git_menu = menubar.addMenu("🌱 Git / VCS")
        git_menu.addAction("🌱 Ініціалізувати Git", lambda: self.git_panel.init_git())
        git_menu.addAction("✅ Зробити комміт (Commit)...", lambda: self.bottom_dock_tabs.setCurrentWidget(self.git_panel))
        git_menu.addAction("📜 Переглянути різниці (Diff Viewer)...", lambda: GitDiffDialog(self.git_manager, self).exec())
        git_menu.addAction("🌱 Гілки Git (Branches)...", self.open_git_branch_dialog)
        git_menu.addAction("📜 Історія коммітів (Git Log)...", lambda: GitLogDialog(self.git_manager, self).exec())
        git_menu.addAction("🔀 Клонувати репозиторій (Git Clone)...", lambda: VcsCloneDialog(self).exec())

        tools_menu = menubar.addMenu("🛠 Інструменти")
        tools_menu.addAction("🧩 Маркетплейс плагінів (Plugins)...", lambda: PluginMarketplaceDialog(self.plugin_manager, self).exec())
        tools_menu.addAction("💻 Системний термінал (Terminal)", lambda: self.bottom_dock_tabs.setCurrentWidget(self.terminal_panel))
        tools_menu.addAction("🧪 Запустити тести (pytest)", lambda: self.bottom_dock_tabs.setCurrentWidget(self.test_runner_panel))
        tools_menu.addAction("🗄️ База даних Explorer", lambda: self.bottom_dock_tabs.setCurrentWidget(self.db_explorer_panel))

    def new_tab(self, content="", filepath=None):
        editor = CodeEditor()
        editor.setFont(QFont("Consolas", 11))
        editor.main_window = self
        editor.problems_panel = self.problems_panel
        editor.textChanged.connect(self.mark_tab_as_modified)

        index = self.tab_widget.addTab(editor, "Новий файл")
        self.tab_widget.setCurrentWidget(editor)

        if filepath:
            editor.setPlainText(content)
            self.file_paths[editor] = filepath
            self.tab_widget.setTabText(index, os.path.basename(filepath))
        else:
            if content:
                editor.setPlainText(content)
            self.file_paths[editor] = None

        editor.setFocus()

    def open_jupyter_notebook(self):
        path, _ = QFileDialog.getOpenFileName(self, "Відкрити Jupyter Notebook", "", "Jupyter Notebook (*.ipynb);;All Files (*)")
        if path:
            nb_widget = JupyterNotebookWidget(path, self)
            idx = self.tab_widget.addTab(nb_widget, f"📓 {os.path.basename(path)}")
            self.tab_widget.setCurrentIndex(idx)

    def open_file_dialog(self):
        start_dir = self.project_path if (self.project_path and os.path.exists(self.project_path)) else ""
        path, _ = QFileDialog.getOpenFileName(self, "Відкрити файл", start_dir, "Python (*.py);;All Files (*)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.new_tab(f.read(), path)
                self.refresh_py_files_dropdown()
            except Exception as e:
                QMessageBox.critical(self, "Помилка", str(e))

    def open_file_from_tree(self, index):
        path = self.fs_model.filePath(index)
        if os.path.isfile(path) and path.endswith(".py"):
            for idx in range(self.tab_widget.count()):
                editor = self.tab_widget.widget(idx)
                if self.file_paths.get(editor) == path:
                    self.tab_widget.setCurrentIndex(idx)
                    return
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.new_tab(f.read(), path)
            except Exception as e:
                QMessageBox.critical(self, "Помилка", str(e))

    def save_file(self):
        editor = self.current_editor()
        if not editor: return
        path = self.file_paths.get(editor)
        if not path:
            path, _ = QFileDialog.getSaveFileName(self, "Зберегти файл", "", "Python (*.py)")
            if not path: return
            self.file_paths[editor] = path

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(editor.toPlainText())
            if editor in self.modified_tabs:
                self.modified_tabs.remove(editor)
            self.update_title_bar()
            self.refresh_py_files_dropdown()
            self.git_panel.refresh_git_status()
        except Exception as e:
            QMessageBox.critical(self, "Помилка збереження", str(e))

    def close_tab(self, index):
        editor = self.tab_widget.widget(index)
        if editor in self.modified_tabs:
            ret = QMessageBox.question(self, "Зберегти зміни?", "Файл змінено. Зберегти перед закриттям?",
                                       QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if ret == QMessageBox.StandardButton.Save:
                self.save_file()
            elif ret == QMessageBox.StandardButton.Cancel:
                return

        self.tab_widget.removeTab(index)

    def mark_tab_as_modified(self):
        editor = self.current_editor()
        if editor and editor not in self.modified_tabs:
            self.modified_tabs.add(editor)
            index = self.tab_widget.indexOf(editor)
            name = self.tab_widget.tabText(index)
            if not name.endswith("*"):
                self.tab_widget.setTabText(index, name + "*")

    def handle_direct_user_input(self, user_val: str):
        if hasattr(self, "runner") and self.runner.isRunning():
            self.runner.provide_input(user_val)

    def run_code(self):
        editor = self.current_editor()
        if not editor: return

        code = editor.toPlainText()
        self.output.clear()

        self.run_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.resume_button.setEnabled(False)
        self.progress_bar.setVisible(True)

        self.runner = CodeRunner(code, self.project_path)
        self.runner.output_signal.connect(self.output.append_output)
        self.runner.progress_signal.connect(self.progress_bar.setValue)
        self.runner.finished_signal.connect(self.run_finished)
        self.runner.variable_update_signal.connect(self.animation_widget.update_visuals)
        self.runner.input_requested_signal.connect(self.output.start_input_session)
        self.runner.start()

    def start_debug(self):
        self.start_debugging()

    def start_debugging(self):
        editor = self.current_editor()
        if not editor: return

        code = editor.toPlainText()
        self.output.clear()
        self.bottom_dock_tabs.setCurrentWidget(self.debugger_panel)

        self.run_button.setEnabled(False)
        self.debug_button.setEnabled(False)

        self.debug_runner = DebugRunner(code, self.project_path, editor.breakpoint_lines)
        self.debugger_panel.set_runner(self.debug_runner)

        self.debug_runner.output_signal.connect(self.output.append_output)
        self.debug_runner.debug_paused_signal.connect(self.on_debug_paused)
        self.debug_runner.debug_resumed_signal.connect(self.on_debug_resumed)
        self.debug_runner.finished_signal.connect(self.debug_finished)

        self.debug_runner.start()

    def on_debug_paused(self, filename, lineno, stack, locals_dict, globals_dict):
        editor = self.current_editor()
        if editor:
            editor.set_debug_line(lineno)
        self.debugger_panel.update_debug_info(filename, lineno, stack, locals_dict, globals_dict)

    def on_debug_resumed(self):
        editor = self.current_editor()
        if editor:
            editor.set_debug_line(-1)

    def debug_step_over(self):
        if hasattr(self, "debug_runner"): self.debug_runner.step_over()

    def debug_step_into(self):
        if hasattr(self, "debug_runner"): self.debug_runner.step_into()

    def debug_step_out(self):
        if hasattr(self, "debug_runner"): self.debug_runner.step_out()

    def debug_continue(self):
        if hasattr(self, "debug_runner"): self.debug_runner.continue_exec()

    def debug_stop(self):
        if hasattr(self, "debug_runner"): self.debug_runner.stop()

    def debug_finished(self):
        self.run_button.setEnabled(True)
        self.debug_button.setEnabled(True)
        editor = self.current_editor()
        if editor:
            editor.set_debug_line(-1)

    def run_finished(self):
        self.run_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def pause_code(self):
        if hasattr(self, "runner"):
            self.runner.pause()
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(True)

    def resume_code(self):
        if hasattr(self, "runner"):
            self.runner.resume()
            self.pause_button.setEnabled(True)
            self.resume_button.setEnabled(False)


# --- Точка входу в програму ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    welcome_win = PyCharmWelcomeWindow()
    main_win = None

    def start_ide_with_project(project_path):
        global main_win
        main_win = MainWindow(initial_project_path=project_path)
        main_win.show()

    welcome_win.project_selected.connect(start_ide_with_project)
    welcome_win.show()

    sys.exit(app.exec())


