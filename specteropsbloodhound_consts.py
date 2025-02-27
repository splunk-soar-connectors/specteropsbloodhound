#
# CCopyright (c) SpecterOps, 2025
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.

# Define your constants here
DEFAULT_REQUEST_TIMEOUT = 60  # in seconds

DIRECTORY_TYPES = [
    "User",
    "Computer",
    "Group",
    "Container",
    "Domain",
    "GPO",
    "Aiaca",
    "Rootca",
    "Enterpriseca",
    "Ntauthstore",
    "Certtemplate",
    "OU",
]

AZURE_TYPES = ["AZApp", "AZGroup", "AZUser", "AZRole", "AZTenant", "AZServicePrincipal"]

AZURE_RELATED_TYPES = {
    "AZApp": {"inbound-control": "inbound_object_control"},
    "AZGroup": {
        "group-membership": "group_membership",
        "group-members": "group_members",
        "roles": "roles",
        "inbound-control": "inbound_object_control",
        "outbound-control": "outbound_object_control",
    },
    "AZRole": {"active-assignments": "active_assignments"},
    "AZServicePrincipal": {
        "roles": "roles",
        "inbound-control": "inbound_object_control",
        "outbound-control": "outbound_object_control",
        "inbound-abusable-app-role-assignments": "inbound_abusable_app_role_assignments",
        "outbound-abusable-app-role-assignments": "outbound_abusable_app_role_assignments",
    },
    "AZUser": {
        "group-membership": "group_membership",
        "roles": "roles",
        "outbound-execution-privileges": "execution_privileges",
        "outbound-control": "outbound_object_control",
        "inbound-control": "inbound_object_control",
    },
}

AZ_TENANT_RELATED_TYPES = [
    "descendent-users",
    "descendent-groups",
    "descendent-management-groups",
    "descendent-subscriptions",
    "descendent-resource-groups",
    "descendent-virtual-machines",
    "descendent-managed-clusters",
    "descendent-vm-scale-sets",
    "descendent-container-registries",
    "descendent-web-apps",
    "descendent-automation-accounts",
    "descendent-key-vaults",
    "descendent-function-apps",
    "descendent-logic-apps",
    "descendent-applications",
    "descendent-service-principals",
    "descendent-devices",
    "inbound-control",
]
