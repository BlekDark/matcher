import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import './assets/main.css'
import axios from "axios";

const app = createApp(App)

let backendURL = import.meta.env.VITE_BACKEND_HOST;
console.log('App started!')
console.log('Current backendURL', backendURL)
let username = import.meta.env.VITE_USERNAME;
let password = import.meta.env.VITE_PASSWORD;
let token = btoa(`${username}:${password}`);

axios.defaults.baseURL = backendURL
axios.defaults.headers.common['Authorization'] = `Basic ${token}`;
axios.defaults.headers.post['Content-Type'] = 'application/json';

app.config.globalProperties.$http = axios
app.config.globalProperties.$projectVersion = '1.0'

app.use(store)

app.use(router, axios)

app.use(ElementPlus)

app.mount('#app')
