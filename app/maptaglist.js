import $ from "jquery";
import chosen from "chosen-js";
import d3Promise from "d3.promise";

export default class {
    constructor(container) {
        this.dataset = this.loadData("data/tag.csv");

        var listHtml = '<option value=""></option>';
        this.dataset.then(data => {
            data.forEach(item => {
                listHtml += `<option value="${item.tag}">${item.tag}</option>`;
            });

            this.list = $("#" + container);
            this.list.append(listHtml);
            this.list.chosen();
        });

        window.addEventListener(
                "primaryTagChange",
                this.onPrimaryTagChange.bind(this),
                false);
    }

    onPrimaryTagChange(event) {//FIXME
        this.list.val(event.detail);
        this.list.trigger("chosen:updated");
    }

    loadData(filename) {
        return d3Promise.csv(filename);
    }
}
