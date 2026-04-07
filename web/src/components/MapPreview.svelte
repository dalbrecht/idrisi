<script lang="ts">
  import { onMount } from 'svelte'
  import L from 'leaflet'
  import 'leaflet/dist/leaflet.css'
  import type { Place } from '../lib/api'

  // Fix default marker icons in bundled Leaflet
  import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
  import markerIcon from 'leaflet/dist/images/marker-icon.png'
  import markerShadow from 'leaflet/dist/images/marker-shadow.png'

  // @ts-ignore - override default icon
  delete (L.Icon.Default.prototype as any)._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: markerIcon2x,
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
  })

  interface Props {
    places?: Place[]
    center?: [number, number]
    zoom?: number
  }

  let { places = [], center = [30, 0], zoom = 2 }: Props = $props()

  let mapContainer: HTMLDivElement
  let map: L.Map | undefined
  let markerLayer: L.LayerGroup | undefined

  onMount(() => {
    map = L.map(mapContainer).setView(center, zoom)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map)
    markerLayer = L.layerGroup().addTo(map)

    return () => {
      map?.remove()
    }
  })

  $effect(() => {
    if (!markerLayer || !map) return
    markerLayer.clearLayers()
    for (const place of places) {
      L.marker([place.lat, place.lon])
        .bindPopup(`<b>${place.name}</b>${place.country ? '<br>' + place.country : ''}`)
        .addTo(markerLayer)
    }
    if (places.length > 0) {
      const bounds = L.latLngBounds(places.map(p => [p.lat, p.lon] as [number, number]))
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 })
    }
  })
</script>

<div class="map-container" bind:this={mapContainer}></div>

<style>
  .map-container {
    width: 100%;
    height: 400px;
    border-radius: 8px;
    border: 1px solid #ddd;
  }
</style>
