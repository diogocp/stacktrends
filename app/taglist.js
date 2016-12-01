import List from "list.js";
import d3Promise from "d3.promise";


export default class {
    constructor(parentId) {
        this.dataset = this.loadData("data/tags.json");
        this.enabledTags = [];

        var options = {
            valueNames: [
                "taglist-name",
                {attr: "value", name: "taglist-value"}
            ],
            item: `<label>
                       <input class="taglist-value" type="checkbox"
                              onclick="taglist.onClick(this)"/>
                       <span class="taglist-name"></span><br/>
                  </label>`
        };

        this.dataset.then(data => {
            this.list = new List(parentId, options, data);
        });
    }

    onClick(elm) {
        var tag = elm.value;

        // Check if a previously selected tag tag was deselected
        var index = this.enabledTags.indexOf(tag);
        if(index > -1 && !elm.checked) {
            this.enabledTags.splice(index, 1);
        }
        // Check if a previously unselected tag was selected
        else if(index == -1 && elm.checked) {
            this.enabledTags.push(tag);
        }
        // This should be unreachable; it means there was no change
        else {
            return;
        }

        // Keep the list sorted (case-insensitive)
        this.enabledTags.sort(
            (a, b) => a.toLowerCase().localeCompare(b.toLowerCase())
        );

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

        var items = this.list.matchingItems;

        // If there is only one tag in the filter results, select it
        if(items.length == 1) {
            items[0].elm.getElementsByTagName("input")[0].click();
            return;
        }
        // Otherwise, look for an exact match and select it if it exists
        var text = event.target.value.toLowerCase();
        items.forEach(item => {
            if(text == item.values()["taglist-value"].toLowerCase()) {
                item.elm.getElementsByTagName("input")[0].click();
            }
        });
    }

    loadData(filename) {
        return d3Promise.json(filename).then(data => {
                return data.map(tag => {
                    return {
                        "taglist-name": tag,
                        "taglist-value": tag
                    };
                });
        });
    }
}
