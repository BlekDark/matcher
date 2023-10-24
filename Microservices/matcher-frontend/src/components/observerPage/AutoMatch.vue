<template>
  <div class="results-block">
    <div class="filters-block">
      <FiltersComponent :currentMode="this.currentMode"/>
    </div>

    <div class="statistic-block">
      <StatisticComponent/>
    </div>
  </div>
</template>

<script>
import FiltersComponent from "@/components/FiltersComponent.vue";
import StatisticComponent from "@/components/StatisticComponent.vue";

export default {
  name: "AutoMatch",
  components: {
    FiltersComponent,
    StatisticComponent,
  },
  data(){
    return{
      currentMode: 1,
    }
  }
}
</script>

<style scoped>
.filters-block {
  height: 24%;
}
</style>