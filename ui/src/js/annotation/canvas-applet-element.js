/**
 * Canvas applet parent class
 *
 * Used in the annotator to display a canvas visualizing the current frame
 * and customized toolbar button(s) and information panel(s).
 *
 * Methods that are expected to be overridden by subclasses are marked as abstract.
 */
import { TatorElement } from "../components/tator-element.js";

export class CanvasAppletElement extends TatorElement {
  /**
   * Constructor
   */
  constructor() {
    super();

    this._applet = null; // Must call init()
    this._active = false;

    this._selectButtonEnabled = true;
    this._zoomInButtonEnabled = true;
    this._zoomOutButtonEnabled = true;
    this._panButtonEnabled = true;
  }

  /**
   * @param {TatorElement.Applet} applet
   */
  init(applet) {
    console.log(
      `Initializing canvas applet element with ${applet.name} (ID: ${applet.id})`
    );

    this._applet = applet;

    this._main = document.createElement("main");
    this._main.setAttribute("class", "d-flex");
    this._shadow.appendChild(this._main);

    this.createToolbar();
    this.createCanvas();
    this.createInfoPanel();

    window.addEventListener("resize", () => {
      if (this._active) {
        this.redrawCanvas();
      }
    });
  }

  /**
   * Utility function to create a button that conforms to the toolbar
   * @param {string} buttonText
   * @param {string} svgHTML
   * @return HTMLElement
   *    Button to add to the toolbar
   */
  static createButton(buttonText, svgHTML) {
    var button = document.createElement("button");
    button.style.width = "100%";
    button.setAttribute(
      "class",
      "mb-2 btn-clear d-flex flex-items-center flex-column flex-justify-center px-2 py-2 rounded-2 f2 text-gray entity__button sidebar-button box-border"
    );
    var innerHTML = svgHTML;
    if (buttonText != null) {
      innerHTML += `<div class="f4 pt-1 text-center">${buttonText}</div>`;
    }
    button.innerHTML = innerHTML;

    return button;
  }

  /**
   * Creates the toolbar to the left of the canvas
   *
   * Note: These buttons have the option of being visually disabled.
   *       They are still constructed because other functions in this class
   *       rely on them being present.
   */
  createToolbar() {
    this._sidebar = document.createElement("div");
    this._sidebar.setAttribute(
      "class",
      "d-flex flex-column flex-items-center py-1 px-3"
    );
    this._sidebar.style.width = "65px";
    this._main.appendChild(this._sidebar);

    //
    // SELECT BUTTON
    //
    this._selectButton = CanvasAppletElement.createButton(
      "Select",
      `
      <svg xmlns="http://www.w3.org/2000/svg" class="no-fill" width="24" height="24" viewBox="0 0 24 24" stroke-width="1" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
        <path d="M7.904 17.563a1.2 1.2 0 0 0 2.228 .308l2.09 -3.093l4.907 4.907a1.067 1.067 0 0 0 1.509 0l1.047 -1.047a1.067 1.067 0 0 0 0 -1.509l-4.907 -4.907l3.113 -2.09a1.2 1.2 0 0 0 -.309 -2.228l-13.582 -3.904l3.904 13.563z"></path>
      </svg>
      `
    );
    this._sidebar.appendChild(this._selectButton);

    this._selectButton.addEventListener("click", () => {
      this.setCanvasMode("select");
      this._selectButton.blur();
    });

    if (!this._selectButtonEnabled) {
      this._selectButton.style.display = "none";
    }

    //
    // APPLET-SPECIFIC BUTTONS
    //
    this.addAppletToolbarButtons();

    //
    // ZOOM-IN BUTTON
    //
    this._zoomInButton = CanvasAppletElement.createButton(
      "Zoom In",
      `
      <svg xmlns="http://www.w3.org/2000/svg" class="no-fill" width="24" height="24" viewBox="0 0 24 24" stroke-width="1" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
        <path d="M10 10m-7 0a7 7 0 1 0 14 0a7 7 0 1 0 -14 0"></path>
        <path d="M7 10l6 0"></path>
        <path d="M10 7l0 6"></path>
        <path d="M21 21l-6 -6"></path>
      </svg>
      `
    );
    this._sidebar.appendChild(this._zoomInButton);

    this._zoomInButton.addEventListener("click", () => {
      this.setCanvasMode("zoom-in");
      this._zoomInButton.blur();
    });

    if (!this._zoomInButtonEnabled) {
      this._zoomInButton.style.display = "none";
    }

    //
    // ZOOM-OUT BUTTON
    //
    this._zoomOutButton = CanvasAppletElement.createButton(
      "Zoom Out",
      `
      <svg xmlns="http://www.w3.org/2000/svg" class="no-fill" width="24" height="24" viewBox="0 0 24 24" stroke-width="1" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
          <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
          <path d="M10 10m-7 0a7 7 0 1 0 14 0a7 7 0 1 0 -14 0"></path>
          <path d="M7 10l6 0"></path>
          <path d="M21 21l-6 -6"></path>
      </svg>
      `
    );
    this._sidebar.appendChild(this._zoomOutButton);

    this._zoomOutButton.addEventListener("click", () => {
      this.setCanvasMode("zoom-out");
      this._zoomOutButton.blur();
    });

    if (!this._zoomOutButtonEnabled) {
      this._zoomOutButton.style.display = "none";
    }

    //
    // PAN BUTTON
    //
    this._panButton = CanvasAppletElement.createButton(
      "Pan",
      `
      <svg xmlns="http://www.w3.org/2000/svg" class="no-fill" width="24" height="24" viewBox="0 0 24 24" stroke-width="1" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="5 9 2 12 5 15">
          </polyline><polyline points="9 5 12 2 15 5"></polyline>
          <polyline points="15 19 12 22 9 19"></polyline>
          <polyline points="19 9 22 12 19 15"></polyline>
          <line x1="2" y1="12" x2="22" y2="12"></line>
          <line x1="12" y1="2" x2="12" y2="22"></line>
      </svg>
      `
    );
    this._sidebar.appendChild(this._panButton);

    this._panButton.addEventListener("click", () => {
      this.setCanvasMode("pan");
      this._panButton.blur();
    });

    if (!this._panButtonEnabled) {
      this._panButton.style.display = "none";
    }
  }

