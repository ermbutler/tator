import { TatorElement } from "../../components/tator-element.js";
import {
  POLICY_ENTITY_NAME,
  POLICY_TARGET_NAME,
  store,
  fetchWithHttpInfo,
} from "../store.js";
import { LoadingSpinner } from "../../components/loading-spinner.js";

const CALCULATOR_COLUMN = [
  "Policy Entity",
  "Policy Target",
  "Exist",
  "Read",
  "Create",
  "Modify",
  "Delete",
  "Execute",
  "Upload",
  "ACL",
  "Actions",
];
const CALCULATOR_COLGROUP = `
<col style="width: 13%" />
<col style="width: 13%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 10%" />
`;

const EDIT_COLUMN = [
  "Level",
  "Exist",
  "Read",
  "Create",
  "Modify",
  "Delete",
  "Execute",
  "Upload",
  "ACL",
  "Shortcuts",
];
const EDIT_COLGROUP = `
<col style="width: 14%" />
<col style="width: 9%" />
<col style="width: 9%" />
<col style="width: 9%" />
<col style="width: 9%" />
<col style="width: 9%" />
<col style="width: 9%" />
<col style="width: 9%" />
<col style="width: 9%" />
<col style="width: 14%" />
`;

const BYTE_COUNT = {
  project: 5,
  media: null,
  localization: null,
  state: null,
  file: null,
  section: 3,
  algorithm: 1,
  version: 2,
  target_organization: 5,
  target_group: 1,
  job_cluster: null,
  bucket: null,
  hosted_template: 1,
};

const ENTITY_TYPE_CHOICES = [
  { label: "User", value: "user" },
  { label: "Group", value: "group" },
  { label: "Organization", value: "organization" },
];
const TARGET_TYPE_CHOICES = [
  { label: "Project", value: "project" },
  // { label: "Media", value: "media" },
  // { label: "File", value: "file" },
  { label: "Section", value: "section" },
  // { label: "Algorithm", value: "algorithm" },
  { label: "Version", value: "version" },
  // { label: "Organization", value: "target_organization" },
  // { label: "Group", value: "target_group" },
  // { label: "Bucket", value: "bucket" },
  // { label: "Hosted Template", value: "hosted_template" },
];
const PARENT_TARGET = {
  section: ["section", "project"],
  project: ["project"],
  version: ["version", "project"],
};

export class PermissionSettingsPolicyCalculatorView extends TatorElement {
  constructor() {
    super();

    const template = document.getElementById("policy-calculator-view").content;
    this._shadow.appendChild(template.cloneNode(true));

    this._title = this._shadow.getElementById("title");
    this._noData = this._shadow.getElementById("no-data");

    this._noPermission = this._shadow.getElementById("no-permission");
    this._permissionInput = this._shadow.getElementById("permission-input");

    this._entityTypeInput = this._shadow.getElementById("entity-type-input");
    this._entityIdInput = this._shadow.getElementById("entity-id-input");
    this._targetTypeInput = this._shadow.getElementById("target-type-input");
    this._targetIdInput = this._shadow.getElementById("target-id-input");
    this._inputs = [
      this._entityTypeInput,
      this._entityIdInput,
      this._targetTypeInput,
      this._targetIdInput,
    ];

    this._table = this._shadow.getElementById("calculator-table");
    this._colgroup = this._shadow.getElementById("calculator-table--colgroup");
    this._tableHead = this._shadow.getElementById("calculator-table--head");
    this._tableBody = this._shadow.getElementById("calculator-table--body");

    this._form = this._shadow.getElementById("calculator-table-form");
    this._saveReset = this._shadow.getElementById(
      "calculator-table--save-reset-section"
    );
    this._saveButton = this._shadow.getElementById("calculator-table-save");
    this._resetButton = this._shadow.getElementById("calculator-table-reset");

    // // loading spinner
    this.loading = new LoadingSpinner();
    this._shadow.appendChild(this.loading.getImg());

    this.modal = document.createElement("modal-dialog");
    this._shadow.appendChild(this.modal);
  }

  connectedCallback() {
    this._inputs.forEach((input) => {
      input.addEventListener("change", this._inputChange.bind(this));
    });

    store.subscribe(
      (state) => state.selectedType,
      this._updateSelectedType.bind(this)
    );

    store.subscribe((state) => state.Policy, this._setData.bind(this));

    this._saveButton.addEventListener("click", this._saveForm.bind(this));
    this._resetButton.addEventListener("click", this._resetTable.bind(this));

    this._permissionInput.addEventListener(
      "change",
      this._changePermissionInput.bind(this)
    );
  }

