<script lang="ts">
  import { onMount } from 'svelte'
  import { fetchPlaces, fetchTrips, fetchProjects } from '../lib/api'

  let placeCount: number = $state(0)
  let tripCount: number = $state(0)
  let projectCount: number = $state(0)
  let loading: boolean = $state(true)

  interface Props {
    navigate?: (view: string) => void
  }

  let { navigate = () => {} }: Props = $props()

  onMount(async () => {
    try {
      const [places, trips, projects] = await Promise.all([
        fetchPlaces(),
        fetchTrips(),
        fetchProjects(),
      ])
      placeCount = places.length
      tripCount = trips.length
      projectCount = projects.length
    } catch {
      // Counts stay at 0 on error
    } finally {
      loading = false
    }
  })
</script>

<h2>Dashboard</h2>

{#if loading}
  <p>Loading...</p>
{:else}
  <div class="stats">
    <div class="stat-card">
      <div class="stat-number">{placeCount}</div>
      <div class="stat-label">Places</div>
    </div>
    <div class="stat-card">
      <div class="stat-number">{tripCount}</div>
      <div class="stat-label">Trips</div>
    </div>
    <div class="stat-card">
      <div class="stat-number">{projectCount}</div>
      <div class="stat-label">Projects</div>
    </div>
  </div>

  <div class="actions">
    <h3>Quick Actions</h3>
    <div class="action-buttons">
      <button onclick={() => navigate('places')}>Manage Places</button>
      <button onclick={() => navigate('trips')}>Manage Trips</button>
      <button onclick={() => navigate('projects')}>Map Composer</button>
    </div>
  </div>
{/if}

<style>
  .stats {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .stat-card {
    flex: 1;
    padding: 1.5rem;
    background: #f0f7ff;
    border-radius: 8px;
    text-align: center;
  }

  .stat-number {
    font-size: 2.5rem;
    font-weight: 700;
    color: #4a90d9;
  }

  .stat-label {
    font-size: 0.9rem;
    color: #666;
    margin-top: 0.25rem;
  }

  .actions {
    margin-top: 1rem;
  }

  .action-buttons {
    display: flex;
    gap: 0.75rem;
  }

  .action-buttons button {
    padding: 0.6rem 1.2rem;
    background: #4a90d9;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .action-buttons button:hover {
    background: #3a7bc8;
  }
</style>
