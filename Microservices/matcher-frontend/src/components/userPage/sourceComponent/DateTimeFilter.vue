<template>
<!--<div class="demo-date-picker">-->
<!--    <div class="block">-->
<!--      <p>Component value：{{ value }}</p>-->
<!--      <el-date-picker-->
<!--        v-model="value"-->
<!--        type="daterange"-->
<!--        start-placeholder="Start date"-->
<!--        end-placeholder="End date"-->
<!--        :default-time="defaultTime"-->
<!--      />-->
<!--    </div>-->
<!--  </div>-->
  <div class="filter-block-second">
    <span class="demonstration">Отфильтровать вызовы по времени</span>
    <el-date-picker
      v-model="value"
      type="datetimerange"
      :shortcuts="shortcuts"
      start-placeholder="Начальная дата"
      end-placeholder="Конечная дата"
      size="small"
      @change="filterChanged()"
      format="DD-MM-YYYY HH:mm:ss"
      value-format="x"
    />
  </div>
</template>

<script>
export default {
  name: "DateTimeFilter",
  emits: [
    'dateTimeFilterChange'
  ],
  data(){
    return{
      value: [],
      // defaultTime: [new Date(2000, 1, 1, 0, 0, 0),
      //               new Date(2023, 2, 1, 23, 59, 59),
      // ],
      shortcuts:[
        {
          text: '15 минут',
          value: () => {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 60 * 1000 * 15)
            return [start, end]
          },
        },
        {
          text: '30 минут',
          value: () => {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 60 * 1000 * 30)
            return [start, end]
          },
        },
        {
          text: '1 час',
          value: () => {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000)
            return [start, end]
          },
        },
        {
          text: '4 часа',
          value: () => {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 4)
            return [start, end]
          },
        },
        {
          text: '12 часов',
          value: () => {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 12)
            return [start, end]
          },
        },
        {
          text: '1 день',
          value: () => {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24)
            return [start, end]
          },
        },
          {
          text: 'Сегодня',
          value: () => {
            const end = new Date()
            const start = new Date()
            start.setHours(0, 0, 0, 0)
            return [start, end]
          },
        },

        {
          text: 'Вчера',
          value: () => {
            const end = new Date()
            const start = new Date()
            start.setHours(0, 0, 0, 0)
            start.setDate(start.getDate() - 1)
            end.setHours(0, 0, 0, 0)
            return [start, end]
          },
        },
        {
          text: 'Эта неделя',
          value: () => {
            const end = new Date()
            const start = new Date()
            start.setHours(0, 0, 0, 0)
            start.setDate(start.getDate() - start.getDay())
            return [start, end]
          },
        },
        {
          text: 'Прошлая неделя',
          value: () => {
            const end = new Date()
            const start = new Date()
            start.setHours(0, 0, 0, 0)
            start.setDate(start.getDate() - start.getDay() - 7)
            end.setHours(0, 0, 0, 0)
            end.setDate(end.getDate() - end.getDay())
            return [start, end]
          },
        },
        {
          text: 'Месяц',
          value: () => {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
            return [start, end]
          },
        },
        {
          text: '3 месяца',
          value: () => {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
            return [start, end]
          },
        },
      ]
    }
  },
  methods:{
    filterChanged(){
      if (this.value){
        localStorage.setItem('timeFilter1', this.value[0])
        localStorage.setItem('timeFilter2', this.value[1])
        this.$emit('dateTimeFilterChange', this.value);
      } else {
        localStorage.setItem('timeFilter1', '')
        localStorage.setItem('timeFilter2', '')
        this.$emit('dateTimeFilterChange', []);
      }
    }
  },
  mounted() {
    let timeFilter1 = localStorage.getItem('timeFilter1')
    let timeFilter2 = localStorage.getItem('timeFilter2')


    if (timeFilter1 && timeFilter2) {
      this.value = [
        parseInt(timeFilter1),
        parseInt(timeFilter2),
      ]
      this.$emit('dateTimeFilterChange', this.value);
    }
  }
}
</script>

<style scoped>
.filter-block-second {
  text-align: center;
  height: 15%;
  flex-basis: 15%;
}

.filter-block-second .demonstration {
  display: block;
  margin-bottom: 10px;
}



</style>

<style>
.el-picker-panel__body {
    margin-left: 150px!important;
}

.el-picker-panel__sidebar{
  width: 150px!important;
}

.el-date-editor .el-range-input {
  width: 32%!important;
  min-width: 115px;
}

.el-date-editor .el-range-separator {
  flex: 0!important;
}

.el-date-editor.el-input__wrapper {
  width: 310px!important;
}
</style>