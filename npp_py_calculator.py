# -*- coding: utf-8 -*-
# npp_py_calculator
# Делаем деление / и // in Python 2 точно таким же, как в Python 3
# 
# 2026-08-03 Изменен формат результата умножение целых чисел, результат 
#            умножения целых всегда выдается в виде целого числа 
# 2026-09-04 
# - Добавлена переменная для задания количество значащих цифр 
#   для чисел с плавающей точкой
# - Реализована полная изоляция контекста одной строки от другой
# - Перед вычисляемым выражением разрешены модификаторы. 
#    - Если модификатора нет используется режим по умолчанию
#     {BN} - банковское округление и число символов, например {B12}
#     {h}  - целые числа, hex формат
#     {b}  - целые числа, двоичный формат
#     {a}  - целые числа, все форматы, например "65 (0x41, 0b1000001)"
#     {help} - справка по использованию калькулятора
#     {math} - справка по библиотеке math
#     {math имя_функции} - справка по конкретной функции библиотеки math
#     {config} - вывод текущих настроек калькулятора
#     {SB} - установить арифметическое округление по умолчанию и сохранить в конфиг
#     {SA} - установить банковское округление по умолчанию и сохранить в конфиг
#     {SN} - установить точность по умолчанию (например, {S3}) и сохранить в конфиг
# - Разрешены вычисления внутри текста
# 2026-09-14
# - Добавлено рекурсивное форматирование элементов контейнеров (списки, 
#   кортежи, словари, множества) с применением DEFAULT_FLOAT_PRECISION
# 2026-10-02
# - Добавлена поддержка модификаторов {math} и {math имя_функции} для вывода справки
# - Добавлена команда {help} для вывода встроенной справки по работе калькулятора
# 2026-10-03
# - Исправлено регулярное выражение: убран нежадный алгоритм, захватывавший '=' внутри
# - Жестко ограничили шаблон поиска только теми модификаторами, которые 
#   задекларированы в спецификации.
# 2026-10-15
# - Интегрирована система позиционного выравнивания результатов (DEFAULT_SPACING_COLUMN).
# - Добавлены локальный модификатор {P<N>} и перманентная команда {SP<N>} с 
#   автосохранением в JSON-конфиг.
# 2026-11-20
# - Удалено банковское округление и все связанное с ним: DEFAULT_ROUND_MODE,
#   команды {SA}/{SB}, модификатор {BN}. Для ручных расчетов оно не нужно.
# - Единственное правило округления — арифметическое (половина уходит от нуля).
# - Вывод вещественных чисел тоже приведён к арифметическому округлению:
#   раньше его делал str.format() по банковскому правилу.
# - Исправлено: {SN} без выражения (например "{S3} =") теперь срабатывает так же,
#   как {SPN}; раньше команда молча игнорировалась.
# - Проверка "сервисных" модификаторов вынесена в is_service_modifier().
# - eval переведён на белый список: функции/константы math плюс безопасные встроенные,
#   __builtins__ очищен. open(), __import__, os, sys, editor в выражениях недоступны.
# - Имена и атрибуты с '_' в начале (__class__, __globals__, __loader__) запрещены.
# - Модуль math доступен как math.xxx через обёртку без служебных атрибутов.
# 2026-11-21
# - Вместо "тихого отказа" теперь выводится причина: если строка похожа на команду
#   калькулятора, но разобрать её нельзя, в конец строки пишется сообщение
#   (неизвестный модификатор, модификатор без выражения, синтаксис с позицией и т.п.).
# - Разбор выделения и строки вынесен в analyze_input(); шаблоны SELECTION_RE/LINE_RE
#   собраны из одного описания модификатора.
# - Строки без '=' в конце и строки-разделители ('=====', '-----') по-прежнему молчат.
# - {h}/{b}/{a} применяются и к float без дробной части: 255.0 -> 0xff, 10/2 -> 5 (0x5, 0b101).
#   Дробные числа (3.7) и nan/inf печатаются как обычно — модификатор их не трогает.
# - Модификаторы можно комбинировать: {P40}{h}255 =, {P20}{.2}10/7 =.
#   Разбор переведён со строки на список блоков; несовместимые ({h}{b}, {P10}{P20})
#   и лишние служебные команды ({S3}{h}) теперь дают понятную ошибку.
# - Ошибки при вычислении выделенного фрагмента больше не портят текст: добавлен
#   ключ конфига ERROR_DISPLAY = auto | dialog | inline | console.
#   auto: выделение -> диалог (документ не меняется), строка-команда -> "# Error:".
#   {config} показывает текущий режим, {SN}/{SPN} его не теряют при сохранении.
# - Исправлено: причина ошибки выделения больше не перетирается разбором всей строки.
# 2026-11-22
# - {help}, {config} и {math...} больше не вставляют многострочный ответ в позицию '=':
#   ответ начинается с новой строки под строкой команды и не рвёт окружающий текст.
# - Добавлена команда {E}: {E} показывает режим ERROR_DISPLAY, {E auto|dialog|inline|console}
#   задаёт его и сохраняет в конфиг; править JSON вручную не обязательно.
# - {.N} и встроенный round() округляют по десятичному представлению (Decimal(repr(x))),
#   поэтому {.2}1.005 -> 1.01, а не 1.00 из-за двоичного хранения числа.
# - {.N} переключается на экспоненциальную форму для крайних значений: очень большие
#   (>= 1e15) и очень малые (< 0.5*10^-N) числа печатаются как 1.00e+300 и 1.00e-20,
#   вместо 300 цифр и 0.00.

