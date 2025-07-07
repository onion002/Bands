module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
    es2021: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended',
    '@vue/typescript/recommended',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    // 确保组件包含必要的标签
    'vue/component-tags-order': ['error', {
      order: ['template', 'script', 'style']
    }],
    'vue/multi-word-component-names': 'off',
    
    // TypeScript 规则
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    
    // 其他规则
    'vue/html-self-closing': 'off',
    'vue/singleline-html-element-content-newline': 'off',
  },
  ignorePatterns: ['dist/**', 'node_modules/**'],
};