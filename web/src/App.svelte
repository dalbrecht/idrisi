<script lang="ts">
  import Dashboard from './routes/Dashboard.svelte'
  import Places from './routes/Places.svelte'
  import Trips from './routes/Trips.svelte'
  import MapComposer from './routes/MapComposer.svelte'

  type View = 'dashboard' | 'places' | 'trips' | 'projects'

  let currentView: View = $state('dashboard')

  function navigate(view: string) {
    currentView = view as View
  }
</script>

<main>
  <nav>
    <h1>Voyages</h1>
    <div class="nav-links">
      <button class:active={currentView === 'dashboard'} onclick={() => currentView = 'dashboard'}>
        Dashboard
      </button>
      <button class:active={currentView === 'places'} onclick={() => currentView = 'places'}>
        Places
      </button>
      <button class:active={currentView === 'trips'} onclick={() => currentView = 'trips'}>
        Trips
      </button>
      <button class:active={currentView === 'projects'} onclick={() => currentView = 'projects'}>
        Map Composer
      </button>
    </div>
  </nav>

  <section class="content">
    {#if currentView === 'dashboard'}
      <Dashboard {navigate} />
    {:else if currentView === 'places'}
      <Places />
    {:else if currentView === 'trips'}
      <Trips />
    {:else if currentView === 'projects'}
      <MapComposer />
    {/if}
  </section>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f5f5f5;
    color: #333;
  }

  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }

  nav {
    display: flex;
    align-items: center;
    gap: 2rem;
    padding: 0.5rem 0;
    border-bottom: 2px solid #ddd;
    margin-bottom: 1.5rem;
  }

  nav h1 {
    margin: 0;
    font-size: 1.5rem;
  }

  .nav-links {
    display: flex;
    gap: 0.5rem;
  }

  .nav-links button {
    padding: 0.5rem 1rem;
    border: 1px solid #ccc;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .nav-links button:hover {
    background: #e9e9e9;
  }

  .nav-links button.active {
    background: #4a90d9;
    color: white;
    border-color: #4a90d9;
  }

  .content {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }
</style>
