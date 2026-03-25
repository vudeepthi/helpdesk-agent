import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import TicketList from './views/TicketList.vue'
import NewTicket from './views/NewTicket.vue'
import TicketDetail from './views/TicketDetail.vue'
import ArticleDetail from './views/ArticleDetail.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: TicketList },
    { path: '/tickets/new', component: NewTicket },
    { path: '/tickets/:id', component: TicketDetail },
    { path: '/knowledge/:id', component: ArticleDetail },
  ],
})

createApp(App).use(router).mount('#app')