  _updateSelectedType(newSelectedType, oldSelectedType) {
    if (
      newSelectedType.typeName !== "Policy" ||
      newSelectedType.typeId === "All"
    ) {
      this._show = false;
      return;
    }

    this._show = true;
    this.id = newSelectedType.typeId;
  }

  /**
   * @param {string} val
   */
  set id(val) {
    this._id = val;

    // New policy
    if (this._id === "New") {
      this._initInputs(true);
      this._title.innerText = "New Policy";
      this._noPermission.setAttribute("hidden", "");
      this._permissionInput.removeAttribute("hidden");
    }
    // Calculator (with no entity and target info preset)
    else if (this._id === "Cal") {
      this._initInputs(true);
      this._title.innerText = "Effective Permission Calculator";
      this._noPermission.setAttribute("hidden", "");
      this._permissionInput.setAttribute("hidden", "");
    }
    // Calculator (with entity and target info preset)
    else if (this._id.startsWith("Cal")) {
      this._initInputs(false);
      this._title.innerText = "Effective Permission Calculator";
      this._noPermission.setAttribute("hidden", "");
      this._permissionInput.setAttribute("hidden", "");
    }
    // Edit policy
    else {
      this._initInputs(false);
      this._title.innerText = "Edit Policy";
      this._noPermission.setAttribute("hidden", "");
      this._permissionInput.removeAttribute("hidden");
    }

    this._setData();
  }

  _setData() {
    if (!this._show) return;
    const { Policy } = store.getState();
    if (!Policy.init) return;

    // New policy
    if (this._id === "New") {
      this._initByData();
    }
    // Calculator (with no entity and target info preset)
    else if (this._id === "Cal") {
      this._initByData();
    }
    // Calculator (with entity and target info preset)
    else if (this._id.startsWith("Cal")) {
      this._initByData(Policy.processedMap.get(+this._id.replace("Cal", "")));
    }
    // Edit policy
    else {
      this._initByData(Policy.processedMap.get(+this._id));
    }
  }

  /**
   * @param {object} val
   */
  _initByData(val) {
    console.log("😇 ~ _initByData ~ val:", val, this._id);

    this._noData.setAttribute("hidden", "");
    this._noPermission.setAttribute("hidden", "");
    this._permissionInput.permission = "Can Edit";
    this._saveReset.style.display = "none";
    this._tableHead.innerHTML = "";
    this._tableBody.innerHTML = "";

    if (val) {
      this.showDimmer();
      this.loading.showSpinner();

      this._entityTypeInput.setValue(val.entityType);
      this._entityIdInput.setValue(val.entityId);
      this._targetTypeInput.setValue(val.targetType);
      this._targetIdInput.setValue(val.targetId);

      this._requestedEntityName = `${
        POLICY_ENTITY_NAME[this._entityTypeInput.getValue()]
      } ${this._entityIdInput.getValue()}`;
      this._requestedTargetName = `${
        POLICY_TARGET_NAME[this._targetTypeInput.getValue()]
      } ${this._targetIdInput.getValue()}`;

      this._getData();
    } else {
      // New policy
      if (this._id === "New") {
        this._entityIdInput.setValue(null);
        this._targetIdInput.setValue(null);
      }
      // Calculator (with no entity and target info preset)
      else if (this._id === "Cal") {
        this._entityIdInput.setValue(null);
        this._targetIdInput.setValue(null);
      }
      // Calculator (with entity and target info preset)
      else if (this._id.startsWith("Cal")) {
        this._noData.removeAttribute("hidden");
        this._noData.innerText = `There is no data for Policy ${this._id.replace(
          "Cal",
          ""
        )}.`;

        if (this.hasAttribute("has-open-modal")) {
          this.hideDimmer();
          this.loading.hideSpinner();
        }
      }
      // Edit policy
      else {
        this._noData.removeAttribute("hidden");
        this._noData.innerText = `There is no data for Policy ${this._id}.`;

        if (this.hasAttribute("has-open-modal")) {
          this.hideDimmer();
          this.loading.hideSpinner();
        }
      }
    }
  }

  async _getData() {
    // Fetch Policy
    try {
      await this._getCalculatorTargets();
    } catch (error) {
      console.error(error);

      if (this.hasAttribute("has-open-modal")) {
        this.hideDimmer();
        this.loading.hideSpinner();
      }
      this._noData.removeAttribute("hidden");
      this._noData.innerText = error;
      return;
    }

    this._getCalculatorEntities();
    const calculatorPolicies = await store
      .getState()
      .getCalculatorPolicies(this.targets);
    this._getTableBodyData(calculatorPolicies);

    if (this._id.startsWith("Cal")) {
      this._renderCalculatorTable();
    } else {
      this._renderEditTable();
    }
  }

