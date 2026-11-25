## Calculator right inside Notepad++
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Русская версия](README_ru.md)

**npp_py_calculator** is a handy calculator built into the **Notepad++** text editor as a script running under the **PythonScript** plugin. Besides ordinary arithmetic, it evaluates one-line Python expressions: lists of numbers, sums, percentages, and text processing.

---

## 🚀 Key features

* **Write a mathematical expression right in the document**, put an `=`, run the script, and the result appears immediately after the equal sign.
* **Calculations inside text are allowed**. To do this, select the expression.
* **About 60 functions and constants** from the standard Python library are supported (`sin`, `cos`, `sqrt`, `pi`, `e`, `log`, etc.).
* **One-line Python commands** — you can sum a list, filter values, convert units, and process text. Ready-made examples are in the section “More than a calculator: one-line Python commands”.  
* **When the source expression is changed and the script is run again**, previous results are automatically shifted to the right, keeping a history of calculations.
* **Cross-version support (Python 2 and Python 3)** guarantees the same behavior for division (`/` — true division, `//` — integer division) and rounding, regardless of the PythonScript version used in Notepad++.
* **Settings can be saved** to a configuration file.
- **Modifiers** for getting help information
  - ***{help}*** — show help on using the calculator
  - ***{math}*** — show help for the `math` library
  - ***{math function_name}*** — show help for a specific `math` function
  - ***{config}*** — show the currently active configuration parameters

- **Modifiers** for changing default parameters and saving them to the configuration file
  - ***{SN}*** — set the default precision: the number of significant digits for floating-point numbers, e.g. {S3}
  - ***{SPN}*** — set the position of the first character of the result, e.g. {SP40}
  - ***{E}*** — show the error display mode (`ERROR_DISPLAY`)
  - ***{E auto}***, ***{E dialog}***, ***{E inline}***, ***{E console}*** — set the mode and save it to the config

- **Modifiers** for changing default parameters only for the current expression
  - ***{.N}*** — ordinary (arithmetic) rounding to N decimal places, e.g. {.1}
  - ***{h}*** — print integers in HEX format
  - ***{b}*** — print integers in binary format
  - ***{a}*** — print integers in all three formats at once, e.g. 65 (0x41, 0b1000001)
  - ***{PN}*** — set the position of the first character of the result for the current expression, e.g. {P40}

  `{h}`, `{b}`, `{a}` apply to integers. A floating-point number without a fractional
  part is also treated as an integer (`10/2 = 5.0` with `{h}` gives `0x5`), while a
  fractional number is printed as usual (`{a}3.7` → `3.7`).

  `{.N}` and the built-in `round()` round according to the decimal representation of
  the number, so `{.2}1.005` → `1.01`, not `1.00`, due to the specifics of binary storage.

  For extreme values `{.N}` switches to exponential notation: very large
  (`|x| >= 1e15`) and very small (less than half of the last digit) numbers are printed
  as `1.00e+300` and `1.00e-20` instead of 300 digits and `0.00`.

  The commands `{help}`, `{config}`, and `{math…}` are multiline: they are executed on
  a separate line, and the response starts on the next line without breaking the
  surrounding text.
## 💡 Usage and examples

### Simple calculations
Write an expression, put an `=` and run the script:

***2+2 =***  
Result:  
***2+2 = 4***

### Using `math` functions

```text
sin(pi*0.5) = 1
sqrt(144) + log10(100) = 14
```

### Recalculation and history shift
If you change an argument in the expression and run the script again, the current result shifts to the right and the new one is inserted after `=`:

1. First calculation:
   ```text
   sin(pi*1.23) = -0.661312
   ```
2. Change `1.23` to `2.23` and run the script again:
   ```text
   sin(pi*2.23) = 0.661312 -0.661312
   ```

---

## 🧠 More than a calculator: one-line Python commands

A regular calculator can only do arithmetic. This one accepts **any one-line Python expression** after the `=` sign, so it handles lists of numbers, strings, percentages, and tables. Python is already included with the PythonScript plugin — no separate installation is needed, and you don't have to know the language: ready-made templates are given below, just substitute your own values.

The main restriction: **the whole expression must be written on one line**. You cannot use `import`, `open`, indented `if`/`for` blocks, or several commands separated by `;`. However, a loop, a filter, and processing of an entire list can all be written in a single line in Python.