  /**
   * Note: If additional buttons have been added, follow the format of this method
   *       and implement a derived version of this method.
   */
  setCanvasMode(mode) {
    this._canvasMode = mode;

    this.deselectAllToolbarButtons();

    var appletCanvasModes = this.getAppletCanvasModes();

    if (appletCanvasModes.includes(mode)) {
      this.selectAppletCanvasMode(mode);
    } else if (this._canvasMode == "select") {
      this._frameCanvas.style.cursor = "select";
      this._selectButton.classList.add("btn-purple50");
    } else if (this._canvasMode == "zoom-in") {
      this._frameCanvas.style.cursor = "zoom-in";
      this._zoomInButton.classList.add("btn-purple50");
    } else if (this._canvasMode == "zoom-out") {
      this._frameCanvas.style.cursor = "zoom-out";
      this._zoomOutButton.classList.add("btn-purple50");
    } else if (this._canvasMode == "pan") {
      this._frameCanvas.style.cursor = "move";
      this._panButton.classList.add("btn-purple50");
    } else {
      console.error(`setCanvasMode: Invalid mode (${mode})`);
    }
  }

  /**
   * Note: If additional buttons have been added, follow the format of this method
   *       and implement a derived version of this method.
   */
  deselectAllToolbarButtons() {
    this._selectButton.classList.remove("btn-purple50");
    this._zoomInButton.classList.remove("btn-purple50");
    this._zoomOutButton.classList.remove("btn-purple50");
    this._panButton.classList.remove("btn-purple50");

    this.deselectAppletToolbarButtons();
  }

  /**
   * Convert the provided visible canvas coordinates (normalized) into the equivalent offscreen version
   *
   * Helper drawing function. Not expected to be reimplemented by derived class.
   *
   * @param {float} x
   *    -1.0 .. 1.0 in visible canvas coordinates (width)
   *    This is a percentage of the offscreenRoi's width
   * @param {float} y
   *    -1.0 .. 1.0 in visible canvas coordinates (height)
   *    This is a percentage of the offscreenRoi's height
   * @param {array} offscreenRoi
   *    [0] = x (0.0 .. 1.0)
   *    [1] = y (0.0 .. 1.0)
   *    [2] = width (0.0 .. 1.0)
   *    [3] = height (0.0 .. 1.0)
   *
   *    If this is null, then this._offscreenRoi is used
   *
   * @return {array}
   *    [0] = x in offscreen canvas coordinates (normalized)
   *    [1] = y in offscreen canvas coordinates (normalized)
   */
  convertVisibleToOffscreen(x, y, offscreenRoi) {
    if (offscreenRoi == null) {
      offscreenRoi = this._offscreenRoi;
    }

    var offscreenX = offscreenRoi[0] + offscreenRoi[2] * x;
    var offscreenY = offscreenRoi[1] + offscreenRoi[3] * y;

    if (offscreenX < 0) {
      offscreenX = 0;
    } else if (offscreenX > 1) {
      offscreenX = 1;
    }

    if (offscreenY < 0) {
      offscreenY = 0;
    } else if (offscreenY > 1) {
      offscreenY = 1;
    }

    return [offscreenX, offscreenY];
  }

