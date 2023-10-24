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
      <JEStatisticComponent
          :taskIsLoading="this.taskIsLoading"
          :selectedTask="this.selectedTask"
          :pairSettings="this.pairSettings"
          :sportFilter="this.sportFilterSettings"
          :sportTypesAll="this.sportTypesAll"
          :fullscreen="this.fullscreen"
          @fullscreenButtonCLick="FullscreenOn"
      />
    </div>
  </div>
</template>

<script>
import FiltersComponent from "@/components/FiltersComponent.vue";
import JEStatisticComponent from "@/components/observerPage/jsonEditor/JEStatisticComponent.vue";

export default {
  name: "JsonEditor",
  props: [
    'selectedTask',
    'receivedData',
    'sportTypesAll',
    'sportTypes',
    'taskIsLoading',
  ],
  components: {
    FiltersComponent,
    JEStatisticComponent,
  },
  data(){
    return{
      currentMode: 3,
      sportFilterSettings: {'allSport': true, 'sport': null},
      fullscreen: false,
      pairSettings: this.receivedData,
    }
  },
  methods: {
    changeSportFilterSettings(item){
      this.sportFilterSettings = item
    },

    FullscreenOn(){
      this.fullscreen = !this.fullscreen
    },
  },

  watch: {
    receivedData(newVal) {
      this.pairSettings = newVal;
    },
  }
}
</script>

<style scoped>

.results-block {
  max-height: 100%;
  height: 100%;
}

.filters-block {
  height: 15%;
  flex-basis: 15%;
  display: flex;
  flex-direction: column;
}

.statistic-block{
  height: 83%;
  flex-basis: 83%;

  display: flex;
  flex-direction: column;
}

.statistic-fullscreen{
  height: 100%;
  flex-basis: 100%;
}
</style>