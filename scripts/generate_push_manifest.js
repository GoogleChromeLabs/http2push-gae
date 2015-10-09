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
var listelements = require('./listresources');

var PUSH_PRIORITY = 1; // TODO: this gives every resource priority 1.

// function generateAssociateContentHeader(urls) {
//   // X-Associated-Content: "https://www.example.com/styles/foo.css",
//   //     "/scripts/bar.js":1,

//   var associateContent = [];

//   for (var url in urls) {
//     var entry = '"' + url + '"';
//     var priority = urls[url];
//     if (priority !== null) {
//       entry += ':' +  priority;
//     }
//     associateContent.push(entry);
//   }

//   return associateContent.join(',');
// }

listelements.list().then(function(urls) {
  console.log('== Found these resource URLs in this app ==');

  for (var i = 0, url; url = urls[i]; ++i) {
    console.log('  ', url);
  }

  var priorityMapping = {};
  urls.map(function(url, i) {
    priorityMapping[url] = PUSH_PRIORITY;
  });

  var fileContent = JSON.stringify(priorityMapping, null, 2);
  fs.writeFile('push_manifest.json', fileContent, function(err) {
    if (err) {
      return console.log(err);
    }

    console.log('\nManifest file written!');
  });

});


