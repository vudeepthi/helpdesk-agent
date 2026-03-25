<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'

const router = useRouter()
const tickets = ref([])
const loading = ref(false)
const error = ref(null)

const loadTickets = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await api.getTickets()
    // Show newest first
    tickets.value = [...res.data].reverse()
  } catch (err) {
    error.value = 'Failed to load tickets. Is the backend running on port 8002?'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => loadTickets())

const categoryColors = {
  Network: { bg: '#dbeafe', color: '#1d4ed8' },
  Software: { bg: '#ede9fe', color: '#7c3aed' },
  Hardware: { bg: '#ffedd5', color: '#c2410c' },
  Security: { bg: '#fee2e2', color: '#b91c1c' },
  Access: { bg: '#ccfbf1', color: '#0f766e' },
  Other: { bg: '#f1f5f9', color: '#475569' },
}

const priorityColors = {
  Low: { bg: '#dcfce7', color: '#15803d' },
  Medium: { bg: '#fef9c3', color: '#a16207' },
  High: { bg: '#ffedd5', color: '#c2410c' },
  Critical: { bg: '#fee2e2', color: '#b91c1c' },
}

const statusColors = {
  Open: { bg: '#dbeafe', color: '#1d4ed8' },
  'In Progress': { bg: '#fef9c3', color: '#a16207' },
  Resolved: { bg: '#dcfce7', color: '#15803d' },
  Closed: { bg: '#f1f5f9', color: '#475569' },
}

function getCategoryStyle(cat) {
  return categoryColors[cat] || categoryColors['Other']
}

function getPriorityStyle(pri) {
  return priorityColors[pri] || { bg: '#f1f5f9', color: '#475569' }
}

function getStatusStyle(status) {
  return statusColors[status] || statusColors['Open']
}

function shortId(id) {
  return id.slice(0, 8).toUpperCase()
}

function formatDate(iso) {
  const d = new Date(iso)
  if (isNaN(d.getTime())) return '—'
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function openTicket(id) {
  router.push(`/tickets/${id}`)
}
</script>

<template>
  <div class="list-view">
    <div class="list-header">
      <div>
        <h1 class="page-title">All Tickets</h1>
        <p class="page-sub">{{ tickets.length }} ticket{{ tickets.length !== 1 ? 's' : '' }} total</p>
      </div>
      <router-link to="/tickets/new" class="btn-primary">+ New Ticket</router-link>
    </div>

    <div v-if="loading" class="state-box">
      <div class="spinner"></div>
      <p>Loading tickets...</p>
    </div>

    <div v-else-if="error" class="state-box error-box">
      <p>{{ error }}</p>
      <button class="btn-ghost" @click="loadTickets">Retry</button>
    </div>

    <div v-else-if="tickets.length === 0" class="state-box">
      <p class="empty-msg">No tickets yet.</p>
      <router-link to="/tickets/new" class="btn-primary">Create your first ticket</router-link>
    </div>

    <div v-else class="ticket-grid">
      <div
        v-for="ticket in tickets"
        :key="ticket.id"
        class="ticket-card"
        @click="openTicket(ticket.id)"
      >
        <div class="card-top">
          <span class="ticket-id">#{{ shortId(ticket.id) }}</span>
          <span
            class="badge"
            :style="{ background: getStatusStyle(ticket.status).bg, color: getStatusStyle(ticket.status).color }"
          >{{ ticket.status }}</span>
        </div>

        <h3 class="ticket-title">{{ ticket.title }}</h3>

        <div class="badge-row">
          <span
            class="badge"
            :style="{ background: getCategoryStyle(ticket.category).bg, color: getCategoryStyle(ticket.category).color }"
          >{{ ticket.category }}</span>
          <span
            class="badge"
            :style="{ background: getPriorityStyle(ticket.priority).bg, color: getPriorityStyle(ticket.priority).color }"
          >{{ ticket.priority }}</span>
        </div>

        <div class="card-footer">
          <span class="meta-item">{{ ticket.assigned_team }}</span>
          <span class="meta-date">{{ formatDate(ticket.created_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.list-view {
  width: 100%;
}

.list-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #0f172a;
}

.page-sub {
  font-size: 0.875rem;
  color: #64748b;
  margin-top: 0.2rem;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  background: #3b82f6;
  color: #fff;
  padding: 0.55rem 1.2rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.15s;
  white-space: nowrap;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-ghost {
  background: transparent;
  border: 1px solid #cbd5e1;
  color: #475569;
  padding: 0.4rem 0.9rem;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  margin-top: 0.75rem;
  transition: border-color 0.15s;
}

.btn-ghost:hover {
  border-color: #94a3b8;
}

.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  color: #64748b;
  gap: 1rem;
}

.error-box {
  color: #b91c1c;
}

.empty-msg {
  font-size: 1rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.ticket-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.ticket-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1.25rem;
  cursor: pointer;
  transition: box-shadow 0.15s, border-color 0.15s, transform 0.1s;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ticket-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border-color: #3b82f6;
  transform: translateY(-1px);
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ticket-id {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  font-family: monospace;
  letter-spacing: 0.05em;
}

.ticket-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.badge-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 0.5rem;
  border-top: 1px solid #f1f5f9;
}

.meta-item {
  font-size: 0.8rem;
  color: #64748b;
}

.meta-date {
  font-size: 0.78rem;
  color: #94a3b8;
}
</style>
