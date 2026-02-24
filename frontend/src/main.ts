import { createApp } from 'vue'
import App from './App.vue'

import { registerPlugins } from './plugins'

createApp(App).use(registerPlugins).mount('#app')