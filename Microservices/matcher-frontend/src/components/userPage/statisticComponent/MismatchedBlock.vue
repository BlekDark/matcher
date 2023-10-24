<template>
  <div class="tools-block"
    :class="{'tools-block-fullscreen': this.fullscreen}"
  >
    <div v-if="sportFilter.allSport" class="sport-container">
      <div v-for="run in this.runs" >
        <div v-if="run.mismatched" class="sport-title">
          {{ sportName(run.sport_id) }}
        </div>

        <div v-if="this.matched[run.run_id]" class="matched">
          <div v-for="match in this.matched[run.run_id]" class="match-items">
            <div class="match-item">
              {{ getEventName(match.event1) }}
            </div>

            <div class="remove-link" @click="removeLink(run.run_id, match)"></div>

            <div class="match-item">
              {{ getEventName(match.event2) }}
            </div>

          </div>

        </div>

        <div v-if="run.mismatched" >
          <div class="result-item" v-if="run.mismatched[Object.keys(run.mismatched)[0]].length > 0 && run.mismatched[Object.keys(run.mismatched)[1]].length > 0">
            <div v-if="run.mismatched[Object.keys(run.mismatched)[0]] && run.mismatched[Object.keys(run.mismatched)[0]].length > 0"
                class="left-list">
              <div v-for="item in this.filteredLeft(run)"
                  :key="item.bk_event_id"
                  class="list-item"
                  :id="`item${item.bk_event_id}`"
                  :class="{ selected: isSelected(item) }"
                  @click="selectLeft(item, run.run_id)">
                {{ item.event_name }}
              </div>
            </div>
            <div v-else class="left-list" style="padding: 20px 30px;">По данному вида спорта у источника нет несматченных пар</div>

            <div class="center-space"></div>

            <div v-if="run.mismatched[Object.keys(run.mismatched)[1]] && run.mismatched[Object.keys(run.mismatched)[1]].length > 0"
                class="right-list">
              <div v-for="item in this.filteredRight(run)"
                  :key="item.bk_event_id"
                  class="list-item"
                  :id="`item${item.bk_event_id}`"
                  :class="{ selected: isSelected(item) }"
                  @click="selectRight(item, run.run_id)">
                {{ item.event_name }}
              </div>
            </div>
            <div v-else class="right-list" style="padding: 20px 30px;">По данному вида спорта у источника нет несматченных пар</div>
          </div>
          <div v-else style="text-align: center; margin-bottom: 40px">По данному вида спорта у источников нет несматченных пар</div>
        </div>
<!--        <div v-else style="text-align: center; margin-bottom: 30px">По данному вида спорта у источников нет несматченных пар</div>-->
      </div>
    </div>

    <div v-else class="sport-container">
      <div v-for="run in this.runs" >
        <div v-if="sportFilter.sport === run.sport_id" >
          <div class="sport-title">
            {{ sportName(run.sport_id) }}
          </div>

          <div v-if="this.matched[run.run_id]" class="matched">
            <div v-for="match in this.matched[run.run_id]" class="match-items">
              <div class="match-item">
                {{ getEventName(match.event1) }}
              </div>

              <div class="remove-link" @click="removeLink(run.run_id, match)"></div>

              <div class="match-item">
                {{ getEventName(match.event2) }}
              </div>
            </div>

          </div>

          <div v-if="run.mismatched">
            <div class="result-item" v-if="run.mismatched[Object.keys(run.mismatched)[0]].length > 0 && run.mismatched[Object.keys(run.mismatched)[1]].length > 0">
              <div v-if="run.mismatched[Object.keys(run.mismatched)[0]] && run.mismatched[Object.keys(run.mismatched)[0]].length > 0"
                  class="left-list">
                <div v-for="item in this.filteredLeft(run)"
                    :key="item.bk_event_id"
                    class="list-item"
                    :id="`item${item.bk_event_id}`"
                    :class="{ selected: isSelected(item) }"
                    @click="selectLeft(item, run.run_id)">
                  {{ item.event_name }}
                </div>
              </div>
              <div v-else class="left-list" style="padding: 20px 30px;">По данному вида спорта у источника нет несматченных пар</div>

              <div class="center-space"></div>

              <div v-if="run.mismatched[Object.keys(run.mismatched)[1]] && run.mismatched[Object.keys(run.mismatched)[1]].length > 0"
                  class="right-list">
                <div v-for="item in this.filteredRight(run)"
                    :key="item.bk_event_id"
                    class="list-item"
                    :id="`item${item.bk_event_id}`"
                    :class="{ selected: isSelected(item) }"
                    @click="selectRight(item, run.run_id)">
                  {{ item.event_name }}
                </div>
              </div>
              <div v-else class="right-list" style="padding: 20px 30px;">По данному вида спорта у источника нет несматченных пар</div>
            </div>
            <div v-else style="text-align: center; margin-bottom: 40px">По данному вида спорта у источников нет несматченных пар</div>
          </div>

