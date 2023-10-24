<template>
  <div class="tools-block"
       :class="{'tools-block-fullscreen': this.fullscreen}"
  >
    <div v-if="!allResultsFiltered" style="width: 100%">
      <div v-if="sportFilter.allSport" class="sport-container">
        <div v-for="run in sortedRuns">
          <div class="sport-title">
            {{ sportName(run.sport_id) }}
          </div>
          <div v-if="run.results.length > 0" v-for="result in run.results" class="result-item">
            <div class="field-items">

              <!-- team1 row -->
              <div class="field-item"
                   :class="{
                              'highlighted-accept': isHighlightedAccept(result.result_id),
                              'highlighted-reject': isHighlightedReject(result.result_id),
                            }"
              >

                <div class="fields">
                  <div class="field">
                    {{ result.event1.team1 }}
                  </div>
                  <div class="field-zero">
                    {{ result.is_swapped ? "Teams are swapped!" : ""}}
                  </div>
                  <div class="field">
                    {{ result.event2.team1 }}
                  </div>
                </div>
              </div>

              <!-- team2 row -->
              <div class="field-item"
                   :class="{
                              'highlighted-accept': isHighlightedAccept(result.result_id),
                              'highlighted-reject': isHighlightedReject(result.result_id),
                            }"
              >

                <div class="fields">
                  <div class="field">
                    {{ result.event1.team2 }}
                  </div>
                  <div class="field-zero">
                    {{ result.overall_similarity ? result.overall_similarity.toFixed(2) + '%' : '' }}
                  </div>
                  <div class="field">
                    {{ result.event2.team2 }}
                  </div>
                </div>
              </div>

              <!-- league_name row -->
              <div class="field-item"
                 :class="{
                            'highlighted-accept': isHighlightedAccept(result.result_id),
                            'highlighted-reject': isHighlightedReject(result.result_id),
                          }"
              >
              <div class="fields">
                <div class="field">
                  {{ result.event1.league_name }}
                </div>
                <div class="field-zero"></div>
                <div class="field">
                  {{ result.event2.league_name }}
                </div>
              </div>
            </div>
          </div>
            <div
              class="button"
              :class="{
                'checkmark-green': currentMatchStatus(result) === null || currentMatchStatus(result) === true,
                'cross-red': currentMatchStatus(result) === false
              }"
              @click="toggleMismatched(result)"
            >
            </div>
          </div>
          <div v-else style="text-align: center; margin-bottom: 40px">Все пары уже размечены</div>
        </div>
      </div>

      <div v-else class="sport-container">
        <div v-for="run in sortedRuns" >
          <div v-if="sportFilter.sport === run.sport_id" >
            <div class="sport-title">
              {{ sportName(run.sport_id) }}
            </div>
            <div v-if="run.results.length > 0" v-for="result in run.results" class="result-item">
              <div class="field-items">

                <!-- team1 row -->
                <div class="field-item"
                     :class="{
                                'highlighted-accept': isHighlightedAccept(result.result_id),
                                'highlighted-reject': isHighlightedReject(result.result_id),
                              }"
                >

                  <div class="fields">
                    <div class="field">
                      {{ result.event1.team1 }}
                    </div>
                    <div class="field-zero">
                      {{ result.is_swapped ? "Teams are swapped!" : ""}}
                    </div>
                    <div class="field">
                      {{ result.event2.team1 }}
                    </div>
                  </div>
                </div>

                <!-- team2 row -->
                <div class="field-item"
                     :class="{
                                'highlighted-accept': isHighlightedAccept(result.result_id),
                                'highlighted-reject': isHighlightedReject(result.result_id),
                              }"
                >

                  <div class="fields">
                    <div class="field">
                      {{ result.event1.team2 }}
                    </div>
                    <div class="field-zero">
                      {{ result.overall_similarity ? result.overall_similarity.toFixed(2) + '%' : '' }}
                    </div>
                    <div class="field">
                      {{ result.event2.team2 }}
                    </div>
                  </div>
                </div>

                <!-- league_name row -->
                <div class="field-item"
                   :class="{
                              'highlighted-accept': isHighlightedAccept(result.result_id),
                              'highlighted-reject': isHighlightedReject(result.result_id),
                            }"
                >
                <div class="fields">
                  <div class="field">
                    {{ result.event1.league_name }}
                  </div>
                  <div class="field-zero"></div>
                  <div class="field">
                    {{ result.event2.league_name }}
                  </div>
                </div>
              </div>
              </div>
              <div
                class="button"
                :class="{
                'checkmark-green': currentMatchStatus(result) === null || currentMatchStatus(result) === true,
                'cross-red': currentMatchStatus(result) === false
              }"
                @click="toggleMismatched(result)"
              >
              </div>
            </div>
            <div v-else style="text-align: center; margin-bottom: 40px">Все пары уже размечены</div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="no-content">Все пары по всем видам спорта уже размечены</div>
  </div>

  <div class="tool-buttons" v-if="!allResultsFiltered">
  <div class="controls">
    <div class="save-button"
         :class="this.buttons_active ? 'success-button' : 'disabled-button'"
         @click="sendMismatched"
    >
      {{ this.submit_text }}
    </div>
    <div class="cancel-button"
         :class="compareMismatchedPairs() && this.buttons_active ? 'danger-button' : 'disabled-button'"
         @click="resetMismatchedPairs"
    >
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
import {ElNotification} from 'element-plus';

