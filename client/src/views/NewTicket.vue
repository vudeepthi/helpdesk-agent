<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'

const router = useRouter()

const form = reactive({
  title: '',
  description: '',
  category: 'Network',
  priority: 'Medium',
})

const errors = reactive({
  title: '',
  description: '',
})

const submitting = ref(false)
const submitError = ref(null)

const categories = ['Network', 'Software', 'Hardware', 'Security', 'Access', 'Other']
const priorities = ['Low', 'Medium', 'High', 'Critical']

function validate() {
  let valid = true
  errors.title = ''
  errors.description = ''

  if (!form.title.trim()) {
    errors.title = 'Title is required.'
    valid = false
  }

  if (!form.description.trim()) {
    errors.description = 'Description is required.'
    valid = false
  } else if (form.description.trim().length < 20) {
    errors.description = 'Description must be at least 20 characters.'
    valid = false
  }

  return valid
}

async function submit() {
  if (!validate()) return

  submitting.value = true
  submitError.value = null
  try {
    const res = await api.createTicket({
      title: form.title.trim(),
      description: form.description.trim(),
      category: form.category,
      priority: form.priority,
    })
    router.push(`/tickets/${res.data.id}`)
  } catch (err) {
    submitError.value = 'Failed to create ticket. Please try again.'
    console.error(err)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="new-ticket-view">
    <div class="form-header">
      <router-link to="/" class="back-link">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        Back to Tickets
      </router-link>
      <h1 class="page-title">New Support Ticket</h1>
      <p class="page-sub">Fill in the details below and we'll route your request to the right team.</p>
    </div>

    <div class="form-card">
      <form @submit.prevent="submit" novalidate>
        <div class="field">
          <label class="label" for="title">Title <span class="required">*</span></label>
          <input
            id="title"
            v-model="form.title"
            type="text"
            class="input"
            :class="{ 'input-error': errors.title }"
            placeholder="Brief summary of your issue"
            autocomplete="off"
          />
          <p v-if="errors.title" class="field-error">{{ errors.title }}</p>
        </div>

        <div class="field">
          <label class="label" for="description">Description <span class="required">*</span></label>
          <textarea
            id="description"
            v-model="form.description"
            class="input textarea"
            :class="{ 'input-error': errors.description }"
            placeholder="Describe the issue in detail (minimum 20 characters)"
            rows="5"
          ></textarea>
          <div class="field-hint-row">
            <p v-if="errors.description" class="field-error">{{ errors.description }}</p>
            <span v-else class="char-count">{{ form.description.length }} chars</span>
          </div>
        </div>

        <div class="field-row">
          <div class="field">
            <label class="label" for="category">Category</label>
            <select id="category" v-model="form.category" class="input select">
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>

          <div class="field">
            <label class="label" for="priority">Priority</label>
            <select id="priority" v-model="form.priority" class="input select">
              <option v-for="pri in priorities" :key="pri" :value="pri">{{ pri }}</option>
            </select>
          </div>
        </div>

        <div v-if="submitError" class="submit-error">{{ submitError }}</div>

        <div class="form-actions">
          <router-link to="/" class="btn-ghost">Cancel</router-link>
          <button type="submit" class="btn-primary" :disabled="submitting">
            <span v-if="submitting" class="btn-spinner"></span>
            {{ submitting ? 'Creating...' : 'Create Ticket' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.new-ticket-view {
  max-width: 640px;
  margin: 0 auto;
}

.form-header {
  margin-bottom: 1.5rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  color: #64748b;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  transition: color 0.15s;
}

.back-link:hover {
  color: #3b82f6;
}

.page-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #0f172a;
}

.page-sub {
  font-size: 0.875rem;
  color: #64748b;
  margin-top: 0.3rem;
}

.form-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.field {
  margin-bottom: 1.25rem;
  flex: 1;
}

.field-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0;
}

.label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.4rem;
}

.required {
  color: #ef4444;
}

.input {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 0.6rem 0.85rem;
  font-size: 0.9rem;
  color: #0f172a;
  background: #fff;
  transition: border-color 0.15s, box-shadow 0.15s;
  outline: none;
  font-family: inherit;
}

.input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.input-error {
  border-color: #ef4444;
}

.input-error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.12);
}

.textarea {
  resize: vertical;
  min-height: 100px;
}

.select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  padding-right: 2.2rem;
  cursor: pointer;
}

.field-hint-row {
  min-height: 1.25rem;
  margin-top: 0.3rem;
}

.field-error {
  font-size: 0.8rem;
  color: #ef4444;
}

.char-count {
  font-size: 0.78rem;
  color: #94a3b8;
}

.submit-error {
  background: #fee2e2;
  color: #b91c1c;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #3b82f6;
  color: #fff;
  padding: 0.6rem 1.4rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: background 0.15s;
  text-decoration: none;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-ghost {
  background: transparent;
  border: 1px solid #d1d5db;
  color: #475569;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  transition: border-color 0.15s;
}

.btn-ghost:hover {
  border-color: #94a3b8;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
