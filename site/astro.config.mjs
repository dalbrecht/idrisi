import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://idrisi.donalbrecht.com',
  integrations: [sitemap()],
  build: {
    format: 'directory',
  },
});
