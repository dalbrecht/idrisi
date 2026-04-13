// API client for the Idrisi backend

export interface Place {
  id: string
  name: string
  lat: number
  lon: number
  country: string | null
  admin1: string | null
  category: string | null
  notes: string | null
  source: string
}

export interface PlaceCreate {
  name: string
  lat: number
  lon: number
  source: string
  country?: string | null
  admin1?: string | null
  category?: string | null
  notes?: string | null
}

export interface Trip {
  id: string
  name: string
  description: string | null
  start_date: string | null
  end_date: string | null
}

export interface TripCreate {
  name: string
  description?: string | null
}

export interface Project {
  id: string
  name: string
  description: string | null
  map_type: string
}

export interface ProjectCreate {
  name: string
  map_type: string
  description?: string | null
}

export interface Region {
  id: string
  name: string
  region_type: string
  region_code: string | null
}

const BASE = '/api'

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API error ${res.status}: ${text}`)
  }
  return res.json()
}

// Places
export async function fetchPlaces(): Promise<Place[]> {
  return json<Place[]>(await fetch(`${BASE}/places`))
}

export async function searchPlaces(query: string): Promise<Place[]> {
  return json<Place[]>(await fetch(`${BASE}/places/search?q=${encodeURIComponent(query)}`))
}

export async function createPlace(place: PlaceCreate): Promise<Place> {
  return json<Place>(await fetch(`${BASE}/places`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(place),
  }))
}

export async function deletePlace(id: string): Promise<void> {
  const res = await fetch(`${BASE}/places/${id}`, { method: 'DELETE' })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API error ${res.status}: ${text}`)
  }
}

// Trips
export async function fetchTrips(): Promise<Trip[]> {
  return json<Trip[]>(await fetch(`${BASE}/trips`))
}

export async function createTrip(trip: TripCreate): Promise<Trip> {
  return json<Trip>(await fetch(`${BASE}/trips`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(trip),
  }))
}

export async function deleteTrip(id: string): Promise<void> {
  const res = await fetch(`${BASE}/trips/${id}`, { method: 'DELETE' })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API error ${res.status}: ${text}`)
  }
}

// Projects
export async function fetchProjects(): Promise<Project[]> {
  return json<Project[]>(await fetch(`${BASE}/projects`))
}

export async function createProject(project: ProjectCreate): Promise<Project> {
  return json<Project>(await fetch(`${BASE}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(project),
  }))
}

export async function deleteProject(id: string): Promise<void> {
  const res = await fetch(`${BASE}/projects/${id}`, { method: 'DELETE' })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API error ${res.status}: ${text}`)
  }
}

// Regions
export async function fetchRegions(): Promise<Region[]> {
  return json<Region[]>(await fetch(`${BASE}/regions`))
}

// Render
export async function triggerRender(projectId: string): Promise<Blob> {
  const res = await fetch(`${BASE}/render/${projectId}`, { method: 'POST' })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Render error ${res.status}: ${text}`)
  }
  return res.blob()
}
