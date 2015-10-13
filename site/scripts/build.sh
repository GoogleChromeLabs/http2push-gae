#!/bin/sh

# Copyright 2015 Google Inc. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# The directory in which this script resides.
readonly BASEDIR=$(dirname $BASH_SOURCE)

readonly STATICDIR=$BASEDIR/../static

echo '=== Vulcanizing HTML Imports ==='
vulcanize $STATICDIR/elements.html --inline-script --inline-css \
    --strip-comments > $STATICDIR/elements.vulcanize.html

echo '=== Generating HTTP2 push resource manifest ==='
npm run push