  /**
   * Utility function used to create normalized coordinates for the visible and
   * offscreen canvases based on the provided mouse event
   * @param {Event} event
   *    Event provided when a mouse event occurs
   * @return
   *    Object with the following fields:
   *    - visible:   Normalized coordinates of mouse in the visible canvas
   *                 (0,0 is top left, 1,1 is bottom right)
   *    - offscreen: Normalized coordinates of mouse in the offscreen canvas
   *                 (0,0 is top left, 1,1 is bottom right)
   */
  createNormalizedCoordinates(event) {
    var visibleCoordinates = [
      event.offsetX / this._frameCanvas.offsetWidth,
      event.offsetY / this._frameCanvas.offsetHeight,
    ];

    for (let idx = 0; idx < 2; idx++) {
      if (visibleCoordinates[idx] > 1.0) {
        visibleCoordinates[idx] = 1;
      }
      if (visibleCoordinates[idx] < 0.0) {
        visibleCoordinates[idx] = 0;
      }
    }

    var offscreenCoordinates = this.convertVisibleToOffscreen(
      visibleCoordinates[0],
      visibleCoordinates[1]
    );

    return {
      visible: visibleCoordinates,
      offscreen: offscreenCoordinates,
    };
  }

  /**
   * Helper drawing function. Not expected to be reimplemented by derived class.
   */
  createCanvas() {
    this._frameCanvas = document.createElement("canvas");
    this._main.appendChild(this._frameCanvas);
    this._frameCanvasContext = this._frameCanvas.getContext("2d");

    this._frameCanvas.offScreenCanvas = document.createElement("canvas");
    this._offscreenCanvasContext =
      this._frameCanvas.offScreenCanvas.getContext("2d");

    this._frameImage = new Image();

    console.log(`Windows device pixel ratio: ${window.devicePixelRatio}`);

    this._dragging = false;

    this._frameCanvas.addEventListener("click", (event) => {
      var coords = this.createNormalizedCoordinates(event);

      //
      // APPLET-SPECIFIC MODE CALLBACK
      //
      var appletCanvasModes = this.getAppletCanvasModes();
      if (appletCanvasModes.includes(this._canvasMode)) {
        this.applyAppletMouseClick(coords.visible, coords.offscreen);
        return;
      }
    });

    this._frameCanvas.addEventListener("mouseout", (event) => {
      this.applyAppletMouseOut();
    });

    this._frameCanvas.addEventListener("mousedown", (event) => {
      this._dragging = true;

      this._event = { start: {}, current: {} };
      this._event.start.time = Date.now();

      var coords = this.createNormalizedCoordinates(event);
      this._event.start.point = coords.visible;

      //
      // APPLET-SPECIFIC MODE CALLBACK
      //
      var appletCanvasModes = this.getAppletCanvasModes();
      if (appletCanvasModes.includes(this._canvasMode)) {
        this.applyAppletMouseDown(coords.visible, coords.offscreen);
        return;
      }
    });

    this._frameCanvas.addEventListener("mouseup", (event) => {
      this._dragging = false;
      this._event = null;
      var coords = this.createNormalizedCoordinates(event);

      //
      // APPLET-SPECIFIC MODE CALLBACK
      //
      var appletCanvasModes = this.getAppletCanvasModes();
      if (appletCanvasModes.includes(this._canvasMode)) {
        this.applyAppletMouseDown(coords.visible, coords.offscreen);
        return;
      }

      //
      // ZOOM MODES
      //
      if (this._canvasMode == "zoom-in") {
        this._canvasZoom *= 2;

        if (this._canvasZoom > 8) {
          this._canvasZoom = 8;
        }

        // The 0.25 is related with zoom.
        this._canvasCenterPoint = [
          coords.visible[0] + 0.25,
          coords.visible[1] + 0.25,
        ];
        this.redrawCanvas();
      } else if (this._canvasMode == "zoom-out") {
        this._canvasZoom *= 0.5;
        if (this._canvasZoom < 1) {
          this._canvasZoom = 1;
        }
        this._canvasCenterPoint = [
          coords.visible[0] - 0.5,
          coords.visible[1] - 0.5,
        ];
        this.redrawCanvas();
      }
    });

    this._frameCanvas.addEventListener("mousemove", (event) => {
      var coords = this.createNormalizedCoordinates(event);

      //
      // APPLET-SPECIFIC MODE CALLBACK
      //
      var appletCanvasModes = this.getAppletCanvasModes();
      if (appletCanvasModes.includes(this._canvasMode)) {
        this.applyAppletMouseMove(coords.visible, coords.offscreen);
        return;
      }

      //
      // PAN TOOL
      //
      if (!this._dragging) {
        return;
      }

      var now = Date.now();
      var duration = now - this._event.start.time;

      if (this._canvasMode == "pan" && duration > 1000.0 / 60) {
        this._deltaX = coords.visible[0] - this._event.start.point[0];
        this._deltaY = coords.visible[1] - this._event.start.point[1];
        this._canvasCenterPoint[0] = 0.5 - this._deltaX;
        this._canvasCenterPoint[1] = 0.5 - this._deltaY;

        this._event.start.time = now;
        this._event.start.point = coords.visible;

        this.redrawCanvas();
      }
    });
  }