from __future__ import division  
import re
import sys
import os
import ast
import json
import math
import decimal
from math import *

# ==============================================================================
# НАСТРОЙКА КАЛЬКУЛЯТОРА (Загрузка из внешнего JSON-файла конфигурации)
# ==============================================================================
# Точность по умолчанию для чисел с плавающей точкой (значащих цифр)
DEFAULT_FLOAT_PRECISION = 5  
# Позиция (колонка) 1-го символа результата (0 — стандартный отступ в 1 пробел)
DEFAULT_SPACING_COLUMN = 0          
# Как показывать ошибки:
#   auto    — выделение в тексте: диалог, строка-команда: "# Error:" в конец строки;
#   dialog  — всегда диалог (документ не меняется);
#   inline  — всегда "# Error:" в конец строки;
#   console  — всегда консоль PythonScript (console.writeError, красным).
ERROR_DISPLAY = 'auto'
ERROR_DISPLAY_MODES = ('auto', 'dialog', 'inline', 'console')

# Определяем путь к каталогу расположения текущего скрипта
try:
    script_dir = os.path.dirname(__file__)
except NameError:
    script_dir = ''

config_path = os.path.join(script_dir, 'npp_py_calculator.json') if script_dir else 'npp_py_calculator.json'

# Допустимые границы значений: защита от опечаток и «бомб» вроде {SP999999999}
CONFIG_PRECISION_MIN = 1
CONFIG_PRECISION_MAX = 17   # столько значащих цифр у double реально есть
CONFIG_SPACING_MIN = 0
CONFIG_SPACING_MAX = 1000
# Предупреждения о некорректном конфиге (показываются в {config})
CONFIG_WARNINGS = []
# Незнакомые ключи из файла: сохраняем, чтобы не стирать чужие настройки
CONFIG_EXTRA = {}
CONFIG_KNOWN_KEYS = ("DEFAULT_FLOAT_PRECISION", "DEFAULT_SPACING_COLUMN", "ERROR_DISPLAY")


def _as_int(value):
    """Целое из значения JSON или None. bool, дробные и мусор не принимаем."""
    if isinstance(value, bool):
        return None
    if isinstance(value, float) and value != int(value):
        return None
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return None


def _read_int_option(config_data, key, min_value, max_value, default):
    """Читает целое из конфига; при ошибке оставляет default и копит предупреждение."""
    if key not in config_data:
        return default
    value = _as_int(config_data[key])
    if value is None or value < min_value or value > max_value:
        CONFIG_WARNINGS.append(
            "{0}: ожидается целое {1}..{2}, в файле {3!r}; оставлено {4}".format(
                key, min_value, max_value, config_data[key], default))
        return default
    return value


def _replace_file(src, dst):
    """Заменяет dst файлом src. os.replace есть в Python 3.3+; в Python 2 — remove + rename."""
    if hasattr(os, 'replace'):
        os.replace(src, dst)
    else:
        if os.path.exists(dst):
            os.remove(dst)
        os.rename(src, dst)


def save_current_config():
    """Пишет конфиг атомарно (temp-файл + замена).

    Возвращает None при успехе или текст ошибки. Вызывающий код не должен
    сообщать «сохранено», если запись не удалась.
    """
    tmp_path = config_path + '.tmp'
    config_data = dict(CONFIG_EXTRA)
    config_data.update({
        "DEFAULT_FLOAT_PRECISION": DEFAULT_FLOAT_PRECISION,
        "DEFAULT_SPACING_COLUMN": DEFAULT_SPACING_COLUMN,
        "ERROR_DISPLAY": ERROR_DISPLAY
    })
    try:
        with open(tmp_path, 'w') as f:
            json.dump(config_data, f, indent=4)
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass
        _replace_file(tmp_path, config_path)
        # Конфиг записан в нормализованном виде — старые предупреждения больше не актуальны
        del CONFIG_WARNINGS[:]
        return None
    except Exception as e:
        # Не оставляем мусорный .tmp рядом с конфигом
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        return str(e)

