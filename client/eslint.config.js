import js from '@eslint/js';
import globals from 'globals';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';

export default [
  {
    ignores: [
      'dist',
      'build',
      'node_modules',
      '.venv',
      '**/*.min.js',
      'eslint.config.js',
      'vite.config.js'
    ],
  },
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2021,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    settings: { react: { version: '18.3' } },
    plugins: {
      react,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...react.configs.recommended.rules,
      ...react.configs['jsx-runtime'].rules,
      ...reactHooks.configs.recommended.rules,

      'react/jsx-no-target-blank': 'off',
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],

      indent: ['error', 4],
      quotes: ['error', 'double'],
      semi: ['error', 'always'],
      'comma-dangle': ['error', 'always-multiline'],
      'brace-style': ['error', 'allman', { allowSingleLine: false }],
      'space-before-blocks': ['error', 'always'],
      'keyword-spacing': ['error', { before: true, after: true }],
      'space-in-parens': ['error', 'never'],
      'object-curly-spacing': ['error', 'never'],
      'array-bracket-spacing': ['error', 'never'],
      camelcase: ['error', { properties: 'always' }],
      'no-underscore-dangle': ['off'],
      'space-infix-ops': ['error', { int32Hint: false }],
      'key-spacing': ['error', { beforeColon: false, afterColon: true }],
      'object-curly-newline': ['error', { multiline: true, consistent: true }],
    },
  },
];
