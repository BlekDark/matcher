<template>
  <div class="source">
    <div class="title">Источник {{ number }}</div>
    <div class="filter">
      <el-input v-model="filter"
                placeholder="Введите название"
                @input="onFilterInput()"
                size="small"
      />
    </div>
    <div class="source-items">
      <div v-if="items.length !== 0"
           v-for="item in items"
           :key="item.source_id"
           class="source-item"
           :class="{ selected: isSelected(item) }"
           @click="onItemClick(item)"
           :title="this.getTitle(item)"
      >
        {{ item.source_name }}
      </div>
      <div v-else>
        По заданным критериям нет источников
      </div>
    </div>

  </div>

</template>

<script>
export default {
  name: "SourceBlock",
  props: [
      'number',
      'items',
  ],
  data(){
    return {
      filter: '',
    }
  },
  methods: {
    onItemClick(item) {
      this.$emit('itemSelected', item);
    },
    isSelected(item) {
      return this.$parent.selectedItems[1] === item || this.$parent.selectedItems[2] === item;
    },
    onFilterInput(){
      this.$emit('filterInput', this.filter)

      if (this.number === 1) {
        localStorage.setItem('sourceFilter1', this.filter)
      } else if (this.number === 2) {
        localStorage.setItem('sourceFilter2', this.filter)
      }
    },
    getTitle(item){
      const timeOptions = {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          timeZoneName: 'short'
        }
      const timestamp = new Date(item.timestamp).toLocaleString('ru-RU', timeOptions);
      return `${item.source_name} | ${timestamp}`
    }
  },
  mounted() {
    if (this.number === 1) {
      this.filter = localStorage.getItem('sourceFilter1')
    } else if (this.number === 2) {
      this.filter = localStorage.getItem('sourceFilter2')
    }
    this.$emit('filterInput', this.filter)
  }
}
</script>

<style scoped>
.source {
  border: 1px solid var(--color-text);
  padding: 20px 10px;
  text-align: center;
  width: 48%;
  display: flex;
  flex-direction: column;
}

.title{
  font-weight: bold;
  padding-bottom: 20px;
}

.filter {
  padding-bottom: 20px;
}

.source-items{
  border: 1px solid var(--color-text);
  flex: 1;
  overflow: auto;
}

.source-item {
  cursor: pointer;
  transition: all 0.1s ease-in-out;
}

.source-item:hover {
  background-color: rgb(131, 136, 141) !important;
  color: black;
}

.selected {
  background-color: rgb(206, 206, 206) !important;
  color: black;
}

</style>