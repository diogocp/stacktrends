import $ from "jquery";
import chosen from "chosen-js";
import d3Promise from "d3.promise";

export default class {
    constructor(container) {
        this.list = $("#" + container);
        this.list.chosen();

        window.addEventListener(
                "tagSelectionChange",
                this.onTagSelectionChange.bind(this),
                false);
        window.addEventListener(
                "primaryTagChange",
                this.onPrimaryTagChange.bind(this),
                false);
    }

    onTagSelectionChange(event) {
        var listHtml = this.generateListHtml(event.detail);
        this.list.empty().append(listHtml);
        this.list.trigger("chosen:updated");
    }

    onPrimaryTagChange(event) {
        this.list.val(event.detail);
        this.list.trigger("chosen:updated");
    }

    generateListHtml(list) {
        var listHtml = '<option value=""></option>';

        list.forEach(item => {
            listHtml += `<option value="${item}">${item}</option>`;
        });

        return listHtml;
    }
}
