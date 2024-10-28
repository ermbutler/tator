import { TatorElement } from "../../components/tator-element.js";
import { svgNamespace } from "../../components/tator-element.js";

/// Generic button implementation
export class PermissionSettingsButton extends TatorElement {
  constructor() {
    super();
  }

  init(titleText, svgPath, viewbox) {
    if (viewbox == undefined) {
      viewbox = "0 0 32 32";
    }
    this._button = document.createElement("button");
    this._button.setAttribute(
      "class",
      "btn-clear py-2 px-0 text-gray hover-text-white d-flex flex-items-center"
    );
    this._shadow.appendChild(this._button);

    const svg = document.createElementNS(svgNamespace, "svg");
    svg.setAttribute("viewBox", viewbox);
    svg.setAttribute("height", "1em");
    svg.setAttribute("width", "1em");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke", "currentColor");
    svg.setAttribute("stroke-width", "2");
    svg.setAttribute("stroke-linecap", "round");
    svg.setAttribute("stroke-linejoin", "round");
    this._button.appendChild(svg);

    const title = document.createElementNS(svgNamespace, "title");
    title.textContent = titleText;
    svg.appendChild(title);

    const path = document.createElementNS(svgNamespace, "path");
    path.setAttribute("d", svgPath);
    svg.appendChild(path);

    this._disabled = false;

    this.addEventListener("click", (evt) => {
      if (this._disabled) {
        console.log("1");
        evt.stopImmediatePropagation();
        return false;
      }
    });
  }

  initWithSvg(titleText, svgElement) {
    this._button = document.createElement("button");
    this._button.setAttribute(
      "class",
      "annotation__shape btn-clear py-3 px-3 d-flex rounded-2 text-gray hover-text-white"
    );
    this._shadow.appendChild(this._button);

    this._button.appendChild(svgElement);
    const title = document.createElementNS(svgNamespace, "title");
    title.textContent = titleText;
    svgElement.appendChild(title);
  }

  static get observedAttributes() {
    return ["class", "disabled", "href"];
  }

  attributeChangedCallback(name, oldValue, newValue) {
    switch (name) {
      case "class":
        if (this.classList.contains("is-selected")) {
          this._button.classList.add("is-selected");
        } else {
          this._button.classList.remove("is-selected");
        }
        break;
      case "disabled":
        if (newValue === null) {
          this._button.removeAttribute("disabled");
          this._disabled = false;
        } else {
          this._button.setAttribute("disabled", "");
          this._disabled = true;
        }
        break;
      case "href":
        this._button.setAttribute("href", newValue);
        break;
    }
  }
}

/// Specific implementations built on svg + name
class EditLineButton extends PermissionSettingsButton {
  constructor() {
    super();
    this.init(
      "Edit Line",
      "M373.2 16.97C395.1-4.901 430.5-4.901 452.4 16.97L495 59.6C516.9 81.47 516.9 116.9 495 138.8L182.3 451.6C170.9 462.9 156.9 471.2 141.5 475.8L20.52 511.3C14.9 512.1 8.827 511.5 4.687 507.3C.5466 503.2-1.002 497.1 .6506 491.5L36.23 370.5C40.76 355.1 49.09 341.1 60.44 329.7L373.2 16.97zM429.8 39.6C420.4 30.22 405.2 30.22 395.8 39.6L341 94.4L417.6 170.1L472.4 116.2C481.8 106.8 481.8 91.6 472.4 82.23L429.8 39.6zM109.6 402.4L173.4 415.2L394.1 193.6L318.4 117L96.84 338.6L109.6 402.4zM70.51 370.2C69.08 373.2 67.88 376.3 66.93 379.5L39.63 472.4L132.4 445.1C135.7 444.1 138.8 442.9 141.8 441.5L92.86 431.7C86.53 430.4 81.58 425.5 80.31 419.1L70.51 370.2z",
      "0 0 512 512"
    );
  }
}

