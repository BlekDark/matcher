<template>
  <div class="title">Настройки системы</div>
  <div class="settings-block">
    <div class="settings-container">
      <div class="general-settings" :class="{'fullscreen-settings': this.fullscreen}">
        <div class="settings-title">
          Общие параметры системы
        </div>
        <div
            v-if="generalSettings"
            class="settings"
            :class="{'fullscreen-settings': this.fullscreen}"
        >
          <div class="margin">
            <div v-for="key in sortedGeneralSettings">
                <span :title="key" class="setting-title">{{ key }}</span>
                <br>
                <input type="number" v-model="generalNew[key]" @input="processGeneralInput(key)" min="0" max="100">
            </div>
          </div>

        </div>
        <div v-else style="margin: 15px 0">
          Нет данных для отображения
        </div>

      </div>

      <div class="pair-settings" :class="{'fullscreen-settings': this.fullscreen}">
        <div class="settings-title">
          Параметры пары источников
        </div>
        <div
            v-if="pairSettings"
            class="settings"
            :class="{'fullscreen-settings': this.fullscreen}"
        >
          <div class="margin">
            <div v-for="key in sortedPairSettings">
              <div v-if="key !== 'source1_id' && key !== 'source2_id' && key !== 'types' && key !== 'default'">
                <span :title="key" class="setting-title">{{ key }}</span>
                <br>
                <input type="number" v-model="pairNew[key]" @input="processPairInput(key)" min="0" max="100">
              </div>
            </div>
          </div>
        </div>
        <div v-else style="margin: 15px 0">
          Нет данных для отображения
        </div>
      </div>

      <div class="sport-settings" :class="{'fullscreen-settings': this.fullscreen}">
      <div class="settings-title">
        Параметры видов спорта
      </div>
      <div
          v-if="pairSettings && JSON.stringify(pairNew['types']) !== '{}'"
          class="settings"
          :class="{'fullscreen-settings': this.fullscreen}"
      >
        <div class="margin">
          <div
              v-if="sportFilterSettings.allSport"
              v-for="(type, key) in pairNew.types"
              style="margin-bottom: 10px;"
          >
              <span :title="getSportTitle(key)" class="settings-title">{{ getSportTitle(key) }}</span>
              <br>
              <div v-for="settingKey in this.sortedTypeSettings(type)">
                <span :title="settingKey" class="setting-title">{{ settingKey }}</span>
                <br>
                <input type="number" v-model="pairNew.types[key][settingKey]" @input="processInputAllSport(key, settingKey)" min="0" max="100">
              </div>
          </div>

          <div v-else>
            <div v-if="pairNew.types[sportFilterSettings.sport]">
              <span :title="getSportTitle(sportFilterSettings.sport)" class="settings-title">{{ getSportTitle(sportFilterSettings.sport) }}</span>
              <br>
               <div v-for="key in this.sortedTypeSettings(pairNew.types[sportFilterSettings.sport])">
                 <span :title="key" class="setting-title">{{ key }}</span>
                 <br>
                 <input type="number" v-model="pairNew.types[sportFilterSettings.sport][key]" @input="processInputSport(key)" min="0" max="100">
               </div>
            </div>

            <div v-else>
              Нет данных для отображения
            </div>
          </div>
        </div>
        <div v-if="this.pairDef.types && sportFilterSettings.allSport && this.undefinedSportConfig().length > 0"
             class="add-block"
        >
          <el-select
          v-model="selectedType"
          size="small"
          collapse-tags
          collapse-tags-tooltip
          :max-collapse-tags="3"
          placeholder="Выберите спорт"
          style="width: 177px"
          clearable
        >
          <el-option
            v-for="type in this.undefinedSportConfig()"
            :key="type[0]"
            :label="type[1]"
            :value="type[0]"
          />
        </el-select>
          <div class="add-button"
               :class="this.selectedType ? 'success-button' : 'disabled-button'"
               @click="addSportConfig"
          >
            Добавить настройки для вида спорта</div>
        </div>
      </div>

      <div v-else style="margin: 15px 0">
        Нет данных для отображения
        <div v-if="this.pairNew.types && sportFilterSettings.allSport && this.undefinedSportConfig().length > 0"
             class="add-block"
        >
          <el-select
          v-model="selectedType"
          size="small"
          collapse-tags
          collapse-tags-tooltip
          :max-collapse-tags="3"
          placeholder="Выберите спорт"
          style="width: 177px"
          clearable
        >
          <el-option
            v-for="type in this.undefinedSportConfig()"
            :key="type[0]"
            :label="type[1]"
            :value="type[0]"
          />
        </el-select>
          <div class="add-button"
               :class="this.selectedType ? 'success-button' : 'disabled-button'"
               @click="addSportConfig"
          >
            Добавить настройки для вида спорта</div>
        </div>
      </div>
    </div>

    </div>
  </div>

  <div class="settings-buttons">
    <div class="controls">
      <div class="save-button"
           :class="readyToChange ? 'success-button' : 'disabled-button'"
           @click="sendConfig"
      >
        Сохранить новые параметры
      </div>
      <div class="cancel-button"
           :class="settingsChanged ? 'danger-button' : 'disabled-button'"
           @click="resetConfig"
      >
        Отмена
      </div>
    </div>


    <div
        v-if="!fullscreen"
        class="default-button"
        @click="onButtonClick()">
      Развернуть на весь экран
    </div>
    <div
        v-else
        class="default-button"
        @click="onButtonClick()">
      Свернуть
    </div>
  </div>



