class FillTrack {
  constructor(videoDef, algoCanvas) {
    console.info("Processing = " + JSON.stringify(videoDef));
    this._mediaId = algoCanvas.activeLocalization.media;
    this._width = videoDef.width;
    this._height = videoDef.height;
    this._newLocalizations = [];

    // Get the currently selected track.
    this._track = algoCanvas._data._trackDb[algoCanvas.activeLocalization.id];

    // Get localizations for this track.
    this._localizations = algoCanvas._data._dataByType
                          .get(algoCanvas.activeLocalization.meta).filter(elem => {
      return algoCanvas._data._trackDb[elem.id].meta == this._track.meta;
    });

    // Sort localizations by frame.
    this._localizations.sort((left, right) => {left.frame - right.frame});

    // Setup the termination criteria, either 10 iteration or move by atleast 1 pt
    this._termCrit = new cv.TermCriteria(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1);
  }

  processFrame(frameIdx, frameData) {
    console.info("Processing frame " + frameIdx);
    // Retrieve the most recent localization in the track before this frame.
    let latest = null;
    for (const localization of this._localizations) {
      if (localization.frame <= frameIdx) {
        latest = localization;
      }
    }
   
    // If the track contains no localizations from before this frame, take no action.
    if (latest === null) {
      return;
    }

    // Convert frame data to a mat.
    const frame = cv.matFromArray(this._height, this._width, cv.CV_8UC4, frameData);
    cv.flip(frame, frame, 0);
    
    if (latest.frame == frameIdx) {
      // If latest is for this current frame, set the mean shift ROI.
      console.info("Setting ROI with existing localization!");
      this._setRoi(latest, frame);
    } else {
      // If the latest is older than current frame, predict the new ROI.
      console.info("Predicting new localization!");
      this._predict(frame, frameIdx);
    }

    // Clean up.
    frame.delete();
  }

  finalize() {
    console.info("Done algorithm");
    // Create new localizations.
    // Clean up.
    this._dst.delete();
    this._hsvVec.delete();
    this._roiHist.delete();
    this._hsv.delete();
  }

  _setRoi(latest, frame) {
    // Set the version.
    this._version = latest.version;

    // Set location of window
    const x = Math.round(latest.x * this._width);
    const y = Math.round(latest.y * this._height);
    const w = Math.round(latest.width * this._width);
    const h = Math.round(latest.height * this._height);
    this._trackWindow = new cv.Rect(x, y, w, h);

    // set up the ROI for tracking
    let roi = frame.roi(this._trackWindow);
    let hsvRoi = new cv.Mat();
    cv.cvtColor(roi, hsvRoi, cv.COLOR_RGBA2RGB);
    cv.cvtColor(hsvRoi, hsvRoi, cv.COLOR_RGB2HSV);
    let mask = new cv.Mat();
    let lowScalar = new cv.Scalar(30, 30, 0);
    let highScalar = new cv.Scalar(180, 180, 180);
    let low = new cv.Mat(hsvRoi.rows, hsvRoi.cols, hsvRoi.type(), lowScalar);
    let high = new cv.Mat(hsvRoi.rows, hsvRoi.cols, hsvRoi.type(), highScalar);
    cv.inRange(hsvRoi, low, high, mask);
    this._roiHist = new cv.Mat();
    let hsvRoiVec = new cv.MatVector();
    hsvRoiVec.push_back(hsvRoi);
    cv.calcHist(hsvRoiVec, [0], mask, this._roiHist, [180], [0, 180]);
    cv.normalize(this._roiHist, this._roiHist, 0, 255, cv.NORM_MINMAX);

    // delete useless mats.
    roi.delete(); hsvRoi.delete(); mask.delete(); low.delete(); high.delete(); hsvRoiVec.delete();

    this._hsv = new cv.Mat(this._height, this._width, cv.CV_8UC3);
    this._dst = new cv.Mat();
    this._hsvVec = new cv.MatVector();
    this._hsvVec.push_back(this._hsv);
  }

  _predict(frame, frameIdx) {

    cv.cvtColor(frame, this._hsv, cv.COLOR_RGBA2RGB);
    cv.cvtColor(this._hsv, this._hsv, cv.COLOR_RGB2HSV);
    cv.calcBackProject(this._hsvVec, [0], this._roiHist, this._dst, [0, 180], 1);

    // Apply meanshift to get the new location
    // and it also returns number of iterations meanShift took to converge,
    // which is useless in this demo.
    [, this._trackWindow] = cv.meanShift(this._dst, this._trackWindow, this._termCrit);

    // Buffer the localization to be saved to platform.
    this._newLocalizations.push({
      media_id: this._mediaId,
      type: Number(this._track.meta.split("_")[1]),
      x: this._trackWindow.x / this._width,
      y: this._trackWindow.y / this._height,
      width: this._trackWindow.width / this._width,
      height: this._trackWindow.height / this._height,
      frame: frameIdx,
      version: this._version,
    });

  }
}

// Eval won't store the 'Algo' class definition globally
// This is actually helpful, we just need a factory method to
// construct it
function algoFactory(videoDef, algoCanvas) {
  return new FillTrack(videoDef, algoCanvas);
}