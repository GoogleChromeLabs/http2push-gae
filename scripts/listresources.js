/**
 * Copyright 2015 Google Inc. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// jshint node: true

'use strict';

var fs = require('fs');
var hyd = require('hydrolysis');
var dom5 = require('dom5');
var url = require('url');
var path = require('path');

var basePath = process.argv[2];
var inputPath = process.argv[3];

if (!inputPath || !basePath) {
  console.error('Need input path!');
  process.exit(1);
}

basePath = path.resolve(basePath);
inputPath = path.resolve(path.resolve(basePath, inputPath));

if (fs.statSync(inputPath).isDirectory()) {
  inputPath = path.join(inputPath, 'index.html');
}

var loader = new hyd.Loader();
loader.addResolver(new hyd.FSResolver({
  root: basePath,
  basePath: '/'
}));
var EXTERNAL = /^(?:https?:)?\/\//;
loader.addResolver(new hyd.NoopResolver(EXTERNAL));

var analyzer = new hyd.Analyzer(false, loader);

function treeToList(tree, accum) {
  if (!accum) {
    accum = [];
  }
  accum.push(tree.href);
  for(var i = 0; i < tree.imports.length; i++) {
  }
}

function styleToUrl(href, style) {
  var src = dom5.getAttribute(style, 'href');
  if (EXTERNAL.test(src)) {
    return;
  }
  if (src) {
    return url.resolve(href, src);
  }
}

function scriptToUrl(href, script) {
  var src = dom5.getAttribute(script, 'src');
  if (EXTERNAL.test(src)) {
    return;
  }
  if (src) {
    return url.resolve(href, src);
  }
}

function treeToUrls(tree, accum) {
  if (!accum) {
    accum = [];
  }
  if (!tree) {
    return accum;
  }
  if (!tree.href) {
    return accum;
  }
  accum.push(tree.href);
  tree.imports.forEach(function(im) {
    if (im.href) {
      treeToUrls(im, accum);
    }
  });
  tree.html.script.forEach(function(script) {
    var u = scriptToUrl(tree.href, script);
    if (u) {
      accum.push(u);
    }
  });
  tree.html.style.forEach(function(style) {
    var u = styleToUrl(tree.href, style);
    if (u) {
      accum.push(u);
    }
  });
  return accum;
}

inputPath = path.join('/', path.relative(basePath, inputPath));

exports.list = function() {
  return analyzer.metadataTree(inputPath).then(function(tree) {
    var list = treeToUrls(tree).slice(1).reverse();
    return list;
  }).catch(function(error) {
    console.log(error);
  });
}
