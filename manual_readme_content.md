[comment]: # " File: README.md"
[comment]: # "  Copyright (c) SpecterOps, 2025"
[comment]: # ""
[comment]: # "Licensed under the Apache License, Version 2.0 (the 'License');"
[comment]: # "you may not use this file except in compliance with the License."
[comment]: # "You may obtain a copy of the License at"
[comment]: # ""
[comment]: # "    http://www.apache.org/licenses/LICENSE-2.0"
[comment]: # ""
[comment]: # "Unless required by applicable law or agreed to in writing, software distributed under"
[comment]: # "the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
[comment]: # "either express or implied. See the License for the specific language governing permissions"
[comment]: # "and limitations under the License."
[comment]: # ""

## Overview

BloodHound uses graph theory to reveal hidden and often unintended relationships within Active Directory or Azure environments. Attackers use BloodHound to identify complex attack paths quickly. Defenders leverage it to identify and eliminate these same attack paths.

The SOAR integration with SpecterOps BloodHound enables defenders to see all attack path findings as Splunk SOAR events. Additionally, the app provides actions to remediate and remove these attack paths.

## Supported Actions

1. **Get Object ID**  
   Fetch the object ID using the asset's name.

2. **Test Connectivity**  
   Validate the asset configuration and ensure connectivity using the supplied configuration.

3. **On Poll**  
   Pull details about Attack Path Findings.

4. **Fetch Asset Information**  
   Retrieve information related to an asset from the API.  
   *Works in both Enterprise and Community Edition (CE).*

5. **Does Path Exist**  
   Fetch the path between two objects.  
   *Works in both Enterprise and Community Edition (CE).*

## Prerequisites

1. **Access To BloodHound Enterprise Server**
    You must have access to the BloodHound Enterprise server to generate Token Key and Token ID for authentication.


