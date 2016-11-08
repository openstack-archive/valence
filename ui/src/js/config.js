/*Copyright (c) 2016 Intel, Inc.
 *
 *   Licensed under the Apache License, Version 2.0 (the "License"); you may
 *   not use this file except in compliance with the License. You may obtain
 *   a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 *   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 *   License for the specific language governing permissions and limitations
 *   under the License.
 */

/*
 * Configuration file for RSC UI.
 */

exports.url = "http://127.0.0.1:8181"

exports.nodeConfig =
{
  "Name": "Test Node",
  "Description": "This is a node composed from the config file.",
  "Processors": [{
    "Model": null
  }],
  "Memory": [{
    "CapacityMiB": 8000
  }],
  "LocalDrives": null
}

