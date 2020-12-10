class ProjectMainEdit extends TatorElement {
  constructor() {
    super();
  }

  init(val, t){
    try{
      console.log("::ProjectEditName::");
      console.log(t);
      // Temporary loading box until FETCH returns
      const settingsBoxHelper = new SettingsBox("loading-settings");
      const project = settingsBoxHelper.headingWrap("Project", "Change the project name or summary.", 1);
      const boxOnPage = settingsBoxHelper.boxWrapDefault( project );

      const settingsInputHelper = new SettingsInput("project-settings");
      // append input for name
      boxOnPage.appendChild( settingsInputHelper.inputText( { "labelText": "Name", "value": val.name} ) );
      // append an input for descriptionText
      boxOnPage.appendChild( settingsInputHelper.inputText( { "labelText": "Name", "value": val.summary} ) );

      return t.after( boxOnPage );

    } catch(e){console.error("ProjectMainEdit:: Failed")}
  }
}

customElements.define("project-main-edit", ProjectMainEdit);
