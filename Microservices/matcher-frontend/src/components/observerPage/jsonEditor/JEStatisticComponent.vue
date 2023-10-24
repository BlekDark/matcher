<template>
  <div v-if="!this.taskIsLoading && this.selectedTask" class="content">

    <div class="tools-block"
      :class="{'tools-block-fullscreen': this.fullscreen}"
    >
      <div class="pairs-block">
        <div v-if="sportFilter.allSport" class="original-comparison">
          <div class="json-1">
            <div class="run-container">
              <div v-for="(run, runIndex) in this.runs" class="run">
                <div class="sport-title">
                  {{ sportName(run.sport_id) }}
                </div>

                <div v-if="run.mismatched[Object.keys(run.mismatched)[0]].length > 0 || run.results.length > 0">
                  <div v-if="run.results.length > 0" v-for="result in run.results" class="result">
                    <div class="result-setting">
                      <span title="event_name" class="setting-title">event_name</span>
                      <textarea
                        v-model="result.event1.event_name"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>

                    <div class="result-setting">
                      <span title="team1" class="setting-title">team1</span>
                      <textarea
                        v-model="result.event1.team1"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>

                    <div class="result-setting">
                      <span title="team2" class="setting-title">team2</span>
                      <textarea
                        v-model="result.event1.team2"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>

                    <div class="result-setting">
                      <span title="league_name" class="setting-title">league_name</span>
                      <textarea
                        v-model="result.event1.league_name"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>
                  </div>

                  <div v-if="run.mismatched">
                    <div v-for="item in run.mismatched[Object.keys(run.mismatched)[0]]" class="result">
                      <div class="result-setting">
                        <span title="event_name" class="setting-title">event_name</span>
                        <textarea
                          v-model="item.event_name"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>

                      <div class="result-setting">
                        <span title="team1" class="setting-title">team1</span>
                        <textarea
                          v-model="item.team1"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>

                      <div class="result-setting">
                        <span title="team2" class="setting-title">team2</span>
                        <textarea
                          v-model="item.team2"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>

                      <div class="result-setting">
                        <span title="league_name" class="setting-title">league_name</span>
                        <textarea
                          v-model="item.league_name"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="no-data-text">Отсутствуют данные для отображения</div>
              </div>
            </div>
          </div>

          <div class="json-2">
            <div class="run-container">
              <div v-for="(run, runIndex) in this.runs" class="run">
                <div class="sport-title">
                  {{ sportName(run.sport_id) }}
                </div>

                <div v-if="run.mismatched[Object.keys(run.mismatched)[1]].length > 0 || run.results.length > 0">
                  <div v-if="run.results.length > 0" v-for="result in run.results" class="result">
                    <div class="result-setting">
                      <span title="event_name" class="setting-title">event_name</span>
                      <textarea
                        v-model="result.event2.event_name"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>

                    <div class="result-setting">
                      <span title="team1" class="setting-title">team1</span>
                      <textarea
                        v-model="result.event2.team1"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>

                    <div class="result-setting">
                      <span title="team2" class="setting-title">team2</span>
                      <textarea
                        v-model="result.event2.team2"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>

                    <div class="result-setting">
                      <span title="league_name" class="setting-title">league_name</span>
                      <textarea
                        v-model="result.event2.league_name"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>
                  </div>

                  <div v-if="run.mismatched">
                    <div v-for="item in run.mismatched[Object.keys(run.mismatched)[1]]" class="result">
                      <div class="result-setting">
                        <span title="event_name" class="setting-title">event_name</span>
                        <textarea
                          v-model="item.event_name"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>

                      <div class="result-setting">
                        <span title="team1" class="setting-title">team1</span>
                        <textarea
                          v-model="item.team1"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>

                      <div class="result-setting">
                        <span title="team2" class="setting-title">team2</span>
                        <textarea
                          v-model="item.team2"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>

                      <div class="result-setting">
                        <span title="league_name" class="setting-title">league_name</span>
                        <textarea
                          v-model="item.league_name"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="no-data-text">Отсутствуют данные для отображения</div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="original-comparison">
          <div class="json-1">
            <div class="run-container">
              <div v-for="run in this.runs" class="run">
                <div v-if="sportFilter.sport === run.sport_id" >
                  <div class="sport-title">
                    {{ sportName(run.sport_id) }}
                  </div>

                  <div v-if="run.mismatched[Object.keys(run.mismatched)[0]].length > 0 || run.results.length > 0">
                  <div v-if="run.results.length > 0" v-for="result in run.results" class="result">
                    <div class="result-setting">
                      <span title="event_name" class="setting-title">event_name</span>
                      <textarea
                        v-model="result.event1.event_name"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>

                    <div class="result-setting">
                      <span title="team1" class="setting-title">team1</span>
                      <textarea
                        v-model="result.event1.team1"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>

                    <div class="result-setting">
                      <span title="team2" class="setting-title">team2</span>
                      <textarea
                        v-model="result.event1.team2"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>

                    <div class="result-setting">
                      <span title="league_name" class="setting-title">league_name</span>
                      <textarea
                        v-model="result.event1.league_name"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>
                  </div>

                  <div v-if="run.mismatched">
                    <div v-for="item in run.mismatched[Object.keys(run.mismatched)[0]]" class="result">
                      <div class="result-setting">
                        <span title="event_name" class="setting-title">event_name</span>
                        <textarea
                          v-model="item.event_name"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>

                      <div class="result-setting">
                        <span title="team1" class="setting-title">team1</span>
                        <textarea
                          v-model="item.team1"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>

                      <div class="result-setting">
                        <span title="team2" class="setting-title">team2</span>
                        <textarea
                          v-model="item.team2"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>

                      <div class="result-setting">
                        <span title="league_name" class="setting-title">league_name</span>
                        <textarea
                          v-model="item.league_name"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>
                    </div>
                  </div>
                </div>
                  <div v-else class="no-data-text">Отсутствуют данные для отображения</div>
                </div>
              </div>
            </div>
          </div>

          <div class="json-2">
            <div class="run-container">
              <div v-for="run in this.runs" class="run">
                <div v-if="sportFilter.sport === run.sport_id" >
                  <div class="sport-title">
                    {{ sportName(run.sport_id) }}
                  </div>

                  <div v-if="run.mismatched[Object.keys(run.mismatched)[1]].length > 0 || run.results.length > 0">
                  <div v-if="run.results.length > 0" v-for="result in run.results" class="result">
                    <div class="result-setting">
                      <span title="event_name" class="setting-title">event_name</span>
                      <textarea
                        v-model="result.event2.event_name"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>

                    <div class="result-setting">
                      <span title="team1" class="setting-title">team1</span>
                      <textarea
                        v-model="result.event2.team1"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>

                    <div class="result-setting">
                      <span title="team2" class="setting-title">team2</span>
                      <textarea
                        v-model="result.event2.team2"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>

                    <div class="result-setting">
                      <span title="league_name" class="setting-title">league_name</span>
                      <textarea
                        v-model="result.event2.league_name"
                        placeholder="Введите значение"
                        class="json-input"
                        @input="processEventInput"
                      />
                    </div>
                  </div>

                  <div v-if="run.mismatched">
                    <div v-for="item in run.mismatched[Object.keys(run.mismatched)[1]]" class="result">
                      <div class="result-setting">
                        <span title="event_name" class="setting-title">event_name</span>
                        <textarea
                          v-model="item.event_name"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>

                      <div class="result-setting">
                        <span title="team1" class="setting-title">team1</span>
                        <textarea
                          v-model="item.team1"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>

                      <div class="result-setting">
                        <span title="team2" class="setting-title">team2</span>
                        <textarea
                          v-model="item.team2"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>

                      <div class="result-setting">
                        <span title="league_name" class="setting-title">league_name</span>
                        <textarea
                          v-model="item.league_name"
                          placeholder="Введите значение"
                          class="json-input"
                          @input="processEventInput"
                        />
                      </div>
                    </div>
                  </div>
                </div>
                  <div v-else class="no-data-text">Отсутствуют данные для отображения</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="Object.keys(this.testMatch).length > 0" class="resulting-comparison">
          <div v-if="sportFilter.allSport" class="run" v-for="run in this.testMatch.runs">
            <div class="sport-title">
              {{ sportName(run.sport_id) }}
            </div>

            <div v-if="run.mismatched[Object.keys(run.mismatched)[0]].length > 0 && run.mismatched[Object.keys(run.mismatched)[1]].length > 0 || run.results.length > 0">
                <div v-if="run.mismatched">
                  <div class="result-item" v-if="run.mismatched[Object.keys(run.mismatched)[0]].length > 0 && run.mismatched[Object.keys(run.mismatched)[1]].length > 0">
                    <div v-if="run.mismatched[Object.keys(run.mismatched)[0]] && run.mismatched[Object.keys(run.mismatched)[0]].length > 0"
                         class="left-list"
                    >
                      <div v-for="item in run.mismatched[Object.keys(run.mismatched)[0]]"
                          :key="item.bk_event_id"
                          class="mismatched-item"
                      >
                        {{ item.event_name }}
                      </div>
                    </div>

                    <div v-else class="left-list" style="padding: 20px 30px;">По данному вида спорта у источника нет несматченных пар</div>

                    <div v-if="run.mismatched[Object.keys(run.mismatched)[1]] && run.mismatched[Object.keys(run.mismatched)[1]].length > 0"
                         class="right-list"
                    >
                      <div v-for="item in run.mismatched[Object.keys(run.mismatched)[1]]"
                          :key="item.bk_event_id"
                          class="mismatched-item"
                      >
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
                        <div class="field success">
                          {{ result.event1.event_name }}
                        </div>
                        <div class="field success">
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


          <div v-else v-for="run in this.testMatch.runs" class="run" >
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
                            class="mismatched-item">
                          {{ item.event_name }}
                        </div>
                      </div>
                      <div v-else class="left-list" style="padding: 20px 30px;">По данному вида спорта у источника нет несматченных пар</div>

                      <div v-if="run.mismatched[Object.keys(run.mismatched)[1]] && run.mismatched[Object.keys(run.mismatched)[1]].length > 0"
                          class="right-list">
                        <div v-for="item in run.mismatched[Object.keys(run.mismatched)[1]]"
                            :key="item.bk_event_id"
                            class="mismatched-item">
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
                          <div class="field success">
                            {{ result.event1.event_name }}
                          </div>
                          <div class="field success">
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

        <div v-else class="help-text">{{ this.helpText }}</div>
      </div>

      <div class="settings-block">
        <div class="pair-settings">
          <div class="settings-title">
            Параметры пары источников
          </div>

          <div
            v-if="pairSettings"
            class="settings"
            :class="{'fullscreen-settings': this.fullscreen}"
          >
            <div v-for="key in this.pairNewFiltered(this.pairNew)" class="pair-setting">
              <span :title="key" class="setting-title">{{ key }}</span>
              <input type="number" v-model="pairNew[key]" @input="processPairInput(key)" min="0" max="100">
            </div>
          </div>
        </div>

        <div class="sport-settings">
          <div class="settings-title">
            Параметры видов спорта
          </div>

          <div
            v-if="pairSettings && JSON.stringify(pairNew['types']) !== '{}'"
            class="settings"
            :class="{'fullscreen-settings': this.fullscreen}"
          >
              <div
                  v-if="sportFilter.allSport"
                  v-for="(type, key) in pairNew.types"
                  style="margin-bottom: 10px;"
              >
                  <span :title="this.sportName(parseInt(key))" class="settings-title" style="font-weight: bold; font-size: 14px">{{ this.sportName(parseInt(key)) }}</span>
                  <div v-for="settingKey in this.sortedTypeSettings(type)" class="sport-setting">
                    <span :title="settingKey" class="setting-title">{{ settingKey }}</span>
                    <input type="number" v-model="pairNew.types[key][settingKey]" @input="processInputAllSport(key, settingKey)" min="0" max="100">
                  </div>
              </div>

              <div v-else>
                <div v-if="pairNew.types[sportFilter.sport]">
                  <span :title="sportName(sportFilter.sport)" class="settings-title" style="font-weight: bold; font-size: 14px">{{ sportName(sportFilter.sport) }}</span>
                   <div v-for="key in this.sortedTypeSettings(pairNew.types[sportFilter.sport])" class="sport-setting">
                     <span :title="key" class="setting-title">{{ key }}</span>
                     <input type="number" v-model="pairNew.types[sportFilter.sport][key]" @input="processInputSport(key)" min="0" max="100">
                   </div>
                </div>

                <div v-else style="display: flex; flex-direction: column; align-items: center;">
                  Нет данных для отображения
                </div>
              </div>
          </div>
        </div>

        <div class="button-block">
          <div :class="this.readyToChange ? 'compare-button' : 'disabled-button'"
               @click="sendConfig"
          >
            Сравнить с новыми параметрами</div>
        </div>
      </div>

    </div>

    <div class="tool-buttons" :class="{'tools-buttons-fullscreen': this.fullscreen}">
      <div class="controls">
        <div class="save-button"
             :class="this.readyToChange ? 'success-button' : 'disabled-button'"
             @click="saveConfig"
        >
          Сохранить новые параметры
        </div>
        <div class="cancel-button"
             :class="this.settingsChanged ? 'danger-button' : 'disabled-button'"
             @click="resetConfig"
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
          @click="fullscreenButtonClick()"
      >
        Свернуть
      </div>
    </div>

  </div>
  <div v-else-if="this.taskIsLoading" class="no-content">
    Вызов загружается, пожалуйста, подождите..
  </div>
  <div v-else class="no-content">
    Выберите вызов, чтобы продолжить..
  </div>
