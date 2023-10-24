<template>
  <div class="title">Фильтры</div>
  <div class="filter-component">
    <div class="sport-choice">
      <el-select
        v-model="sport"

        collapse-tags
        collapse-tags-tooltip
        :max-collapse-tags="3"
        placeholder="Выберите спорт"
        style="width: 200px"
        @change="sportChanged()"
      >
        <el-option
          v-for="type in types"
          :key="type[0]"
          :label="type[1]"
          :value="type[0]"
        />
      </el-select>
<!--      multiple-->

      <el-checkbox v-model="allSport" label="All sports" size="large" @change="allSportChecked()" />
    </div>

    <div v-if="this.currentMode === 0" class="status-choice">
      <div class="filter-mode"
           :class="{'enabled': this.filterMode === 1, 'disabled-button': this.isButtonsDisabled()}"
           @click="filterMode = 1"
      >
        &#10003; Сматченные
      </div>
      <div class="filter-mode"
           :class="{'enabled': this.filterMode === 2, 'disabled-button': this.isButtonsDisabled()}"
           @click="filterMode = 2"
      >
        &#10005; Не сматченные
      </div>
      <div class="filter-mode"
           :class="{'enabled': this.filterMode === 3, 'disabled-button': this.isButtonsDisabled()}"
           @click="filterMode = 3"
      >
        &#10003; &#10005; Все
      </div>
    </div>

  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "FiltersComponent",
  props: [
    'currentMode',
    'modeFilter',
    'sportTypes',
    'isTaskSelected',
    'sportFilterSetting'
  ],
  emits: [
    'sportFilterChange',
    'modeFilterChange',
  ],
  data(){
    return{
      // current_mode: this.mode,
      types: [],
      sport: null,
      allSport: true,
      filterMode: 0,
    }
  },
  methods: {
    allSportChecked(){
      if(this.allSport){
        this.sport = null
        let filter = {'allSport': this.allSport, 'sport': null}
        this.$emit('sportFilterChange', filter);
      } else {
        this.allSport = true
      }
    },

    sportChanged(){
      this.allSport = false
      let filter = {'allSport': this.allSport, 'sport': this.sport}
      this.$emit('sportFilterChange', filter);
    },

    isButtonsDisabled(){
      return !this.isTaskSelected
    }
  },
  watch: {
    filterMode(newVal) {
      this.$emit('modeFilterChange', newVal)
    },

    modeFilter(newVal){
      this.filterMode = newVal
    },

    sportTypes(newVal){
      this.types = newVal
    },

    sportFilterSetting(newVal){
      this.allSport = newVal['allSport']
      this.sport = newVal['sport']
    }
  }
}
</script>

<style scoped>
.title {
  padding-top: 10px;
  text-align: center;
  font-weight: bold;
  font-size: 18px;
  flex-basis: 35%;
  height: 35%;
}
.filter-component {
  padding: 10px;
  display: flex;
  gap: 10px;
  flex-basis: 65%;
  height: 65%;
}
.sport-choice{
  padding: 10px 20px;
  border: 1px solid var(--color-text);
  display: flex;
  gap: 20px;
  align-items: center
}

.el-checkbox{
  color: var(--color-text)!important;
}
.status-choice{
  padding: 10px 20px;
  border: 1px solid var(--color-text);
  display: flex;
  justify-content: space-between;
  align-items: center;
  /*gap: 20px;*/
  width: 100%;
}
.filter-mode{
  border: 1px solid var(--color-text);
  padding: 5px;
  cursor: pointer;
  transition: all 0.1s ease-in-out;
  font-size: 12px;
}
.filter-mode:hover{
  background-color: var(--color-text);
  color: var(--color-background);
  border: 1px solid var(--color-background);
}

</style>