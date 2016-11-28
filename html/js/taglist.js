import List from "list.js";
import d3Promise from "d3.promise";


export default class {
    constructor(parentId) {
        this.dataset = this.loadData("data/tag.csv");
        this.enabledTags = [];

        var options = {
            valueNames: ["tag"],
            item: ['<label>',
            '<input type="checkbox" onclick="taglist.onTagSelectionChange(this)"/>',
            '<span class="tag"></span><br/>',
            '</label>'].join("")
        };

        this.dataset.then(data => {
            this.list = new List(parentId, options, data);
        });
    }

    onTagSelectionChange(elem) {
        var tag = elem.nextElementSibling.innerText;
        var index = this.enabledTags.indexOf(tag);

        if(index > -1 && !elem.checked) {
            this.enabledTags.splice(index, 1);
        } else if(index == -1 && elem.checked) {
            this.enabledTags.push(tag);
        } else {
            return;
        }

        window.dispatchEvent(new CustomEvent(
                    "tagSelectionChange", {
                        detail: this.enabledTags
                    }));
    }

    onSearchKeyPress(event) {
        var keyPressed = event.keyCode || event.which;

        // We only care about ENTER
        if(keyPressed != 13) {
            return;
        }

        // If there is only one tag in the filter results, select it
        if(this.list.matchingItems.length == 1) {
            this.list
                .matchingItems[0]
                .elm
                .getElementsByTagName("input")[0]
                .click();
        }
    }

    loadData(filename) {
        return d3Promise.csv(filename);
    }
}
