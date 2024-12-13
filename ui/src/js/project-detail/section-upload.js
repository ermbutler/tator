import { UploadElement } from "../components/upload-element.js";
import "../components/upload-dialog-init.js";
import { svgNamespace } from "../components/tator-element.js";
import { store } from "./store.js";

export class SectionUpload extends UploadElement {
	constructor() {
		super();

		this._pageLink = document.createElement("a");
		this._pageLink.setAttribute("class", "text-light-gray hover-text-white");
		this._pageLink.style.cursor = "pointer";
		this._pageLink.setAttribute("title", "Go to Upload Page");
		this._shadow.appendChild(this._pageLink);

		const svg = document.createElementNS(svgNamespace, "svg");
		svg.setAttribute("id", "icon-upload");
		svg.setAttribute("viewBox", "0 0 24 24");
		svg.setAttribute("height", "1em");
		svg.setAttribute("width", "1em");
		this._pageLink.appendChild(svg);

		const title = document.createElementNS(svgNamespace, "title");
		title.textContent = "Upload";
		svg.appendChild(title);

		const path = document.createElementNS(svgNamespace, "path");
		path.setAttribute(
			"d",
			"M20 15v4c0 0.137-0.027 0.266-0.075 0.382-0.050 0.122-0.125 0.232-0.218 0.325s-0.203 0.167-0.325 0.218c-0.116 0.048-0.245 0.075-0.382 0.075h-14c-0.137 0-0.266-0.027-0.382-0.075-0.122-0.050-0.232-0.125-0.325-0.218s-0.167-0.203-0.218-0.325c-0.048-0.116-0.075-0.245-0.075-0.382v-4c0-0.552-0.448-1-1-1s-1 0.448-1 1v4c0 0.405 0.081 0.793 0.228 1.148 0.152 0.368 0.375 0.698 0.651 0.974s0.606 0.499 0.974 0.651c0.354 0.146 0.742 0.227 1.147 0.227h14c0.405 0 0.793-0.081 1.148-0.228 0.368-0.152 0.698-0.375 0.974-0.651s0.499-0.606 0.651-0.974c0.146-0.354 0.227-0.742 0.227-1.147v-4c0-0.552-0.448-1-1-1s-1 0.448-1 1zM11 5.414v9.586c0 0.552 0.448 1 1 1s1-0.448 1-1v-9.586l3.293 3.293c0.391 0.391 1.024 0.391 1.414 0s0.391-1.024 0-1.414l-5-5c-0.001-0.001-0.003-0.002-0.004-0.004-0.095-0.094-0.204-0.165-0.32-0.213-0.245-0.101-0.521-0.101-0.766 0-0.116 0.048-0.225 0.119-0.32 0.213-0.001 0.001-0.003 0.002-0.004 0.004l-5 5c-0.391 0.391-0.391 1.024 0 1.414s1.024 0.391 1.414 0z"
		);
		svg.appendChild(path);

		this._fileInput = document.createElement("input");
		this._fileInput.setAttribute("class", "sr-only");
		this._fileInput.setAttribute("type", "file");
		this._fileInput.setAttribute("multiple", "");
		this._pageLink.after(this._fileInput);

		this._fileInput.addEventListener("change", this._fileSelectCallback);

		this.uploadDialogInit = document.createElement("upload-dialog-init");
		this._shadow.appendChild(this.uploadDialogInit);

		// label.addEventListener("click", () => {
		// 	this.uploadDialogInit.open();
		// });

		// this.uploadDialogInit.addEventListener(
		// 	"choose-files",
		// 	this._handleUpdateVars.bind(this)
		// );

		// this.uploadDialogInit._mediaType.addEventListener(
		// 	"change",
		// 	this._handleMediaType.bind(this)
		// );
	}

	connectedCallback() {
		this.init(store);
	}

	_handleDirectoryUpload() {
		this._allowDirectoryUpload =
			this.uploadDialogInit._directoryUpload.getChecked();
		if (this._allowDirectoryUpload) {
			this._fileInput.setAttribute("webkitdirectory", "");
			this._fileInput.setAttribute("directory", "");
		} else {
			this._fileInput.removeAttribute("webkitdirectory");
			this._fileInput.removeAttribute("directory");
		}
	}

	_handleMediaType(evt) {
		console.log("Media type changed", evt.target.getValue());
		if (evt.target.getValue() == this.uploadDialogInit._anyMediaType) {
			this._chosenMediaType = null;
			this._uploadAttributes = {};
			this._fileInput.removeAttribute("accept");
			this.uploadDialogInit._mediaAttributes.dataType = null;
			this.uploadDialogInit._mediaAttributes.reset();
			return;
		}

		this._chosenMediaType = this._mediaTypes.find(
			(type) => type.id === Number(evt.target.getValue())
		);

		this.uploadDialogInit._mediaAttributes.dataType = this._chosenMediaType;

		if (this._chosenMediaType.dtype === "image") {
			this._fileInput.setAttribute("accept", this._acceptedImageExt.join(","));
		} else if (this._chosenMediaType.dtype === "video") {
			this._fileInput.setAttribute("accept", this._acceptedVideoExt.join(","));
		}
	}

	_handleUpdateVars(event) {
		this._fileInput.click();

		const sectionId = Number(this.uploadDialogInit._parentFolders?.getValue());
		if (sectionId !== this.uploadDialogInit._noParentName) {
			this._chosenSection =
				sectionId && this._sectionData?._sectionIdMap?.[sectionId]?.name
					? this._sectionData._sectionIdMap[sectionId].name
					: null;

			this.section = this._chosenSection;
		}

		const mediaType = this.uploadDialogInit._mediaType.getValue();
		this._chosenMediaType = this._mediaTypes.find(
			(type) => type.id === Number(mediaType)
		);

		this._uploadAttributes = event.detail.attributes;
	}

	set sectionData(val) {
		this._sectionData = val;
		this.uploadDialogInit._sectionData = val;
	}

	set mediaTypes(val) {
		this._mediaTypes = val;

		this.uploadDialogInit.mediaTypes = val;
	}

	static get observedAttributes() {
		return ["section"].concat(UploadElement.observedAttributes);
	}

	attributeChangedCallback(name, oldValue, newValue) {
		switch (name) {
			case "section":
				if (newValue && newValue.indexOf("{") > -1) {
					const json = JSON.parse(newValue);
					this._section = json.name;
					this._pageLink.setAttribute(
						"href",
						`/${this._project.id}/upload?section=${json.id}`
					);
					this._uploadSection = async () => {
						return json.name;
					};
				} else {
					this._section = newValue;

					this._pageLink.setAttribute(
						"href",
						`/${this._project.id}/upload?section=${newValue}`
					);
					this._uploadSection = async () => {
						return newValue;
					};
				}
				break;
		}
	}

	set project(val) {
		this._project = val;
		this._pageLink.setAttribute("href", `/${this._project.id}/upload`);
	}
}

customElements.define("section-upload", SectionUpload);