</template>

<script>
import axios from "axios";
import { ElNotification, ElMessageBox } from 'element-plus';

export default {
  name: "SettingsComponent",
  props: [
    'fullscreen',
    'generalSettings',
    'pairSettings',
    'sportFilterSettings',
    'sportTypesDef',
    'sportTypes',
    'sportTypesAll',
  ],
  emits: [
      'fullscreenButtonCLick',
      'newSportTypes',
      'restartSportFilter'
  ],
  data(){
    return{
      pairDef: [],
      pairNew: {},

      generalDef: [],
      generalNew: [],

      sportTypesNew:[],

      currentTypesList: [],
      selectedType: '',

      settingsChanged: false,
      readyToChange: false,
      sportTypeAdded: false,

      sportFilter: this.sportFilterSettings,
    }
  },
  methods: {
    onButtonClick(){
      this.$emit('fullscreenButtonCLick');
    },

    processGeneralInput(key){
      const intValue = parseFloat(this.generalNew[key]);
      if (!isNaN(intValue)) {
        this.generalNew[key] = intValue
      }

      if(this.sportTypeAdded){
        this.settingsChanged = true
        this.readyToChange = true
      } else {
        this.settingsChanged = this.generalDef[key] !== this.generalNew[key];
        this.readyToChange = this.generalDef[key] !== this.generalNew[key];
      }

      this.zeroFieldsCheck()
    },

    processPairInput(key){
      const intValue = parseFloat(this.pairNew[key]);
      if (!isNaN(intValue)) {
        this.pairNew[key] = intValue
      }
      if(this.sportTypeAdded){
        this.settingsChanged = true
        this.readyToChange = true
      } else {
        this.settingsChanged = this.pairDef[key] !== this.pairNew[key];
        this.readyToChange = this.pairDef[key] !== this.pairNew[key];
      }

      this.zeroFieldsCheck()

      // for (let key in this.pairNew) {
      //  if (typeof this.pairNew[key] === "undefined" || this.pairNew[key] === "") {
      //     this.readyToChange = false
      //   }
      // }
    },
    processInputAllSport(key, settingKey){
      const intValue = parseFloat(this.pairNew.types[key][settingKey]);
      if (!isNaN(intValue)) {
        this.pairNew.types[key][settingKey] = intValue
      }
      if(this.sportTypeAdded){
        this.settingsChanged = true
        this.readyToChange = true
      } else {
        this.settingsChanged = this.pairDef.types[key][settingKey] !== this.pairNew.types[key][settingKey];
        this.readyToChange = this.pairDef.types[key][settingKey] !== this.pairNew.types[key][settingKey];
      }

      this.zeroFieldsCheck()

      // for (let settingKey in this.pairNew.types[key]) {
      //  if (typeof this.pairNew.types[key][settingKey] === "undefined" || this.pairNew.types[key][settingKey] === "") {
      //     this.readyToChange = false
      //   }
      // }
    },
    processInputSport(key){
      const intValue = parseFloat(this.pairNew.types[this.sportFilterSettings.sport][key]);
      if (!isNaN(intValue)) {
        this.pairNew.types[this.sportFilterSettings.sport][key] = intValue
      }
      if(this.sportTypeAdded){
        this.settingsChanged = true
        this.readyToChange = true
      } else {
        this.settingsChanged = this.pairDef.types[this.sportFilterSettings.sport][key] !== this.pairNew.types[this.sportFilterSettings.sport][key];
        this.readyToChange = this.pairDef.types[this.sportFilterSettings.sport][key] !== this.pairNew.types[this.sportFilterSettings.sport][key];
      }

      this.zeroFieldsCheck()

      // for (let key in this.pairNew.types[this.sportFilterSettings.sport]) {
      //  if (typeof this.pairNew.types[this.sportFilterSettings.sport][key] === "undefined" ||
      //      this.pairNew.types[this.sportFilterSettings.sport][key] === "") {
      //     this.readyToChange = false
      //   }
      // }
    },
    zeroFieldsCheck(){
      for (let key in this.generalNew) {
        if (typeof this.generalNew[key] === "undefined" || this.generalNew[key] === "") {
          this.readyToChange = false
        }
      }

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


          for (let key in this.pairNew.types[this.sportFilterSettings.sport]) {
            if (typeof this.pairNew.types[this.sportFilterSettings.sport][key] === "undefined" ||
                this.pairNew.types[this.sportFilterSettings.sport][key] === "") {
              this.readyToChange = false
            }
          }
        }


      }
    },

    resetConfig(){
      this.generalNew = JSON.parse(JSON.stringify(this.generalDef));
      this.pairNew = JSON.parse(JSON.stringify(this.pairDef));
      this.settingsChanged = false;
      this.readyToChange = false;

      if (this.pairDef.types){
        let keys = Object.keys(this.pairDef.types)
        if (keys.length > 0){
          this.currentTypesList = keys.map(key => {
            return parseInt(key)
          })
        } else {
          this.currentTypesList = []
        }

        this.sportTypesNew = this.sportTypesDef
        this.$emit('newSportTypes', this.sportTypesDef)
        this.$emit('restartSportFilter')
      }

    },

    async sendConfig() {
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
          try {
            let body = this.pairNew

            if (this.generalDef !== this.generalNew){
              body.default = this.generalNew
            } else {
              delete body['default']
            }

            console.log(JSON.stringify(body))
            await axios
                .post('/config/', body)
                .then(response => {
                  console.log('Response:', response.data);
                  this.generalDef = JSON.parse(JSON.stringify(this.generalNew));
                  this.pairDef = JSON.parse(JSON.stringify(this.pairNew));

                  this.settingsChanged = false;
                  this.readyToChange = false;
                })
                .catch(error => {
                  console.error('Error:', error);
                  ElNotification({
                      title: 'Ошибка!',
                      message: `Произошла ошибка при отправке запроса на сервер`,
                      type: 'error',
                      duration: 7500,
                  })
                });
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

    getSportTitle(key){
      return this.sportTypesNew.find(item => item[0] == key)[1]
    },

    undefinedSportConfig(){
      return this.sportTypesAll.filter(item => !this.currentTypesList.includes(item[0]))
    },

    addSportConfig(){
      this.currentTypesList.push(this.selectedType)
      this.pairNew.types[this.selectedType] = {}
      this.pairNew.types[this.selectedType] = this.generalDef
      this.sportTypesNew = this.sportTypesAll.filter(item => this.currentTypesList.includes(item[0]))
      this.$emit('newSportTypes', this.sportTypesNew)

      this.settingsChanged = true
      this.readyToChange = true
      this.sportTypeAdded = true
      this.zeroFieldsCheck()
      this.selectedType = ''
    },

    sortedTypeSettings(type){
      return Object.keys(type).sort();
    }
  },
  computed: {
    sortedGeneralSettings() {
      return Object.keys(this.generalNew).sort();
    },

    sortedPairSettings() {
      return Object.keys(this.pairNew).sort();
    },


  },
  watch: {
    pairSettings(newVal) {
      this.pairDef = newVal;
      this.pairNew = JSON.parse(JSON.stringify(this.pairDef));

      let keys = Object.keys(newVal.types)
      if (keys.length > 0){
        this.currentTypesList = keys.map(key => {
          return parseInt(key)
        })
      } else {
        this.currentTypesList = []
      }
    },

    generalSettings(newVal) {
      this.generalDef = newVal;
      this.generalNew = JSON.parse(JSON.stringify(this.generalDef));
    },

    sportTypes(newVal) {
      this.sportTypesNew = JSON.parse(JSON.stringify(newVal));
    },

    sportFilterSettings(newVal) {
      this.sportFilter = newVal
    },

    // sportTypesAll:{
    //   immediate: true,
    //   handler (newVal) {
    //     this.sportTypes = newVal
    //     console.log(this.sportTypes)
    //   }
    // },

  },
}
</script>

