import App from './routes/+page.svelte';

import '@milkdown/theme-nord/style.css';

const app = new App({
  target: document.getElementById('app') as HTMLElement
});

export default app;