  /**
   * Helper function not expected to be re-implemented in a derived class.
   */
  redrawCanvas() {
    console.log("******************** canvas-applet: redrawCanvas");

    console.log(
      `currentCanvasPoint - ${this._canvasCenterPoint[0]} ${this._canvasCenterPoint[1]}`
    );

    //
    // Set the visible canvas size based on available document space
    // while maintaining frame image ratio.
    //
    var canvasHeight = window.innerHeight - 100;
    var ratio = canvasHeight / this._frameImage.height;

    var imageCanvasSize = [
      Math.round(ratio * this._frameImage.width),
      Math.round(ratio * this._frameImage.height),
    ];
    this._frameCanvas.width = imageCanvasSize[0];
    this._frameCanvas.height = imageCanvasSize[1];

    // #TODO Figure out zoom based on the ratio
    console.log(`frameImage <-> document space ratio: ${ratio}`);
    console.log(`imageCanvasSize: ${imageCanvasSize[0]} ${imageCanvasSize[1]}`);

    //
    // Create the offscreen canvas size based on the frame image ratio and requested zoom
    //
    var offScreenCanvasSize = [0, 0];
    offScreenCanvasSize[0] = Math.round(imageCanvasSize[0] * this._canvasZoom);
    offScreenCanvasSize[1] = Math.round(imageCanvasSize[1] * this._canvasZoom);
    this._frameCanvas.offScreenCanvas.width = offScreenCanvasSize[0];
    this._frameCanvas.offScreenCanvas.height = offScreenCanvasSize[1];

    console.log(
      `offScreenCanvasSize - ${offScreenCanvasSize[0]} ${offScreenCanvasSize[1]}`
    );
    console.log(`canvasZoom: ${this._canvasZoom}`);

    //
    // Draw the stuff on the offscreen canvas
    //
    this._offscreenCanvasContext.clearRect(
      0,
      0,
      offScreenCanvasSize[0],
      offScreenCanvasSize[1]
    );
    this._offscreenCanvasContext.drawImage(
      this._frameImage,
      0,
      0,
      offScreenCanvasSize[0],
      offScreenCanvasSize[1]
    );

    //
    // 1. Convert the selected canvas point into the corresponding offscreen point
    // 2. Using the known visible canvas size, figure out the relative offscreen roi
    //
    var rOffscreenTopLeft = this.convertVisibleToOffscreen(
      this._canvasCenterPoint[0] - 0.5,
      this._canvasCenterPoint[1] - 0.5,
      this._offscreenRoi
    );

    var rWidth = imageCanvasSize[0] / offScreenCanvasSize[0];
    if (rWidth + rOffscreenTopLeft[0] > 1.0) {
      rOffscreenTopLeft[0] = 1 - rWidth;
    }
    if (rOffscreenTopLeft[0] < 0) {
      rOffscreenTopLeft[0] = 0;
    }

    var rHeight = imageCanvasSize[1] / offScreenCanvasSize[1];
    if (rHeight + rOffscreenTopLeft[1] > 1.0) {
      rOffscreenTopLeft[1] = 1 - rHeight;
    }
    if (rOffscreenTopLeft[0] < 0) {
      rOffscreenTopLeft[1] = 0;
    }

    this._offscreenRoi = [
      rOffscreenTopLeft[0],
      rOffscreenTopLeft[1],
      rWidth,
      rHeight,
    ];

    //
    // Draw applet specific stuff before taking a ROI thumbnail of the offscreen canvas
    // and placing it onto the visible canvas
    //
    this.drawAppletData();

    //
    // Draw
    //
    this._frameCanvasContext.clearRect(
      0,
      0,
      imageCanvasSize[0],
      imageCanvasSize[1]
    );
    this._frameCanvasContext.drawImage(
      this._frameCanvas.offScreenCanvas,
      this._offscreenRoi[0] * offScreenCanvasSize[0], // sx
      this._offscreenRoi[1] * offScreenCanvasSize[1], // sy
      this._offscreenRoi[2] * offScreenCanvasSize[0], // swidth
      this._offscreenRoi[3] * offScreenCanvasSize[1], // swidth
      0, // dx
      0, // dy
      imageCanvasSize[0], // dwidth
      imageCanvasSize[1]
    ); // dheight
  }

