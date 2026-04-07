<script lang="ts">
  import { onMount } from 'svelte'
  import MapPreview from '../components/MapPreview.svelte'
  import { fetchPlaces, searchPlaces, createPlace, deletePlace } from '../lib/api'
  import type { Place } from '../lib/api'

  let places: Place[] = $state([])
  let searchQuery: string = $state('')
  let searchResults: Place[] = $state([])
  let error: string = $state('')

  onMount(async () => {
    await loadPlaces()
  })

  async function loadPlaces() {
    try {
      places = await fetchPlaces()
    } catch (e: any) {
      error = e.message
    }
  }

  async function handleSearch() {
    if (!searchQuery.trim()) return
    error = ''
    try {
      searchResults = await searchPlaces(searchQuery)
    } catch (e: any) {
      error = e.message
    }
  }

  async function handleAdd(result: Place) {
    error = ''
    try {
      await createPlace({
        name: result.name,
        lat: result.lat,
        lon: result.lon,
        source: result.source || 'search',
        country: result.country,
        admin1: result.admin1,
        category: result.category,
        notes: result.notes,
      })
      searchResults = searchResults.filter(r => r.id !== result.id)
      await loadPlaces()
    } catch (e: any) {
      error = e.message
    }
  }

  async function handleDelete(id: string) {
    error = ''
    try {
      await deletePlace(id)
      await loadPlaces()
    } catch (e: any) {
      error = e.message
    }
  }
</script>

<h2>Places</h2>

{#if error}
  <p class="error">{error}</p>
{/if}

<div class="search-bar">
  <input
    type="text"
    placeholder="Search for a place..."
    bind:value={searchQuery}
    onkeydown={(e: KeyboardEvent) => e.key === 'Enter' && handleSearch()}
  />
  <button onclick={handleSearch}>Search</button>
</div>

{#if searchResults.length > 0}
  <div class="search-results">
    <h3>Search Results</h3>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Country</th>
          <th>Lat</th>
          <th>Lon</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {#each searchResults as result (result.id)}
          <tr>
            <td>{result.name}</td>
            <td>{result.country ?? ''}</td>
            <td>{result.lat.toFixed(4)}</td>
            <td>{result.lon.toFixed(4)}</td>
            <td><button class="btn-add" onclick={() => handleAdd(result)}>Add</button></td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}

{#if places.length > 0}
  <MapPreview places={places} />
{/if}

<div class="saved-places">
  <h3>Saved Places ({places.length})</h3>
  {#if places.length === 0}
    <p>No places saved yet. Use the search bar above to find and add places.</p>
  {:else}
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Country</th>
          <th>Category</th>
          <th>Lat</th>
          <th>Lon</th>
          <th>Source</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {#each places as place (place.id)}
          <tr>
            <td>{place.name}</td>
            <td>{place.country ?? ''}</td>
            <td>{place.category ?? ''}</td>
            <td>{place.lat.toFixed(4)}</td>
            <td>{place.lon.toFixed(4)}</td>
            <td>{place.source}</td>
            <td><button class="btn-delete" onclick={() => handleDelete(place.id)}>Delete</button></td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>

<style>
  .search-bar {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .search-bar input {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 0.9rem;
  }

  .search-bar button {
    padding: 0.5rem 1rem;
    background: #4a90d9;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .search-results {
    margin-bottom: 1rem;
    padding: 1rem;
    background: #f0f7ff;
    border-radius: 8px;
  }

  .saved-places {
    margin-top: 1rem;
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

  .btn-add {
    padding: 0.25rem 0.75rem;
    background: #4caf50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
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
