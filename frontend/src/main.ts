import { createApp } from 'vue'
import App from './App.vue'

import './styles/app.css'

import { registerPlugins } from './plugins'

createApp(App).use(registerPlugins).mount('#app')