  /**
   * Reinitialize the canvas with the frame image to update
   * @param {blob} frameBlob
   *    Blob of media frame image to display in the canvas
   * @postcondition
   *    Resets the canvas zoom scaling back to 1
   * @return {Promise}
   *    Resolves when the image is loaded with the provided frame blob
   */
  updateFrame(frameBlob) {
    this._frameBlob = frameBlob;
    return new Promise((resolve) => {
      this._canvasZoom = 1;
      this._canvasCenterPoint = [0.5, 0.5];
      this._offscreenRoi = [0, 0, 1.0, 1.0]; // Initialize with 1-to-1 mapping

      var that = this;
      this._frameImage.onload = function () {
        that.redrawCanvas();
        that.appletFrameUpdateCallback();
        resolve();
      };
      this._frameImage.src = URL.createObjectURL(frameBlob);
    });
  }

  /**
   * @return {string}
   *    Text to display in the applet menu and annotator header
   */
  getTitle() {
    return this._applet.name;
  }

  /**
   * @return {string}
   *    Description to display in the applet menu
   */
  getDescription() {
    return this._applet.description;
  }

  /**
   * Note: This should be overridden if the select button is not used.
   *
   * @return {string}
   *    Mode that the applet will start off with when shown
   */
  getDefaultMode() {
    return "select";
  }

  //
  // ABSTRACT METHODS
  // The methods in this block should be updated by the derived class
  //

  /**
   * @abstract
   *    Derived implementation should return a unique applet icon. This icon is used in the
   *    annotator applet menu list. The width/height and class should match the example below
   * @return {string}
   *    <svg> HTML of the icon associated with this applet
   */
  getIcon() {
    return `
    <svg xmlns="http://www.w3.org/2000/svg" class="no-fill" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
      <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
      <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0"></path>
      <path d="M9 10l.01 0"></path>
      <path d="M15 10l.01 0"></path>
      <path d="M9.5 15a3.5 3.5 0 0 0 5 0"></path>
    </svg>`;
  }

  /**
   * @abstract
   *    Derived implementation should override this to perform tasks whenever the frame
   *    has been updated.
   */
  async appletFrameUpdateCallback() {
    return;
  }

  /**
   * Creates the information panel to the right of the canvas
   *
   * @abstract
   *    Add applet specific information panels
   */
  createInfoPanel() {
    return;
  }

  /**
   * Called when the sidebar is initialized
   *
   * @abstract
   *    Add applet specific buttons to this._sidebar
   */
  addAppletToolbarButtons() {
    return;
  }

  /**
   * Deselect applet specific toolbar buttons
   * @abstract
   *    Clear out specific classes from applet toolbar buttons.
   *    Refer to deselectAllToolbarButtons
   */
  deselectAppletToolbarButtons() {
    return;
  }

  /**
   * @abstract
   *    Derived implementation should return an array of canvas mode strings specific
   *    to the applet's functions. Generally there should be a mode associated with a
   *    toolbar button.
   * @return {array}
   *    Array of strings - applet specific canvas modes (e.g. ["mode_a", "mode_b"])
   */
  getAppletCanvasModes() {
    return [];
  }

