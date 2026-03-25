<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'

const route = useRoute()
const router = useRouter()

const ticket = ref(null)
const loading = ref(false)
const error = ref(null)

const messageInput = ref('')
const sending = ref(false)
const sendError = ref(null)
const chatEl = ref(null)

const statusOptions = ['Open', 'In Progress', 'Resolved', 'Closed']
const updatingStatus = ref(false)

// ---------------------------------------------------------------------------
// Load ticket
// ---------------------------------------------------------------------------
const loadTicket = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await api.getTicket(route.params.id)
    ticket.value = res.data
    await nextTick()
    scrollToBottom()
  } catch (err) {
    error.value = 'Ticket not found or failed to load.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => loadTicket())

// ---------------------------------------------------------------------------
// Status update
// ---------------------------------------------------------------------------
async function changeStatus(newStatus) {
  if (!ticket.value || ticket.value.status === newStatus) return
  updatingStatus.value = true
  try {
    const res = await api.updateStatus(ticket.value.id, newStatus)
    ticket.value.status = res.data.status
  } catch (err) {
    console.error('Failed to update status', err)
  } finally {
    updatingStatus.value = false
  }
}

// ---------------------------------------------------------------------------
// Send message
// ---------------------------------------------------------------------------
async function sendMessage() {
  const content = messageInput.value.trim()
  if (!content || sending.value) return

  sending.value = true
  sendError.value = null
  try {
    const res = await api.sendMessage(ticket.value.id, content)
    // Append both returned messages (user + agent reply)
    ticket.value.messages.push(...res.data)
    messageInput.value = ''
    await nextTick()
    scrollToBottom()
  } catch (err) {
    sendError.value = 'Failed to send message.'
    console.error(err)
  } finally {
    sending.value = false
  }
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

function scrollToBottom() {
  if (chatEl.value) {
    chatEl.value.scrollTop = chatEl.value.scrollHeight
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function formatTime(iso) {
  const d = new Date(iso)
  if (isNaN(d.getTime())) return ''
  return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
}

function formatDate(iso) {
  const d = new Date(iso)
  if (isNaN(d.getTime())) return '—'
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function shortId(id) {
  return id ? id.slice(0, 8).toUpperCase() : ''
}

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
</script>

<template>
  <div class="detail-view">
    <div v-if="loading" class="state-box">
      <div class="spinner"></div>
      <p>Loading ticket...</p>
    </div>

    <div v-else-if="error" class="state-box error-box">
      <p>{{ error }}</p>
      <router-link to="/" class="btn-ghost">Back to Tickets</router-link>
    </div>

    <div v-else-if="ticket" class="detail-layout">
      <!-- ---------------------------------------------------------------- -->
      <!-- Left panel: ticket info                                           -->
      <!-- ---------------------------------------------------------------- -->
      <aside class="info-panel">
        <router-link to="/" class="back-link">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          All Tickets
        </router-link>

        <div class="info-card">
          <div class="info-id">#{{ shortId(ticket.id) }}</div>
          <h2 class="info-title">{{ ticket.title }}</h2>
          <p class="info-desc">{{ ticket.description }}</p>

          <div class="info-badges">
            <span
              class="badge"
              :style="{ background: getCategoryStyle(ticket.category).bg, color: getCategoryStyle(ticket.category).color }"
            >{{ ticket.category }}</span>
            <span
              class="badge"
              :style="{ background: getPriorityStyle(ticket.priority).bg, color: getPriorityStyle(ticket.priority).color }"
            >{{ ticket.priority }}</span>
          </div>

          <div class="info-section">
            <div class="info-row">
              <span class="info-label">Status</span>
              <div class="status-select-wrap">
                <select
                  :value="ticket.status"
                  class="status-select"
                  :disabled="updatingStatus"
                  :style="{ background: getStatusStyle(ticket.status).bg, color: getStatusStyle(ticket.status).color }"
                  @change="changeStatus($event.target.value)"
                >
                  <option v-for="s in statusOptions" :key="s" :value="s">{{ s }}</option>
                </select>
              </div>
            </div>

            <div class="info-row">
              <span class="info-label">Assigned Team</span>
              <span class="info-value">{{ ticket.assigned_team }}</span>
            </div>

            <div class="info-row">
              <span class="info-label">Assigned Agent</span>
              <span class="info-value">{{ ticket.assigned_agent }}</span>
            </div>

            <div class="info-row">
              <span class="info-label">Created</span>
              <span class="info-value">{{ formatDate(ticket.created_at) }}</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- ---------------------------------------------------------------- -->
      <!-- Right panel: chat                                                 -->
      <!-- ---------------------------------------------------------------- -->
      <section class="chat-panel">
        <div class="chat-header">
          <span class="chat-header-title">Conversation</span>
          <span class="chat-msg-count">{{ ticket.messages.length }} message{{ ticket.messages.length !== 1 ? 's' : '' }}</span>
        </div>

        <!-- Messages -->
        <div ref="chatEl" class="chat-messages">
          <template v-for="msg in ticket.messages" :key="msg.id">
            <!-- System message -->
            <div v-if="msg.sender_type === 'system'" class="msg-system">
              <span>{{ msg.content }}</span>
              <span class="msg-time">{{ formatTime(msg.timestamp) }}</span>
            </div>

            <!-- User message (right) -->
            <div v-else-if="msg.sender_type === 'user'" class="msg-row msg-row-user">
              <div class="msg-bubble msg-bubble-user">
                <div class="msg-sender">{{ msg.sender }}</div>
                <div class="msg-content">{{ msg.content }}</div>
                <div class="msg-time msg-time-user">{{ formatTime(msg.timestamp) }}</div>
              </div>
              <div class="msg-avatar msg-avatar-user">Y</div>
            </div>

            <!-- Agent message (left) -->
            <div v-else class="msg-row msg-row-agent">
              <div class="msg-avatar msg-avatar-agent">{{ msg.sender.charAt(0) }}</div>
              <div class="msg-bubble msg-bubble-agent">
                <div class="msg-sender">{{ msg.sender }}</div>
                <div class="msg-content">{{ msg.content }}</div>
                <div class="msg-time">{{ formatTime(msg.timestamp) }}</div>
              </div>
            </div>
          </template>
        </div>

        <!-- Input area -->
        <div class="chat-input-area">
          <div v-if="sendError" class="send-error">{{ sendError }}</div>
          <div class="input-row">
            <textarea
              v-model="messageInput"
              class="chat-input"
              placeholder="Type a message... (Enter to send)"
              rows="2"
              :disabled="sending"
              @keydown="handleKeydown"
            ></textarea>
            <button
              class="send-btn"
              :disabled="sending || !messageInput.trim()"
              @click="sendMessage"
            >
              <span v-if="sending" class="btn-spinner"></span>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.detail-view {
  width: 100%;
  height: calc(100vh - 56px - 4rem);
  min-height: 500px;
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

.detail-layout {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1.25rem;
  height: 100%;
}

/* ---- Info panel ---- */
.info-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  color: #64748b;
  font-size: 0.875rem;
  transition: color 0.15s;
}

.back-link:hover {
  color: #3b82f6;
}

.info-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-id {
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
  font-family: monospace;
  letter-spacing: 0.05em;
}

.info-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.4;
}

.info-desc {
  font-size: 0.875rem;
  color: #475569;
  line-height: 1.5;
}

.info-badges {
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

.info-section {
  border-top: 1px solid #f1f5f9;
  padding-top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.info-row {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.info-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 0.875rem;
  color: #0f172a;
}

.status-select-wrap {
  display: inline-flex;
}

.status-select {
  border: none;
  border-radius: 999px;
  padding: 0.2rem 1.8rem 0.2rem 0.7rem;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.4rem center;
  outline: none;
  transition: opacity 0.15s;
}

.status-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-ghost {
  background: transparent;
  border: 1px solid #d1d5db;
  color: #475569;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  transition: border-color 0.15s;
}

.btn-ghost:hover {
  border-color: #94a3b8;
}

/* ---- Chat panel ---- */
.chat-panel {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #f1f5f9;
}

.chat-header-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
}

.chat-msg-count {
  font-size: 0.8rem;
  color: #94a3b8;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  scroll-behavior: smooth;
}

/* System message */
.msg-system {
  text-align: center;
  font-size: 0.78rem;
  color: #94a3b8;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  padding: 0.3rem 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  align-self: center;
  max-width: 90%;
}

.msg-time {
  font-size: 0.7rem;
  color: #94a3b8;
  white-space: nowrap;
}

/* Message rows */
.msg-row {
  display: flex;
  align-items: flex-end;
  gap: 0.6rem;
}

.msg-row-user {
  justify-content: flex-end;
}

.msg-row-agent {
  justify-content: flex-start;
}

.msg-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.78rem;
  font-weight: 700;
  flex-shrink: 0;
}

.msg-avatar-user {
  background: #3b82f6;
  color: #fff;
}

.msg-avatar-agent {
  background: #e2e8f0;
  color: #475569;
}

.msg-bubble {
  max-width: 70%;
  padding: 0.65rem 0.9rem;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.msg-bubble-user {
  background: #3b82f6;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.msg-bubble-agent {
  background: #f1f5f9;
  color: #0f172a;
  border-bottom-left-radius: 4px;
}

.msg-sender {
  font-size: 0.72rem;
  font-weight: 700;
  opacity: 0.75;
}

.msg-content {
  font-size: 0.875rem;
  line-height: 1.45;
  white-space: pre-wrap;
  word-break: break-word;
}

.msg-time-user {
  color: rgba(255, 255, 255, 0.65);
}

/* Input area */
.chat-input-area {
  border-top: 1px solid #e2e8f0;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.send-error {
  font-size: 0.8rem;
  color: #b91c1c;
  background: #fee2e2;
  border-radius: 6px;
  padding: 0.4rem 0.75rem;
}

.input-row {
  display: flex;
  gap: 0.6rem;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 0.6rem 0.85rem;
  font-size: 0.875rem;
  font-family: inherit;
  color: #0f172a;
  resize: none;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  line-height: 1.4;
}

.chat-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.chat-input:disabled {
  background: #f8fafc;
  cursor: not-allowed;
}

.send-btn {
  width: 42px;
  height: 42px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s;
}

.send-btn:hover:not(:disabled) {
  background: #2563eb;
}

.send-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
</style>
