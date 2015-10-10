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

deployVersion=$1

if [ -z "$deployVersion" ]
then
  echo "App version not specified."
  exit 1
fi

readonly BASEDIR=$(dirname $BASH_SOURCE)

echo "\nBuilding app version: $deployVersion\n"
$BASEDIR/build.sh

echo "Deploying app version: $deployVersion"
gcloud preview app deploy $BASEDIR/../app.yaml \
    --project http2-push --version $deployVersion
