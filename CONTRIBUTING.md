# Project Code Style Guide

This guide outlines our team's standard coding conventions. Consistency is key—please follow these rules across the entire codebase.

---

## Naming Conventions

### Variables & Functions

* Use `camelCase` for all variable and function names **in JavaScript**.

  ```js
  let userName = "Ada";
  function getUserName()
  {
      return userName;
  }
  ```
* Use `snake_case` for all variable and function names **in Python**, to align with community standards and automatic tooling.

  ```python
  def get_user_name():
      return user_name
  ```

### File & Folder Structure

* Use `camelCase` for file and folder names.

  ```
  /src/userProfile/
  └── userSettings.js
  ```

### Classes & Types

* Use `PascalCase` for class names and type declarations.

  ```js
  class UserProfile
  {
      constructor(name)
      {
          this.name = name;
      }
  }

  type UserSettings =
  {
      darkMode: boolean,
      language: string,
  };
  ```
* In Python, use `PascalCase` for class names as per PEP 8.

  ```python
  class UserProfile:
      def __init__(self, name):
          self.name = name
  ```

### Private Variables

* Prefix private fields with an underscore `_`.

  ```js
  this._isReady = false;
  ```

  ```python
  self._is_ready = False
  ```

---

## Formatting

### Indentation

* Use 4 spaces for all indentation—no tabs.

### Semicolons

* For JavaScript, always use semicolons at the end of statements.

  ```js
  const max_value = 100;
  ```
* Python does not require semicolons; do not use them in Python code.

### Quotes

* Use double quotes for all strings in both JavaScript and Python.

  ```js
  const default_message = "Hello world";
  ```

  ```python
  greeting = "Hello world"
  ```

### Bracket and Parenthesis Spacing

* Use a space before and after parentheses and curly braces, but do not use spaces inside parentheses or braces (JavaScript).

  ```js
  if (condition)
  {
      doSomething();
  }
  ```
* In Python, follow PEP 8: no space inside parentheses, brackets, or braces, and standard spacing around operators.

  ```python
  if (x + y == 2):
      return True
  ```

### Bracket Style

* **JavaScript**: Use lined-up brackets (Allman style) for functions, conditionals, and loops.

  ```js
  function greet()
  {
      console.log("Hello");
  }

  if (condition)
  {
      doSomething();
  }
  ```
* **Python**: Use standard K\&R bracket style, as enforced by `black`.

  ```python
  def greet():
      print("Hello")

  if condition:
      do_something()
  ```

### Trailing Commas

* Use trailing commas in multiline objects, arrays, and function parameters.

  ```js
  const data = {
      name: "Ada",
      age: 30,
  };
  ```

  ```python
  config = {
      "name": "Ada",
      "age": 30,
  }
  ```

---

## Git & Branch Naming

### Branch Names

* Prefix all branch names with the related task number:

  * Format: `SCHED-<num>-short-description`

  ```bash
  git checkout -b SCHED-89-add-user-login
  ```