class GrantAllButton extends PermissionSettingsButton {
  constructor() {
    super();
    this.init(
      "Grant All Permission",
      "M536 96c-22.09 0-40 17.91-40 40c0 8.998 3.521 16.89 8.537 23.57l-89.63 71.7c-5.955 4.764-12.99 7.019-19.94 7.019c-11.61 0-22.98-6.298-28.68-17.7l-57.6-115.2C320 98.34 327.1 86.34 327.1 72C327.1 49.91 310.1 32 288 32S247.1 49.91 247.1 72c0 14.34 7.963 26.34 19.3 33.4L209.7 220.6C204 231.1 192.6 238.3 181 238.3c-6.945 0-13.98-2.255-19.94-7.019l-89.63-71.7C76.48 152.9 79.1 144.1 79.1 136c0-22.09-17.91-40-40-40s-40 17.91-40 40s17.91 40 40 40c.248 0 .457-.1164 .7051-.1203l50.52 277.8C93.99 468.9 107.2 480 122.7 480h330.6c15.46 0 28.72-11.06 31.48-26.27l50.52-277.9C535.5 175.9 535.8 176 536 176C558.1 176 576 158.1 576 136S558.1 96 536 96zM439.9 432H136.1l-33.89-186.4l28.94 23.15c14.14 11.31 31.87 17.54 49.92 17.54c30.53 0 57.97-16.95 71.61-44.23L288 171.3l35.37 70.73c13.64 27.28 41.08 44.23 71.61 44.23c18.06 0 35.79-6.229 49.92-17.54l28.94-23.15L439.9 432z",
      "0 0 576 512"
    );
  }
}
class RemovePermissionButton extends PermissionSettingsButton {
  constructor() {
    super();
    this.init(
      "Remove This Policy",
      "M384 208C401.7 208 416 222.3 416 240V272C416 289.7 401.7 304 384 304H128C110.3 304 96 289.7 96 272V240C96 222.3 110.3 208 128 208H384zM512 256C512 397.4 397.4 512 256 512C114.6 512 0 397.4 0 256C0 114.6 114.6 0 256 0C397.4 0 512 114.6 512 256zM256 48C141.1 48 48 141.1 48 256C48 370.9 141.1 464 256 464C370.9 464 464 370.9 464 256C464 141.1 370.9 48 256 48z",
      "0 0 512 512"
    );
  }
}
class ChangeBackButton extends PermissionSettingsButton {
  constructor() {
    super();
    this.init(
      "Back to Original",
      "M40 16C53.25 16 64 26.75 64 40v102.1C103.7 75.57 176.3 32.11 256.1 32.11C379.6 32.11 480 132.5 480 256s-100.4 223.9-223.9 223.9c-52.31 0-103.3-18.33-143.5-51.77c-10.19-8.5-11.56-23.62-3.062-33.81c8.5-10.22 23.66-11.56 33.81-3.062C174.9 417.5 214.9 432 256 432c97.03 0 176-78.97 176-176S353 80 256 80c-66.54 0-126.8 38.28-156.5 96H200C213.3 176 224 186.8 224 200S213.3 224 200 224h-160C26.75 224 16 213.3 16 200v-160C16 26.75 26.75 16 40 16z",
      "0 0 512 512"
    );
  }
}
class HasPermissionButton extends PermissionSettingsButton {
  constructor() {
    super();
    this.init(
      "Remove this permission",
      "M440.1 103C450.3 112.4 450.3 127.6 440.1 136.1L176.1 400.1C167.6 410.3 152.4 410.3 143 400.1L7.029 264.1C-2.343 255.6-2.343 240.4 7.029 231C16.4 221.7 31.6 221.7 40.97 231L160 350.1L407 103C416.4 93.66 431.6 93.66 440.1 103V103z",
      "0 0 448 512"
    );
  }
}
class NoPermissionButton extends PermissionSettingsButton {
  constructor() {
    super();
    this.init(
      "Grant this permission",
      "M312.1 375c9.369 9.369 9.369 24.57 0 33.94s-24.57 9.369-33.94 0L160 289.9l-119 119c-9.369 9.369-24.57 9.369-33.94 0s-9.369-24.57 0-33.94L126.1 256L7.027 136.1c-9.369-9.369-9.369-24.57 0-33.94s24.57-9.369 33.94 0L160 222.1l119-119c9.369-9.369 24.57-9.369 33.94 0s9.369 24.57 0 33.94L193.9 256L312.1 375z",
      "0 0 320 512"
    );
  }
}

customElements.define("permission-settings-button", PermissionSettingsButton);
customElements.define("edit-line-button", EditLineButton);
customElements.define("grant-all-button", GrantAllButton);
customElements.define("remove-permission-button", RemovePermissionButton);
customElements.define("change-back-button", ChangeBackButton);
customElements.define("has-permission-button", HasPermissionButton);
customElements.define("no-permission-button", NoPermissionButton);