# Загружаем настройки или создаем файл с дефолтными значениями при первом запуске
if os.path.exists(config_path):
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        if isinstance(config_data, dict):
            DEFAULT_FLOAT_PRECISION = _read_int_option(
                config_data, "DEFAULT_FLOAT_PRECISION",
                CONFIG_PRECISION_MIN, CONFIG_PRECISION_MAX, DEFAULT_FLOAT_PRECISION)
            DEFAULT_SPACING_COLUMN = _read_int_option(
                config_data, "DEFAULT_SPACING_COLUMN",
                CONFIG_SPACING_MIN, CONFIG_SPACING_MAX, DEFAULT_SPACING_COLUMN)
            if "ERROR_DISPLAY" in config_data:
                # Приводим к unicode безопасно: в Python 2 str() может упасть на кириллице
                raw_mode = config_data["ERROR_DISPLAY"]
                try:
                    raw_mode = u"%s" % (raw_mode,)
                except Exception:
                    raw_mode = u""
                raw_mode = raw_mode.strip().lower()
                if raw_mode in ERROR_DISPLAY_MODES:
                    ERROR_DISPLAY = raw_mode
                else:
                    CONFIG_WARNINGS.append(
                        "ERROR_DISPLAY: ожидается {0}, в файле {1!r}; оставлено '{2}'".format(
                            "/".join(ERROR_DISPLAY_MODES), config_data["ERROR_DISPLAY"], ERROR_DISPLAY))
            for key in config_data:
                if key not in CONFIG_KNOWN_KEYS:
                    CONFIG_EXTRA[key] = config_data[key]
        else:
            CONFIG_WARNINGS.append(
                "файл конфигурации должен содержать объект {{...}}; используются значения по умолчанию")
    except Exception as e:
        CONFIG_WARNINGS.append(
            "не удалось прочитать файл конфигурации ({0}); используются значения по умолчанию".format(e))
else:
    save_current_config()
# ==============================================================================

# Проверка версии интерпретатора (Python 2 / Python 3)
IS_PY3 = sys.version_info[0] >= 3

# Встроенные функции, доступные внутри вычисляемого выражения.
# Список явный: в eval больше не попадают open, __import__, os, sys, editor и т.п.
SAFE_CALC_BUILTINS = {
    'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool, 'chr': chr,
    'complex': complex, 'dict': dict, 'dir': dir, 'divmod': divmod,
    'enumerate': enumerate, 'filter': filter, 'float': float, 'format': format,
    'frozenset': frozenset, 'hex': hex, 'int': int, 'isinstance': isinstance,
    'len': len, 'list': list, 'map': map, 'max': max, 'min': min, 'oct': oct,
    'ord': ord, 'pow': pow, 'range': range, 'repr': repr, 'set': set,
    'sorted': sorted, 'str': str, 'sum': sum, 'tuple': tuple, 'type': type,
    'zip': zip,
}
if not IS_PY3:
    # В Python 2 это не ключевые слова, поэтому их нужно положить в пространство имён
    SAFE_CALC_BUILTINS.update({
        'long': long, 'xrange': xrange, 'unicode': unicode,
        'True': True, 'False': False, 'None': None,
    })


class _MathNamespace(object):
    """Обёртка над math: видны только публичные имена (без __loader__, __spec__ и т.п.)."""

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError("math.{0} недоступно".format(name))
        return getattr(math, name)

    def __dir__(self):
        return [name for name in dir(math) if not name.startswith('_')]


MATH_NAMESPACE = _MathNamespace()


def build_calc_globals(round_func):
    """Пространство имён для eval: функции/константы math + безопасные встроенные.

    __builtins__ очищен, поэтому open(), __import__, os, sys, editor недоступны.
    """
    calc_globals = {
        '__builtins__': {},
        'math': MATH_NAMESPACE,
        'round': round_func,
    }
    calc_globals.update(SAFE_CALC_BUILTINS)
    for name in dir(math):
        if not name.startswith('_'):
            calc_globals[name] = getattr(math, name)
    return calc_globals


def is_safe_expression(expr):
    """Запрещаем имена и атрибуты с '_' в начале (__class__, __globals__, __loader__...).

    Это не герметичная песочница, но обрубает типовые обходы через dunder-атрибуты.
    """
    try:
        tree = ast.parse(expr, mode='eval')
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id.startswith('_'):
            return False
        if isinstance(node, ast.Attribute) and node.attr.startswith('_'):
            return False
    return True


def is_service_modifier(mod):
    """Модификаторы, которые выполняются сами по себе, без выражения перед '='.

    Единая точка правды: используется и при разборе выделения, и при разборе строки,
    чтобы список команд не мог разъехаться между двумя ветками.
    """
    if not mod:
        return False
    first = mod.strip().split()[0]
    return (first in ('help', 'config', 'math')
            or mod.startswith('E')
            or re.match(r'^(?:SP\d+|S\d+)$', mod) is not None)

# Единые шаблоны разбора: ноль или несколько блоков {...} подряд, затем выражение до '='
_MODIFIER_BODY = (r"help|math(?:[ \t]+\w+)?|config|E(?:[ \t]*[A-Za-z]+)?|"
                  r"SP\d+|P\d+|S\d+|\.\d+|[hba]")
