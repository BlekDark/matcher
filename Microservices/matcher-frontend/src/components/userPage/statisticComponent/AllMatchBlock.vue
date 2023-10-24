<template>

  <div class="tools-block"
    :class="{'tools-block-fullscreen': this.fullscreen}"
  >
    <div v-if="sportFilter.allSport" class="sport-container">
      <div v-for="run in this.runs" >
        <div v-if="run.mismatched" class="sport-title">
          {{ sportName(run.sport_id) }}
        </div>

        <div v-if="run.mismatched[Object.keys(run.mismatched)[0]].length > 0 && run.mismatched[Object.keys(run.mismatched)[1]].length > 0 || run.results.length > 0">
          <div v-if="run.mismatched">
            <div class="result-item" v-if="run.mismatched[Object.keys(run.mismatched)[0]].length > 0 && run.mismatched[Object.keys(run.mismatched)[1]].length > 0">
              <div v-if="run.mismatched[Object.keys(run.mismatched)[0]] && run.mismatched[Object.keys(run.mismatched)[0]].length > 0"
                  class="left-list">
                <div v-for="item in run.mismatched[Object.keys(run.mismatched)[0]]"
                    :key="item.bk_event_id"
                    class="list-item">
                  {{ item.event_name }}
                </div>
              </div>
              <div v-else class="left-list" style="padding: 20px 30px;">По данному вида спорта у источника нет несматченных пар</div>

              <div v-if="run.mismatched[Object.keys(run.mismatched)[1]] && run.mismatched[Object.keys(run.mismatched)[1]].length > 0"
                  class="right-list">
                <div v-for="item in run.mismatched[Object.keys(run.mismatched)[1]]"
                    :key="item.bk_event_id"
                    class="list-item">
                  {{ item.event_name }}
                </div>
              </div>
              <div v-else class="right-list" style="padding: 20px 30px;">По данному вида спорта у источника нет несматченных пар</div>
            </div>
            <div v-else style="text-align: center; margin-bottom: 40px">По данному вида спорта у источников нет несматченных пар</div>
          </div>

          <div v-if="run.results.length > 0" v-for="result in run.results">
            <div class="field-items">
              <div class="field-item">

                <div class="fields">
                  <div class="field">
                    {{ result.event1.event_name }}
                  </div>
                  <div class="field">
                    {{ result.event2.event_name }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else style="text-align: center; margin-bottom: 40px">По данному вида спорта у источников нет сматченных пар</div>
        </div>
        <div v-else style="text-align: center; margin-bottom: 40px">По данному вида спорта у источников нет сматченных или несматченных пар</div>
      </div>
    </div>

    <div v-else class="sport-container">
      <div v-for="run in this.runs" >
        <div v-if="sportFilter.sport === run.sport_id" >
          <div class="sport-title">
            {{ sportName(run.sport_id) }}
          </div>

          <div v-if="run.mismatched[Object.keys(run.mismatched)[0]].length > 0 && run.mismatched[Object.keys(run.mismatched)[1]].length > 0 || run.results.length > 0">
            <div v-if="run.mismatched" >
              <div class="result-item" v-if="run.mismatched[Object.keys(run.mismatched)[0]].length > 0 && run.mismatched[Object.keys(run.mismatched)[1]].length > 0">
                <div v-if="run.mismatched[Object.keys(run.mismatched)[0]] && run.mismatched[Object.keys(run.mismatched)[0]].length > 0"
                    class="left-list">
                  <div v-for="item in run.mismatched[Object.keys(run.mismatched)[0]]"
                      :key="item.bk_event_id"
                      class="list-item">
                    {{ item.event_name }}
                  </div>
                </div>
                <div v-else class="left-list" style="padding: 20px 30px;">По данному вида спорта у источника нет несматченных пар</div>

                <div v-if="run.mismatched[Object.keys(run.mismatched)[1]] && run.mismatched[Object.keys(run.mismatched)[1]].length > 0"
                    class="right-list">
                  <div v-for="item in run.mismatched[Object.keys(run.mismatched)[1]]"
                      :key="item.bk_event_id"
                      class="list-item">
                    {{ item.event_name }}
                  </div>
                </div>
                <div v-else class="right-list" style="padding: 20px 30px;">По данному вида спорта у источника нет несматченных пар</div>
              </div>
              <div v-else style="text-align: center; margin-bottom: 40px">По данному вида спорта у источников нет несматченных пар</div>
            </div>

            <div v-if="run.results.length > 0" v-for="result in run.results">
          <div class="field-items">
            <div class="field-item">

              <div class="fields">
                <div class="field">
                  {{ result.event1.event_name }}
                </div>
                <div class="field">
                  {{ result.event2.event_name }}
                </div>
              </div>
            </div>
          </div>
        </div>
            <div v-else style="text-align: center; margin-bottom: 40px">По данному вида спорта у источников нет сматченных пар</div>
          </div>
          <div v-else style="text-align: center; margin-bottom: 40px">По данному вида спорта у источников нет сматченных или несматченных пар</div>
        </div>
      </div>
    </div>
  </div>

  <div class="tool-buttons">
    <div class="controls"></div>
    <div
        v-if="!fullscreen"
        class="default-button"
        @click="fullscreenButtonClick()"
    >
      Развернуть на весь экран
    </div>
    <div
        v-else
        class="default-button"
        @click="fullscreenButtonClick()">
      Свернуть
    </div>
  </div>
</template>

<script>
export default {
  name: "AllMatchBlock",
  props: [
    'selectedTask',
    'modeFilter',
    'sportFilter',
    'sportTypesAll',
    'fullscreen',
  ],
  emits: [
    "fullscreenButtonCLick",
  ],
  data(){
    return {
      runs: [],
    }
  },
  methods: {
    sportName(sport_id){
      return this.sportTypesAll.find(subarr => subarr[0] === sport_id)[1]
    },

    fullscreenButtonClick(){
      this.$emit('fullscreenButtonCLick')
    },
  },
  watch: {
    selectedTask:{
      immediate: true,
      handler (newVal) {
        this.runs = newVal.runs
        // console.log(newVal.runs)
        // this.runs.forEach(run => {
        //   let keys = Object.keys(run.mismatched)
        //   if(keys[0] === 'null'){
        //     delete run['mismatched']
        //   }
        //
        // })
      }
    }
  }
}
</script>

<style scoped>
.sport-container {
  width: 100%;
  max-width: 80rem;
}

.sport-title{
  text-align: center;
  margin: 20px 0 ;
  font-weight: bold;
  font-size: 18px;
}

.result-item{
  display: flex;
  flex-direction: row;
  margin-bottom: 20px;
}

.left-list, .right-list{
  width: 50%;
  flex-basis: 50%;
  text-align: center;
}


.list-item{
  padding: 20px 30px;
  border: 1px solid var(--color-text);
  background-color: var(--el-color-danger);
  color: var(--color-background);
  height: 6rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.1s ease-in-out;
}

.field-items {
    width: 100%;
}

.fields {
  display: flex;
  flex-direction: row;
  width: 100%;
}

.field {
  width: 50%;
  flex-basis: 50%;
  padding: 20px 30px;
  border: 1px solid var(--color-text);
  background-color: var(--el-color-success);
  color: var(--color-background);
  height: 6rem;
  display: flex;
  text-align: center;
  align-items: center;
  justify-content: center;
  transition: all 0.1s ease-in-out;
}

.tool-buttons {
  padding: 20px 30px;
  display: flex;
  bottom: 0;
  width: 100%;
  justify-content: space-between;
}
</style>