<!--          <div v-else style="text-align: center; margin-bottom: 30px">По данному вида спорта у источников нет несматченных пар</div>-->

        </div>
      </div>
    </div>
  </div>

  <div class="tool-buttons">
    <div class="controls">
      <div class="save-button"
           :class="isChanged() ? 'success-button' : 'disabled-button'"
           @click="sendMatches">

        Запомнить пары
      </div>
      <div class="cancel-button"
           :class="isChanged() ? 'danger-button' : 'disabled-button'"
           @click="resetMatchedPairs">

        Отмена
      </div>
    </div>
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
import axios from "axios";
import { ElNotification } from 'element-plus';

export default {
  name: "MismatchedBlock",
  props: [
    'selectedItems',
    'selectedTask',
    'modeFilter',
    'sportFilter',
    'sportTypesAll',
    'fullscreen',
  ],
  emits: [
    "fullscreenButtonCLick",
    // "taskChanged",
    "dataSent"
  ],
  data() {
    return {
      runs: [],
      events: {},
      selectedLeft: {},
      selectedRight: {},
      matched: {}
    }
  },
  methods: {
    sportName(sport_id){
      return this.sportTypesAll.find(subarr => subarr[0] === sport_id)[1]
    },

    fullscreenButtonClick(){
      this.$emit('fullscreenButtonCLick')
    },

    selectLeft(item, run_id) {
      if (this.selectedRight[run_id]){
        if (this.matched[run_id]){
          this.matched[run_id].push({event1: item.bk_event_id, event2: this.selectedRight[run_id] })
        } else {
          this.matched[run_id] = []
          this.matched[run_id].push({event1: item.bk_event_id, event2: this.selectedRight[run_id] })
        }

        delete this.selectedRight[run_id]
      } else {
        if (this.selectedLeft[run_id] === item.bk_event_id){
          delete this.selectedLeft[run_id]
        } else {
          this.selectedLeft[run_id] = item.bk_event_id
        }
      }
    },

    selectRight(item, run_id) {
      if (this.selectedLeft[run_id]){
        if (this.matched[run_id]){
          this.matched[run_id].push({event1: this.selectedLeft[run_id], event2: item.bk_event_id })
        } else {
          this.matched[run_id] = []
          this.matched[run_id].push({event1: this.selectedLeft[run_id], event2: item.bk_event_id })
        }

        delete this.selectedLeft[run_id]
      } else {
        if (this.selectedRight[run_id] === item.bk_event_id){
          delete this.selectedRight[run_id]
        } else {
          this.selectedRight[run_id] = item.bk_event_id
        }
      }
    },

    isSelected(item){
      return (Object.values(this.selectedLeft).includes(item.bk_event_id) || Object.values(this.selectedRight).includes(item.bk_event_id))
    },

    filteredLeft(run){
      let results = run.mismatched[Object.keys(run.mismatched)[0]]
      // console.log(results)

      return results.map((item) => {
        for (let key in this.matched) {
          let events = this.matched[key];
          for (let i = 0; i < events.length; i++) {
            let event1 = events[i].event1;
            if (item.bk_event_id === event1) {
              return null;
            }
          }
        }
        return item;
      }).filter((item) => item !== null)
    },

    filteredRight(run){
      let results = run.mismatched[Object.keys(run.mismatched)[1]]

      return results.map((item) => {
        for (let key in this.matched) {
          let events = this.matched[key];
          for (let i = 0; i < events.length; i++) {
            let event2 = events[i].event2;
            if (item.bk_event_id === event2) {
              return null;
            }
          }
        }
        return item;
      }).filter((item) => item !== null)
    },

    getEventName(bk_event_id){
      return this.events[bk_event_id].event_name
    },

    removeLink(run_id, match){
      this.matched[run_id] = this.matched[run_id].filter(d => d["event1"] !== match["event1"] || d["event2"] !== match["event2"])
      if(this.matched[run_id].length === 0){
        delete this.matched[run_id]
      }
    },

    isChanged(){
      return Object.keys(this.matched).length !== 0
    },

    async sendMatches(){
      for (const key in this.matched) {
        if (this.matched.hasOwnProperty(key)) {
          const value = this.matched[key];
          for (let i = 0; i < value.length; i++) {
            const item = value[i];
            for (const eventKey of ["event1", "event2"]) {
              const eventId = item[eventKey];
              item[eventKey] = this.events[eventId] || {};
            }
            item["is_match"] = true;
            item["mismatch"] = true;
          }
        }
      }

      console.log(this.matched)
      console.log('sent data')
      console.log(JSON.stringify(this.matched))
      await axios
          .post('/pairs/', JSON.stringify(this.matched),{
              headers: {
                'Content-Type': 'application/json'
              }
            })
          .then(response => {
            console.log('Response:', response.data);

            this.matched = {}
            // setTimeout(() => {this.requestTask(this.selectedTask['task_id'])},1000)

            ElNotification({
              title: 'Успешно!',
              message: 'Пары успешно приняты',
              type: 'success',
              duration: 4500,
            });

            setTimeout(() =>{this.$emit('dataSent')},1000)
          })
          .catch(error => {
            console.error('Error:', error);
            ElNotification({
                title: 'Ошибка!',
                message: `Произошла ошибка при отправке данных`,
                type: 'error',
                duration: 7500,
            })
          });
    },

    async requestTask(task_id){
      await axios
          .get(`/pairs/?task_id=${task_id}`)
          .then(response => {
            this.$emit('taskChanged', response.data.result[0])
            console.log('New requested Task')
            console.log(response.data.result[0])
          })
          .catch(error => {
            console.error('Error:', error);
            ElNotification({
                title: 'Ошибка!',
                message: `Произошла ошибка при запросе данных вызова`,
                type: 'error',
                duration: 7500,
            })
          });
    },

    resetMatchedPairs(){
      this.matched = {}
    },

    resetComponent(){
      this.runs = []
      this.events = {}
      this.selectedLeft = {}
      this.selectedRight = {}
      this.matched = {}
    }

  },
  mounted() {

  },
  watch: {
    selectedTask:{
      immediate: true,
      handler (newVal) {
        this.resetComponent()

        this.runs = newVal.runs
        // console.log(this.runs)
        this.runs.forEach(run => {
          let keys = Object.keys(run.mismatched)
          run.mismatched[keys[0]].forEach(item => {
            this.events[item.bk_event_id] = item
          })
          run.mismatched[keys[1]].forEach(item => {
            this.events[item.bk_event_id] = item
          })
          // if(keys[0] !== 'null'){
          //   run.mismatched[keys[0]].forEach(item => {
          //     this.events[item.bk_event_id] = item
          //   })
          //   run.mismatched[keys[1]].forEach(item => {
          //     this.events[item.bk_event_id] = item
          //   })
          // } else {
          //   delete run['mismatched']
          // }

        })
      }
    }
  },
}
</script>