_MODIFIER_RUN_PATTERN = r"(?P<mods>(?:\{(?:" + _MODIFIER_BODY + r")\}[ \t]*)*)"
_MODIFIER_ITEM_RE = re.compile(r"\{(" + _MODIFIER_BODY + r")\}")
SELECTION_RE = re.compile(r"^\s*" + _MODIFIER_RUN_PATTERN + r"\s*(?P<expr>.*)=\s*$")
LINE_RE = re.compile(r"^\s*" + _MODIFIER_RUN_PATTERN + r"\s*(?P<expr>.*)=(?P<rest>.*)$")

# Локальные модификаторы, которые можно комбинировать между собой.
# Служебные (help/config/math/SP/S) сюда не входят: они выполняются только одиночными.
_MODIFIER_GROUP_NAMES = {
    'position': 'позиция',
    'precision': 'точность',
    'int_format': 'формат целых',
}


def modifier_group(mod):
    """Группа локального модификатора или None для служебной команды."""
    if mod.startswith('P') and mod[1:].isdigit():
        return 'position'
    if mod.startswith('.') and mod[1:].isdigit():
        return 'precision'
    if mod in ('h', 'b', 'a'):
        return 'int_format'
    return None


def validate_modifier_list(modifiers):
    """Проверяет сочетание модификаторов.

    Возвращает текст проблемы или None. Разрешено комбинировать локальные
    {PN}, {.N} и один из {h}/{b}/{a} в любом порядке. Служебные команды
    ({help}, {config}, {math}, {SN}, {SPN}) — только одиночные.
    """
    commands = [mod for mod in modifiers if modifier_group(mod) is None]
    if commands and len(modifiers) > 1:
        return "команда {{{0}}} не сочетается с другими модификаторами".format(commands[0])

    seen = {}
    for mod in modifiers:
        group = modifier_group(mod)
        if group is None:
            continue
        prev = seen.get(group)
        if prev is not None:
            if prev == mod:
                return "модификатор {{{0}}} указан дважды".format(mod)
            return ("модификаторы {{{0}}} и {{{1}}} несовместимы ({2}); оставьте один"
                    .format(prev, mod, _MODIFIER_GROUP_NAMES[group]))
        seen[group] = mod
    return None


def to_unicode(text):
    """Приводит текст к unicode: в Python 2 messageBox/console ждут unicode."""
    if IS_PY3:
        return text
    if isinstance(text, unicode):
        return text
    return text.decode('utf-8', 'replace')


def _messagebox_flags():
    """Флаги MB_OK | MB_ICONERROR. MESSAGEBOXFLAGS есть не во всех сборках — есть запасной путь."""
    try:
        return MESSAGEBOXFLAGS.OK | MESSAGEBOXFLAGS.ICONERROR
    except NameError:
        pass
    try:
        from Npp import MESSAGEBOXFLAGS as flags
        return flags.OK | flags.ICONERROR
    except Exception:
        return 0x00000010  # MB_ICONERROR при кнопке OK по умолчанию


def error_context(expression, modifier_list):
    """Текст «что именно считали»: модификаторы + выражение."""
    text = "".join("{{{0}}}".format(mod) for mod in (modifier_list or []))
    if expression:
        text = (text + " " + expression).strip()
    return text


def show_error_dialog(message, context=""):
    """Модальное окно с причиной ошибки. Документ при этом не меняется."""
    try:
        if context:
            text = u"Не удалось вычислить: {0}\n\n{1}".format(
                to_unicode(context), to_unicode(message))
        else:
            text = to_unicode(message)
        notepad.messageBox(text, u"Калькулятор Notepad++", _messagebox_flags())
        return True
    except Exception:
        return False


def write_error_console(message, context=""):
    """Пишет ошибку в консоль PythonScript красным и показывает консоль."""
    try:
        if context:
            line = u"Калькулятор: {0} — {1}\n".format(
                to_unicode(context), to_unicode(message))
        else:
            line = u"Калькулятор: {0}\n".format(to_unicode(message))
        console.writeError(line)
        console.show()
        return True
    except Exception:
        return False


def resolve_error_mode(from_selection):
    """auto: выделение в тексте -> диалог, строка-команда -> комментарий в конец строки."""
    if ERROR_DISPLAY == 'auto':
        return 'dialog' if from_selection else 'inline'
    return ERROR_DISPLAY


def report_error(message, from_selection=False, context=""):
    """Показывает причину ошибки, не вставляя текст в документ без необходимости.

    dialog — документ не трогаем; inline — "# Error:" в конец строки;
    console — красная строка в консоли PythonScript. Если выбранный способ
    недоступен (нет notepad/console), откатываемся на inline.
    """
    mode = resolve_error_mode(from_selection)
    if mode == 'dialog' and show_error_dialog(message, context):
        return
    if mode == 'console' and write_error_console(message, context):
        return
    editor.lineEnd()
    editor.addText("\n# Error: {0}".format(message))


