import { OrgTypeFormTemplate } from "./components/org-type-form-template.js";

export class BucketEdit extends OrgTypeFormTemplate {
  constructor() {
    super();
    this.typeName = "Bucket";
    this.readableTypeName = "Bucket";
    this._hideAttributes = true;
  
    // used to set up form
    this._currentBucketType = null;
    this.bucketInputs = new Map(); // setup later
    this._bucketFieldsByType = new Map();
    this._bucketFieldsByType.set("aws", ["access_key", "secret_key", "endpoint_url", "region", "archive_sc", "live_sc"]);
    this._bucketFieldsByType.set("gcs", ["archive_sc", "live_sc", "gcs_key_info"]);
    this._allFields = ["access_key", "secret_key", "endpoint_url", "region", "archive_sc", "live_sc", "gcs_key_info"];   

    // 
    var templateInner = document.getElementById("bucket-edit");
    var innerClone = document.importNode(templateInner.content, true);
    this._shadow.appendChild(innerClone);

    this._form = this._shadow.getElementById("bucket-edit--form");
    this._editName = this._shadow.getElementById("bucket-edit--name");
    this._editBucketType = this._shadow.getElementById("bucket-edit--bucket-type");
    this._editAccessKey = this._shadow.getElementById("bucket-edit--access-key");
    this._editSecretKey = this._shadow.getElementById("bucket-edit--secret-key");
    this._editEndpointUrl = this._shadow.getElementById("bucket-edit--endpoint-url");
    this._editRegion = this._shadow.getElementById("bucket-edit--region");
    this._editArchiveSc = this._shadow.getElementById("bucket-edit--archive-storage-class");
    this._editLiveSc = this._shadow.getElementById("bucket-edit--live-storage-class");
    this._editGcsKeyInfo = this._shadow.getElementById("bucket-edit--gcs-key-info");

    //
    this.bucketInputs.set("secret_key", this._editSecretKey);
    this.bucketInputs.set("region", this._editRegion);
    this.bucketInputs.set("archive_sc", this._editArchiveSc);
    this.bucketInputs.set("live_sc", this._editLiveSc);
    this.bucketInputs.set("gcs_key_info", this._editGcsKeyInfo);
    this.bucketInputs.set("access_key", this._editAccessKey);
    this.bucketInputs.set("endpoint_url", this._editEndpointUrl);


    this._editBucketType.choices = [
      { name: "AWS", value: "aws", checked: false },
      { name: "GCS", value: "gcs", checked: false },
    ]
    // this._editBucketType.default = bucketTypes;

  }


  async _setupFormUnique() {
    // name
    if (this._data.id === "New") {
      this._editName.setValue("");
      this._editName.default = ""; 
    } else {
      this._editName.setValue(this._data.name);
      this._editName.default = this._data.name; 
    }

    // type
    if (this._data.id == "New") {
      this._editBucketType.setValue("");
      this._editBucketType.default ="";
      this._editBucketType.addEventListener("change", this._setBucketType.bind(this));
    }


    // access key
    this._editAccessKey.setValue(this._data.access_key);
    this._editAccessKey.default = this._data.access_key;
    this._editAccessKey.hidden = true;
   

    // secret key
    this._editSecretKey.setValue(this._data.secret_key);
    this._editSecretKey.default = this._data.secret_key;
    this._editSecretKey.hidden = true;
    

    // endpoint url
    this._editEndpointUrl.setValue(this._data.endpoint_url);
    this._editEndpointUrl.default = this._data.endpoint_url;
    this._editEndpointUrl.hidden = true;
    

    // region
    this._editRegion.setValue(this._data.region);
    this._editRegion.default = this._data.region;
    this._editRegion.hidden = true;
    

    // archive storage class
    this._editArchiveSc.setValue(this._data.archive_sc);
    this._editArchiveSc.default = this._data.archive_sc;
    this._editArchiveSc.hidden = true;
    

    // live storage class
    this._editLiveSc.setValue(this._data.live_sc);
    this._editLiveSc.default = this._data.live_sc;
    this._editLiveSc.hidden = true;
    

    // GCS key info
    this._editGcsKeyInfo.setValue(this._data.gcs_key_info);
    this._editGcsKeyInfo.default = this._data.gcs_key_info;
    this._editGcsKeyInfo.hidden = true;

    if (this._data.id !== "New") this._showBestGuess();
  }

  _showBestGuess() {
    let hasGcsInfo = (this._data.gcs_key_info !== null);
    let hasAwsInfo = (this._data.region !== null || this._data.secret_key !== null || this._data.access_key !== null);

    if (hasGcsInfo && !hasAwsInfo) {
      this._showBucketFields("gcs");
    } else if (hasAwsInfo && !hasGcsInfo) {
      this._showBucketFields("aws");
    } else  { //if (hasGcsInfo && hasAwsInfo), or for some other reason
      for (let field of this._allFields) {
        this._currentBucketType = "none";
        this.bucketInputs.get(field).hidden = false;
      }
    }
  }

  _setBucketType() {
    let type = this._editBucketType.getValue();
    this._showBucketFields(type);
  }

  _showBucketFields(type) {
    this._currentBucketType = type;
    let hideType = type == "aws" ? "gcs" : "aws";
    console.log("SHOW BUCKET FIELdS FOR "+type.toUpperCase());
    this._editBucketType.setValue(type);
    
    // hide non-relevent fields
    // #todo expand to loops list of hideTypes if we have > 2 (ie. Wasabi)
    const hideThese = this._bucketFieldsByType.get(hideType);
    console.log("hideThese",hideThese);
    for (let field of hideThese) {
      console.log(this.bucketInputs.get(field));
      this.bucketInputs.get(field).hidden = true;
    }
    
    // show relevent fields
    const showThese = this._bucketFieldsByType.get(type);
    console.log("showThese",showThese);
    for (let field of showThese) {
      console.log(this.bucketInputs.get(field));
      this.bucketInputs.get(field).hidden = false;
    }
  }

  _getFormData() {
    let formData = {};
    let bucketType = this._currentBucketType !== null ? this._currentBucketType : "none";
    const isNew = true; // schema doesn't accept nulls

    if (this._editName.changed() || isNew) {
      formData.name = this._editName.getValue();
    }

    if (this._editAccessKey.changed() && bucketType !== "gcs") {
      formData.access_key = this._editAccessKey.getValue();
    }

    if (this._editSecretKey.changed() && bucketType !== "gcs") {
      formData.secret_key = this._editSecretKey.getValue();
    }

    if (this._editEndpointUrl.changed() && bucketType !== "gcs") {
      formData.endpoint_url = this._editEndpointUrl.getValue();
    }

    if (this._editRegion.changed() && bucketType !== "gcs") {
      formData.region = this._editRegion.getValue();
    }

    if (this._editArchiveSc.changed() || isNew)  {
      formData.archive_sc = this._editArchiveSc.getValue();
    }

    if (this._editLiveSc.changed()  || isNew) {
      formData.live_sc = this._editLiveSc.getValue();
    }

    if (this._editGcsKeyInfo.changed() && bucketType !== "aws") {
      formData.gcs_key_info = this._editGcsKeyInfo.getValue();
    }

    return formData;
  }
}

customElements.define("bucket-edit", BucketEdit);
