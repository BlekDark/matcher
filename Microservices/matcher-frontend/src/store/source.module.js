export default {
  namespaced: true,
  state: {
    filterInput1: '',
    filterInput2: '',
    selectedItems: {
      1: null,
      2: null,
    }
  },
  mutations: {
    setFilterInput1(state, input) {
      state.filterInput1 = input
    },
    setFilterInput2(state, input) {
      state.filterInput2 = input
    },
    setSelectedItems(state, selectedItems) {
      state.selectedItems = selectedItems
    },
  },
  getters: {
    getFilterInput1: state => state.filterInput1,
    getFilterInput2: state => state.filterInput2,
    getSelectedItems: state => state.selectedItems,
  }
}