  _renderCalculatorTable() {
    // Head
    this._renderCalculatorTableHead();

    // Body -- Create Row
    Array.from(this._singleRowData.entries()).forEach(
      ([targetName, policies]) => {
        Array.from(policies.keys()).forEach((entityName) => {
          // single policy row
          const tr = document.createElement("tr");
          tr.id = `${targetName}--${entityName}`;
          this._tableBody.appendChild(tr);
        });

        // OR'd row
        const tr = document.createElement("tr");
        tr.id = `${targetName}--ord`;
        this._tableBody.appendChild(tr);
      }
    );
    //// final effective permission Row
    const tr = document.createElement("tr");
    tr.id = `final-row`;
    this._tableBody.appendChild(tr);

    // Body -- Fill in data
    Array.from(this._singleRowData.entries()).forEach(
      ([targetName, policies]) => {
        Array.from(policies.keys()).forEach((entityName) => {
          this._renderCalculatorTableBodySingleRow(targetName, entityName);
        });
        this._renderCalculatorTableBodyOrdRow(targetName);
      }
    );
    this._renderCalculatorTableBodyFinalRow();

    this._saveReset.style.display = "";
    this._checkPermissionOnOperatePolicy();
    if (this.hasAttribute("has-open-modal")) {
      this.hideDimmer();
      this.loading.hideSpinner();
    }
  }

  async _renderEditTable() {
    this._permissionInputValue = {};

    // Head
    this._renderEditTableHead();

    // Body
    this._resetTable();

    this._saveReset.style.display = "";
    // this._checkPermissionOnOperatePolicy();
    if (this.hasAttribute("has-open-modal")) {
      this.hideDimmer();
      this.loading.hideSpinner();
    }
  }

  _renderEditTableBody() {
    this._tableBody.innerHTML = "";

    this._permissionInput.setValue(this._permissionInputValue.decimal);
    const chunks = this._splitIntoChunksOf8Chars(
      this._permissionInputValue.binary
    );
    const levelCount = chunks.length;

    // Note: reverse() modify the original array
    chunks.reverse().forEach((byte, level) => {
      const tr = document.createElement("tr");

      // Level Column
      const tdLevel = document.createElement("td");
      tdLevel.innerText = `Level ${level + 1}`;
      tr.appendChild(tdLevel);

      // Permission Columns
      byte
        .split("")
        .reverse()
        .forEach((char, index) => {
          // id is the index of this char in binaryPermission
          const id = (levelCount - level) * 8 - (index + 1);
          const td = document.createElement("td");
          if (char === "0") {
            const xmark = document.createElement("no-permission-button");
            xmark.setAttribute("data-id", id);
            xmark.addEventListener(
              "click",
              this._changeEditTableCell.bind(this)
            );
            td.appendChild(xmark);
          } else if (char === "1") {
            const check = document.createElement("has-permission-button");
            check.setAttribute("data-id", id);
            check.addEventListener(
              "click",
              this._changeEditTableCell.bind(this)
            );
            td.appendChild(check);
          }
          tr.appendChild(td);
        });

      // Shortcuts Column
      const tdSc = document.createElement("td");
      tdSc.innerText = `123`;
      tr.appendChild(tdSc);

      this._tableBody.appendChild(tr);
    });
  }

  _renderCalculatorTableBodySingleRow(targetName, entityName) {
    const id = `${targetName}--${entityName}`;
    const tr = document.createElement("tr");
    tr.id = id;

    const tdEntity = document.createElement("td");
    tdEntity.innerText = entityName;
    tr.appendChild(tdEntity);

    const isFirstRow =
      Array.from(this._singleRowData.get(targetName).keys()).indexOf(
        entityName
      ) === 0;
    if (isFirstRow) {
      const entityCount = this._singleRowData.get(targetName).size;
      const tdTarget = document.createElement("td");
      tdTarget.innerText = targetName;
      tdTarget.setAttribute("rowspan", entityCount);
      tr.appendChild(tdTarget);
    }

    const { permissionBits } = this._singleRowData
      .get(targetName)
      .get(entityName);
    const noACL = permissionBits === "0-------";
    // .split("").reverse(): reverse the string, bc the rightmost is "Exist", the left most is "ACL". But in the table it is the opposite
    permissionBits
      .split("")
      .reverse()
      .forEach((char, index) => {
        const td = document.createElement("td");
        if (char === "0") {
          if (!noACL) {
            const xmark = document.createElement("no-permission-button");
            xmark.setAttribute("data-id", `${id}--${index}`);
            xmark.addEventListener("click", this._changeRowCell.bind(this));
            td.appendChild(xmark);
          }
        } else if (char === "1") {
          const check = document.createElement("has-permission-button");
          check.setAttribute("data-id", `${id}--${index}`);
          check.addEventListener("click", this._changeRowCell.bind(this));
          td.appendChild(check);
        }
        tr.appendChild(td);
      });

    const tdActions = document.createElement("td");
    const div = document.createElement("div");
    div.classList.add("d-flex", "flex-row", "flex-justify-center");
    div.style.gap = "5px";
    tdActions.appendChild(div);
    tr.appendChild(tdActions);

    const back = document.createElement("change-back-button");
    back.setAttribute("data-id", `${targetName}--${entityName}`);
    back.addEventListener("click", this._changeRowBack.bind(this));
    div.appendChild(back);
    if (permissionBits === "--------") {
      const grant = document.createElement("grant-all-button");
      grant.setAttribute("data-id", `${targetName}--${entityName}`);
      grant.addEventListener("click", this._grantRow.bind(this));
      div.appendChild(grant);
    } else {
      const remove = document.createElement("remove-permission-button");
      remove.setAttribute("data-id", `${targetName}--${entityName}`);
      remove.addEventListener("click", this._removeRow.bind(this));
      div.appendChild(remove);
    }
    // if (noACL) {
    //   for (const child of div.children) {
    //     child.setAttribute("disabled", "");
    //   }
    // }

    const trOld = this._shadow.getElementById(id);
    this._tableBody.replaceChild(tr, trOld);
  }

