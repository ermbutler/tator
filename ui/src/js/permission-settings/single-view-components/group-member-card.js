import { TatorElement } from "../../components/tator-element.js";
import { store } from "../store.js";

export class GroupMemberCard extends TatorElement {
  constructor() {
    super();

    const template = document.getElementById("group-member-card").content;
    this._shadow.appendChild(template.cloneNode(true));

    this._div = this._shadow.getElementById("group-member-card-div");
    this._username = this._shadow.getElementById("group-member-card--username");
    this._email = this._shadow.getElementById("group-member-card--email");
  }

  connectedCallback() {}

  static get observedAttributes() {
    return ["username", "email", "type"];
  }

  attributeChangedCallback(name, oldValue, newValue) {
    switch (name) {
      case "username":
        this._username.innerText = newValue;
        break;
      case "email":
        this._email.innerText = newValue;
        break;
      case "type":
        if (newValue === "to-be-added") {
          this._div.classList.remove("to-be-deleted");
          this._div.classList.add("to-be-added");
        } else if (newValue === "to-be-deleted") {
          this._div.classList.remove("to-be-added");
          this._div.classList.add("to-be-deleted");
        }
    }
  }

  /**
   * @param {object} val
   */
  set data(val) {
    this._data = val;
  }
}

customElements.define("group-member-card", GroupMemberCard);
