# Project Code Style Guide

This guide outlines our team's standard coding conventions. Consistency is key—please follow these rules across the entire codebase.

---

## Naming Conventions

### Variables & Functions
- Use `camelCase` for all variable and function names.
  ```js
  let userName = "Ada";
  function getUserName()
  {
      return userName;
  }
  ```

### File & Folder Structure
- Use `camelCase` for file and folder names.
  ```
  /src/userProfile/
  └── userSettings.js
  ```

### Classes & Types
- Use `PascalCase` for class names and type declarations.
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

### Constants
- Use `SCREAMING_SNAKE_CASE` for constants.
  ```js
  const MAX_RETRIES = 5;
  const DEFAULT_COUNT = 0;
  ```

### Private Variables
- Prefix private fields with an underscore `_`.
  ```js
  this._isReady = false;
  ```

---

## Formatting

### Indentation
- Use 4 spaces for all indentation—no tabs.

### Semicolons
- For JavaScript, always use semicolons at the end of statements.
  ```js
  const MAX_VALUE = 100;
  ```
- Python does not require semicolons; do not use them in Python code.

### Quotes
- Use double quotes for all strings.
  ```js
  const DEFAULT_MESSAGE = "Hello world";
  ```

### Bracket and Parenthesis Spacing
- Use a space before and after parentheses and curly braces, but do not use spaces inside parentheses or braces.
  ```js
  if (condition)
  {
      doSomething();
  }
  ```
- Spaces around arithmetic and logical operators within parentheses/braces are allowed and encouraged for readability.
  ```js
  if (x + y == 2)
  {
      return true;
  }
  ```

### Bracket Style
- Use lined-up brackets (Allman style) for functions, conditionals, and loops.
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
- Use inline brackets for object literals and data structures such as JavaScript objects and Python lists/dictionaries, where it is standard syntax.
  ```js
  const user = {
      name: "Ada",
      age: 30,
  };
  ```

### Trailing Commas
- Use trailing commas in multiline objects, arrays, and function parameters.
  ```js
  const data = {
      name: "Ada",
      age: 30,
  };
  ```

---

## Git & Branch Naming

### Branch Names
- Prefix all branch names with the related task number:
  - Format: `SCHED-<num>-short-description`
  ```bash
  git checkout -b SCHED-89-add-user-login
  ```

