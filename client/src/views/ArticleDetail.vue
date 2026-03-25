<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'

const route = useRoute()
const router = useRouter()

const article = ref(null)
const loading = ref(false)
const error = ref(null)

// ---------------------------------------------------------------------------
// Markdown-like parser — no external library, line-by-line
// ---------------------------------------------------------------------------
function parseMarkdown(text) {
  if (!text) return ''

  const lines = text.split('\n')
  const output = []

  // Track open list/table contexts
  let inUl = false
  let inOl = false
  let inTable = false
  let tableHeaderDone = false
  let inFence = false
  let fenceLines = []
  let fenceLang = ''

  function closeUl() {
    if (inUl) { output.push('</ul>'); inUl = false }
  }
  function closeOl() {
    if (inOl) { output.push('</ol>'); inOl = false }
  }
  function closeTable() {
    if (inTable) { output.push('</tbody></table>'); inTable = false; tableHeaderDone = false }
  }
  function closeLists() {
    closeUl(); closeOl(); closeTable()
  }

  // Inline formatting: bold, inline code
  function inlineFormat(str) {
    // Bold: **text**
    str = str.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Inline code: `code`
    str = str.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    return str
  }

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i]

    // ---- Fenced code block ------------------------------------------------
    if (raw.trimStart().startsWith('```')) {
      if (!inFence) {
        // Opening fence — extract optional language hint
        closeLists()
        fenceLang = raw.trim().slice(3).trim()
        fenceLines = []
        inFence = true
      } else {
        // Closing fence
        const escaped = fenceLines
          .join('\n')
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
        const langAttr = fenceLang ? ` class="language-${fenceLang}"` : ''
        output.push(`<pre class="code-block"><code${langAttr}>${escaped}</code></pre>`)
        inFence = false
        fenceLines = []
        fenceLang = ''
      }
      continue
    }

    if (inFence) {
      fenceLines.push(raw)
      continue
    }

    // ---- Headings ---------------------------------------------------------
    if (raw.startsWith('### ')) {
      closeLists()
      output.push(`<h3>${inlineFormat(raw.slice(4))}</h3>`)
      continue
    }
    if (raw.startsWith('## ')) {
      closeLists()
      output.push(`<h2>${inlineFormat(raw.slice(3))}</h2>`)
      continue
    }
    if (raw.startsWith('# ')) {
      closeLists()
      output.push(`<h1>${inlineFormat(raw.slice(2))}</h1>`)
      continue
    }

    // ---- Table rows -------------------------------------------------------
    if (raw.trimStart().startsWith('|')) {
      // Skip separator rows like |---|---|
      if (/^\|[\s\-:|]+\|/.test(raw.trim())) {
        // This is a header/body separator — mark header as done
        tableHeaderDone = true
        continue
      }

      // Parse cells
      const cells = raw.trim()
        .replace(/^\|/, '')
        .replace(/\|$/, '')
        .split('|')
        .map(c => inlineFormat(c.trim()))

      if (!inTable) {
        closeUl(); closeOl()
        output.push('<table class="md-table"><thead><tr>')
        cells.forEach(c => output.push(`<th>${c}</th>`))
        output.push('</tr></thead><tbody>')
        inTable = true
        tableHeaderDone = false
      } else {
        output.push('<tr>')
        cells.forEach(c => output.push(`<td>${c}</td>`))
        output.push('</tr>')
      }
      continue
    } else if (inTable) {
      closeTable()
    }

    // ---- Checkbox list items: - [ ] or - [x] ------------------------------
    if (/^- \[[ x]\] /.test(raw)) {
      const checked = raw.startsWith('- [x]')
      const text = inlineFormat(raw.slice(checked ? 6 : 6))
      if (!inUl) { closeOl(); output.push('<ul class="md-list">'); inUl = true }
      const checkbox = checked
        ? '<span class="cb cb-checked">&#10003;</span>'
        : '<span class="cb">&#9633;</span>'
      output.push(`<li class="cb-item">${checkbox} ${text}</li>`)
      continue
    }

    // ---- Unordered list ---------------------------------------------------
    if (raw.startsWith('- ')) {
      if (!inUl) { closeOl(); closeTable(); output.push('<ul class="md-list">'); inUl = true }
      output.push(`<li>${inlineFormat(raw.slice(2))}</li>`)
      continue
    } else if (inUl && raw.trim() !== '') {
      // Non-empty, non-list line closes the list
      closeUl()
    }

    // ---- Ordered list -----------------------------------------------------
    if (/^\d+\. /.test(raw)) {
      if (!inOl) { closeUl(); closeTable(); output.push('<ol class="md-list">'); inOl = true }
      const content = raw.replace(/^\d+\. /, '')
      output.push(`<li>${inlineFormat(content)}</li>`)
      continue
    } else if (inOl && raw.trim() !== '') {
      closeOl()
    }

    // ---- Empty line → paragraph break ------------------------------------
    if (raw.trim() === '') {
      closeLists()
      output.push('<div class="para-break"></div>')
      continue
    }

    // ---- Plain paragraph line --------------------------------------------
    output.push(`<p>${inlineFormat(raw)}</p>`)
  }

  // Close any open blocks at end of input
  closeLists()
  if (inFence && fenceLines.length) {
    const escaped = fenceLines
      .join('\n')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
    output.push(`<pre class="code-block"><code>${escaped}</code></pre>`)
  }

  return output.join('\n')
}

