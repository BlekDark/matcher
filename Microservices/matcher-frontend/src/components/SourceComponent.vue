<template>
  <div class="title">Выбор источника</div>

  <div class="source-component">

    <div class="filter-block">
      <span class="demonstration">Отфильтровать источники по дате последнего вызова</span>

      <el-select
          v-model="selectedTimestampOption"
          class="m-2"
          placeholder="Выберите время"
          clearable
          size="small"
          @change="lastFilterChange()"
      >
        <el-option
          v-for="item in timestampOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
    </div>

    <div class="sources">
      <SourceBlock
          :number="1"
          :items="filteredItems1"
          @itemSelected="onItemSelected1"
          @filterInput="onFilterInput1"/>
      <SourceBlock
          :number="2"
          :items="filteredItems2"
          @itemSelected="onItemSelected2"
          @filterInput="onFilterInput2"/>
    </div>

<!--    <div class="filter">-->
      <DateTimeFilter v-if="this.currentMode !== 4" @dateTimeFilterChange="onDateTimeFilterChange"/>
<!--    </div>-->

    <div class="compare-block">
      <div class="compare-button"
         :class="compareButtonStatus ? 'success-button' : 'disabled-button'"
         @click="compareSources">
        Сравнить пару источников
      </div>
    </div>

  </div>
</template>

<script>
import DateTimeFilter from "@/components/userPage/sourceComponent/DateTimeFilter.vue";
import SourceBlock from "@/components/userPage/sourceComponent/SourceBlock.vue";
import axios from "axios";
import { ElNotification } from 'element-plus';
import { mapState, mapMutations, mapGetters } from 'vuex'
import {createElementBlock} from "vue";