  _renderCalculatorTableBodyOrdRow(targetName) {
    const id = `${targetName}--ord`;
    const tr = document.createElement("tr");
    tr.id = id;
    tr.classList.add("ord-row");

    const td = document.createElement("td");
    td.innerText = `${this._requestedEntityName}'s effective permission against ${targetName}`;
    td.setAttribute("colspan", 2);
    tr.appendChild(td);

    const ordPermission = this._ordRowData.get(targetName);
    if (ordPermission === "0-------") {
      td.innerText += `\nYou don't have permission to fetch data of ${targetName}.`;
    }

    // .split("").reverse(): reverse the string, bc the rightmost is "Exist", the left most is "ACL". But in the table it is the opposite
    ordPermission
      .split("")
      .reverse()
      .forEach((char) => {
        const td = document.createElement("td");
        if (char === "0") {
          const xmark = document.createElement("no-permission-button");
          xmark.setAttribute("disabled", "");
          td.appendChild(xmark);
        } else if (char === "1") {
          const check = document.createElement("has-permission-button");
          check.setAttribute("disabled", "");
          td.appendChild(check);
        } else if (char === "-") {
          const question = document.createElement("question-mark-button");
          question.setAttribute("disabled", "");
          td.appendChild(question);
        }
        tr.appendChild(td);
      });

    const tdActions = document.createElement("td");
    tr.appendChild(tdActions);

    const trOld = this._shadow.getElementById(id);
    this._tableBody.replaceChild(tr, trOld);
  }

  _renderCalculatorTableBodyFinalRow() {
    const id = `final-row`;
    const tr = document.createElement("tr");
    tr.id = id;
    tr.classList.add("final-row");

    const td = document.createElement("td");
    td.innerText = `${this._requestedEntityName}'s final effective permission against ${this._requestedTargetName}`;
    td.setAttribute("colspan", 2);
    tr.appendChild(td);

    // .split("").reverse(): reverse the string, bc the rightmost is "Exist", the left most is "ACL". But in the table it is the opposite
    this._finalPermission
      .split("")
      .reverse()
      .forEach((char) => {
        const td = document.createElement("td");
        if (char === "0") {
          const xmark = document.createElement("no-permission-button");
          xmark.setAttribute("disabled", "");
          td.appendChild(xmark);
        } else if (char === "1") {
          const check = document.createElement("has-permission-button");
          check.setAttribute("disabled", "");
          td.appendChild(check);
        } else if (char === "-") {
          const question = document.createElement("question-mark-button");
          question.setAttribute("disabled", "");
          td.appendChild(question);
        }
        tr.appendChild(td);
      });

    const tdActions = document.createElement("td");
    tr.appendChild(tdActions);

    const trOld = this._shadow.getElementById(id);
    this._tableBody.replaceChild(tr, trOld);
  }

