import $ from "jquery";
import chosen from "chosen-js";
import {countries} from "country-data";

export default class {
    constructor(container) {
        var listHtml = '<option value=""></option>';
        countries.all.forEach(item => {
            listHtml += `<option value="${item.alpha3}">${item.name}</option>`;
        });

        this.list = $("#" + container);
        this.list.append(listHtml);
        this.list.chosen();

        window.addEventListener(
                "countryClick",
                this.onCountryClick.bind(this),
                false);
    }

    onCountryClick(event) {
        this.list.val(event.detail);
        this.list.trigger("chosen:updated");
    }
}
