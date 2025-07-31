import globals from 'globals';
import jsLint from '@eslint/js';
import pluginVue from 'eslint-plugin-vue';
import vueEslintParser from 'vue-eslint-parser';
import babelEslintParser from '@babel/eslint-parser'; // <-- Add this
// import pluginPrettierRecommended from 'eslint-plugin-prettier/recommended';
// import eslintConfigPrettier from 'eslint-config-prettier';

const projectGlobals = {
    ...globals.browser,
    ...globals.node,
    ...globals.jquery,
    es6: true,
    moment: true,
    swal: true,
    bootstrap: true,
    env: true,
    _: true, // Lodash
};

export default [
    jsLint.configs.recommended,
    // pluginPrettierRecommended,
    ...pluginVue.configs['flat/essential'],
    // eslintConfigPrettier,
    // {
    //     ignores: ['.venv/', '.env/', '.env', 'node_modules/'],
    // },
    {
        files: ['**/*.{js,mjs,cjs,ts,mts,jsx,tsx}'],
        languageOptions: {
            parser: babelEslintParser,
            parserOptions: {
                sourceType: 'module',
                ecmaVersion: 2020,
                ecmaFeatures: { jsx: true },
                requireConfigFile: false,
            },
            globals: projectGlobals,
        },
        rules:{
            'vue/jsx-uses-vars': 'error',
        }
    },
    {
        files: ['src/**/*.vue'],
        plugins: {
            vue: pluginVue,
        },
        languageOptions: {
            sourceType: 'module',
            ecmaVersion: 12,
            parser: vueEslintParser,
            parserOptions: {
                sourceType: 'module',
                ecmaVersion: 12,
                ecmaFeatures: { jsx: true },
            },
            globals: projectGlobals,
        },
        rules: {
            // 'prettier/prettier': 'error',
            'no-redeclare': 'warn',
            'no-unused-vars': 'warn',
            'vue/no-mutating-props': 'off',
            'vue/jsx-uses-vars': 'error',
        },
    },
    
];