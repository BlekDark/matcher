<template>
  <div class="user-view">
<!--    <div class="navbar">-->
<!--      <div class="title">User Page</div>-->
<!--      <div class="logo-container">-->
<!--        <div class="logo">logo</div>-->
<!--      </div>-->
<!--    </div>-->

    <div class="main-block">
      <div class="source-block">
        <SourceComponent
            :currentMode="this.mode"
            :items="sources"
            endpoint="tasks"
            @dataReceived="dataProcess"
            @dateTimeRangeChanged="dateTimeRangeChange"
            @itemsSelected="itemsSelected"
        />
      </div>

      <div class="call-block">
        <CallComponent
            :currentMode="this.mode"
            :data="receivedData"
            :dateTimeRange="this.dateTimeRange"
            @taskSelected="taskProcess"
        />
      </div>

      <div class="results-block"
           :class="{'results-fullscreen': this.fullscreen}">
        <div class="filters-block"
             :class="{'removed': this.fullscreen}">
          <FiltersComponent
              :currentMode="this.mode"
              :modeFilter="this.modeFilter"
              :sportTypes="this.sportTypes"
              :isTaskSelected="this.isTaskSelected"
              @sportFilterChange="changeSportFilter"
              @modeFilterChange="changeModeFilter"
          />
        </div>

        <div class="statistic-block"
             :class="{'statistic-fullscreen': this.fullscreen}">
          <StatisticComponent
              :selectedItems="this.selectedItems"
              :selectedTask="this.selectedTask"
              :taskIsLoading="this.taskIsLoading"
              :modeFilter="this.modeFilter"
              :sportFilter="this.sportFilter"
              :sportTypesAll="this.sportTypesAll"
              :fullscreen="this.fullscreen"
              @fullscreenButtonCLick="fullscreenClick"
              @dataSent="dataSent"
          />
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import SourceComponent from "@/components/SourceComponent.vue";
import CallComponent from "@/components/CallComponent.vue";
import FiltersComponent from "@/components/FiltersComponent.vue";
import StatisticComponent from "@/components/StatisticComponent.vue";
import axios from 'axios';
import { ElNotification } from 'element-plus';

export default {
  name: "UserView",
  components: {
    SourceComponent,
    CallComponent,
    FiltersComponent,
    StatisticComponent,
  },
  data() {
    return {
      mode: 0,
      sources: [],
      sportTypesAll: [],
      sportTypes: [],
      receivedData: '',
      selectedTask: '',
      selectedItems: {},
      isTaskSelected: false,
      taskIsLoading: false,
      dateTimeRange: {},
      sportFilter: {'allSport': true, 'sport': null},
      modeFilter: 0,
      fullscreen: false
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
            console.log('Sources successfully loaded')
            // console.log(this.sources)
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
      this.receivedData = data.tasks
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
            this.isTaskSelected = true
            this.taskIsLoading = false
            this.modeFilter = 1

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
      console.log(data)
    },

    changeSportFilter(data){
      this.sportFilter = data
    },

    changeModeFilter(data){
      this.modeFilter = data
    },

    fullscreenClick(){
      this.fullscreen = !this.fullscreen
    },

    itemsSelected(data){
      this.selectedItems = data
    },

    async dataSent(){
      console.log('requesting updated task')
      await axios
          .get(`/pairs/?task_id=${this.selectedTask.task_id}`)
          .then(response => {
            this.selectedTask = response.data.result[0]

             let sports = this.selectedTask.runs.map(function(run){
              return run.sport_id
            })

            this.sportTypes = this.sportTypesAll.filter(subarr => sports.includes(subarr[0]));
            console.log('New requested Task')
            console.log(response.data.result[0])
          })
          .catch(error => {
            console.error('Error:', error);
            ElNotification({
                title: 'Ошибка!',
                message: `Произошла ошибка при повторном запросе данных вызова`,
                type: 'error',
                duration: 7500,
            })
          });

      console.log(this.selectedItems)
      let request = `?source1_id=${this.selectedItems["1"].source_id}&source2_id=${this.selectedItems["2"].source_id}`

      console.log('requesting updated tasks')
      const fetchResults = async () => {
        try {
          const response = await axios.get(`tasks/${request}`);

          console.log(response.data)
          if (response.data.status_code === 200) {
            // console.log()
            this.$emit('dataReceived', response.data.result);
          } else {
            this.$emit('dataReceived', []);
          }
        } catch (error) {
          console.log(error)
          ElNotification({
                title: 'Ошибка!',
                message: `Произошла ошибка при фоновом запросе вызовов`,
                type: 'error',
                duration: 7500,
            })
        }
      }
      await fetchResults();

    },
  }
}
</script>

<style scoped>
.main-block {
  height: 87vh;
}

/*.results-fullscreen{  */
/*  margin: 0;*/
/*}*/

</style>

<style>
.el-notification .el-notification__closeBtn {
  top: 7px!important;
  right: 0!important;
}

.el-notification__group {
   flex: 1;
}
</style>