</template>

<script>
import axios from "axios";
import { ElNotification, ElMessageBox } from 'element-plus';


export default {
  name: "JEStatisticComponent",

  props: [
      'selectedTask',
      'pairSettings',
      'sportFilter',
      'sportTypesAll',
      'fullscreen',
      'taskIsLoading',
  ],

  emits: [
      'fullscreenButtonCLick',
  ],

  components: {
  },

  data() {
    return {
      runs: [],
      defaultRuns: [],

      pairDef: {},
      pairNew: {},

      settingsChanged: false,
      readyToChange: false,

      receivedTaskId: '',
      testMatch: {},
      helpText: 'Измените параметры, чтобы получить новые результаты',
    }
  },

  mounted(){
    this.pairDef = this.$parent.pairSettings;
    if(this.pairDef)
    {
      this.pairNew = JSON.parse(JSON.stringify(this.pairDef));
    }
  },

  methods: {
    sportName(sport_id){
      return this.sportTypesAll.find(subarr => subarr[0] === sport_id)[1]
    },

    fullscreenButtonClick(){
      this.$emit('fullscreenButtonCLick')
    },

    pairNewFiltered(settings){
      let settingTemp = JSON.parse(JSON.stringify(settings))

      delete settingTemp.source1_id
      delete settingTemp.source2_id
      delete settingTemp.types

      return Object.keys(settingTemp).sort();
    },

    sortedTypeSettings(type){
      return Object.keys(type).sort();
    },

    processPairInput(key){
      const intValue = parseFloat(this.pairNew[key]);

      if (!isNaN(intValue)) {
        this.pairNew[key] = intValue
      }

      let state = this.deepEqual(this.runs, this.defaultRuns)
      this.settingsChanged = this.pairDef[key] !== this.pairNew[key] || !state;
      this.readyToChange = this.pairDef[key] !== this.pairNew[key] || !state;

      this.zeroFieldsCheck()
    },

    processInputAllSport(key, settingKey){
      const intValue = parseFloat(this.pairNew.types[key][settingKey]);

      if (!isNaN(intValue)) {
        this.pairNew.types[key][settingKey] = intValue
      }

      let state = this.deepEqual(this.runs, this.defaultRuns)
      this.settingsChanged = this.pairDef.types[key][settingKey] !== this.pairNew.types[key][settingKey] || !state;
      this.readyToChange = this.pairDef.types[key][settingKey] !== this.pairNew.types[key][settingKey] || !state;

      this.zeroFieldsCheck()
    },

    processInputSport(key){
      const intValue = parseFloat(this.pairNew.types[this.sportFilter.sport][key]);
      if (!isNaN(intValue)) {
        this.pairNew.types[this.sportFilter.sport][key] = intValue
      }

      this.settingsChanged = this.pairDef.types[this.sportFilter.sport][key] !== this.pairNew.types[this.sportFilter.sport][key];
      this.readyToChange = this.pairDef.types[this.sportFilter.sport][key] !== this.pairNew.types[this.sportFilter.sport][key];

      this.zeroFieldsCheck()
    },

    processEventInput(){
      let state = this.deepEqual(this.runs, this.defaultRuns)
      this.settingsChanged = !state
      this.readyToChange = !state

      this.zeroFieldsCheck()
    },

    deepEqual(obj1, obj2) {
      return JSON.stringify(obj1) === JSON.stringify(obj2);
    },

    zeroFieldsCheck(){
      if(this.pairNew.length !== 0){
        for (let key in this.pairNew) {
          if (typeof this.pairNew[key] === "undefined" || this.pairNew[key] === "") {
            this.readyToChange = false
          }
        }

        if(this.pairNew.types){
          for (let key in this.pairNew.types){
            for (let settingKey in this.pairNew.types[key]) {
              if (typeof this.pairNew.types[key][settingKey] === "undefined" || this.pairNew.types[key][settingKey] === "") {
                this.readyToChange = false
              }
            }
          }


          for (let key in this.pairNew.types[this.sportFilter.sport]) {
            if (typeof this.pairNew.types[this.sportFilter.sport][key] === "undefined" ||
                this.pairNew.types[this.sportFilter.sport][key] === "") {
              this.readyToChange = false
            }
          }
        }


      }
    },

    async sendConfig(){
      this.helpText = 'Пожалуйста, подождите, Ваш запрос обрабатывается..'
      this.testMatch = {}

      let settingTemp = JSON.parse(JSON.stringify(this.pairNew))

      delete settingTemp.source1_id
      delete settingTemp.source2_id

      let source1_data = []
      let source2_data = []
      this.runs.forEach(run => {
        if (run.results.length > 0){
          run.results.forEach(result => {
            source1_data.push(result.event1)
            source2_data.push(result.event2)
          })
        }
        if (run.mismatched){
          run.mismatched[Object.keys(run.mismatched)[0]].forEach(item => {
            source1_data.push(item)
          })
          run.mismatched[Object.keys(run.mismatched)[1]].forEach(item => {
            source2_data.push(item)
          })
        }

      })

      let body  = {
        task_id: this.selectedTask.task_id,
        source1_id: this.pairSettings.source1_id,
        source2_id: this.pairSettings.source2_id,
        source1_data: source1_data,
        source2_data: source2_data,
        parameters: settingTemp,
      }

      console.log('The body of the request to the server', body)

      const startTime = Date.now();

      await axios
          .post('/test_task/', JSON.stringify(body))
          .then( response => {
              this.receivedTaskId = response.data.result
              this.getTestMatch(startTime)
          })
          .catch( error => {
            console.log(error)
            ElNotification({
                title: 'Ошибка!',
                message: `Произошла ошибка при отправке запроса на сервер`,
                type: 'error',
                duration: 7500,
            })
          })
      // this.receivedTaskId = 559

    },

    async getTestMatch(startTime){
      await axios
        .get(`pairs/?task_id=${this.receivedTaskId}`)
        .then( response => {
          this.testMatch = response.data.result[0]
          console.log('Received test match task', this.testMatch)

          const endTime = Date.now();
          const timeTaken = endTime - startTime;

          ElNotification({
              title: 'Успешно',
              message: `Запрос занял ${timeTaken} мс`,
              type: 'success',
              duration: 7500,
          })
        })
        .catch( error => {
          console.log('Error:', error)
          ElNotification({
                title: 'Ошибка!',
                message: `Произошла ошибка при запросе нового вызова`,
                type: 'error',
                duration: 7500,
            })
        })
    },

    async saveConfig() {
      try {
        const result = await ElMessageBox.confirm(
            'Вы действительно хотите сохранить параметры? Неверные параметры могут непредсказуемо повлиять на поведение системы',
            'Внимание',
            {
              confirmButtonText: 'Сохранить',
              cancelButtonText: 'Отмена',
              type: 'warning',
            }
        );

        if (result) {
          let body = this.pairNew;
          try {
            this.pairDef = JSON.parse(JSON.stringify(this.pairNew));
            this.settingsChanged = false;
            this.readyToChange = false;
            const response = await axios.post('/config/', JSON.stringify(body));
            console.log('Response:', response.data);
            ElNotification({
              title: 'Успешно!',
              message: 'Новые параметры системы сохранены',
              type: 'success',
              duration: 7500,
            });
          } catch (error) {
            console.log(error);
            ElNotification({
              title: 'Ошибка!',
              message: 'Произошла ошибка при отправке запроса на сервер',
              type: 'error',
              duration: 7500,
            });
          }
        }
      } catch (e) {
        console.log("User cancelled");
      }
    },

    resetConfig(){
      this.pairNew = JSON.parse(JSON.stringify(this.pairDef));
      this.runs = JSON.parse(JSON.stringify(this.defaultRuns));
      this.settingsChanged = false;
      this.readyToChange = false;
    },
  },

  watch: {
    selectedTask:{
          immediate: true,
          handler (newVal) {
            this.runs = newVal.runs
            if(this.runs){
              this.defaultRuns = JSON.parse(JSON.stringify(this.runs));
            }
            // if (this.runs){
            //   this.runs = this.runs.map((run) => {
            //     const json2str = run.results.map((result) => {
            //      return {
            //        result_id: result.result_id,
            //        is_match: result.is_match,
            //        mismatch: result.mismatch,
            //        event1: JSON.stringify(result.event1),
            //        event2: JSON.stringify(result.event2)
            //      }
            //     });
            //
            //     return {
            //       results: json2str,
            //       run_id: run.run_id,
            //       runtime: run.runtime,
            //       sport_id: run.sport_id,
            //       status_observer: run.status_observer,
            //       status_user: run.status_user
            //     };
            //   });
            // }
          }
    },

    pairSettings(newVal){
      this.pairDef = newVal;
      this.pairNew = JSON.parse(JSON.stringify(this.pairDef));
    }

  },

}
</script>

