const assert = require("node:assert/strict");

const handlers = {};
const source = {
  dataset: { src: "assets/FWBC-demo.mp4" },
  src: "",
  removeAttribute(name) {
    if (name === "data-src") delete this.dataset.src;
  },
};
const video = {
  loadCalls: 0,
  playCalls: 0,
  querySelector(selector) {
    assert.equal(selector, "source[data-src]");
    return source;
  },
  addEventListener(event, handler) {
    handlers[event] = handler;
  },
  load() {
    this.loadCalls += 1;
  },
  play() {
    this.playCalls += 1;
    return Promise.resolve();
  },
};

global.document = {
  getElementById() {
    return null;
  },
  querySelector(selector) {
    assert.equal(selector, "[data-lazy-video]");
    return video;
  },
};

require("../assets/script.js");

assert.equal(source.src, "");
assert.equal(video.loadCalls, 0);
assert.equal(video.playCalls, 0);
assert.equal(typeof handlers.click, "function");

handlers.click();

assert.equal(source.src, "assets/FWBC-demo.mp4");
assert.equal(video.loadCalls, 1);
assert.equal(video.playCalls, 1);
