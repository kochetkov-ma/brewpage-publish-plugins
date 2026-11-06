import js from '@eslint/js';

export default [
  { ignores: ['node_modules/', 'build/'] },
  js.configs.recommended,
  {
    files: ['**/*.js'],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: 'commonjs',
      globals: {
        require: 'readonly',
        module: 'writable',
        process: 'readonly',
        Buffer: 'readonly',
        URL: 'readonly',
        console: 'readonly',
      },
    },
    rules: { 'no-control-regex': 'off' },
  },
];
