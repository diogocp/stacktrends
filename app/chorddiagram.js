import d3 from "d3";
import d3Promise from "d3.promise";


export default class {
    constructor(parentId) {
        this.parentId = parentId;
    }

    loadData(filename) {
        return d3Promise.csv(filename);
    }
}
