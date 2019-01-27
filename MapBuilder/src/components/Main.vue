<template>
  <v-app id="mapbuilder">
    <v-navigation-drawer
      :clipped="$vuetify.breakpoint.lgAndUp"
      v-model="drawer"
      fixed
      app
    >
      <v-text-field
        flat
        solo-inverted
        hide-details
        prepend-inner-icon="search"
        label="Find Place"
        @keyup.enter="find_places"
        v-model="search_term"
        placeholder="where?"></v-text-field>
      <template v-if="search_results">
        <v-list two-line>
          <template v-for="(item, index) in search_results">
            <v-list-tile
              :key="item.geoname_id"
              ripple
              @click="add_to_map(item)"
            >
              <v-list-tile-content>
                <v-list-tile-title>{{ item.name }}, {{ item.admin1_code }}</v-list-tile-title>
                <v-list-tile-sub-title>{{ item.latitude }},{{ item.longitude}}</v-list-tile-sub-title>
              </v-list-tile-content>

              <v-list-tile-action>

                <v-icon
                  color="red darken-2"
                >
                  place
                </v-icon>
                <v-list-tile-action-text>Add To Map</v-list-tile-action-text>

              </v-list-tile-action>

            </v-list-tile>
            <v-divider
              v-if="index + 1 < search_results.length"
              :key="index"
            ></v-divider>
          </template>
        </v-list>
      </template>
    </v-navigation-drawer>
    <v-toolbar
      :clipped-left="$vuetify.breakpoint.lgAndUp"
      color="grey darken-3"
      dark
      app
      fixed
    >
      <v-toolbar-title style="width: 300px" class="ml-0 pl-3">
        <v-toolbar-side-icon @click.stop="drawer = !drawer"></v-toolbar-side-icon>
        <span class="hidden-sm-and-down">MapBuilder</span>
      </v-toolbar-title>

      <v-spacer></v-spacer>
    </v-toolbar>
    <v-content>
      <v-container fluid fill-height child flex-1>
            <v-data-table
              :headers="headers"
              :items="places"
              class="fill-height fluid"
              fill-height
              fluid
            >
              <template slot="items" slot-scope="props">
                <td>{{ props.item.name }}</td>
                <td class="text-xs-right">{{ props.item.latitude }}</td>
                <td class="text-xs-right">{{ props.item.longitude }}</td>
                <td class="text-xs-right">{{ props.item.admin1_code }}</td>
                <td class="text-xs-right">{{ props.item.geoname_id }}</td>
              </template>
                  <template slot="no-data">
      <v-alert :value="true" color="warning" icon="warning">
        No Places Added, use the tools to the left to add places
      </v-alert>
    </template>
            </v-data-table>
      </v-container>
    </v-content>
    <v-btn
      fab
      bottom
      right
      color="pink"
      dark
      fixed
      @click="dialog = !dialog"
    >
      <v-icon>add</v-icon>
    </v-btn>
    <v-dialog v-model="dialog" width="800px">
      <v-card>
        <v-card-title
          class="grey lighten-4 py-4 title"
        >
          Create contact
        </v-card-title>
        <v-container grid-list-sm class="pa-4">
          <v-layout row wrap>
            <v-flex xs12 align-center justify-space-between>
              <v-layout align-center>
                <v-avatar size="40px" class="mr-3">
                  <img
                    src="//ssl.gstatic.com/s2/oz/images/sge/grey_silhouette.png"
                    alt=""
                  >
                </v-avatar>
                <v-text-field
                  placeholder="Name"
                ></v-text-field>
              </v-layout>
            </v-flex>
            <v-flex xs6>
              <v-text-field
                prepend-icon="business"
                placeholder="Company"
              ></v-text-field>
            </v-flex>
            <v-flex xs6>
              <v-text-field
                placeholder="Job title"
              ></v-text-field>
            </v-flex>
            <v-flex xs12>
              <v-text-field
                prepend-icon="mail"
                placeholder="Email"
              ></v-text-field>
            </v-flex>
            <v-flex xs12>
              <v-text-field
                type="tel"
                prepend-icon="phone"
                placeholder="(000) 000 - 0000"
                mask="phone"
              ></v-text-field>
            </v-flex>
            <v-flex xs12>
              <v-text-field
                prepend-icon="notes"
                placeholder="Notes"
              ></v-text-field>
            </v-flex>
          </v-layout>
        </v-container>
        <v-card-actions>
          <v-btn flat color="primary">More</v-btn>
          <v-spacer></v-spacer>
          <v-btn flat color="primary" @click="dialog = false">Cancel</v-btn>
          <v-btn flat @click="dialog = false">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<script>

import axios from 'axios'

export default {
  data: () => ({
    headers: [
      {text: 'Place', value: 'name'},
      {text: 'Latitude', value: 'latitude'},
      {text: 'Longitude', value: 'longitude'},
      {text: 'country', value: 'Country'},
      {text: 'gid', value: 'gid'}
    ],
    dialog: false,
    drawer: null,
    search_term: '',
    search_results: [
      {
        'geoname_id': 2615876,
        'name': 'Odense',
        'latitude': 55.39594,
        'longitude': 10.38831,
        'admin1_code': 'DK'
      },
      {
        'geoname_id': 4276573,
        'name': 'Odense',
        'latitude': 37.7031,
        'longitude': -95.25192,
        'admin1_code': 'US'
      }
    ],
    places: []
  }),
  props: {
    source: String
  },
  methods: {
    add_to_map: function (item) {
      this.places.push(item)
      axios.post('http://localhost:5000/projects/1/places/',
        {'geoname_id': item.geoname_id},
        {
          headers: {
            'Content-Type': 'application/json'
          }
        })
        .then(response => {
        }).catch(e => {
          this.errors.push(e)
        })
    },
    find_places: function (event) {
      axios.get('http://localhost:5000/lookup/' + this.search_term)
        .then(response => {
          // JSON responses are automatically parsed.
          this.search_results = response.data
        })
        .catch(e => {
          this.errors.push(e)
        })
    }
  },

  created () {
    axios.get('http://localhost:5000/projects/1')
      .then(response => {
        // JSON responses are automatically parsed.
        this.places = response.data
      })
      .catch(e => {
        this.errors.push(e)
      })
  }
}
</script>
