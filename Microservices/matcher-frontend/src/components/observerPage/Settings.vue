<template>
  <div class="results-block"
       :class="{'results-fullscreen': this.fullscreen}">
    <div class="filters-block"
         :class="{'removed': this.fullscreen}">
      <FiltersComponent
          :currentMode="this.currentMode"
          :sportTypes="this.sportTypes"
          :sportFilterSetting="this.sportFilterSettings"
          @sportFilterChange="changeSportFilterSettings"
      />
    </div>

    <div class="statistic-block"
         :class="{'statistic-fullscreen': this.fullscreen}">
      <SettingsComponent
          :generalSettings="this.generalSettings"
          :pairSettings="this.pairSettings"
          :sportFilterSettings="this.sportFilterSettings"
          :sportTypesDef="this.sportTypesDef"
          :sportTypes="this.sportTypes"
          :sportTypesAll="this.sportTypesAll"
          :fullscreen="this.fullscreen"
          @fullscreenButtonCLick="FullscreenOn"
          @newSportTypes="newSportTypes"
          @restartSportFilter="restartSportFilter"
      />
    </div>
  </div>
</template>

<script>
import FiltersComponent from "@/components/FiltersComponent.vue";
import StatisticComponent from "@/components/StatisticComponent.vue";
import SettingsComponent from "@/components/observerPage/Settings/SettingsComponent.vue";
import axios from "axios";
import { ElNotification } from 'element-plus';

export default {
  name: "Settings",
  props: [
    'receivedData',
    'sportTypesAll',
  ],
  components: {
    SettingsComponent,
    FiltersComponent,
    StatisticComponent,
  },
  data(){
    return{
      currentMode: 4,
      sportFilterSettings: {'allSport': true, 'sport': null},
      fullscreen: false,
      generalSettings: {},
      pairSettings: this.receivedData,
      sportTypes: [],
      sportTypesDef: [],
      // sportSettings : [],
    }
  },
  beforeMount() {
    this.getGeneralSettings()
  },

  methods: {
    async getGeneralSettings(){
      await axios
          .get('config/?default=true')
          .then(response => {
            this.generalSettings = response.data.result
          })
          .catch(error => {
            console.log(error)
            ElNotification({
                title: 'Ошибка!',
                message: `Произошла ошибка при запросе основных параметров системы`,
                type: 'error',
                duration: 7500,
            })
          })
    },

    FullscreenOn(){
      this.fullscreen = !this.fullscreen
    },
    changeSportFilterSettings(item){
      this.sportFilterSettings = item
      // console.log(this.sportFilterSettings)
    },

    newSportTypes(newVal){
      this.sportTypes = newVal
    },

    restartSportFilter() {
      this.sportFilterSettings = {'allSport': true, 'sport': null}
    }

  },

  watch: {
    receivedData(newVal) {
      this.pairSettings = newVal;

      let tempArr = []
      for (const [key, value] of Object.entries(newVal['types'])) {
        for (const subarr of this.sportTypesAll) {
          if (subarr[0] === parseInt(key)) {
              tempArr.push([parseInt(key), subarr[1]]);
          }
        }
      }
      this.sportTypes = tempArr
      this.sportTypesDef = tempArr
      // console.log(this.sportTypes)
      // console.log(this.pairSettings)
    },
  },
}
</script>

<style scoped>
.filters-block {
  height: 15%;
  flex-basis: 15%;
  display: flex;
  flex-direction: column;
}

.statistic-block{
  display: flex;
  flex-direction: column;
}

.results-block {
  width: 71%;
  flex-basis: 71%;
}
</style>