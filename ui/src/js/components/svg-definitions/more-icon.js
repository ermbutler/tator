import { TatorElement } from "../tator-element.js";
import { svgNamespace } from "../tator-element.js";

export class MoreIcon extends TatorElement {
  constructor() {
    super();

    this._svg = document.createElementNS(svgNamespace, "svg");
    this._svg.setAttribute("id", "icon-more-horizontal");
    this._svg.setAttribute("viewBox", "0 0 24 24");
    this._svg.setAttribute("height", "1em");
    this._svg.setAttribute("width", "1em");
    this._shadow.appendChild(this._svg);

    const title = document.createElementNS(svgNamespace, "title");
    title.textContent = "More";
    this._svg.appendChild(title);

    const path = document.createElementNS(svgNamespace, "path");
    path.setAttribute("d", "M14 12c0-0.269-0.054-0.528-0.152-0.765-0.102-0.246-0.25-0.465-0.434-0.649s-0.404-0.332-0.649-0.434c-0.237-0.098-0.496-0.152-0.765-0.152s-0.528 0.054-0.765 0.152c-0.246 0.102-0.465 0.25-0.649 0.434s-0.332 0.404-0.434 0.649c-0.098 0.237-0.152 0.496-0.152 0.765s0.054 0.528 0.152 0.765c0.102 0.246 0.25 0.465 0.434 0.649s0.404 0.332 0.649 0.434c0.237 0.098 0.496 0.152 0.765 0.152s0.528-0.054 0.765-0.152c0.246-0.102 0.465-0.25 0.649-0.434s0.332-0.404 0.434-0.649c0.098-0.237 0.152-0.496 0.152-0.765zM21 12c0-0.269-0.054-0.528-0.152-0.765-0.102-0.246-0.25-0.465-0.434-0.649s-0.404-0.332-0.649-0.434c-0.237-0.098-0.496-0.152-0.765-0.152s-0.528 0.054-0.765 0.152c-0.246 0.102-0.465 0.25-0.649 0.434s-0.332 0.404-0.434 0.649c-0.098 0.237-0.152 0.496-0.152 0.765s0.054 0.528 0.152 0.765c0.102 0.246 0.25 0.465 0.434 0.649s0.404 0.332 0.649 0.434c0.237 0.098 0.496 0.152 0.765 0.152s0.528-0.054 0.765-0.152c0.246-0.102 0.465-0.25 0.649-0.434s0.332-0.404 0.434-0.649c0.098-0.237 0.152-0.496 0.152-0.765zM7 12c0-0.269-0.054-0.528-0.152-0.765-0.102-0.246-0.25-0.465-0.434-0.649s-0.404-0.332-0.649-0.434c-0.237-0.098-0.496-0.152-0.765-0.152s-0.528 0.054-0.765 0.152c-0.246 0.102-0.465 0.25-0.649 0.434s-0.332 0.404-0.434 0.649c-0.098 0.237-0.152 0.496-0.152 0.765s0.054 0.528 0.152 0.765c0.102 0.246 0.25 0.465 0.434 0.649s0.404 0.332 0.649 0.434c0.237 0.098 0.496 0.152 0.765 0.152s0.528-0.054 0.765-0.152c0.246-0.102 0.465-0.25 0.649-0.434s0.332-0.404 0.434-0.649c0.098-0.237 0.152-0.496 0.152-0.765z");
    this._svg.appendChild(path);
  }
}

customElements.define("more-icon", MoreIcon);