  _renderCalculatorTableHead() {
    this._colgroup.innerHTML = CALCULATOR_COLGROUP;

    // Head row 1
    const tr1 = document.createElement("tr");

    const th0 = document.createElement("th");
    th0.innerText = CALCULATOR_COLUMN[0];
    th0.setAttribute("rowspan", 2);
    tr1.appendChild(th0);

    const th1 = document.createElement("th");
    th1.innerText = CALCULATOR_COLUMN[1];
    th1.setAttribute("rowspan", 2);
    tr1.appendChild(th1);

    const ths = document.createElement("th");
    ths.innerText = `Each policy's permission on ${this._requestedTargetName} (with corresponding bit shift)`;
    ths.setAttribute("colspan", 8);
    tr1.appendChild(ths);

    const thLast = document.createElement("th");
    thLast.innerText = CALCULATOR_COLUMN.at(-1);
    thLast.setAttribute("rowspan", 2);
    tr1.appendChild(thLast);

    this._tableHead.appendChild(tr1);

    // Head row 2
    const tr2 = document.createElement("tr");
    CALCULATOR_COLUMN.slice(2, CALCULATOR_COLUMN.length - 1)
      .map((val) => {
        const th = document.createElement("th");
        th.innerText = val;
        return th;
      })
      .forEach((th) => {
        tr2.appendChild(th);
      });
    this._tableHead.appendChild(tr2);
  }

  _renderEditTableHead() {
    this._colgroup.innerHTML = EDIT_COLGROUP;

    const tr = document.createElement("tr");
    EDIT_COLUMN.map((val) => {
      const th = document.createElement("th");
      th.innerText = val;
      return th;
    }).forEach((th) => {
      tr.appendChild(th);
    });
    this._tableHead.appendChild(tr);
  }

  _getTableBodyData(policies) {
    console.log("😇 ~ _getTableBodyData ~ policies:", policies);

    // Clear values
    this._singleRowData = new Map();
    this._ordRowData = new Map();

    this._setSinglePolicyRowData(policies);
    [...this._singleRowData.keys()].forEach((targetName) =>
      this._setOrdRowData(targetName)
    );
    this._setFinalRowData();

    console.log(
      "😇 ~ _getTableBodyData ~ this._singleRowData :",
      this._singleRowData
    );
  }

  _setSinglePolicyRowData(policies) {
    this.targets.forEach((target) => {
      const targetName = `${POLICY_TARGET_NAME[target[0]]} ${target[1]}`;
      this._singleRowData.set(targetName, new Map());

      // If current user has no ACL permission on this target
      if (
        policies.findIndex(
          (policy) =>
            policy.entityName === "ALL" && policy.targetName === targetName
        ) > -1
      ) {
        this.entities.forEach((entity) => {
          const entityName = `${POLICY_ENTITY_NAME[entity[0]]} ${entity[1]}`;

          let binaryShiftedPermission = "0-------";
          const obj = {
            policyId: null,
            permissionBits: binaryShiftedPermission,
            originalPermissionBits: binaryShiftedPermission,
            entityType: entity[0],
            entityId: entity[1],
            targetType: target[0],
            targetId: target[1],
            permission: -1,
          };

          this._singleRowData.get(targetName).set(entityName, obj);
        });
      } else {
        this.entities.forEach((entity) => {
          const entityName = `${POLICY_ENTITY_NAME[entity[0]]} ${entity[1]}`;

          let binaryShiftedPermission = "--------";
          let policyId = null;
          let permission = null;
          const policy = policies.find(
            (policy) =>
              policy.entityName === entityName &&
              policy.targetName === targetName
          );
          if (policy) {
            policyId = policy.id;
            permission = policy.permission;
            const shiftedPermission =
              BigInt(policy.permission) >> BigInt(target[2]); // In JavaScript, the >> (bitwise right shift) operator only works on 32-bit signed integers. Therefore, need help of BigInt()
            binaryShiftedPermission = this._getRightmost8Bits(
              shiftedPermission.toString(2)
            );
          }
          const obj = {
            policyId,
            permissionBits: binaryShiftedPermission,
            originalPermissionBits: binaryShiftedPermission,
            entityType: entity[0],
            entityId: entity[1],
            targetType: target[0],
            targetId: target[1],
            permission,
          };

          this._singleRowData.get(targetName).set(entityName, obj);
        });
      }
    });
  }
  _setOrdRowData(targetName) {
    let ordPermission = "";
    const permissionStrings = Array.from(
      this._singleRowData.get(targetName).values()
    ).map((obj) => obj.permissionBits);

    if (permissionStrings[0] === "0-------") {
      ordPermission = "0-------";
    } else {
      ordPermission = this._bitwiseOrBinaryStrings(permissionStrings);
    }

    this._ordRowData.set(targetName, ordPermission);
  }
  _setFinalRowData() {
    this._finalPermission = Array.from(this._ordRowData.values()).at(-1);
  }

