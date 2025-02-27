[comment]: # "Auto-generated SOAR connector documentation"
# SpecterOps BloodHound

Publisher: SpecterOps  
Connector Version: 1.0.0  
Product Vendor: SpecterOps  
Product Name: Specterops Bloodhound  
Product Version Supported (regex): ".\*"  
Minimum Product Version: 6.3.0  

BloodHound uses graph theory to reveal the hidden and often unintended relationships within an Active Directory or Azure environment. Attackers can use BloodHound to easily identify highly complex attack paths that would otherwise be impossible to identify quickly. Defenders can use BloodHound to identify and eliminate those same attack paths. The SOAR integration with SpecterOps BloodHound enables the defenders to see all the attack path findings from BloodHound as Splunk SOAR events. The actions provided with the app can be used to remediate and remove the attack paths

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




### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Specterops Bloodhound asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**bloodhound_base_url** |  required  | string | BloodHound Enterprise Domain
**token_id** |  required  | password | Token ID
**token_key** |  required  | password | Token Key

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration  
[on poll](#action-on-poll) - Pull Attack Path Finding Details  
[fetch asset information](#action-fetch-asset-information) - Pull information related to an asset from the API (works in Enterprise or CE)  
[does path exist](#action-does-path-exist) - Pull a path between two objects (works in Enterprise or CE)  
[get object id](#action-get-object-id) - Fetch object id from asset's name  

## action: 'test connectivity'
Validate the asset configuration for connectivity using supplied configuration

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'on poll'
Pull Attack Path Finding Details

Type: **ingest**  
Read only: **False**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'fetch asset information'
Pull information related to an asset from the API (works in Enterprise or CE)

Type: **investigate**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**object_id** |  required  | Object Id | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.data.\*.data.props.name | string |  |  
action_result.data.\*.data.props.domain | string |  |  
action_result.data.\*.data.props.objectid | string |  |  
action_result.data.\*.data.props.domainsid | string |  |  
action_result.data.\*.data.props.functionallevel | string |  |  
action_result.data.\*.data.props.distinguishedname | string |  |  
action_result.data.\*.data.props.isaclprotected | boolean |  |  
action_result.data.data.\*.props.system_tags | string |  |  
action_result.message | string |  |  
action_result.summary | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1 
action_result.status | string |  |   success  failed   

## action: 'does path exist'
Pull a path between two objects (works in Enterprise or CE)

Type: **investigate**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**start_node** |  required  | Start Node | string | 
**end_node** |  required  | End Node | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.start_node | string |  |  
action_result.parameter.end_node | string |  |  
action_result.data.\*.response | string |  |  
action_result.message | string |  |  
action_result.summary | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1 
action_result.status | string |  |   success  failed   

## action: 'get object id'
Fetch object id from asset's name

Type: **investigate**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**name** |  required  | Name | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.name | string |  |  
action_result.data.\*.object_id | string |  |  
action_result.message | string |  |  
action_result.summary | string |  |  
summary.total_objects | numeric |  |   1 
summary.total_objects_successful | numeric |  |   1 
action_result.status | string |  |   success  failed 