// ---------------------------------------------------------------------------
// Data fetching
// ---------------------------------------------------------------------------
const loadArticle = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await api.getKnowledgeArticle(route.params.id)
    article.value = res.data
  } catch (err) {
    error.value = 'Article not found or failed to load.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => loadArticle())
</script>

<template>
  <div class="article-view">

    <!-- Loading -->
    <div v-if="loading" class="state-box">
      <div class="spinner"></div>
      <p>Loading article...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="state-box error-box">
      <p>{{ error }}</p>
      <button class="btn-ghost" @click="router.back()">Go back</button>
    </div>

    <!-- Article -->
    <div v-else-if="article" class="article-card">
      <div class="article-header">
        <button class="back-btn" @click="router.back()">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          Back
        </button>
        <span class="article-id-badge">{{ article.id }}</span>
      </div>

      <h1 class="article-title">{{ article.title }}</h1>

      <p v-if="article.summary" class="article-summary">{{ article.summary }}</p>

      <div class="article-divider"></div>

      <!-- Rendered content -->
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div class="article-content" v-html="parseMarkdown(article.content)"></div>
    </div>

  </div>
</template>

<style scoped>
.article-view {
  max-width: 760px;
  margin: 0 auto;
}

/* ---- Loading / error states ---- */
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

/* ---- Card ---- */
.article-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 2rem 2.25rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

/* ---- Header row ---- */
.article-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: transparent;
  border: 1px solid #d1d5db;
  color: #64748b;
  padding: 0.35rem 0.8rem;
  border-radius: 7px;
  font-size: 0.83rem;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
  font-family: inherit;
}

.back-btn:hover {
  color: #3b82f6;
  border-color: #93c5fd;
}

.article-id-badge {
  font-size: 0.72rem;
  font-weight: 700;
  color: #0284c7;
  background: #e0f2fe;
  border-radius: 5px;
  padding: 0.2rem 0.55rem;
  letter-spacing: 0.02em;
  font-family: monospace;
}

/* ---- Title & summary ---- */
.article-title {
  font-size: 1.55rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.3;
  margin: 0 0 0.6rem;
}

.article-summary {
  font-size: 0.95rem;
  color: #64748b;
  line-height: 1.55;
  margin: 0;
}

.article-divider {
  border-top: 1px solid #e2e8f0;
  margin: 1.5rem 0;
}

/* ---- Rendered markdown content ---- */
.article-content {
  font-size: 0.93rem;
  color: #1e293b;
  line-height: 1.7;
}

/* Scoped deep styles for parsed HTML */
.article-content :deep(h1) {
  font-size: 1.35rem;
  font-weight: 700;
  color: #0f172a;
  margin: 1.5rem 0 0.5rem;
  line-height: 1.3;
}

.article-content :deep(h2) {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0f172a;
  margin: 1.4rem 0 0.45rem;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 0.3rem;
}

.article-content :deep(h3) {
  font-size: 0.97rem;
  font-weight: 700;
  color: #334155;
  margin: 1.2rem 0 0.4rem;
}

.article-content :deep(p) {
  margin: 0 0 0.5rem;
}

.article-content :deep(.para-break) {
  height: 0.6rem;
}

.article-content :deep(strong) {
  font-weight: 700;
  color: #0f172a;
}

/* Inline code */
.article-content :deep(.inline-code) {
  background: #f1f5f9;
  color: #be185d;
  padding: 0.1em 0.4em;
  border-radius: 4px;
  font-size: 0.88em;
  font-family: 'Consolas', 'Menlo', 'Monaco', monospace;
}

/* Fenced code blocks */
.article-content :deep(.code-block) {
  background: #1e293b;
  color: #e2e8f0;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  margin: 1rem 0;
  overflow-x: auto;
  font-size: 0.85rem;
  line-height: 1.6;
}

.article-content :deep(.code-block code) {
  font-family: 'Consolas', 'Menlo', 'Monaco', monospace;
  background: transparent;
  color: inherit;
  padding: 0;
}

/* Lists */
.article-content :deep(.md-list) {
  padding-left: 1.5rem;
  margin: 0.5rem 0 0.75rem;
}

.article-content :deep(.md-list li) {
  margin-bottom: 0.3rem;
  line-height: 1.55;
}

/* Checkbox items */
.article-content :deep(.cb-item) {
  list-style: none;
  margin-left: -0.25rem;
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
}

.article-content :deep(.cb) {
  font-size: 0.9em;
  color: #94a3b8;
  flex-shrink: 0;
}

.article-content :deep(.cb-checked) {
  color: #16a34a;
}

/* Tables */
.article-content :deep(.md-table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  margin: 1rem 0;
}

.article-content :deep(.md-table th) {
  background: #f8fafc;
  color: #374151;
  font-weight: 700;
  text-align: left;
  padding: 0.55rem 0.85rem;
  border: 1px solid #e2e8f0;
  font-size: 0.83rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.article-content :deep(.md-table td) {
  padding: 0.5rem 0.85rem;
  border: 1px solid #e2e8f0;
  color: #1e293b;
  vertical-align: top;
}

.article-content :deep(.md-table tr:nth-child(even) td) {
  background: #f8fafc;
}

/* ---- Shared button ---- */
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
  font-family: inherit;
}

.btn-ghost:hover {
  border-color: #94a3b8;
}
</style>