def is_meaningful_expression(expr):
    """Есть ли в тексте хоть одна буква/цифра (иначе это строка-разделитель)."""
    return bool(re.search(r'\w', expr))


def looks_like_unknown_modifier(content):
    """Похоже ли содержимое {...} на неизвестный модификатор, а не на множество."""
    content = content.strip()
    if not content or not content[0].isalpha():
        return False
    if re.match(r"^[A-Za-z][A-Za-z0-9_ \t]*$", content):
        return True
    first = content.split()[0]
    return (first in ('math', 'help', 'config')
            or re.match(r"^(?:SP|P|S|B)\d", content) is not None)


def analyze_input(text, anchored):
    """Разбирает текст как команду калькулятора.

    Возвращает (match, modifiers, expression, problem):
      match=None      — текст не похож на команду калькулятора, молчим;
      modifiers       — список модификаторов в порядке записи (может быть пустым);
      problem=None    — можно вычислять;
      problem=<текст> — команда распознана, но вычислить нельзя, вот причина.
    """
    match = (SELECTION_RE if anchored else LINE_RE).search(text)
    if match is None:
        return None, None, None, None

    modifiers = [m.strip() for m in _MODIFIER_ITEM_RE.findall(match.group('mods') or '')]
    candidate_expr = (match.group('expr') or '').strip()
    problem = None

    if not modifiers:
        block = re.match(r'^\s*\{([^}]*)\}', text)
        if block and looks_like_unknown_modifier(block.group(1)):
            problem = "неизвестный модификатор {{{0}}} (см. {{help}})".format(block.group(1).strip())
        elif not is_meaningful_expression(candidate_expr):
            return None, None, None, None
    else:
        extra = re.match(r'^\s*\{([^}]*)\}', candidate_expr)
        if extra and looks_like_unknown_modifier(extra.group(1)):
            problem = "неизвестный модификатор {{{0}}} (см. {{help}})".format(extra.group(1).strip())
        else:
            problem = validate_modifier_list(modifiers)
        is_command = any(is_service_modifier(mod) for mod in modifiers)
        if problem is None and not is_command and not candidate_expr:
            problem = "модификатор {{{0}}} требует выражения".format(modifiers[0])

    if problem is None and not any(is_service_modifier(mod) for mod in modifiers):
        try:
            compile(candidate_expr, '<string>', 'eval')
        except SyntaxError as e:
            msg = e.msg or str(e)
            if getattr(e, 'offset', None):
                problem = "синтаксис: {0} (позиция {1})".format(msg, e.offset)
            else:
                problem = "синтаксис: {0}".format(msg)
        except Exception as e:
            problem = "синтаксис: {0}".format(e)

    return match, modifiers, candidate_expr, problem


line_index = editor.lineFromPosition(editor.getCurrentPos())
line_content = editor.getLine(line_index)
sel_text = editor.getSelText()

is_valid_input = False
parse_error = None
from_selection = False
modifier_list = None
expression = None
insert_position = None
insert_offset_in_line = 0

# Шаг 1: НАИВЫСШИЙ ПРИОРИТЕТ - Проверяем выделенный текст (обязательно должен заканчиваться на '=')
if sel_text and '\n' not in sel_text and '\r' not in sel_text:
    match_sel, cand_mods, candidate_expr, problem = analyze_input(sel_text, anchored=True)
    if match_sel is not None:
        # Выделение — это осознанный выбор пользователя, ошибку строки оно не перекрывает
        from_selection = True
        modifier_list = cand_mods
        expression = candidate_expr
        if problem is None:
            is_valid_input = True
            insert_position = editor.getSelectionEnd()
            insert_offset_in_line = insert_position - editor.positionFromLine(line_index)
        else:
            parse_error = problem

# Шаг 2: РЕЗЕРВНЫЙ ВАРИАНТ - Если выделение не распознано как команда, проверяем строку
if not is_valid_input and not from_selection:
    match_line, cand_mods, candidate_expr, problem = analyze_input(line_content, anchored=False)
    if match_line is not None:
        modifier_list = cand_mods
        expression = candidate_expr
        if problem is None:
            is_valid_input = True
            line_start_pos = editor.positionFromLine(line_index)
            insert_position = line_start_pos + match_line.start('rest')
            insert_offset_in_line = match_line.start('rest')
        else:
            parse_error = problem