### Mini-dictionary of notation

| Expression | Meaning |
|---|---|
| `[1, 2, 3]` | a list of values |
| `range(5)` | the numbers 0, 1, 2, 3, 4 |
| `range(1, 6)` | the numbers 1, 2, 3, 4, 5 (the right bound is exclusive) |
| `x**2` | x squared |
| `x % 2` | the remainder of x divided by 2 |
| `x > 100` | the condition “x is greater than 100” |
| `[x for x in ...]` | “take each x from …” |
| `[... if condition]` | keep only the matching elements |
| `'text'[5:]` | part of the string from the 6th character to the end |
| `'text'[::-1]` | the string in reverse order |

### Lists: many numbers at once

A list is written in square brackets, and the result is also printed as a list. This lets you calculate a whole table of values at once:

```text
[x**2 for x in range(1, 6)] = [1, 4, 9, 16, 25]
```

Read as: “for each `x` from 1 to 5, take `x` squared”. A condition after `if` keeps only the needed elements:

```text
[x for x in range(20) if x % 2 == 0] = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
[n for n in range(1, 31) if n % 3 == 0] = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
[x for x in [120, 45, 300, 80] if x > 100] = [120, 300]
```

The first two lines give even numbers and multiples of 3. The third filters **its own** list: only values greater than 100 remain.

### Two lists at once (`zip`)

`zip` pairs up elements of two lists. This lets you compute something pairwise — for example, add a number to a bonus from the second list:

```text
[x**2 + y for x, y in zip([2,3,5], [4,3,2])] = [8, 12, 27]
```

In the next example the second list is shifted by one step: `[5,6,7][1:]` is `[6, 7]` and `[5,6,7][:1]` is `[5]`; together they give `[6, 7, 5]`.

```text
[x*y for x, y in zip([1,2,3], [5,6,7][1:] + [5,6,7][:1])] = [6, 14, 15]
```

`enumerate` adds the index (starting from zero) to each list element:

```text
[i*n for i, n in enumerate([10, 20, 30])] = [0, 20, 60]
```

### Totals and statistics

```text
sum([1250, 3400, 980]) = 5630
sum([1250, 3400, 980]) * 1.2 = 6756
sum(range(1, 101)) = 5050
sum(x*x for x in range(1, 11)) = 385
sum(1 for x in range(1, 101) if x % 3 == 0) = 33
max([1250, 3400, 980]) = 3400
min([1250, 3400, 980]) = 980
max([1250, 3400, 980]) - min([1250, 3400, 980]) = 2420
sorted([3, 1, 2], reverse=True) = [3, 2, 1]
```

`sum(1 for ... if ...)` is a convenient way to **count items**: here 33 numbers from 1 to 100 are divisible by 3. `sorted(..., reverse=True)` sorts in descending order.

### Money, percentages, and formatting

```text
[round(x*1.18, 2) for x in [123.45, 250, 500]] = [145.67, 295, 590]
[round(p*0.13, 2) for p in [1234.5, 2500.75]] = [160.49, 325.1]
'{:,}'.format(1234567) = 1,234,567
'{:,.2f}'.format(1234567.891) = 1,234,567.89
'{:.1%}'.format(0.1234) = 12.3%
'{:.2f}'.format(10/3) = 3.33
```

* `round(x, 2)` — round to 2 decimal places (arithmetic rounding in the calculator, half away from zero);
* `'{:,}'.format(x)` — insert thousands separators;
* `'{:,.2f}'.format(x)` — thousands separators and exactly 2 decimal places;
* `'{:.1%}'.format(x)` — show a fraction as a percentage;
* `'{:.2f}'.format(x)` — exactly 2 decimal places.

The same result can be achieved with the `{.N}` modifier — it also works with lists, see below.

### Text and strings

```text
len('calculator') = 10
'2026-11-22'[5:] = 11-22
'abcdef'[::-1] = fedcba
'2026-11-22'.split('-') = ['2026', '11', '22']
'-'.join(str(x) for x in range(1, 6)) = 1-2-3-4-5
'=' * 20 = ====================
'  text  '.strip() = text
'abc'.upper() = ABC
```

