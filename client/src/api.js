import axios from 'axios'

const client = axios.create({
  baseURL: 'http://localhost:8003/api',
  headers: { 'Content-Type': 'application/json' },
})

export const api = {
  getTickets() {
    return client.get('/tickets')
  },

  createTicket(data) {
    return client.post('/tickets', data)
  },

  getTicket(id) {
    return client.get(`/tickets/${id}`)
  },

  updateStatus(id, status) {
    return client.patch(`/tickets/${id}/status`, { status })
  },

  sendMessage(id, content) {
    return client.post(`/tickets/${id}/messages`, { content })
  },

  getKnowledgeArticles(category) {
    return client.get('/knowledge', { params: { category } })
  },
}