# Шаг 3: Вычисление и вывод результатов
if is_valid_input:
    
    current_precision = DEFAULT_FLOAT_PRECISION
    current_spacing_col = DEFAULT_SPACING_COLUMN
    is_explicit_decimal = False
    int_format_mode = 'default'
    is_math_help = False
    is_calc_help = False
    is_config_cmd = False
    is_error_cmd = False
    is_sp_cmd = False
    new_sp_val = None
    new_precision_val = None
    new_error_mode = None
    temp_spacing_col = None
    math_target_func = None
    
    # Применяем модификаторы по очереди. Порядок записи не важен: каждый
    # настраивает свой параметр, конфликты уже отсеяны validate_modifier_list().
    for mod in (modifier_list or []):
        if mod == 'help':
            is_calc_help = True
        elif mod == 'config':
            is_config_cmd = True
        elif mod.startswith('E'):
            is_error_cmd = True
            new_error_mode = mod[1:].strip().lower()
        elif mod.startswith('SP') and mod[2:].isdigit():
            is_sp_cmd = True
            new_sp_val = int(mod[2:])
        elif mod.startswith('P') and mod[1:].isdigit():
            temp_spacing_col = int(mod[1:])
        elif mod.startswith('S') and mod[1:].isdigit():
            new_precision_val = int(mod[1:])
        elif mod == 'math' or mod.startswith('math ') or mod.startswith('math\t'):
            is_math_help = True
            mod_parts = mod.split(None, 1)
            if len(mod_parts) > 1:
                math_target_func = mod_parts[1].strip()
            elif expression:
                math_target_func = expression.strip()
        elif mod in ('h', 'b', 'a'):
            int_format_mode = mod
        else:
            m_arith = re.match(r'^\.(\d+)$', mod)
            if m_arith:
                current_precision = int(m_arith.group(1))
                is_explicit_decimal = True

    # Применяем временную или постоянную позицию колонки, если задана в модификаторе
    if temp_spacing_col is not None:
        current_spacing_col = temp_spacing_col

    # Расчет отступа (padding) для выравнивания по заданной колонке
    if current_spacing_col > 0:
        target_index = current_spacing_col - 1  # 1-based позиция переводится в 0-based индекс
        spaces_needed = target_index - insert_offset_in_line
        # Если выражение слишком длинное и заходит за целевую колонку — fallback на 1 пробел
        padding = " " * spaces_needed if spaces_needed >= 1 else " "
    else:
        padding = " "

    def custom_round(x, ndigits=0):
        """Арифметическое округление: половина уходит от нуля (2.5 -> 3, -2.5 -> -3).

        Считаем по десятичному представлению (Decimal(repr(x))): иначе 1.005
        из-за двоичного хранения выглядит как 1.0049999... и округляется вниз.
        """
        # NaN и бесконечности не округляются (как и во встроенном round())
        if isnan(x) or isinf(x):
            return x
        ndigits = int(ndigits)
        try:
            with decimal.localcontext() as ctx:
                ctx.prec = max(28, ndigits + 5)
                quantum = decimal.Decimal(1).scaleb(-ndigits)
                rounded = decimal.Decimal(repr(x)).quantize(
                    quantum, rounding=decimal.ROUND_HALF_UP)
            final_result = float(rounded)
            return int(final_result) if ndigits == 0 else final_result
        except (decimal.InvalidOperation, ValueError, OverflowError):
            # Запасной путь для чисел, где quantize не справляется (например, 1e300)
            pass
        try:
            factor = 10 ** ndigits
            val = x * factor
        except (OverflowError, ValueError):
            # слишком большая/маленькая степень десятки — оставляем число как есть
            return x
        res = floor(val + 0.5) if val >= 0 else ceil(val - 0.5)
        final_result = res / factor
        return int(final_result) if ndigits == 0 else final_result

    def round_significant(x, sig):
        """Арифметическое округление до sig значащих цифр (режим DEFAULT_FLOAT_PRECISION)."""
        if x == 0 or isnan(x) or isinf(x):
            return x
        sig = max(1, int(sig))  # точность 0 значащих цифр смысла не имеет
        try:
            ndigits = sig - 1 - int(floor(log10(abs(x))))
            return custom_round(x, ndigits)
        except (OverflowError, ValueError):
            return x

    def use_scientific(x, ndigits):
        """{.N}: включать экспоненциальную форму там, где f врёт или раздувается.

        * очень большие числа (>= 1e15): у double кончаются точные цифры, f печатает мусор;
        * очень малые (0.5 * 10^-N и меньше): f дал бы 0.00 для ненулевого числа.
        Для N = 0 правило «малых» не применяется: там округление до целого и так даёт 0.
        """
        if x == 0 or isnan(x) or isinf(x):
            return False
        ax = abs(x)
        if ax >= 1e15:
            return True
        return ndigits > 0 and ax < 0.5 * (10.0 ** -ndigits)

    try:
        if is_calc_help:
            formatted_result = (
                "Справка по калькулятору Notepad++:\n"
                "  Формат: <выражение> =\n"
                "  Модификаторы перед выражением в фигурным скобках {}:\n"
                "    {help} - вызов справки по калькулятору\n"
                "    {math} - список всех функций и констант модуля math\n"
                "    {math <функция>} - справка по конкретной функции (напр. {math cos})\n"
                "    {config} - вывод текущих активных параметров конфигурации\n"
                "    {SN} - установить DEFAULT_FLOAT_PRECISION = N (число значащих цифр) и сохранить в конфиг (напр. {S3})\n"
                "    {SPN} - установить DEFAULT_SPACING_COLUMN = N и сохранить в конфиг (напр. {SP40})\n"
                "    {E} - показать ERROR_DISPLAY; {E auto|dialog|inline|console} - задать и сохранить\n"
                "    {PN} - установить позицию 1-го символа результата для текущего выражения (напр. {P40})\n"
                "    {.N} - арифметическое округление до N знаков после запятой для текущего выражения (напр. {.3})\n"
                "    {h} - вывод целых чисел в шестнадцатеричном формате (0x...)\n"
                "    {b} - вывод целых чисел в двоичном формате (0b...)\n"
                "    {a} - вывод целых чисел во всех форматах: дес (0xHex, 0bBin)\n"
                "  Локальные модификаторы можно комбинировать в любом порядке:\n"
                "  {P40}{h}255 =, {P20}{.2}10/7 =. {SN}, {SPN}, {E}, {help}, {config}, {math}\n"
                "  выполняются только одиночными (меняют конфиг или печатают справку).\n"
                "  {h}/{b}/{a} применяются к целым; float без дробной части тоже считается\n"
                "  целым (10/2 = 5.0 -> 0x5), дробное число печатается как обычно.\n"
                "  {.N} для очень больших (>= 1e15) и очень малых (< 0.5*10^-N) чисел\n"
                "  печатает экспоненциальную форму: 1.00e+300, 1.00e-20.\n"
                "  Доступны все функции модуля math (sin, cos, sqrt, log, pi, e и др.),\n"
                "  базовые встроенные функции (abs, round, len, sum, min, max, zip, range...)\n"
                "  и контейнеры. Доступа к файлам и системе нет (open/os/sys недоступны), например:\n"
                "  [x**2 + y for x, y in zip([2,3,5], [4,3,2])] = [8, 12, 27]\n"  
                "  [x*y for x, y in zip([1,2,3], [5,6,7][1:] + [5,6,7][:1])]= [6, 14, 15]\n" 
                "  Ошибки: режим ERROR_DISPLAY (см. {E}) — auto (выделение: окно,\n"
                "  строка: комментарий в конец), dialog (всегда окно), inline\n"
                "  (всегда комментарий), console (консоль PythonScript). Режим виден в {config}.\n"
            )
        elif is_config_cmd:
            config_text = (
                "\nТекущие параметры калькулятора:\n"
                "  DEFAULT_FLOAT_PRECISION = {0}\n"
                "  DEFAULT_SPACING_COLUMN = {1}\n"
                "  ERROR_DISPLAY = {2}\n"
                "  Файл конфигурации: {3}"
            ).format(DEFAULT_FLOAT_PRECISION, DEFAULT_SPACING_COLUMN,
                     ERROR_DISPLAY, config_path)
            if CONFIG_WARNINGS:
                config_text += "\n  Предупреждения:"
                for warning in CONFIG_WARNINGS:
                    config_text += "\n    - {0}".format(warning)
            formatted_result = config_text
        elif is_error_cmd:
            if not new_error_mode:
                formatted_result = "ERROR_DISPLAY = {0} (допустимо: {1})".format(
                    ERROR_DISPLAY, "/".join(ERROR_DISPLAY_MODES))
            elif new_error_mode not in ERROR_DISPLAY_MODES:
                formatted_result = "Ошибка: ERROR_DISPLAY: ожидается {0} (получено '{1}')".format(
                    "/".join(ERROR_DISPLAY_MODES), new_error_mode)
            else:
                ERROR_DISPLAY = new_error_mode
                error = save_current_config()
                if error is None:
                    formatted_result = "ERROR_DISPLAY установлен в {0} и сохранен в файл: {1}".format(
                        new_error_mode, config_path)
                else:
                    formatted_result = ("ERROR_DISPLAY установлен в {0}, но сохранить не удалось: {1}"
                                        "\n  значение действует до перезапуска").format(new_error_mode, error)
        elif is_sp_cmd:
            if new_sp_val < CONFIG_SPACING_MIN or new_sp_val > CONFIG_SPACING_MAX:
                formatted_result = "Ошибка: позиция должна быть {0}..{1} (получено {2})".format(
                    CONFIG_SPACING_MIN, CONFIG_SPACING_MAX, new_sp_val)
            else:
                DEFAULT_SPACING_COLUMN = new_sp_val
                error = save_current_config()
                if error is None:
                    formatted_result = "DEFAULT_SPACING_COLUMN установлен в {0} и сохранен в файл: {1}".format(new_sp_val, config_path)
                else:
                    formatted_result = ("DEFAULT_SPACING_COLUMN установлен в {0}, но сохранить не удалось: {1}"
                                        "\n  значение действует до перезапуска").format(new_sp_val, error)
        elif new_precision_val is not None:
            if new_precision_val < CONFIG_PRECISION_MIN or new_precision_val > CONFIG_PRECISION_MAX:
                formatted_result = "Ошибка: точность должна быть {0}..{1} (получено {2})".format(
                    CONFIG_PRECISION_MIN, CONFIG_PRECISION_MAX, new_precision_val)
            else:
                DEFAULT_FLOAT_PRECISION = new_precision_val
                error = save_current_config()
                if error is None:
                    formatted_result = "DEFAULT_FLOAT_PRECISION установлен в {0} и сохранен в файл: {1}".format(new_precision_val, config_path)
                else:
                    formatted_result = ("DEFAULT_FLOAT_PRECISION установлен в {0}, но сохранить не удалось: {1}"
                                        "\n  значение действует до перезапуска").format(new_precision_val, error)
        elif is_math_help:
            target = math_target_func.rstrip('()') if math_target_func else ""
            if target:
                if hasattr(math, target):
                    obj = getattr(math, target)
                    doc = getattr(obj, '__doc__', None)
                    if doc:
                        formatted_result = "{0}: {1}".format(target, doc.strip())
                    else:
                        formatted_result = "{0}: Справка отсутствует.".format(target)
                else:
                    formatted_result = "Ошибка: Функция '{0}' не найдена в библиотеке math".format(target)
            else:
                doc = math.__doc__.strip() if math.__doc__ else "Модуль math"
                funcs = [name for name in dir(math) if not name.startswith("__")]
                formatted_result = "{0}\nДоступные функции и константы: {1}".format(doc, ", ".join(sorted(funcs)))
        else:
            if not is_safe_expression(expression):
                raise ValueError("имена и атрибуты, начинающиеся с '_', запрещены")
            calc_globals = build_calc_globals(custom_round)

            result = eval(expression, calc_globals)
            
            def as_whole_int(val):
                """float без дробной части -> int; иначе None (для {h}/{b}/{a})."""
                if not isinstance(val, float) or isnan(val) or isinf(val):
                    return None
                try:
                    whole = int(val)
                except (OverflowError, ValueError):
                    return None
                return whole if val == whole else None

            def format_int(val):
                if int_format_mode == 'h':
                    return "{0:#x}".format(val)
                elif int_format_mode == 'b':
                    return "{0:#b}".format(val)
                elif int_format_mode == 'a':
                    return "{0} ({0:#x}, {0:#b})".format(val)
                else:
                    return str(val)

            def format_value(val, top_level=False):
                if IS_PY3:
                    is_int = isinstance(val, int) and not isinstance(val, bool)
                else:
                    is_int = isinstance(val, (int, long)) and not isinstance(val, bool)
                    
                is_float = isinstance(val, float)
                
                if is_int:
                    return format_int(val)
                elif is_float:
                    # Целозначный float считаем целым: 10/2 = 5.0 при {h} даёт 0x5.
                    whole = as_whole_int(val)
                    if whole is not None and int_format_mode != 'default':
                        return format_int(whole)
                    if is_explicit_decimal:
                        if use_scientific(val, current_precision):
                            # В экспоненциальной форме N знаков после запятой = N+1 значащих цифр
                            sci = round_significant(val, current_precision + 1)
                            return "{0:.{1}e}".format(sci, current_precision)
                        return "{0:.{1}f}".format(custom_round(val, current_precision), current_precision)
                    else:
                        return "{0:.{1}g}".format(round_significant(val, current_precision), current_precision)
                elif isinstance(val, list):
                    return "[" + ", ".join(format_value(x, top_level=False) for x in val) + "]"
                elif isinstance(val, tuple):
                    if len(val) == 1:
                        return "(" + format_value(val[0], top_level=False) + ",)"
                    return "(" + ", ".join(format_value(x, top_level=False) for x in val) + ")"
                elif isinstance(val, set):
                    if not val:
                        return "set()"
                    return "{" + ", ".join(format_value(x, top_level=False) for x in val) + "}"
                elif isinstance(val, dict):
                    return "{" + ", ".join(format_value(k, top_level=False) + ": " + format_value(v, top_level=False) for k, v in val.items()) + "}"
                else:
                    if top_level:
                        return str(val)
                    else:
                        return repr(val)

            formatted_result = format_value(result, top_level=True)

        if is_calc_help or is_config_cmd or is_math_help:
            # Справка/конфиг — многострочный блок. Вставляем только с новой строки,
            # чтобы не рвать строку с командой: сама команда остаётся как есть,
            # ответ начинается со следующей строки.
            block_text = formatted_result.strip('\n')
            line_start_pos = editor.positionFromLine(line_index)
            line_end_pos = line_start_pos + len(line_content)
            editor.insertText(line_end_pos, "\n" + block_text)
        else:
            text_to_insert = "{0}{1} ".format(padding, formatted_result)
            editor.insertText(insert_position, text_to_insert)
        
    except Exception as e:
        report_error(str(e), from_selection, error_context(expression, modifier_list))
else:
    if parse_error:
        report_error(parse_error, from_selection, error_context(expression, modifier_list))