* `len(...)` — the length of a string;
* `[5:]` — take part of the string from the 6th character (zero-based numbering);
* `[::-1]` — reverse the string;
* `.split('-')` — split by a separator;
* `'-'.join(...)` — join a list into a string using a separator;
* `'=' * 20` — repeat a string 20 times (handy for a separator line);
* `.strip()` — remove whitespace at the edges, `.upper()` — uppercase.

### Unit conversion and value tables

```text
[round(c*9/5+32, 1) for c in [0, 20, 37]] = [32, 68, 98.6]
[round(kg*2.20462, 1) for kg in [1, 5, 10]] = [2.2, 11, 22]
[math.factorial(n) for n in range(1, 8)] = [1, 2, 6, 24, 120, 720, 5040]
[int(d) for d in str(12345)] = [1, 2, 3, 4, 5]
```

Tables are built the same way: Celsius → Fahrenheit, kilograms → pounds, factorials, digits of a number.

### Checks and logic

```text
'even' if 10 % 2 == 0 else 'odd' = even
divmod(17, 5) = (3, 2)
abs(-7) = 7
int('42') + 8 = 50
float('2.5') * 4 = 10
```

* `A if condition else B` — choose one of two values;
* `divmod(17, 5)` — quotient and remainder: 17 = 3·5 + 2;
* `int(...)` and `float(...)` — turn text into a number.

### Modifiers and lists

The modifiers `{.N}`, `{h}`, `{b}`, `{a}` are applied to each list element:

```text
{.2}[10/3, 20/3] = [3.33, 6.67]
{h}[255, 16] = [0xff, 0x10]
{a}65 = 65 (0x41, 0b1000001)
{P20}{.2}10/7 =    1.43
```

### What is not allowed

* one line — one expression: `;`, `import`, `open`, file and network access are forbidden;
* variables are not preserved between runs: each calculation starts from a clean slate;
* names and attributes starting with `_` are forbidden (protection against dangerous expressions);
* instead of indented `if`/`for` blocks, use the lists and generators from the examples above.

See the “Expression restrictions” section below for details on the available functions.

---

## ⚙️ Using modifiers

The purpose of the modifiers is clear from their names, except for the ***{PN}*** modifier. It is used to print results starting from a given column. Let's look at a concrete example:

```text
{P20}3*2=          6   
{P20}3.3*2.5=      8.25    
{P20}sin(1.23)=    0.9424888  
```

### Combining modifiers

Local modifiers can be written one after another in any order — each sets its own parameter:

```text
{P40}{h}255 =      →  0xff in column 40
{P40}{.2}10/7 =    →  1.43 in column 40
{P40}{.2}{a}65 =   →  65 (0x41, 0b1000001) in column 40
```

Combinable:

* position — `{PN}`;
* precision — `{.N}`;
* integer format — one of `{h}`, `{b}`, `{a}`.

The service commands `{help}`, `{config}`, `{math…}`, `{SN}`, `{SPN}` are executed only on their own: they print help or change the config, rather than formatting a result.

If you specify two modifiers from the same group (`{h}{b}`, `{P10}{P20}`, `{.2}{.3}`) or add something to a service command, the reason will be written at the end of the line.

---

## 🐍 Division specifics (Python 2 vs Python 3)

The calculator works the same way with PythonScript versions based on Python 2 and on Python 3:

* the `/` operator performs **true division** (`7 / 2 = 3.5`);
* the `//` operator performs **integer division** (`7 // 2 = 3`).

---

## ⚠️ Error handling

If the script determines that a line is meant for the calculator (it contains `=`) but cannot evaluate it, it reports the reason. **Where** it reports is configured with the `{E …}` command or the `ERROR_DISPLAY` key in the config:

| Value | Behavior |
|---|---|
| `auto` (default) | selection in the middle of text → dialog box (document unchanged); whole command line → `# Error:` appended to the line |
| `dialog` | always a dialog box, document unchanged |
| `inline` | always `# Error:` appended to the line |
| `console` | always a red line in the PythonScript console (the console is shown automatically) |

Why this way: when calculating in the middle of text, the result is part of the text but an error message is not. In this case `auto` shows a window so that `# Error:` is not inserted into a paragraph and the caret is not moved. For a standalone expression line, a comment is more convenient: it stays next to the expression.

Examples of messages (in `inline` mode, and in `dialog`/`console` modes with the same text):

