<template>
  <div v-if="!this.taskIsLoading && this.selectedTask" class="content">
    <div class="title"
         :title="titleText(selectedTask)"
    >
      Вызов {{ selectedTask.task_id }}
    </div>

      <MatchedBlock
          v-if="modeFilter === 1"
          :selectedTask.sync="selectedTask"
          :modeFilter="modeFilter"
          :sportFilter="sportFilter"
          :sportTypesAll="sportTypesAll"
          :fullscreen="fullscreen"
          @fullscreenButtonCLick="fullscreenButtonCLick"
          @dataSent="dataSent"
      />
    <!--      @taskChanged="taskChanged"-->
      <MismatchedBlock
          v-if="modeFilter === 2"
          :selectedItems="selectedItems"
          :selectedTask.sync="selectedTask"
          :modeFilter="modeFilter"
          :sportFilter="sportFilter"
          :sportTypesAll="sportTypesAll"
          :fullscreen="fullscreen"
          @fullscreenButtonCLick="fullscreenButtonCLick"
          @dataSent="dataSent"
      />
    <!-- @taskChanged="taskChanged"-->
      <AllMatchBlock
        v-if="modeFilter === 3"
        :selectedTask.sync="selectedTask"
        :modeFilter="modeFilter"
        :sportFilter="sportFilter"
        :sportTypesAll="sportTypesAll"
        :fullscreen="fullscreen"
        @fullscreenButtonCLick="fullscreenButtonCLick"
    />
    </div>
  <div v-else-if="this.taskIsLoading" class="no-content">
    Вызов загружается, пожалуйста, подождите..
  </div>
  <div v-else class="no-content">
    Выберите вызов, чтобы продолжить..
  </div>
</template>

<script>
import MatchedBlock from "@/components/userPage/statisticComponent/MatchedBlock.vue";
import MismatchedBlock from "@/components/userPage/statisticComponent/MismatchedBlock.vue";
import AllMatchBlock from "@/components/userPage/statisticComponent/AllMatchBlock.vue";
import axios from "axios";

export default {
  name: "StatisticView",
  props: [
    'selectedItems',
    'selectedTask',
    'taskIsLoading',
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
  components: {
    MatchedBlock,
    MismatchedBlock,
    AllMatchBlock,
  },
  data() {
    return{

    }
  },
  methods: {
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
    fullscreenButtonCLick(){
      this.$emit('fullscreenButtonCLick')
    },

    dataSent(){
      this.$emit('dataSent')
    }
  }
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

.title {
  text-align: center;
  font-weight: bold;
  font-size: 18px;
  height: 7%;
  flex-basis: 7%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
</style>