  _changeRowCell(evt) {
    const id = evt.target.dataset.id;
    if (id) {
      const val = id.split("--");
      if (val.length === 3) {
        const { permissionBits } = this._singleRowData.get(val[0]).get(val[1]);
        // 7-index: bc in a binary permission string, the rightmost is "Exist", the left most is "ACL". But in the table it is the opposite
        const index = 7 - parseInt(val[2]);
        const bit = permissionBits[index];

        const newPermissionBits =
          permissionBits.slice(0, index) +
          (bit === "1" ? "0" : "1") +
          permissionBits.slice(index + 1);
        const oldObj = this._singleRowData.get(val[0]).get(val[1]);

        this._singleRowData
          .get(val[0])
          .set(val[1], { ...oldObj, permissionBits: newPermissionBits });
        this._setOrdRowData(val[0]);
        this._setFinalRowData();

        this._renderCalculatorTableBodySingleRow(val[0], val[1]);
        this._renderCalculatorTableBodyOrdRow(val[0]);
        this._renderCalculatorTableBodyFinalRow();
      }
    }
  }

  _changeRowBack(evt) {
    const id = evt.target.dataset.id;
    if (id) {
      const val = id.split("--");
      if (val.length === 2) {
        const newPermissionBits = this._singleRowData
          .get(val[0])
          .get(val[1]).originalPermissionBits;

        const oldObj = this._singleRowData.get(val[0]).get(val[1]);
        this._singleRowData
          .get(val[0])
          .set(val[1], { ...oldObj, permissionBits: newPermissionBits });
        this._setOrdRowData(val[0]);
        this._setFinalRowData();

        this._renderCalculatorTableBodySingleRow(val[0], val[1]);
        this._renderCalculatorTableBodyOrdRow(val[0]);
        this._renderCalculatorTableBodyFinalRow();
      }
    }
  }

  _grantRow(evt) {
    const id = evt.target.dataset.id;
    if (id) {
      const val = id.split("--");
      if (val.length === 2) {
        const newPermissionBits = "11111111";

        const oldObj = this._singleRowData.get(val[0]).get(val[1]);
        this._singleRowData
          .get(val[0])
          .set(val[1], { ...oldObj, permissionBits: newPermissionBits });
        this._setOrdRowData(val[0]);
        this._setFinalRowData();

        this._renderCalculatorTableBodySingleRow(val[0], val[1]);
        this._renderCalculatorTableBodyOrdRow(val[0]);
        this._renderCalculatorTableBodyFinalRow();
      }
    }
  }

  _removeRow(evt) {
    const id = evt.target.dataset.id;
    if (id) {
      const val = id.split("--");
      if (val.length === 2) {
        const newPermissionBits = "--------";

        const oldObj = this._singleRowData.get(val[0]).get(val[1]);
        this._singleRowData
          .get(val[0])
          .set(val[1], { ...oldObj, permissionBits: newPermissionBits });
        this._setOrdRowData(val[0]);
        this._setFinalRowData();

        this._renderCalculatorTableBodySingleRow(val[0], val[1]);
        this._renderCalculatorTableBodyOrdRow(val[0]);
        this._renderCalculatorTableBodyFinalRow();
      }
    }
  }

  _changeEditTableCell(evt) {
    const index = +evt.target.dataset.id;
    if (isNaN(index)) return;

    const oldBinary = this._permissionInputValue.binary;
    const oldChar = oldBinary.at(index);
    const newChar = oldChar === "0" ? "1" : "0";
    let newBinary =
      oldBinary.slice(0, index) + newChar + oldBinary.slice(index + 1);
    const newDecimal = parseInt(newBinary, 2);
    this._permissionInputValue.binary = newBinary;
    this._permissionInputValue.decimal = newDecimal;
    this._renderEditTableBody();
  }
  _changePermissionInput() {
    const newDecimal = this._permissionInput.getValue();
    this._permissionInputValue.decimal = newDecimal;

    const binary = newDecimal.toString(2);
    // If binary's level count is smaller than it defined in BYTE_COUNT, then pad it with "0"s
    this._permissionInputValue.binary = this._padToAnyBits(
      this._permissionInputValue.levelCount * 8,
      binary
    );

    this._renderEditTableBody();
  }

  _checkPermissionOnOperatePolicy() {
    for (const [targetName, policies] of this._singleRowData) {
      const noPermission = Array.from(policies.values()).some(
        (policy) => policy.permission === -1
      );
      if (noPermission) {
        if (this._id === "New") {
          this._noPermission.removeAttribute("hidden");
          this._noPermission.innerText = `You don't have permission to create new policy on ${this._requestedEntityName} against ${this._requestedTargetName}.`;
          this._saveReset.style.display = "none";
          this._permissionInput.permission = "View Only";
        } else {
          const actionButtons = this._tableBody.querySelectorAll(
            `[data-id^="${targetName}"]`
          );
          actionButtons.forEach((btn) => btn.setAttribute("disabled", ""));
        }
      }
    }
  }

