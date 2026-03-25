<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="app-shell">
    <header class="navbar">
      <div class="navbar-inner">
        <div class="brand">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 13.5 19.79 19.79 0 0 1 1.61 5a2 2 0 0 1 2-2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 10.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 17z"/>
          </svg>
          <span class="brand-name">IT Helpdesk</span>
        </div>
        <nav class="nav-links">
          <router-link to="/" class="nav-link">All Tickets</router-link>
          <router-link to="/tickets/new" class="nav-link nav-link-cta">New Ticket</router-link>
        </nav>
      </div>
    </header>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style>
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f8fafc;
  color: #0f172a;
  min-height: 100vh;
}

a {
  text-decoration: none;
  color: inherit;
}
</style>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: #0f172a;
  color: #fff;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.navbar-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 2rem;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: #fff;
}

.brand-name {
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-link {
  color: #cbd5e1;
  padding: 0.4rem 0.9rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.nav-link.router-link-active {
  color: #fff;
  background: rgba(59, 130, 246, 0.3);
}

.nav-link-cta {
  background: #3b82f6;
  color: #fff !important;
  margin-left: 0.5rem;
}

.nav-link-cta:hover {
  background: #2563eb !important;
}

.main-content {
  flex: 1;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
}
</style>
