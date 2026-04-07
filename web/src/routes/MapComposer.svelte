<script lang="ts">
  import { onMount } from 'svelte'
  import { fetchProjects, createProject, deleteProject, triggerRender } from '../lib/api'
  import type { Project } from '../lib/api'

  let projects: Project[] = $state([])
  let newName: string = $state('')
  let newDescription: string = $state('')
  let newMapType: string = $state('travel')
  let error: string = $state('')
  let renderingId: string | null = $state(null)

  const mapTypes = ['travel', 'region', 'route']

  onMount(async () => {
    await loadProjects()
  })

  async function loadProjects() {
    try {
      projects = await fetchProjects()
    } catch (e: any) {
      error = e.message
    }
  }

  async function handleCreate() {
    if (!newName.trim()) return
    error = ''
    try {
      await createProject({
        name: newName.trim(),
        map_type: newMapType,
        description: newDescription.trim() || null,
      })
      newName = ''
      newDescription = ''
      newMapType = 'travel'
      await loadProjects()
    } catch (e: any) {
      error = e.message
    }
  }

  async function handleDelete(id: string) {
    error = ''
    try {
      await deleteProject(id)
      await loadProjects()
    } catch (e: any) {
      error = e.message
    }
  }

  async function handleRender(project: Project) {
    error = ''
    renderingId = project.id
    try {
      const blob = await triggerRender(project.id)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${project.name}.png`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (e: any) {
      error = e.message
    } finally {
      renderingId = null
    }
  }
</script>

<h2>Map Composer</h2>

{#if error}
  <p class="error">{error}</p>
{/if}

<div class="create-form">
  <h3>Create Project</h3>
  <div class="form-row">
    <input
      type="text"
      placeholder="Project name"
      bind:value={newName}
    />
    <input
      type="text"
      placeholder="Description (optional)"
      bind:value={newDescription}
    />
    <select bind:value={newMapType}>
      {#each mapTypes as mt}
        <option value={mt}>{mt}</option>
      {/each}
    </select>
    <button onclick={handleCreate}>Create</button>
  </div>
</div>

<div class="project-list">
  <h3>All Projects ({projects.length})</h3>
  {#if projects.length === 0}
    <p>No projects yet. Create one above.</p>
  {:else}
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Description</th>
          <th>Map Type</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {#each projects as project (project.id)}
          <tr>
            <td>{project.name}</td>
            <td>{project.description ?? ''}</td>
            <td>{project.map_type}</td>
            <td class="actions">
              <button
                class="btn-render"
                onclick={() => handleRender(project)}
                disabled={renderingId === project.id}
              >
                {renderingId === project.id ? 'Rendering...' : 'Render'}
              </button>
              <button class="btn-delete" onclick={() => handleDelete(project.id)}>Delete</button>
            </td>
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

  .form-row select {
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

  .actions {
    display: flex;
    gap: 0.5rem;
  }

  .btn-render {
    padding: 0.25rem 0.75rem;
    background: #4caf50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .btn-render:disabled {
    background: #999;
    cursor: not-allowed;
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
