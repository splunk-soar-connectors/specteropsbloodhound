# SpecterOps BloodHound App

**Publisher**: SpecterOps  
**Contributors**: N/A  
**App Version**: 1.0.0  
**Product Vendor**: SpecterOps  
**Product Name**: SpecterOps BloodHound  
**Supported Product Version (Regex)**: `.*`

---

## Overview

BloodHound uses graph theory to reveal hidden and often unintended relationships within Active Directory or Azure environments. Attackers use BloodHound to identify complex attack paths quickly. Defenders leverage it to identify and eliminate these same attack paths.

The SOAR integration with SpecterOps BloodHound enables defenders to see all attack path findings as Splunk SOAR events. Additionally, the app provides actions to remediate and remove these attack paths.

---

## Configuration Variables

The following configuration variables are required to set up the SpecterOps BloodHound App in Splunk SOAR:

| **Variable**            | **Required** | **Type**   | **Description**                      |
|--------------------------|--------------|------------|---------------------------------------|
| `token_id`              | Required     | Password   | Token ID                              |
| `token_key`             | Required     | Password   | Token Key                             |
| `bloodhound_base_url`   | Required     | String     | BloodHound Enterprise Domain          |

---

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

---

### Action: Get Object ID  
**Description**: Fetch the object ID from an asset's name.  
**Type**: Investigate  
**Read Only**: No  

#### Parameters

| **Parameter** | **Required** | **Description** | **Type** |
|---------------|--------------|-----------------|----------|
| `name`        | Required     | Name            | String   |
#### Output

| **Data Path**                      | **Type**   |
|------------------------------------|------------|
| `action_result.parameter.name`    | String     |
| `action_result.data.*.object_id`  | String     |
| `action_result.message`           | String     |
| `summary.total_objects`           | Numeric    |
| `summary.total_objects_successful`| Numeric    |

---

### Action: Test Connectivity  
**Description**: Validate the asset configuration for connectivity using the supplied configuration.  
**Type**: Test  
**Read Only**: Yes  

#### Parameters

_No parameters required._

#### Output

_No output._

---

### Action: On Poll  
**Description**: Pull Attack Path Finding details.  
**Type**: Ingest  
**Read Only**: No  

#### Parameters

_No parameters required._

#### Output

_No output._

---

### Action: Fetch Asset Information  
**Description**: Retrieve information related to an asset from the API.  
*Works in both Enterprise and Community Edition (CE).*  
**Type**: Investigate  
**Read Only**: No  

#### Parameters

| **Parameter**   | **Required** | **Description** | **Type**   |
|------------------|--------------|-----------------|------------|
| `object_id`     | Required     | Object ID       | String     |

#### Output

| **Data Path**                                       | **Type**   |
|----------------------------------------------------|------------|
| `action_result.data.data.*.props.name`                  | String     |
| `action_result.data.data.*.props.domain`                | String     |
| `action_result.data.data.*.props.objectid`              | String     |
| `action_result.data.data.*.props.domainsid`             | String     |
| `action_result.data.data.*.props.functionallevel`       | String     |
| `action_result.data.data.*.props.distinguishedname`     | String     |
| `action_result.data.data.*.props.isaclprotected`        | Boolean    |
| `action_result.data.data.*.props.system_tags`           | String     |

---

### Action: Does Path Exist  
**Description**: Fetch a path between two objects.  
*Works in both Enterprise and Community Edition (CE).*  
**Type**: Investigate  
**Read Only**: No  

#### Parameters

| **Parameter**   | **Required** | **Description** | **Type**   |
|------------------|--------------|-----------------|------------|
| `start_node`     | Required     | Start Node      | String     |
| `end_node`       | Required     | End Node        | String     |

#### Output

| **Data Path**                      | **Type**   |
|------------------------------------|------------|
| `action_result.parameter.start_node` | String    |
| `action_result.parameter.end_node`   | String    |
| `action_result.data.*.response`      | String    |