  _getCalculatorEntities() {
    const requestedEntityType = this._entityTypeInput.getValue();
    const requestedEntityId = this._entityIdInput.getValue();

    const {
      user,
      groupList,
      organizationList,
      Group: { userIdGroupIdMap },
    } = store.getState();

    this.entities = [];

    if (requestedEntityType === "organization") {
      this.entities.push(["organization", requestedEntityId]);
    } else if (requestedEntityType === "group") {
      // const group = groupList.find((gr) => gr.id === requestedEntityId);
      // entities.push(["organization", group.organization__id]);
      this.entities.push(["group", requestedEntityId]);
    } else if (requestedEntityType === "user") {
      organizationList.forEach((org) => {
        this.entities.push(["organization", org.id]);
      });
      if (userIdGroupIdMap.has(requestedEntityId)) {
        userIdGroupIdMap.get(requestedEntityId).forEach((groupId) => {
          this.entities.push(["group", groupId]);
        });
      }
      this.entities.push(["user", requestedEntityId]);
    }
  }

  async _getCalculatorTargets() {
    const targetType = this._targetTypeInput.getValue();
    const targetId = this._targetIdInput.getValue();
    this.targets = [];

    if (targetType === "project") {
      const response = await fetchWithHttpInfo(`/rest/Project/${targetId}`);

      if (response.response?.ok) {
        const project = response.data;
        this.targets.push(["project", project.id, 0]);
      } else {
        throw new Error(response.data?.message || "Could not fetch data.");
      }
    } else if (targetType === "section") {
      const response = await fetchWithHttpInfo(`/rest/Section/${targetId}`);

      if (response.response?.ok) {
        const section = response.data;
        this.targets.push(["project", section.project, 8]);
        this.targets.push(["section", section.id, 0]);
      } else {
        throw new Error(response.data?.message || "Could not fetch data.");
      }
    } else if (targetType === "version") {
      const response = await fetchWithHttpInfo(`/rest/Version/${targetId}`);

      if (response.response?.ok) {
        const version = response.data;
        this.targets.push(["project", version.project, 8]);
        this.targets.push(["version", version.id, 0]);
      } else {
        throw new Error(response.data?.message || "Could not fetch data.");
      }
    }
  }

  _saveForm(evt) {
    evt.preventDefault();

    if (this._id === "New") {
    } else {
      const policyToBeCreated = [];
      const policyToBeDeleted = [];
      const policyToBeEdited = [];
      for (const [targetName, policies] of this._singleRowData) {
        for (const [entityName, policy] of policies) {
          if (policy.permissionBits !== policy.originalPermissionBits) {
            if (policy.originalPermissionBits === "--------") {
              policyToBeCreated.push(policy);
            } else if (policy.permissionBits === "--------") {
              policyToBeDeleted.push(policy);
            } else {
              policyToBeEdited.push(policy);
            }
          }
        }
      }

      this._calculateChanges(
        policyToBeCreated,
        policyToBeDeleted,
        policyToBeEdited
      );
    }
  }

  _calculateChanges(policyToBeCreated, policyToBeDeleted, policyToBeEdited) {
    const toBeCreated = [];
    const toBeDeleted = [];
    const toBeEdited = [];
    policyToBeEdited.forEach((policy) => {
      const target = this.targets.find(
        (target) => target[0] === policy.targetType
      );

      const newBinaryPermissionOnTarget = this._getRightmost8Bits(
        BigInt(`0b${policy.permissionBits}`).toString(2)
      );

      const binaryPermission = this._padToAnyBits(
        8,
        BigInt(policy.permission).toString(2)
      );

      const newBinaryPermission = `${binaryPermission.slice(
        0,
        -target[2] - 8
      )}${newBinaryPermissionOnTarget}${
        target[2] === 0 ? "" : `${binaryPermission.slice(-target[2])}`
      }`;

      const newPermission = parseInt(newBinaryPermission, 2);
      console.log(newPermission);
    });
  }

  _setUpWarningSavingMsg() {
    this._warningDeleteMessage = `
    Pressing confirm will create these policies:<br/><br/>
    ${1}
    <br/>
    <br/><br/>
    Do you want to continue?
    `;
    return this._warningDeleteMessage;
  }

