/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory(require("ReactDOM"), require("React"));
	else if(typeof define === 'function' && define.amd)
		define(["ReactDOM", "React"], factory);
	else if(typeof exports === 'object')
		exports["gridContainer"] = factory(require("ReactDOM"), require("React"));
	else
		root["gridContainer"] = factory(root["ReactDOM"], root["React"]);
})(self, (__WEBPACK_EXTERNAL_MODULE_react_dom__, __WEBPACK_EXTERNAL_MODULE_react__) => {
return /******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./node_modules/react-dom/client.js":
/*!******************************************!*\
  !*** ./node_modules/react-dom/client.js ***!
  \******************************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

eval("\n\nvar m = __webpack_require__(/*! react-dom */ \"react-dom\");\nif (false) {} else {\n  var i = m.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED;\n  exports.createRoot = function(c, o) {\n    i.usingClientEntryPoint = true;\n    try {\n      return m.createRoot(c, o);\n    } finally {\n      i.usingClientEntryPoint = false;\n    }\n  };\n  exports.hydrateRoot = function(c, h, o) {\n    i.usingClientEntryPoint = true;\n    try {\n      return m.hydrateRoot(c, h, o);\n    } finally {\n      i.usingClientEntryPoint = false;\n    }\n  };\n}\n\n\n//# sourceURL=webpack://Container/./node_modules/react-dom/client.js?");

/***/ }),

/***/ "./src/components/core/GridContainer.jsx":
/*!***********************************************!*\
  !*** ./src/components/core/GridContainer.jsx ***!
  \***********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (__WEBPACK_DEFAULT_EXPORT__)\n/* harmony export */ });\n/* harmony import */ var react_dom_client__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react-dom/client */ \"./node_modules/react-dom/client.js\");\n/* harmony import */ var _SensorDisplay__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./SensorDisplay */ \"./src/components/core/SensorDisplay.js\");\nfunction _slicedToArray(r, e) { return _arrayWithHoles(r) || _iterableToArrayLimit(r, e) || _unsupportedIterableToArray(r, e) || _nonIterableRest(); }\nfunction _nonIterableRest() { throw new TypeError(\"Invalid attempt to destructure non-iterable instance.\\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.\"); }\nfunction _unsupportedIterableToArray(r, a) { if (r) { if (\"string\" == typeof r) return _arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return \"Object\" === t && r.constructor && (t = r.constructor.name), \"Map\" === t || \"Set\" === t ? Array.from(r) : \"Arguments\" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? _arrayLikeToArray(r, a) : void 0; } }\nfunction _arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }\nfunction _iterableToArrayLimit(r, l) { var t = null == r ? null : \"undefined\" != typeof Symbol && r[Symbol.iterator] || r[\"@@iterator\"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t[\"return\"] && (u = t[\"return\"](), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }\nfunction _arrayWithHoles(r) { if (Array.isArray(r)) return r; }\n// src/GridContainer.jsx\n\n // Adjust path if needed\n\nvar GridContainer = function GridContainer() {\n  var AttachStreamView = function AttachStreamView(gridId, streamId, widgetType) {\n    var gridIdValue = (gridId === null || gridId === void 0 ? void 0 : gridId.value) || gridId;\n    var streamIdValue = (streamId === null || streamId === void 0 ? void 0 : streamId.value) || streamId;\n    var widgetTypeValue = (widgetType === null || widgetType === void 0 ? void 0 : widgetType.value) || widgetType || \"GraphDisplay\";\n    console.log(\"Attaching stream view:\", {\n      gridId: gridIdValue,\n      streamId: streamIdValue,\n      widgetType: widgetTypeValue\n    });\n    var gridElement = document.querySelector(\"[gs-id=\\\"\".concat(gridIdValue, \"\\\"]\"));\n    if (!gridElement) {\n      console.error(\"Grid with gs-id \\\"\".concat(gridIdValue, \"\\\" not found\"));\n      return;\n    }\n    var contentDiv = gridElement.querySelector('.grid-stack-item-content');\n    if (!contentDiv) {\n      console.error('Grid item content div not found');\n      return;\n    }\n    var componentContainer = document.createElement('div');\n    componentContainer.className = 'component-container';\n    contentDiv.appendChild(componentContainer);\n    var root = (0,react_dom_client__WEBPACK_IMPORTED_MODULE_0__.createRoot)(componentContainer);\n    if (widgetTypeValue === \"SensorDisplay\") {\n      root.render(/*#__PURE__*/React.createElement(_SensorDisplay__WEBPACK_IMPORTED_MODULE_1__[\"default\"], {\n        streamId: streamIdValue\n      }));\n    } else if (widgetTypeValue === \"GraphDisplay\") {\n      if (window.GraphDisplay) {\n        root.render(/*#__PURE__*/React.createElement(window.GraphDisplay, {\n          streamId: streamIdValue\n        }));\n      } else {\n        root.render(/*#__PURE__*/React.createElement(\"div\", null, \"Loading graph component...\"));\n        var checkInterval = setInterval(function () {\n          if (window.GraphDisplay) {\n            root.render(/*#__PURE__*/React.createElement(window.GraphDisplay, {\n              streamId: streamIdValue\n            }));\n            clearInterval(checkInterval);\n          }\n        }, 100);\n      }\n    } else {\n      root.render(/*#__PURE__*/React.createElement(\"div\", null, \"Unknown widget type: \", widgetTypeValue));\n    }\n    if (window.subscribeToStream) {\n      var _streamIdValue$split = streamIdValue.split('.'),\n        _streamIdValue$split2 = _slicedToArray(_streamIdValue$split, 2),\n        moduleId = _streamIdValue$split2[0],\n        streamName = _streamIdValue$split2[1];\n      window.subscribeToStream(moduleId, streamName);\n    }\n  };\n  window.AttachStreamView = AttachStreamView;\n  return /*#__PURE__*/React.createElement(\"div\", {\n    className: \"grid-stack\"\n  });\n};\n/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (GridContainer);\n\n//# sourceURL=webpack://Container/./src/components/core/GridContainer.jsx?");

