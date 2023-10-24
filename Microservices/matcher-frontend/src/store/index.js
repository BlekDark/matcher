import {createStore} from 'vuex'
import sourceModule from "./source.module";

export default createStore({
    modules: {
        source: sourceModule,
    }
})