  _resetTable() {
    // Calculator table
    if (this._id.startsWith("Cal")) {
      for (const [targetName, policies] of this._singleRowData) {
        for (const [entityName, policy] of policies) {
          if (policy.permissionBits !== policy.originalPermissionBits) {
            const { originalPermissionBits } = policy;
            this._singleRowData.get(targetName).set(entityName, {
              ...policy,
              permissionBits: originalPermissionBits,
            });
            this._renderCalculatorTableBodySingleRow(targetName, entityName);
          }
        }
        this._setOrdRowData(targetName);
        this._renderCalculatorTableBodyOrdRow(targetName);
      }
      this._setFinalRowData();
      this._renderCalculatorTableBodyFinalRow();
    }
    // Edit/New Policy table
    else {
      const policy = this._singleRowData
        .get(this._requestedTargetName)
        .get(this._requestedEntityName);
      this._permissionInputValue.decimal = policy.permission;

      const binary = policy.permission.toString(2);
      // If binary's level count is smaller than it defined in BYTE_COUNT, then pad it with "0"s
      const levelCount = Math.max(
        Math.ceil(binary.length / 8),
        BYTE_COUNT[policy.targetType]
      );

      this._permissionInputValue.binary = this._padToAnyBits(
        levelCount * 8,
        binary
      );
      this._permissionInputValue.levelCount = levelCount;
      this._renderEditTableBody();
    }
  }

  _initInputs(canEdit) {
    this._entityTypeInput.choices = ENTITY_TYPE_CHOICES;
    this._targetTypeInput.choices = TARGET_TYPE_CHOICES;

    if (canEdit) {
      this._entityTypeInput.permission = "Can Edit";
      this._entityIdInput.permission = "Can Edit";
      this._targetTypeInput.permission = "Can Edit";
      this._targetIdInput.permission = "Can Edit";
    } else {
      this._entityTypeInput.permission = "View Only";
      this._entityIdInput.permission = "View Only";
      this._targetTypeInput.permission = "View Only";
      this._targetIdInput.permission = "View Only";
    }
  }

  _inputChange() {
    const values = this._inputs.map((input) => {
      return [input.dataset.key, input.getValue()];
    });

    if (values.some((value) => !value[1])) return;

    this._initByData(Object.fromEntries(values));
  }

  _bitwiseOrBinaryStrings(binaryStrings) {
    const validBinaryStrings = binaryStrings.filter((str) => str !== "");

    if (validBinaryStrings.length === 0) return "";

    let result = parseInt(validBinaryStrings[0], 2);

    for (let i = 1; i < validBinaryStrings.length; i++) {
      result |= parseInt(validBinaryStrings[i], 2);
    }

    return result.toString(2).padStart(8, "0");
  }

  _getRightmost8Bits(binaryStr) {
    // If the binary string is shorter than 8 bits, pad it with leading zeros
    const paddedBinaryStr = binaryStr.padStart(8, "0");

    // Return the rightmost 8 bits
    return paddedBinaryStr.slice(-8);
  }

  _padToAnyBits(targetLength, binaryStr) {
    return binaryStr.padStart(targetLength, "0");
  }

  _splitIntoChunksOf8Chars(str) {
    let chunks = [];
    for (let i = 0; i < str.length; i += 8) {
      chunks.push(str.substring(i, i + 8));
    }
    return chunks;
  }

  /**
   * Modal for this page, and handler
   * @returns sets page attribute that changes dimmer
   */
  showDimmer() {
    return this.setAttribute("has-open-modal", "");
  }

  hideDimmer() {
    return this.removeAttribute("has-open-modal");
  }
}

customElements.define(
  "permission-settings-policy-calculator-view",
  PermissionSettingsPolicyCalculatorView
);

class PermissionMask {
  // These bits are repeated so the left-byte is for children objects. This allows
  // a higher object to store the default permission for children objects by bitshifting by the
  // level of abstraction.
  // [0:7] Self-level objects (projects, algos, versions)
  // [8:15] Children objects (project -> section* -> media -> metadata)
  // [16:23] Grandchildren objects (project -> section -> media* -> metadata)
  // [24:31] Great-grandchildren objects (project -> section -> media -> metadata*)
  // If a permission points to a child object, that occupies [0:7]
  // Permission objects exist against either projects, algos, versions or sections

  static EXIST = 0x1; // Allows a row to be seen in a list, or individual GET
  static READ = 0x2; // Allows a references to be accessed, e.g. generate presigned URLs
  static CREATE = 0x4; // Allows a row to be created (e.g. POST)
  static MODIFY = 0x8; // Allows a row to be PATCHED (but not in-place, includes variant delete)
  static DELETE = 0x10; // Allows a row to be deleted (pruned for metadata)
  static EXECUTE = 0x20; // Allows an algorithm to be executed (applies to project-level or algorithm)
  static UPLOAD = 0x40; // Allows media to be uploaded
  static ACL = 0x80; // Allows ACL modification for a row, if not a creator
  static FULL_CONTROL = 0xff; // All bits and all future bits are set
}