<style scoped>
.sport-container {
  width: 100%;
  max-width: 80rem;
}

.sport-title{
  text-align: center;
  margin-bottom: 20px;
  font-weight: bold;
  font-size: 18px;
}

.matched{
  margin-bottom: 20px;
}

.match-items{
  display: flex;
  flex-direction: row;
}

.match-item{
  width: 40%;
  flex-basis: 40%;
  text-align: center;
  padding: 20px 30px;
  border: 1px solid var(--color-text);
  height: 6rem;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  background-color: rgb(206, 206, 206) !important;
  color: var(--color-background);
}

.remove-link{
  width: 20%;
  flex-basis: 20%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease-in-out;
  cursor: pointer;
}

.remove-link:before {
  content: '✗';
  color: var(--el-color-danger);
  font-size: 3rem;
  transition: all 0.3s ease-in-out;
}

.remove-link:hover{
  background-color: var(--el-color-danger);
  color: var(--color-background);
}

.remove-link:hover:before{
  color: var(--color-background);
}

.result-item{
  display: flex;
  flex-direction: row;
}

.left-list, .right-list{
  width: 40%;
  flex-basis: 40%;
  text-align: center;
}

.center-space {
  width: 20%;
  flex-basis: 20%;
}

.list-item{
  padding: 20px 30px;
  border: 1px solid var(--color-text);
  height: 6rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.1s ease-in-out;
}

.list-item:hover{
  background-color: rgb(131, 136, 141);
  color: black;
}

.selected{
  background-color: rgb(206, 206, 206) !important;
  color: black;
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