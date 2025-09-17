import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';
import eslint from 'vite-plugin-eslint2';
import { viteStaticCopy } from 'vite-plugin-static-copy';
import svgLoader from 'vite-svg-loader';
import { visualizer } from 'rollup-plugin-visualizer';
import vueJsx from '@vitejs/plugin-vue-jsx';


const applicationNameShort = 'disturbance';
const port = process.env.PORT ? parseInt(process.env.PORT) : 5173;
const host = process.env.HOST || '0.0.0.0';

export default defineConfig(() => {
    const analyze = process.env.ANALYZE;
    return {
        base: `/static/${applicationNameShort}_vue/`,
        server: {
            host: host,
            port: port,
            strictPort: true,
            open: false,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers':
                    'Origin, X-Requested-With, Content-Type, Accept',
            },
            hmr: {
                protocol: 'ws',
                host: 'localhost',
                port: port,
            },
        },
        plugins: [
            vue(),
            eslint(),
            vueJsx(),
            svgLoader({
                defaultImport: 'url',
            }),
            viteStaticCopy({
                // Had to do this to get the relative paths to work
                // Probably a better way but I couldn't figure it out
                targets: [
                    // Copy the non-svgs to src but leave the svgs in assets
                    // { src: 'src/assets/*.gif', dest: 'src' },
                    { src: 'src/assets/*.jpg', dest: 'src' },
                    { src: 'src/assets/*.json', dest: 'src' },
                    { src: 'src/assets/*.png', dest: 'src' },
                    {
                        src: 'node_modules/font-awesome/fonts',
                        dest: 'node_modules/font-awesome',
                    },
                    {
                        src: 'node_modules/summernote/dist/font',
                        dest: 'node_modules/summernote/dist',
                    },
                ],
            }),
            analyze &&
                visualizer({
                    filename: 'bundle-stats.html',
                    template: 'treemap',
                    gzipSize: true,
                    brotliSize: true,
                    open: true,
                }),
        ].filter(Boolean),
        resolve: {
            alias: {
                '@': path.resolve(__dirname, './src'),
                '@vue-utils': path.resolve(__dirname, 'src/utils/vue'),
                '@common-utils': path.resolve(
                    __dirname,
                    'src/components/common/'
                ),
                '@assets': path.resolve(__dirname, 'src/assets'),
            },
        },
        esbuild: {
            drop: ['console', 'debugger'],
            minify: true,
            jsxFactory: 'h',
            jsxFragment: 'Fragment',
            include: /\.js$/,
        },
        build: {
            manifest: 'manifest.json',
            commonjsOptions: { transformMixedEsModules: true },
            root: path.resolve(__dirname, './src'),
            outDir: path.resolve(
                __dirname,
                `../../static/${applicationNameShort}_vue`
            ),
            sourcemap: false,
            rollupOptions: {
                input: {
                    main: path.resolve(__dirname, 'src/main.js'),
                },
                external: ['moment'],
            },
            emptyOutDir: true,
        },
    };
});