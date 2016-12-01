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
        // Store the currently selected tag
        var currentTag = this.list.val();

        // Generate the new tag list
        var selectedTags = event.detail;
        var listHtml = this.generateListHtml(selectedTags);
        this.list.empty().append(listHtml);

        // Reselect the previously selected tag, if possible.
        if(event.detail.indexOf(currentTag) != -1) {
            this.list.val(currentTag);
        }
        else if(selectedTags.length == 1) {
            window.dispatchEvent(
                new CustomEvent(
                    "primaryTagChange",
                    {detail: selectedTags[0]}
                ));
        }
        else {
            window.dispatchEvent(
                new CustomEvent(
                    "primaryTagChange",
                    {detail: ""}
                ));
        }

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
