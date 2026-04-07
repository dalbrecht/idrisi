<script lang="ts">
  import { onMount } from 'svelte'
  import { fetchTrips, createTrip, deleteTrip } from '../lib/api'
  import type { Trip } from '../lib/api'

  let trips: Trip[] = $state([])
  let newName: string = $state('')
  let newDescription: string = $state('')
  let error: string = $state('')

  onMount(async () => {
    await loadTrips()
  })

  async function loadTrips() {
    try {
      trips = await fetchTrips()
    } catch (e: any) {
      error = e.message
    }
  }

  async function handleCreate() {
    if (!newName.trim()) return
    error = ''
    try {
      await createTrip({
        name: newName.trim(),
        description: newDescription.trim() || null,
      })
      newName = ''
      newDescription = ''
      await loadTrips()
    } catch (e: any) {
      error = e.message
    }
  }

  async function handleDelete(id: string) {
    error = ''
    try {
      await deleteTrip(id)
      await loadTrips()
    } catch (e: any) {
      error = e.message
    }
  }
</script>

<h2>Trips</h2>

{#if error}
  <p class="error">{error}</p>
{/if}

<div class="create-form">
  <h3>Create Trip</h3>
  <div class="form-row">
    <input
      type="text"
      placeholder="Trip name"
      bind:value={newName}
      onkeydown={(e: KeyboardEvent) => e.key === 'Enter' && handleCreate()}
    />
    <input
      type="text"
      placeholder="Description (optional)"
      bind:value={newDescription}
      onkeydown={(e: KeyboardEvent) => e.key === 'Enter' && handleCreate()}
    />
    <button onclick={handleCreate}>Create</button>
  </div>
</div>

<div class="trip-list">
  <h3>All Trips ({trips.length})</h3>
  {#if trips.length === 0}
    <p>No trips yet. Create one above.</p>
  {:else}
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Description</th>
          <th>Start Date</th>
          <th>End Date</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {#each trips as trip (trip.id)}
          <tr>
            <td>{trip.name}</td>
            <td>{trip.description ?? ''}</td>
            <td>{trip.start_date ?? '-'}</td>
            <td>{trip.end_date ?? '-'}</td>
            <td><button class="btn-delete" onclick={() => handleDelete(trip.id)}>Delete</button></td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>

<style>
  .create-form {
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: #f0f7ff;
    border-radius: 8px;
  }

  .form-row {
    display: flex;
    gap: 0.5rem;
  }

  .form-row input {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 0.9rem;
  }

  .form-row button {
    padding: 0.5rem 1rem;
    background: #4a90d9;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 0.5rem;
  }

  th, td {
    text-align: left;
    padding: 0.5rem;
    border-bottom: 1px solid #eee;
  }

  th {
    font-weight: 600;
    color: #555;
  }

  .btn-delete {
    padding: 0.25rem 0.75rem;
    background: #e53935;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .error {
    color: #e53935;
    padding: 0.5rem;
    background: #ffebee;
    border-radius: 4px;
  }

  h3 {
    margin-top: 0;
  }
</style>
