<template>
  <div class="user-view">
<!--    <div class="navbar">-->
<!--      <div class="title">Observer Page</div>-->
<!--      <div class="logo-container">-->
<!--        <div class="logo">logo</div>-->
<!--      </div>-->
<!--    </div>-->

    <div class="mode-block">
      <div class="mode-item"
           :class="{'enabled': this.mode === 1, 'disabled-button': true}"
           @click="this.switchMode(1)">
        Просмотр автоматического мэтчинга
      </div>
      <div class="mode-item"
           :class="{'enabled': this.mode === 2}"
           @click="this.switchMode(2)">
        Обзор обработанных пользователем пар
      </div>
      <div class="mode-item"
           :class="{'enabled': this.mode === 3}"
           @click="this.switchMode(3)">
        Проверка json
      </div>
      <div class="mode-item"
           :class="{'enabled': this.mode === 4}"
           @click="this.switchMode(4)">
        Настройка параметров системы
      </div>
      <div class="mode-item"
           :class="{'enabled': this.mode === 5}"
           @click="this.switchMode(5)">
        Статистика
      </div>
    </div>


    <div  class="main-block">
      <div v-if="mode !== 5" class="source-block">
        <SourceComponent
            :currentMode="this.mode"
            :items="sources"
            :endpoint="currentEndpoint"
            @dataReceived="dataProcess"
            @dateTimeRangeChanged="dateTimeRangeChange"
            @itemsSelected="itemsSelected"
        />
      </div>

      <div v-if="mode !== 4 && mode !== 5" class="call-block">
        <CallComponent
            :currentMode="this.mode"
            :data="receivedData.tasks"
            :dateTimeRange="this.dateTimeRange"
            @taskSelected="taskProcess"
        />
      </div>

      <AutoMatch v-if="mode === 1"/>
      <UserModeration v-if="mode === 2"
                      :selectedTask="this.selectedTask"
                      :receivedData="this.receivedData.config"
                      :sportTypesAll="this.sportTypesAll"
                      :sportTypes="this.sportTypes"
                      :taskIsLoading="this.taskIsLoading"
      />
      <JsonEditor v-if="mode === 3"
                  :selectedTask="this.selectedTask"
                  :receivedData="this.receivedData.config"
                  :sportTypesAll="this.sportTypesAll"
                  :sportTypes="this.sportTypes"
                  :taskIsLoading="this.taskIsLoading"
      />
      <Settings
          v-if="mode === 4"
          :receivedData="this.receivedData.config"
          :sportTypesAll="this.sportTypesAll"
      />

      <Statistic
          v-if="mode === 5"
      />
    </div>
  </div>
</template>

<script>
import SourceComponent from "@/components/SourceComponent.vue";
import CallComponent from "@/components/CallComponent.vue";
import AutoMatch from "@/components/observerPage/AutoMatch.vue";
import UserModeration from "@/components/observerPage/UserModeration.vue";
import JsonEditor from "@/components/observerPage/JsonEditor.vue";
import Settings from "@/components/observerPage/Settings.vue";
import Statistic from "@/components/observerPage/Statistic.vue";
import axios from "axios";
import { ElNotification } from 'element-plus';

export default {
  name: "ObserverView",
  components: {
    SourceComponent,
    CallComponent,
    AutoMatch,
    UserModeration,
    JsonEditor,
    Settings,
    Statistic
  },
  data() {
    return {
      mode: 2,
      sources: [],
      sportTypesAll: [],
      sportTypes: [],
      receivedData: '',
      selectedTask: '',
      taskIsLoading: false,
      isTaskSelected: false,
      selectedItems: {},
      dateTimeRange: {},
    }
  },
  beforeMount() {
    this.getSources()
    this.getTypes()
  },
  methods: {
    async getSources(){
      await axios
          .get('source/')
          .then(response => {
            this.sources = response.data.result
          })
          .catch(error => {
            console.log(error)
            ElNotification({
                title: 'Ошибка!',
                message: `Произошла ошибка при запросе источников`,
                type: 'error',
                duration: 7500,
            })
          })
    },

    async getTypes(){
      await axios
          .get('types/')
          .then(response => {
            this.sportTypesAll = response.data.result
            console.log('Types successfully loaded')

            const resultMap = new Map();

            for (const arr of this.sportTypesAll) {
              const key = arr[1];
              const value = arr[2];

              if (resultMap.has(key)) {
                if (value === "1") {
                  resultMap.set(key, true);
                }
              } else {
                resultMap.set(key, value === 1);
              }
            }

            const resultArray = [];

            for (const arr of this.sportTypesAll) {
              const key = arr[1];
              const value = arr[2];

              if (resultMap.get(key) && value === "1") {
                resultArray.push([arr[0], `${key} (cyber)`]);
              } else {
                resultArray.push([arr[0], key]);
              }
            }

            this.sportTypesAll = resultArray
            console.log('Список всех видов спорта', resultArray);
          })
          .catch(error => {
            console.log(error)
            ElNotification({
                title: 'Ошибка!',
                message: `Произошла ошибка при запросе видов спорта`,
                type: 'error',
                duration: 7500,
            })
          })
    },

    dataProcess(data){
      this.receivedData = data

      console.log('result_container', data)
      // console.log(this.receivedData)
    },

    async taskProcess(task){
      this.taskIsLoading = true
      const start = Date.now();

      await axios
        .get(`pairs/?task_id=${task.task_id}`)
        .then( response => {
          this.selectedTask = response.data.result[0]

          const end = Date.now();
          const timeTaken = end - start;

          ElNotification({
              title: 'Успешно',
              message: `Запрос занял ${timeTaken} мс`,
              type: 'success',
              duration: 7500,
          })

          let sports = this.selectedTask.runs.map(function(run){
            return run.sport_id
          })

          this.sportTypes = this.sportTypesAll.filter(subarr => sports.includes(subarr[0]));

          console.log(this.selectedTask)
          this.taskIsLoading = false
          this.isTaskSelected = true
        })
        .catch( error => {
          console.log('Error:', error)
          ElNotification({
              title: 'Ошибка!',
              message: `Произошла ошибка при запросе данных вызова`,
              type: 'error',
              duration: 7500,
          })
          this.taskIsLoading = false
        })
    },

    dateTimeRangeChange(data){
      this.dateTimeRange = data
      // console.log(data)
    },

    itemsSelected(data){
      this.selectedItems = data
    },

    switchMode(mode){
      this.mode = mode
      this.selectedTask = ''
    }
  },
  computed: {
    currentEndpoint(){
      switch (this.mode){
        case 1:
          return 'default1'
        case 2:
          return 'tasks'
        case 3:
          return 'tasks'
        case 4:
          return 'config'
        case 5:
          return 'statistic'
      }
    },
    currentMode(mode){
      if (this.mode === mode){
        return true
      }
    },
  }
}
</script>

<style scoped>
.main-block{
  height: 90%;
  max-height: 90%;
  flex-basis: 90%;
}
</style>