  /**
   * @abstract
   *    Derived implementation should act on the requested applet specific canvas mode
   * @param {string} mode
   *    Requested canvas mode
   */
  selectAppletCanvasMode(mode) {
    return;
  }

  /**
   * Method called when the mousemove event is caught and an applet specific canvas mode is active
   *
   * @abstract
   *    Override if applet needs to respond to mousemove events in the visible canvas
   * @param {array} visibleCoordinates
   *    Normalized mouse location relative to the visible canvas
   *    (e.g. top left is 0,0 and the bottom right is 1,1)
   * @param {array} offscreenCoordinates
   *    Normalized mouse location relative to the offscreen canvas
   *    (e.g. top left is 0,0 and the bottom right is 1,1)
   *    If zoom level is 1, this is the same as the visible coordinates.
   */
  applyAppletMouseMove(visibleCoordinates, offscreenCoordinates) {
    return;
  }

  /**
   * Method called when the mousedown event is caught and an applet specific canvas mode is active
   *
   * @abstract
   *    Override if applet needs to respond to mousedown events in the visible canvas
   * @param {array} visibleCoordinates
   *    Normalized mouse location relative to the visible canvas
   *    (e.g. top left is 0,0 and the bottom right is 1,1)
   * @param {array} offscreenCoordinates
   *    Normalized mouse location relative to the offscreen canvas
   *    (e.g. top left is 0,0 and the bottom right is 1,1)
   *    If zoom level is 1, this is the same as the visible coordinates.
   */
  applyAppletMouseDown(visibleCoordinates, offscreenCoordinates) {
    return;
  }

  /**
   * Method called when the mouseup event is caught and an applet specific canvas mode is active
   *
   * @abstract
   *    Override if applet needs to respond to mouseup events in the visible canvas
   * @param {array} visibleCoordinates
   *    Normalized mouse location relative to the visible canvas
   *    (e.g. top left is 0,0 and the bottom right is 1,1)
   * @param {array} offscreenCoordinates
   *    Normalized mouse location relative to the offscreen canvas
   *    (e.g. top left is 0,0 and the bottom right is 1,1)
   *    If zoom level is 1, this is the same as the visible coordinates.
   */
  applyAppletMouseUp(visibleCoordinates, offscreenCoordinates) {
    return;
  }

  /**
   * Method called when the mouseout event is caught and an applet specific canvas mode is active
   *
   * @abstract
   *    Override if applet needs to respond to click events in the visible canvas
   * @param {array} visibleCoordinates
   *    Normalized mouse location relative to the visible canvas
   *    (e.g. top left is 0,0 and the bottom right is 1,1)
   * @param {array} offscreenCoordinates
   *    Normalized mouse location relative to the offscreen canvas
   *    (e.g. top left is 0,0 and the bottom right is 1,1)
   *    If zoom level is 1, this is the same as the visible coordinates.
   */
  applyAppletMouseClick(visibleCoordinates, offscreenCoordinates) {
    return;
  }

  /**
   * Method called when the mouseout event is caught and an applet specific canvas mode is active
   *
   * @abstract
   *    Override if applet needs to respond to mouseout events in the visible canvas
   */
  applyAppletMouseOut() {
    return;
  }

  /**
   * Method called when the redrawCanvas function is executed
   *
   * @abstract
   *    Override if applet needs to draw stuff on top of the frame image
   */
  drawAppletData() {
    return;
  }

  /**
   * Called when the applet is active/shown in the annotator
   *
   * @abstract
   *    #TODO
   *
   * @param data {Object}
   * - frame
   * - version
   * - media
   * - projectId
   * - selectedTrack
   * - selectedLocalization
   * - annotationData
   * - canvas
   */
  show(data) {
    this._active = true;
    this.setCanvasMode(this.getDefaultMode());
  }

  /**
   * Called when the user requests to close the applet
   *
   * @abstract
   *    Derived implementation should decide if it is ready to close (e.g. all data has been saved)
   *    and also inform the user in the UI appropriately.
   *
   * @return {bool}
   *    True if the applet is ready to close. False otherwise.
   */
  allowedToClose() {
    return true;
  }

  /**
   * Called when the applet is not active in the annotator
   *
   * allowedToClose() should have returned true prior to calling this
   *
   * @abstract
   *    Derived implementation should do the tasks needed to close up shop.
   */
  close() {
    this._active = false;
  }
}

customElements.define("canvas-applet-element", CanvasAppletElement);
