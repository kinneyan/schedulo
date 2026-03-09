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
  const maxValue = 100;
  ```
* Python does not require semicolons; do not use them in Python code.

### Quotes

* Use double quotes for all strings in both JavaScript and Python.

  ```js
  const defaultMessage = "Hello world";
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

## Docstrings & Documentation

### Python — Sphinx style

Write a one-line summary, then use `:param:` and `:return:` tags. Include `:raises:` when a function raises intentionally.

```python
def get_user(user_id: int) -> User:
    """Fetch a user by their ID.

    :param int user_id: Primary key of the user to fetch.
    :return: The matching User instance.
    :rtype: User
    :raises ValueError: If no user with the given ID exists.
    """
```


### JavaScript / React — JSDoc style

Use JSDoc for plain functions and utilities:

```js
/**
 * Formats a phone number for display.
 *
 * @param {string} raw - Unformatted phone number string.
 * @returns {string} Phone number in (xxx) xxx-xxxx format.
 */
function formatPhone(raw)
{
    // ...
}
```

For React components, document props and the return type:

```jsx
/**
 * Button that submits the enclosing form.
 *
 * @param {Object} props
 * @param {string} props.buttonText - Label shown on the button.
 * @returns {JSX.Element}
 */
const SubmitButton = ({ buttonText }) =>
{
    // ...
};
```