export default {
  name: "MatchedBlock",
  props: [
    'selectedTask',
    'modeFilter',
    'sportFilter',
    'sportTypesAll',
    'fullscreen',
  ],
  emits: [
    "fullscreenButtonCLick",
    "update:selectedTask",
    // "taskChanged",
    "dataSent"
  ],
  data() {
    return {
      runs: [],
      sortedRuns: [],
      allResultsFiltered: false,

      mismatchedPairsDef: [],
      mismatchedPairsNew: [],
      differentResults: [],
      highlited_reject: 0,
      highlited_accept: 0,
      highlited_forget: 0,

      submit_text: 'Принять пары',
      buttons_active: true,
    }
  },

  methods: {
    sortRuns() {
      let whitelist = JSON.parse(localStorage.getItem('whitelist')) || [];
      let banlist = JSON.parse(localStorage.getItem('banlist')) || [];

      this.allResultsFiltered = true;
      this.sortedRuns = this.runs.map(run => {
        let filteredResults = run.results.filter(result => {
          let matchData = [
            result.event1.event_name,
            result.event2.event_name,
            result.event1.league_name,
            result.event2.league_name,
          ];

          if (!whitelist.some(wl => JSON.stringify(wl) === JSON.stringify(matchData))
              && !banlist.some(bl => JSON.stringify(bl) === JSON.stringify(matchData))) {
            this.allResultsFiltered = false;
            return true;
          } else {
            return false;
          }
        });

        return {
          ...run,
          results: filteredResults.sort((a, b) => {
            if (a.overall_similarity === null) return 1;
            if (b.overall_similarity === null) return -1;
            return a.overall_similarity - b.overall_similarity;
          }),
        };
      });
    },


    titleText(task) {
      const timeOptions = {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZoneName: 'short'
      }

      const startedAt = new Date(task.started_at);
      const startedAtFormatted = startedAt.toLocaleString('ru-RU', timeOptions);

      const title = `Вызов ${task.task_id} | ${startedAtFormatted}`;

      if (task.finished_at) {
        const finishedAt = new Date(task.finished_at);
        const finishedAtFormatted = finishedAt.toLocaleString('ru-RU', timeOptions);
        return `${title} - ${finishedAtFormatted}`;
      } else {
        return title;
      }
    },

    sportName(sport_id){
      return this.sportTypesAll.find(subarr => subarr[0] === sport_id)[1]
    },

    currentMatchStatus(result){
      let index = this.mismatchedPairsNew.findIndex(item => item.result_id === result.result_id)

      if (this.mismatchedPairsNew[index].mismatch === null || this.mismatchedPairsNew[index].is_match === true) {
        return true
      }
      else if(this.mismatchedPairsNew[index].is_match === false) {
        return false
      }
    },

    toggleMismatched(result) {
      let index = this.mismatchedPairsNew.findIndex(item => item.result_id === result.result_id)

      if (this.mismatchedPairsNew[index].mismatch === null || this.mismatchedPairsNew[index].is_match === true){
        this.mismatchedPairsNew[index].mismatch = false
        this.mismatchedPairsNew[index].is_match = false

        this.highlited_reject = result.result_id
        setTimeout(() => {
          this.highlited_reject = 0
        }, 500);
      }
      else if (this.mismatchedPairsNew[index].is_match === false){
        this.mismatchedPairsNew[index].is_match = true

        this.highlited_accept = result.result_id
        setTimeout(() => {
          this.highlited_accept = 0
        }, 500);
      }
    },

    compareMismatchedPairs() {
      return JSON.stringify(this.mismatchedPairsNew) !== JSON.stringify(this.mismatchedPairsDef)



      // if(this.mismatchedPairsNew.length !== this.mismatchedPairsDef.length){
      //   for (let i = 0; i < this.mismatchedPairsNew.length; i++) {
      //     const newDict = this.mismatchedPairsNew[i]
      //     const defDict = this.mismatchedPairsDef.find((dict) => dict.result_id === newDict.result_id);;
      //
      //     if(!defDict){
      //       if(newDict.mismatch === null){
      //         continue
      //       } else{
      //         return true
      //       }
      //     } else if (defDict.mismatch !== newDict.mismatch){
      //       return true
      //     }
      //
      //   }
      //   return false
      // }
      //
      // for (let i = 0; i < this.mismatchedPairsDef.length; i++) {
      //   const defDict = this.mismatchedPairsDef[i];
      //   const newDict = this.mismatchedPairsNew.find((dict) => dict.result_id === defDict.result_id);
      //   if (!newDict || JSON.stringify(defDict) !== JSON.stringify(newDict)) {
      //     return true;
      //   }
      // }
      // return false
    },

    resetMismatchedPairs() {
      this.mismatchedPairsNew = this.mismatchedPairsDef.map(obj => ({...obj}));
    },

    isHighlightedAccept(result_id){
      return result_id === this.highlited_accept
    },

    isHighlightedReject(result_id){
      return result_id === this.highlited_reject
    },

    isHighlightedForget(result_id){
      return result_id === this.highlited_forget
    },

    compareDicts(dict1, dict2) {
      for (let key in dict1) {
        if (!dict2.hasOwnProperty(key)) {
          return false;
        }
        const val1 = dict1[key];
        const val2 = dict2[key];
        if (typeof val1 === 'object' && typeof val2 === 'object') {
          const nestedResult = this.compareDicts(val1, val2);
          if (!nestedResult) {
            return false;
          }
        } else if (val1 !== val2) {
          return false;
        }
      }
      return true;
    },

    async sendMismatched(){

      // buttons toggle off
      this.submit_text = 'Подождите..'
      this.buttons_active = false

      // old implementation
      // for (let i = 0; i < this.mismatchedPairsNew.length; i++){
      //   const dict1 = this.mismatchedPairsNew[i]
      //   const dict2 = this.mismatchedPairsDef[i]
      //   if(!this.compareDicts(dict1,dict2)) {
      //     this.differentResults.push(dict1)
      //   }
      // }

      // new implementation
      let updatedPairs = [];
      if (!this.sportFilter.allSport) {
        console.log(this.sportFilter.sport);
        this.sortedRuns.forEach(run => {
            if (run.sport_id === this.sportFilter.sport) {
                let results = [];
                run.results.forEach(result => {
                    results.push({
                        result_id: result.result_id,
                        is_match: result.is_match === null ? true : result.is_match,
                        mismatched: result.mismatched ? result.mismatched : false
                    });
                });
                updatedPairs = [...updatedPairs, ...results];
            }
        });
        console.log(updatedPairs);
        } else {
        this.sortedRuns.forEach(run => {
            run.results.forEach(result => {
                updatedPairs.push({
                    result_id: result.result_id,
                    is_match: result.is_match === null ? true : result.is_match,
                    mismatched: result.mismatched ? result.mismatched : false
                });
            });
        });
        console.log(updatedPairs);
      }

      // old implementation of frontend event caching
      // let updatedPairs = this.mismatchedPairsNew.map(pair => {
      //     return {
      //         result_id: pair.result_id,
      //         is_match: pair.is_match === null ? true : pair.is_match,
      //         mismatch: false
      //     };
      // });

      let data = {
          results: updatedPairs
      }
      console.log('Измененные данные, которые отправлены на сервер', updatedPairs)
      console.log('Отправка данных')

      // console.log(JSON.stringify(data))

      await axios
          .put('/pairs/', JSON.stringify(data),{
              headers: {
                'Content-Type': 'application/json'
              }
            })
          .then(response => {
            console.log('Данные успешно отправлены! Ответ сервера:', response.data);

            this.mismatchedPairsDef = this.mismatchedPairsNew.map(obj => ({...obj}));
            this.differentResults = []
            // this.updateProp()

            ElNotification({
              title: 'Успешно!',
              message: 'Пары успешно приняты',
              type: 'success',
              duration: 4500,
            });

            console.log('Сохранение размеченных пар в локальном хранилище браузера..')

            // implementation of frontend event caching
            let whitelist = JSON.parse(localStorage.getItem('whitelist')) || [];
            let banlist = JSON.parse(localStorage.getItem('banlist')) || [];

            for (let i = 0; i < this.sortedRuns.length; i++){
              let run = this.sortedRuns[i];

              if (!this.sportFilter.allSport && run.sport_id !== this.sportFilter.sport) continue;

              for(let j = 0; j < run.results.length; j++){
                let result = run.results[j];

                // implementation variant
                // let matchData = {
                //   "event1.team1": result.event1.team1,
                //   "event1.team2": result.event1.team2,
                //   "event2.team1": result.event2.team1,
                //   "event2.team2": result.event2.team2,
                //   "event1.league": result.event1.league_name,
                //   "event2.league": result.event2.league_name
                // };
                let matchData = [
                    result.event1.event_name,
                    result.event2.event_name,
                    result.event1.league_name,
                    result.event2.league_name,
                ]

                if (result.is_match === true || result.is_match === null) {
                  if (!whitelist.some(existing => JSON.stringify(existing) === JSON.stringify(matchData))) {
                    whitelist.push(matchData);
                  }
                } else if(result.is_match === false) {
                  if (!banlist.some(existing => JSON.stringify(existing) === JSON.stringify(matchData))) {
                    banlist.push(matchData);
                  }
                }
              }
            }

            localStorage.setItem('whitelist', JSON.stringify(whitelist));
            localStorage.setItem('banlist', JSON.stringify(banlist));

            this.sortRuns();

            console.log('Размеченные пары успешно сохранены в браузере!')
            if (this.fullscreen){
              this.fullscreenButtonClick()
            }

            // this.allResultsFiltered = true

            // ElNotification({
            //   title: 'Успешно!',
            //   message: 'Размеченные пары успешно сохранены в браузере',
            //   type: 'success',
            //   duration: 2500,
            // });

            setTimeout(() =>{this.$emit('dataSent')},1000)

            this.submit_text = 'Принять пары'
            this.buttons_active = true
          })
          .catch(error => {
            console.error('Error:', error);
            ElNotification({
                title: 'Ошибка!',
                message: `Произошла ошибка при отправке данных`,
                type: 'error',
                duration: 7500,
            })
            this.submit_text = 'Принять пары'
            this.buttons_active = true
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

    fullscreenButtonClick(){
      this.$emit('fullscreenButtonCLick')
    },

    updateProp(){
      this.selectedTask.runs.forEach(run => {
        run.results.forEach(result => {
          const dictResultId = result.result_id;
          const arrayItem = this.mismatchedPairsNew.find(item => item.result_id === dictResultId);
          if(arrayItem){
            result.mismatch = arrayItem.mismatch;
            result.is_match = arrayItem.is_match
          }
        })
      })
      this.$emit('update:selectedTask', this.selectedTask)
    },

    resetComponent(){
      this.runs = []
      this.mismatchedPairsDef = []
      this.mismatchedPairsNew = []
      this.differentResults = []
    }
  },
  watch: {
    selectedTask:{
      immediate: true,
      handler (newVal) {
        this.resetComponent()
        this.runs = newVal.runs
        this.runs.forEach(run => {
          run.results.forEach(result => {
            // if(result.mismatch !== null){
              this.mismatchedPairsDef.push({result_id: result.result_id, is_match: result.is_match, mismatch: result.mismatch})
              this.mismatchedPairsNew.push({result_id: result.result_id, is_match: result.is_match, mismatch: result.mismatch})
            // }
          })
        })
        this.sortRuns()
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

.no-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 18px;
  flex: 1;
}

.result-item{
  margin-bottom: 30px;
  display: flex;
  flex-direction: row;
  border: 1px solid var(--color-text);
}

.field-items{
  width: 90%;
  flex-basis: 90%;
}

.field-item{
  background-color: #232323;
  transition:  all 0.3s ease-in-out;
}

.highlighted-accept{
  background-color: rgba(103, 194, 58, 0.75);
  color: var(--color-background);
  transition:  all 0.3s ease-in-out;
}

.highlighted-reject{
  background-color: rgba(245, 108, 108, 0.75);
  color: var(--color-background);
  transition: all 0.3s ease-in-out;
}

.highlighted-forget{
  background-color: rgba(154, 152, 152, 0.75);
  color: var(--color-background);
  transition: all 0.3s ease-in-out;
}

.fields{
  display: flex;
  flex-direction: row;
}

.field{
  width: 45%;
  flex-basis: 45%;
  text-align: center;
  padding: 20px 30px;
  outline: 1px solid var(--color-text);
  display: flex;
  align-items: center;
  justify-content: center;
}

.field-zero{
  width: 13%;
  flex-basis: 13%;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
}

.button {
  width: 10%;
  flex-basis: 10%;
  outline: 1px solid var(--color-text);
  cursor: pointer;
  transition: 0.1s all ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: bold;
}

.tool-buttons {
  padding: 20px 30px;
  display: flex;
  bottom: 0;
  width: 100%;
  justify-content: space-between;
}

.checkmark-gray:before {
  content: '✓';
  color: gray;
  font-size: 3rem;
}

.checkmark-green:before {
  content: '✓';
  color: var(--el-color-success);
  font-size: 3rem;
}

.cross-red:before {
  content: '✗';
  color: var(--el-color-danger);
  font-size: 3rem;
}
</style>