export default {
  name: "SourceComponent",
  components: {
    DateTimeFilter,
    SourceBlock,
  },
  props: [
    'items',
    'endpoint',
    'currentMode',
  ],
  emits: [
    'dataReceived',
    'dateTimeRangeChanged',
    'itemsSelected',
  ],
  data(){
    return{
      selectedItems: {
        1: null,
        2: null,
      },
      filterInput1: '',
      filterInput2: '',
      selectedTimestampOption: null,
      timestampOptions: [
        { label: '15 минут', value: 15 },
        { label: '30 минут', value: 30 },
        { label: '1 час', value: 60 },
        { label: '4 часа', value: 60 * 4 },
        { label: '12 часов', value: 60 * 12 },
        { label: '24 часа', value: 60 * 24 },
        { label: 'Неделя', value: 60 * 24 * 7 },
        { label: 'Месяц', value: 60 * 24 * 30 },
        { label: '3 месяца', value: 60 * 24 * 90 },
      ],

      // dateTimeStamp1: '',
      // dateTimeStamp2: '',
      result_container: {},
      intervalId: null,
    }
  },
  computed: {

    filteredItems1() {
      let filteredItems = this.filterItemsBySelectionAndName(this.items, this.selectedItems[2], this.filterInput1);

      // if (this.dateTimeStamp1 && this.dateTimeStamp2) {
      //   filteredItems = filteredItems.filter(item => {
      //     const timestamp = new Date(item.timestamp).getTime();
      //     return timestamp >= this.dateTimeStamp1 && timestamp <= this.dateTimeStamp2;
      //   });
      // }

      if(this.selectedTimestampOption){
        const now = new Date()
        const lastTimestamp = new Date(now.getTime() - (this.selectedTimestampOption * 60 * 1000));

        filteredItems = filteredItems.filter(source => {
          const sourceTimestamp = new Date(source.timestamp)
            return (sourceTimestamp - sourceTimestamp.getTimezoneOffset() * 60 * 1000) >= lastTimestamp
        })
      }

      if (this.selectedItems[1] && !filteredItems.includes(this.selectedItems[1])) {
        filteredItems.unshift(this.selectedItems[1])
      }

      return filteredItems;
    },

    filteredItems2() {
      let filteredItems = this.filterItemsBySelectionAndName(this.items, this.selectedItems[1], this.filterInput2);

      // if (this.dateTimeStamp1 && this.dateTimeStamp2) {
      //   filteredItems = filteredItems.filter(item => {
      //     const timestamp = new Date(item.timestamp).getTime();
      //     return timestamp >= this.dateTimeStamp1 && timestamp <= this.dateTimeStamp2;
      //   });
      // }

      if(this.selectedTimestampOption){
        const now = new Date()
        const lastTimestamp = new Date(now.getTime() - (this.selectedTimestampOption * 60 * 1000));

        filteredItems = filteredItems.filter(source => {
          const sourceTimestamp = new Date(source.timestamp)
            return (sourceTimestamp - sourceTimestamp.getTimezoneOffset() * 60 * 1000) >= lastTimestamp
        })
      }

      if (this.selectedItems[2] && !filteredItems.includes(this.selectedItems[2])) {
        filteredItems.unshift(this.selectedItems[2])
      }

      return filteredItems;
    },

    compareButtonStatus() {
      return (this.selectedItems[1] != null && this.selectedItems[2] != null)
    },

  },
  methods: {

    onItemSelected1(item) {
      if (this.selectedItems[1] === item) {
        // deselect item if it was already selected
        this.selectedItems[1] = null;
      } else if (this.selectedItems[2] !== item) {
        // select item
        this.selectedItems[1] = item;
        localStorage.setItem('selectedSource1', item.source_id)
      }
      this.$emit('itemsSelected', this.selectedItems)
    },
    onItemSelected2(item) {
      if (this.selectedItems[2] === item) {
        // deselect item if it was already selected
        this.selectedItems[2] = null;
      } else if (this.selectedItems[1] !== item) {
        // select item
        this.selectedItems[2] = item;
        localStorage.setItem('selectedSource2', item.source_id)
      }
      this.$emit('itemsSelected', this.selectedItems)
    },


    onFilterInput1(input){
      this.filterInput1 = input
      // this.setFilterInput1(input)
    },
    onFilterInput2(input){
      this.filterInput2 = input
      // this.setFilterInput2(input)
    },

    onDateTimeFilterChange(data){
      // if (data){
      //   this.dateTimeStamp1 = data[0]
      //   this.dateTimeStamp2 = data[1]
      //   this.$emit('dateTimeRangeChanged', data)
      // } else {
      //   this.dateTimeStamp1 = ''
      //   this.dateTimeStamp2 = ''
      this.$emit('dateTimeRangeChanged', data)
      // }
    },


    filterItemsBySelectionAndName(items, selected, filterInput) {
      let filteredItems = items.filter(item => item !== selected);
      if (filterInput) {
        filteredItems = filteredItems.filter(item => item.source_name.toLowerCase().includes(filterInput.toLowerCase()));
      }
      return filteredItems;
    },


    async compareSources(){
      // TODO recode to Array[endpoint]
      let request = `?source1_id=${this.selectedItems["1"].source_id}&source2_id=${this.selectedItems["2"].source_id}`

      let result_container  = {}

      const fetchResults = async (isInitialCall = false) => {
        console.log('query line for request: ',request)
        try {
          const response = await axios.get(`${this.endpoint}/${request}`);
          console.log(response.data)
          if (response.data.status_code === 200) {
            this.result_container[this.endpoint] = response.data.result
            this.$emit('dataReceived',  this.result_container);

            // Notifications for count of received calls
            if (this.endpoint === 'tasks') {
              if (isInitialCall && this.result_container[this.endpoint].length > 0){
                ElNotification({
                    title: 'Успешно!',
                    message: `Для данной пары источников найдено вызовов: ${this.result_container[this.endpoint].length}`,
                    type: 'success',
                    duration: 7500,
                });
              } else if (isInitialCall){
                ElNotification({
                    title: 'Внимание!',
                    message: `Для данной пары источников не найдено вызовов`,
                    type: 'warning',
                    duration: 7500,
                });
              }
            }

          } else {
            this.result_container[this.endpoint] = []
            // this.$emit('dataReceived', []);
          }
        } catch (error) {
          console.log(error)
          ElNotification({
              title: 'Ошибка!',
              message: `Произошла ошибка при запросе`,
              type: 'error',
              duration: 7500,
          })
        }
      }

      clearInterval(this.intervalId);

      await fetchResults(true);

      if (this.endpoint === 'tasks') {
        this.intervalId = setInterval(fetchResults, 60000);
      }

      if (this.currentMode === 2 || this.currentMode === 3){
        await axios
            .get(`config/${request}`)
            .then( response => {
              if (response.data.status_code === 200) {
                this.result_container['config'] = response.data.result
                this.$emit('dataReceived', this.result_container);
              }
              else {
                this.result_container['config'] = []
              }
            })
            .catch( error => {
              console.log(error)
              ElNotification({
                  title: 'Ошибка!',
                  message: `Произошла ошибка при запросе настроек`,
                  type: 'error',
                  duration: 7500,
              })
            })
      }
    },

    lastFilterChange(){
      // console.log('ебать')
      // localStorage.setItem('lastFilter', this.selectedTimestampOption)
    }
  },
  // mounted() {
  //   this.selectedTimestampOption = localStorage.getItem('lastFilter')
  // },
  watch: {
    items (newVal) {
      let selectedSource1 = localStorage.getItem('selectedSource1')
      let selectedSource2 = localStorage.getItem('selectedSource2')

      if(selectedSource1){
        newVal.forEach(source => {
          if (source.source_id == selectedSource1) {
            this.selectedItems[1] = source
          }
        })
      }

      if(selectedSource2){
        newVal.forEach(source => {
          if (source.source_id == selectedSource2) {
            this.selectedItems[2] = source
          }
        })
      }
      this.$emit('itemsSelected', this.selectedItems)
    }
  }
  // created() {
  //   this.loadStateFromStore()
  // }
}
</script>

<style scoped>
.title {
  text-align: center;
  font-weight: bold;
  font-size: 18px;
  height: 5%;
  flex-basis: 5%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.source-component{
  padding: 10px;
  height: 95%;
  flex-basis: 95%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 10px;
}

.filter-block {
  text-align: center;
  border: 1px solid var(--color-text);
  padding: 13px;
  height: 15%;
  flex-basis: 15%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.filter-block-second {
  text-align: center;
  border: 1px solid var(--color-text);
  padding: 13px;
}

.filter-block .demonstration {
  display: block;
  margin-bottom: 10px;
}

.filter {
  border: 1px solid var(--color-text);
  padding: 20px;
  text-align: center;
}
.sources {
  flex: 1;
  display: flex;
  justify-content: space-between;
}

.compare-block{
  height: 8%;
  flex-basis: 8%;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.compare-button{
  padding: 10px 30px;
  height: 100%;
}
</style>