```text
10 / 0 =
# Error: float division by zero

1;2 =
# Error: syntax: invalid syntax (position 2)

{x}2+2 =
# Error: unknown modifier {x} (see {help})

{P25} =
# Error: modifier {P25} requires an expression

{h}{b}255 =
# Error: modifiers {h} and {b} are incompatible (integer format); keep one

{S3}{h}1 =
# Error: command {S3} cannot be combined with other modifiers
```

In the dialog box the message looks like this:

```text
Could not evaluate: 10/0

division by zero
```

The current mode is shown by `{E}`, and changed by a command — without editing a file:

```text
{E} =          →  ERROR_DISPLAY = auto (allowed: auto/dialog/inline/console)
{E dialog} =   →  ERROR_DISPLAY set to dialog and saved to file: …
```

The compact form `{Einline}` (no space) also works. When the config is saved by the `{SN}`, `{SPN}`, and `{E …}` commands, the `ERROR_DISPLAY` key is not lost. Editing `npp_py_calculator.json` manually is still possible, but no longer required.

Typical causes:

| Message | What happened |
|---|---|
| `# Error: <exception text>` | the expression is valid, but an error occurred during evaluation (`10/0`, unknown name) |
| `# Error: syntax: … (position N)` | the expression has a syntax error; `N` is the position in the expression (1-based) |
| `# Error: unknown modifier {x} (see {help})` | a `{…}` block did not match any modifier (typo, different case, extra argument) |
| `# Error: modifier {P25} requires an expression` | a modifier that needs an expression was specified, but it is empty |
| `# Error: modifiers {h} and {b} are incompatible (integer format); keep one` | two modifiers from the same group: `{h}{b}`, `{P10}{P20}`, `{.2}{.3}` |
| `# Error: modifier {h} specified twice` | the same modifier is repeated (`{h}{h}`) |
| `# Error: command {S3} cannot be combined with other modifiers` | other modifiers were added to a service command (`{help}`, `{config}`, `{math}`, `{SN}`, `{SPN}`, `{E}`) |

The script stays **silent** (inserts nothing and reports no errors) if the line does not look like a calculator command:

* the line has no `=`;
* the line is empty or consists only of separator characters (`=====`, `-----`).

This is done so that ordinary text editing is not cluttered with messages.

---

## 🔒 Expression restrictions

Expressions are evaluated in a restricted environment. Available:

* all functions and constants of the `math` module (`sin`, `cos`, `sqrt`, `log`, `pi`, `e`, …), including as `math.xxx`;
* basic built-in functions: `abs`, `round`, `len`, `sum`, `min`, `max`, `zip`, `range`, `sorted`, `int`, `float`, `str`, `format`, etc.;
* containers, list comprehensions, and dictionary comprehensions.

There is no access to files, the network, or the system: `open`, `__import__`, `os`, `sys`, and `editor` are unavailable, and names and attributes starting with `_` (`__class__`, `__globals__`, etc.) are forbidden.

This is protection against accidental and simple malicious expressions in text, not a hermetic sandbox: complete isolation within a single Python process is impossible.

---

## Installation steps:

1. Install the PythonScript plugin via the Notepad++ Plugin Manager: Plugins → Plugins Admin. Find PythonScript in the list and install it.
2. On first use, the PythonScript plugin does not always create the required `scripts` folder automatically. So do the following:
* For a normal Notepad++ installation: put the scripts in `%APPDATA%\Notepad++\plugins\config\PythonScript\scripts`
* For the portable version of Notepad++: put the scripts in `(folder containing notepad++.exe)\plugins\config\PythonScript\scripts`
* If the `PythonScript\scripts` folder does not exist, create it manually. Put the script file (for example, `npp_py_inline2.py`) into the `scripts` folder.
3. Go to the main menu: Plugins → PythonScript → Configuration…. Move the script you loaded from the User Scripts section to the Menu items section. Restart Notepad++.
4. Assign a keyboard shortcut for running the script. Go to the main menu: Options → Shortcut Mapper → Plugins (in the Russian UI). Usually your script is found near the end of the table. Set a convenient key combination for it.

## Project status

✅ All planned functionality is implemented.  
🤝 Pull Requests with sensible additions are welcome.

## 📝 License
The project is distributed under the MIT license. See [LICENSE](./LICENSE) for details.
