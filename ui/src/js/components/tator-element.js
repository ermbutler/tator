export const svgNamespace = "http://www.w3.org/2000/svg";

import reset from "/static/css/reset.css" with { type: "css" };
import variables from "/static/css/variables.css" with { type: "css" };
import text from "/static/css/text.css" with { type: "css" };
import utilities from "/static/css/utilities.css" with { type: "css" };
import base from "/static/css/base.css" with { type: "css" };
import action from "/static/css/components/action.css" with { type: "css" };
import addNew from "/static/css/components/add-new.css" with { type: "css" };
import analysis from "/static/css/components/analysis.css" with { type: "css" };
import annotation from "/static/css/components/annotation.css" with { type: "css" };
import avatar from "/static/css/components/avatar.css" with { type: "css" };
import bulkEdit from "/static/css/components/bulk-edit.css" with { type: "css" };
import button from "/static/css/components/button.css" with { type: "css" };
import entityGallery from "/static/css/components/entity-gallery.css" with { type: "css" };
import file from "/static/css/components/file.css" with { type: "css" };
import form from "/static/css/components/form.css" with { type: "css" };
import header from "/static/css/components/header.css" with { type: "css" };
import labelTree from "/static/css/components/label-tree.css" with { type: "css" };
import label from "/static/css/components/label.css" with { type: "css" };
import loading from "/static/css/components/loading.css" with { type: "css" };
import modal from "/static/css/components/modal.css" with { type: "css" };
import more from "/static/css/components/more.css" with { type: "css" };
import nav from "/static/css/components/nav.css" with { type: "css" };
import newProject from "/static/css/components/new-project.css" with { type: "css" };
import pagination from "/static/css/components/pagination.css" with { type: "css" };
import placeholders from "/static/css/components/placeholders.css" with { type: "css" };
import progress from "/static/css/components/progress.css" with { type: "css" };
import project from "/static/css/components/project.css" with { type: "css" };
import search from "/static/css/components/search.css" with { type: "css" };
import section from "/static/css/components/section.css" with { type: "css" };
import sideNav from "/static/css/components/side-nav.css" with { type: "css" };
import table from "/static/css/components/table.css" with { type: "css" };
import toggleContent from "/static/css/components/toggle-content.css" with { type: "css" };
import tooltip from "/static/css/components/tooltip.css" with { type: "css" };
import entityPanelImage from "/static/css/components/entity-panel-image.css" with { type: "css" };

export class TatorElement extends HTMLElement {
  constructor() {
    super();
    this._shadow = this.attachShadow({ mode: "open" });
    this._shadow.adoptedStyleSheets.push(reset);
    this._shadow.adoptedStyleSheets.push(variables);
    this._shadow.adoptedStyleSheets.push(text);
    this._shadow.adoptedStyleSheets.push(utilities);
    this._shadow.adoptedStyleSheets.push(base);
    this._shadow.adoptedStyleSheets.push(action);
    this._shadow.adoptedStyleSheets.push(addNew);
    this._shadow.adoptedStyleSheets.push(analysis);
    this._shadow.adoptedStyleSheets.push(annotation);
    this._shadow.adoptedStyleSheets.push(avatar);
    this._shadow.adoptedStyleSheets.push(bulkEdit);
    this._shadow.adoptedStyleSheets.push(button);
    this._shadow.adoptedStyleSheets.push(entityGallery);
    this._shadow.adoptedStyleSheets.push(entityPanelImage);
    this._shadow.adoptedStyleSheets.push(file);
    this._shadow.adoptedStyleSheets.push(form);
    this._shadow.adoptedStyleSheets.push(header);
    this._shadow.adoptedStyleSheets.push(labelTree);
    this._shadow.adoptedStyleSheets.push(label);
    this._shadow.adoptedStyleSheets.push(loading);
    this._shadow.adoptedStyleSheets.push(modal);
    this._shadow.adoptedStyleSheets.push(more);
    this._shadow.adoptedStyleSheets.push(nav);
    this._shadow.adoptedStyleSheets.push(newProject);
    this._shadow.adoptedStyleSheets.push(pagination);
    this._shadow.adoptedStyleSheets.push(placeholders);
    this._shadow.adoptedStyleSheets.push(progress);
    this._shadow.adoptedStyleSheets.push(project);
    this._shadow.adoptedStyleSheets.push(search);
    this._shadow.adoptedStyleSheets.push(section);
    this._shadow.adoptedStyleSheets.push(sideNav);
    this._shadow.adoptedStyleSheets.push(table);
    this._shadow.adoptedStyleSheets.push(toggleContent);
    this._shadow.adoptedStyleSheets.push(tooltip);
  }
}