<style scoped>
.title {
  text-align: center;
  font-weight: bold;
  font-size: 18px;
  height: 8%;
  flex-basis: 8%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.settings-block{
  padding: 20px 30px;
  height: 75%;
  flex: 1;
}

.settings-container{
  height: 100%;
  display: flex;
  justify-content: space-between;
}

.general-settings, .pair-settings, .sport-settings{
  width: 33%;
  border: 1px solid var(--color-text);
  /*padding: 20px;*/
  text-align: center;
  display: flex;
  flex-direction: column;
}

.settings-title{
  font-weight: bold;
  margin: 20px 20px 0 20px;
  height: 15%;
  flex-basis: 15%;
}

.settings {
  overflow: auto;
  padding-top: 15px;
  height: 85%;
  flex-basis: 85%;
}

.fullscreen-settings{

}

.margin{
  margin-bottom: 10px;
}

.setting-title{
  font-size: 12px;
}

.settings-buttons {
  padding: 20px 30px;
  display: flex;
  bottom: 0;
  width: 100%;
  justify-content: space-between;
}

.add-block{
  margin-top: 40px;
}

.add-button{
  margin: 20px 20px!important;
  font-size: 14px;
}

.compare-button{
  bottom: 30px!important;
}

input[type="number"] {
    width: 60%;
}
</style>
