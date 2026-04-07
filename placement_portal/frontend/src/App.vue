<template>
  <div id="app" class="d-flex flex-column min-vh-100">
    <header class="bg-dark text-white text-center py-3">
      <h2 class="mb-0">Placement Portal</h2>
    </header>

    <main class="flex-grow-1">
      <router-view></router-view>
    </main>

    <footer class="bg-light text-center py-3 mt-auto border-top">
      <p class="mb-0 text-muted">Placement portal MAD 2 project</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
body {
  margin: 0;
  font-family: Arial, sans-serif;
}
</style>
