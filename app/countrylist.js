import $ from "jquery";
import chosen from "chosen-js";
import d3Promise from "d3.promise";


export default class {
    constructor(container) {
        this.countries = this.loadData("data/countries.json");

        this.countries.then(data => {
            var listHtml = '<option value="XXX">Worldwide</option>';

            for(var c in data) {
                listHtml += `<option value="${c}">${data[c].name}</option>`;
            }

            this.list = $("#" + container);
            this.list.append(listHtml);
            this.list.chosen();
        });

        window.addEventListener(
                "countryClick",
                this.onCountryClick.bind(this),
                false);
    }

    onCountryClick(event) {
        this.list.val(event.detail);
        this.list.trigger("chosen:updated");
    }

    loadData(filename) {
        return d3Promise.json(filename);
    }
}