<style scoped>

.content{
  height: 100%;
  display: flex;
  flex-direction: column;
}

.no-content{
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 18px;
}

.tools-block {
  padding: 20px 30px 0;
  display: flex;
  justify-content: space-between;
  overflow: inherit;
  height: 85%;
  flex-basis: 85%;
}

.tools-block-fullscreen{
  height: 88%;
  flex-basis: 88%;
}

.pairs-block {
  flex-basis: 70%;
  width: 70%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.original-comparison{
  flex: 1;
  /*max-height: 50%;*/
  overflow: auto;
  /*border: 1px solid;*/
  /*margin: 5px;*/
  display: flex;
  flex-direction: row;
}

.run-container{
  height: 100%;
}

.run{

}

.json-1{
  flex: 1;
  overflow: auto;
  border: 1px solid;
  margin: 5px;
  /*height: 100%;*/
}

.json-2{
  flex: 1;
  overflow: auto;
  border: 1px solid;
  margin: 5px;
}

.result {
  border: 1px solid;
  padding: 0.5rem;
  margin: 0.5rem 0.5rem 2rem;
}

.result-setting {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
}

.json-input{
  width: 95%!important;
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
}

.no-data-text{
  text-align: center;
  margin-bottom: 20px;
  margin-left: 10px;
  margin-right: 10px;
}

.resulting-comparison{
  height: 50%;
  flex-basis: 50%;
  padding-bottom: 10px;
  overflow: auto;
  border: 1px solid;
  margin: 5px;
}

.help-text {
  height: 50%;
  flex-basis: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.settings-block {
  flex-basis: 30%;
  width: 30%;
  display: flex;
  flex-direction: column;
}

.pair-settings{
  height: 45%;
  flex-basis: 45%;
  display: flex;
  flex-direction: column;
  border: 1px solid;
  margin: 5px;
}

.settings-title{
  flex-basis: 15%;
  height: 15%;
  display: flex;
  text-align: center;
  justify-content: center;
  align-items: center;
  font-weight: bold;
}

.settings{
  flex-basis: 85%;
  height: 85%;
  display: flex;
  flex-direction: column;
  font-size: 12px;
  /* align-content: center; */
  /* overflow: auto; */
  overflow-y: auto;
  overflow-x: hidden;
}

.pair-setting{
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 25%;
  flex-basis: 25%;
}

input[type="number"] {
    width: 50%;
}

.sport-settings{
  height: 45%;
  flex-basis: 45%;
  border: 1px solid;
  margin: 5px;
}

.sport-setting{
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 10px;
}

.pair-setting{
  display: flex;
  flex-direction: column;
  align-items: center;
}

.button-block{
  height: 10%;
  flex-basis: 10%;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  margin: 5px;
}

.compare-button{
  cursor: pointer;
  pointer-events: auto;
  border: 1px solid var(--el-color-success);
  color: var(--el-color-success);
  transition: all 0.1s ease-in-out;
  padding: 5px 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.compare-button:hover {
  background-color: var(--el-color-success);
  color: var(--color-background);
}

.tool-buttons {
  padding: 25px 30px;
  display: flex;
  bottom: 0;
  width: 100%;
  justify-content: space-between;
  flex-basis: 15%;
}

.tools-buttons-fullscreen{
  flex-basis: 12%;
}

.default-button, .save-button, .cancel-button{
  padding: 10px 20px;
}

.sport-container {
  height: 100%;
}

.sport-title{
  text-align: center;
  margin: 10px 0 ;
  font-weight: bold;
  font-size: 18px;
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
  border: 1px solid var(--color-text);
  color: var(--color-background);
  font-size: 13px;
  height: 5rem;
  display: flex;
  text-align: center;
  align-items: center;
  justify-content: center;
  transition: all 0.1s ease-in-out;
}

.danger{
  background-color: var(--el-color-danger);
}

.success {
  background-color: var(--el-color-success);
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

.mismatched-item{
  padding: 20px 30px;
  border: 1px solid var(--color-text);
  background-color: var(--el-color-danger);
  color: var(--color-background);
  height: 5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.1s ease-in-out;
}
</style>