"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.useMturkTask = useMturkTask;
exports.SubmitTask = SubmitTask;
exports.Task = Task;
Object.defineProperty(exports, "serialize", {
  enumerable: true,
  get: function get() {
    return _mturkUtils.serialize;
  }
});
Object.defineProperty(exports, "deserialize", {
  enumerable: true,
  get: function get() {
    return _mturkUtils.deserialize;
  }
});
Object.defineProperty(exports, "serializeURI", {
  enumerable: true,
  get: function get() {
    return _mturkUtils.serializeURI;
  }
});
Object.defineProperty(exports, "deserializeURI", {
  enumerable: true,
  get: function get() {
    return _mturkUtils.deserializeURI;
  }
});

var _react = _interopRequireDefault(require("react"));

var _mturkUtils = require("mturk-utils");

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _typeof(obj) { if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance"); }

function _iterableToArrayLimit(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function useMturkTask() {
  return _react.default.useMemo(_mturkUtils.getMturkTaskInfo, []);
}

function SubmitTask(_ref) {
  var task = _ref.task,
      data = _ref.data,
      onSubmit = _ref.onSubmit,
      encodeURI = _ref.encodeURI,
      render = _ref.render;

  var _React$useState = _react.default.useState(false),
      _React$useState2 = _slicedToArray(_React$useState, 2),
      isSubmitting = _React$useState2[0],
      setIsSubmitting = _React$useState2[1];

  var formRef = _react.default.useRef(null);

  var submitForm = function submitForm() {
    formRef.current && formRef.current.submit();
    setIsSubmitting(false);
  };

  var handleSubmit = function handleSubmit() {
    setIsSubmitting(true);

    if (!onSubmit) {
      submitForm();
    }

    var result = onSubmit(data);

    if (!isPromise(result)) {
      submitForm();
    }

    result.then(function () {
      return submitForm();
    });
  };

  return _react.default.createElement("div", null, _react.default.createElement("form", {
    ref: formRef,
    action: task.mturk.turkSubmitTo,
    method: "POST",
    style: {
      margin: 0,
      padding: 0,
      width: 0,
      height: 0
    }
  }, _react.default.createElement("input", {
    readOnly: true,
    hidden: true,
    type: "text",
    name: "assignmentId",
    value: task.mturk.assignmentId
  }), _react.default.createElement("input", {
    readOnly: true,
    hidden: true,
    type: "text",
    name: "data",
    value: (0, _mturkUtils.serialize)(data, encodeURI)
  })), render({
    handleSubmit: handleSubmit,
    isSubmitting: isSubmitting
  }));
}

function Task(_ref2) {
  var renderPreview = _ref2.renderPreview,
      renderReview = _ref2.renderReview,
      renderLive = _ref2.renderLive,
      _ref2$defaultReviewSt = _ref2.defaultReviewState,
      defaultReviewState = _ref2$defaultReviewSt === void 0 ? {} : _ref2$defaultReviewSt,
      _ref2$initialLiveStat = _ref2.initialLiveState,
      initialLiveState = _ref2$initialLiveStat === void 0 ? {} : _ref2$initialLiveStat;

  if (!(renderPreview && renderLive)) {
    throw new Error("The two states for renderPreview and renderLive must be defined.");
  }

  var task = useMturkTask();

  var _React$useState3 = _react.default.useState(initialLiveState),
      _React$useState4 = _slicedToArray(_React$useState3, 2),
      state = _React$useState4[0],
      setState = _React$useState4[1];

  if (task.isPreview) {
    return renderPreview({
      task: task
    });
  }

  if (task.isReview) {
    var reviewData = task.isReview && task.reviewData ? (0, _mturkUtils.deserializeURI)(task.reviewData) : defaultReviewState;
    return renderReview({
      reviewData: reviewData,
      task: task
    });
  }

  if (task.isLive) {
    return renderLive({
      task: task,
      state: state,
      setState: setState
    });
  }
}

function isPromise(obj) {
  return !!obj && (_typeof(obj) === "object" || typeof obj === "function") && typeof obj.then === "function";
}
