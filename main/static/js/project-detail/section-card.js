class SectionCard extends TatorElement {
  constructor() {
    super();

    this._li = document.createElement("li");
    this._li.style.cursor = "pointer";
    this._li.setAttribute("class", "section d-flex flex-items-center flex-justify-between px-2 rounded-1");
    this._shadow.appendChild(this._li);

    this._link = document.createElement("a");
    this._link.setAttribute("class", "section__link d-flex flex-items-center text-gray");
    this._li.appendChild(this._link);

    this._title = document.createElement("h2");
    this._title.setAttribute("class", "section__name py-1 px-1 css-truncate");
    this._link.appendChild(this._title);
  }

  init(section, sectionType) {
    this._section = section;
    this._sectionType = sectionType;
    if (section === null) {
      this._title.textContent = "All Media";
    } else {
      this._title.textContent = section.name;
    }

    const svg = document.createElementNS(svgNamespace, "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("height", "1em");
    svg.setAttribute("width", "1em");
    svg.setAttribute("fill", "none");
    svg.style.fill = "none";
    svg.setAttribute("stroke", "currentColor");
    svg.setAttribute("stroke-width", "2");
    svg.setAttribute("stroke-linecap", "round");
    svg.setAttribute("stroke-linejoin", "round");
    this._link.insertBefore(svg, this._title);

    // Null section means display all media.
    if (section === null) {
      const path = document.createElementNS(svgNamespace, "path");
      path.setAttribute("d", "M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z");
      svg.appendChild(path);

      const poly = document.createElementNS(svgNamespace, "polyline");
      poly.setAttribute("points", "9 22 9 12 15 12 15 22");
      svg.appendChild(poly);
    }
    if (sectionType == "folder") {
      const path = document.createElementNS(svgNamespace, "path");
      path.setAttribute("d", "M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z");
      svg.appendChild(path);
    } else if (sectionType == "savedSearch") {
      const circle = document.createElementNS(svgNamespace, "circle");
      circle.setAttribute("cx", "11");
      circle.setAttribute("cy", "11");
      circle.setAttribute("r", "8");
      svg.appendChild(circle);

      const line = document.createElementNS(svgNamespace, "line");
      line.setAttribute("x1", "21");
      line.setAttribute("y1", "21");
      line.setAttribute("x2", "16.65");
      line.setAttribute("y2", "16.65");
      svg.appendChild(line);
    }
  }

  rename(name) {
    this._title.textContent = name;
  }

  set active(enabled) {
    if (enabled) {
      this._li.classList.add("is-active");
    } else {
      this._li.classList.remove("is-active");
    }
  }
}

customElements.define("section-card", SectionCard);