/***/ }),

/***/ "./src/components/core/SensorDisplay.js":
/*!**********************************************!*\
  !*** ./src/components/core/SensorDisplay.js ***!
  \**********************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (__WEBPACK_DEFAULT_EXPORT__)\n/* harmony export */ });\n/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ \"react\");\nfunction _slicedToArray(r, e) { return _arrayWithHoles(r) || _iterableToArrayLimit(r, e) || _unsupportedIterableToArray(r, e) || _nonIterableRest(); }\nfunction _nonIterableRest() { throw new TypeError(\"Invalid attempt to destructure non-iterable instance.\\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.\"); }\nfunction _unsupportedIterableToArray(r, a) { if (r) { if (\"string\" == typeof r) return _arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return \"Object\" === t && r.constructor && (t = r.constructor.name), \"Map\" === t || \"Set\" === t ? Array.from(r) : \"Arguments\" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? _arrayLikeToArray(r, a) : void 0; } }\nfunction _arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }\nfunction _iterableToArrayLimit(r, l) { var t = null == r ? null : \"undefined\" != typeof Symbol && r[Symbol.iterator] || r[\"@@iterator\"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t[\"return\"] && (u = t[\"return\"](), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }\nfunction _arrayWithHoles(r) { if (Array.isArray(r)) return r; }\n// src/components/SensorDisplay.js\n\nvar SensorDisplay = function SensorDisplay(_ref) {\n  var streamId = _ref.streamId;\n  var _useState = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(null),\n    _useState2 = _slicedToArray(_useState, 2),\n    sensorValue = _useState2[0],\n    setSensorValue = _useState2[1];\n  (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(function () {\n    // Subscribe to stream updates when component mounts\n    if (!streamId) return;\n    var _streamId$split = streamId.split('.'),\n      _streamId$split2 = _slicedToArray(_streamId$split, 2),\n      moduleId = _streamId$split2[0],\n      streamName = _streamId$split2[1];\n\n    // Setup update interval\n    var updateInterval = setInterval(function () {\n      var _window$GlobalData;\n      // Check if GlobalData exists and has the required data\n      if ((_window$GlobalData = window.GlobalData) !== null && _window$GlobalData !== void 0 && (_window$GlobalData = _window$GlobalData.data) !== null && _window$GlobalData !== void 0 && (_window$GlobalData = _window$GlobalData[moduleId]) !== null && _window$GlobalData !== void 0 && (_window$GlobalData = _window$GlobalData.streams) !== null && _window$GlobalData !== void 0 && _window$GlobalData[streamName]) {\n        setSensorValue(window.GlobalData.data[moduleId].streams[streamName].value);\n      }\n    }, 100); // Update every 100ms\n\n    // Cleanup interval on unmount\n    return function () {\n      return clearInterval(updateInterval);\n    };\n  }, [streamId]); // Re-run effect if streamId changes\n\n  return /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0__.createElement(\"div\", {\n    className: \"sensor-display\"\n  }, /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0__.createElement(\"h3\", null, \"Stream Display\"), /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0__.createElement(\"p\", null, \"Monitoring Stream: \", streamId), /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0__.createElement(\"p\", null, \"Current Value: \", sensorValue !== null ? sensorValue : 'No data'));\n};\n/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (SensorDisplay);\n\n//# sourceURL=webpack://Container/./src/components/core/SensorDisplay.js?");

/***/ }),

/***/ "react":
/*!************************!*\
  !*** external "React" ***!
  \************************/
/***/ ((module) => {

module.exports = __WEBPACK_EXTERNAL_MODULE_react__;

/***/ }),

/***/ "react-dom":
/*!***************************!*\
  !*** external "ReactDOM" ***!
  \***************************/
/***/ ((module) => {

module.exports = __WEBPACK_EXTERNAL_MODULE_react_dom__;

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	var __webpack_exports__ = __webpack_require__("./src/components/core/GridContainer.jsx");
/******/ 	
/******/ 	return __webpack_exports__;
/******/ })()
;
});