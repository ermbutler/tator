/**
 * Element used to encapsulate the filter modal dialog.
 */
class FilterDialog extends ModalDialog {

  constructor()
  {
    super();

    this._div.setAttribute("class", "modal-wrap modal-extra-wide d-flex");
    this._modal.setAttribute("class", "modal rounded-2");
    this._header.setAttribute("class", "px-6 py-6");
    this._titleDiv.setAttribute("class", "h2");
    this._title.nodeValue = "Filter Data";

    this._conditionsDiv = document.createElement("div");
    this._conditionsDiv.setAttribute("class", "analysis__filter_conditions_list");
    this._main.appendChild(this._conditionsDiv);

    const favesDiv = document.createElement("div");
    favesDiv.setAttribute("class", "annotation__panel-group py-2 text-gray f2");
    this._main.appendChild(favesDiv);

    this._favorites = document.createElement("favorites-panel");
    favesDiv.appendChild(this._favorites);

    const apply = document.createElement("button");
    apply.setAttribute("class", "btn btn-clear");
    apply.textContent = "Apply Filters";
    this._footer.appendChild(apply);

    const cancel = document.createElement("button");
    cancel.setAttribute("class", "btn btn-clear btn-charcoal");
    cancel.textContent = "Cancel";
    this._footer.appendChild(cancel);

    /**
     * Event handlers
     */

    // Handler when user hits the apply button.
    apply.addEventListener("click", () => {
      var filterString = ""; // #TODO

      this.dispatchEvent(new CustomEvent("newFilterSet", {
        detail: {
          filterString: filterString
        },
        composed: true,
      }));
    });

    this._data = null;

    // Handler when user hits the cancel button.
    cancel.addEventListener("click", () => {
      this.dispatchEvent(new Event("close"));
    });
  }


  /**
   * Sets the available dataset that can be selected by the user
   *
   * @param {array} val - List of objects with the following fields
   *   .name - str - Name of attribute type
   *   .attribute_types - array - Array of objects with the following fields
   *     .name - str - Name of attribute
   *     .dtype - str - string|bool|float|int|datetime|geopos|enum
   *     .choices - array - Valid only if enum was provided
   */
  set data(val)
  {
    if (this._data != null)
    {
      console.warn("filter-dialog already binded with a dataset");
    }

    this._data = val;

    // Set the GUI elements
    this._filter_condition_group = document.createElement("filter-condition-group");
    this._filter_condition_group.data = this._data;
    this._filter_condition_group._div.style.marginTop = "10px";
    this._conditionsDiv.appendChild(this._filter_condition_group);

    // Parse the URL then for settings information
    // #TODO
  }

  /**
   * @returns {array} - Array of condition objects requested by the user.
   */
  getConditions()
  {
    return this._filter_condition_group.getConditions();
  }
}

customElements.define("filter-dialog", FilterDialog);