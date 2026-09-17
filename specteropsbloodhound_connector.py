# File: specteropsbloodhound_consts.py
#
# Copyright (c) SpecterOps, 2026
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

import base64
import datetime
import hashlib
import hmac
from urllib.parse import quote

import phantom.app as phantom
import requests
from phantom.action_result import ActionResult
from phantom.base_connector import BaseConnector

from specteropsbloodhound_consts import *


class RetVal(tuple):
    def __new__(cls, val1, val2=None):
        return tuple.__new__(RetVal, (val1, val2))


class SpecteropsbloodhoundConnector(BaseConnector):
    def __init__(self):
        super().__init__()
        self._state = None
        self._base_url = None
        self._token_key = None
        self._token_id = None
        self._port = None
        self._scheme = None
        self._start_date = None
        self._end_date = None

    def _process_empty_response(self, response, action_result):
        if response.status_code == 200:
            return RetVal(phantom.APP_SUCCESS, {})
        return RetVal(
            action_result.set_status(
                action_result.set_status(phantom.APP_ERROR, "Empty response and no information in the header"),
                None,
            )
        )

    def _process_html_response(self, response, action_result):
        status_code = response.status_code
        try:
            error_text = response.text
        except Exception:
            error_text = "Cannot parse error details"

        message = f"Status Code: {status_code}. Data from server:\n{error_text}\n"
        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_json_response(self, r, action_result):
        try:
            resp_json = r.json()
        except Exception as e:
            return RetVal(
                action_result.set_status(phantom.APP_ERROR, f"Unable to parse JSON response. Error: {e!s}"),
                None,
            )

        if 200 <= r.status_code < 399:
            return RetVal(phantom.APP_SUCCESS, resp_json)

        message = f"Error from server. Status Code: {r.status_code} Data from server: {r.text.replace('{', '{{').replace('}', '}}')}"
        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_response(self, r, action_result):
        self.debug_print(f"Processing response: Status Code {r.status_code}")
        self.debug_print(f"Response Text: {r.text[:500]}")  # Log first 500 chars

        if hasattr(action_result, "add_debug_data"):
            action_result.add_debug_data({"r_status_code": r.status_code})
            action_result.add_debug_data({"r_text": r.text})
            action_result.add_debug_data({"r_headers": r.headers})

        if "json" in r.headers.get("Content-Type", ""):
            return self._process_json_response(r, action_result)
        if "html" in r.headers.get("Content-Type", ""):
            return self._process_html_response(r, action_result)
        if not r.text:
            return self._process_empty_response(r, action_result)
        else:
            return RetVal(phantom.APP_SUCCESS, r.text)

    def _request(self, method: str, uri: str, action_result, body: bytes | None = None) -> RetVal:
        digester = hmac.new(self._token_key.encode(), None, hashlib.sha256)
        digester.update(f"{method}{uri}".encode())
        digester = hmac.new(digester.digest(), None, hashlib.sha256)
        datetime_formatted = datetime.datetime.now().astimezone().isoformat("T")
        digester.update(datetime_formatted[:13].encode())
        digester = hmac.new(digester.digest(), None, hashlib.sha256)

        if body is not None:
            digester.update(body)

        try:
            r = requests.request(
                method=method,
                url=self._base_url + uri,
                headers={
                    "Authorization": f"bhesignature {self._token_id}",
                    "RequestDate": datetime_formatted,
                    "Signature": base64.b64encode(digester.digest()).decode("ascii"),
                    "Content-Type": "application/json",
                },
                data=body,
            )
        except Exception as e:
            return RetVal(
                action_result.set_status(phantom.APP_ERROR, f"Error Connecting to server. Details: {e!s}"),
                None,
            )

        return self._process_response(r, action_result)

    def _handle_test_connectivity(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))
        self.save_progress("Testing Connectivity...")
        ret_val, response = self._request("GET", "/api/version", action_result)

        if phantom.is_fail(ret_val):
            self.save_progress("Test Connectivity Failed.")
            return action_result.get_status()

        action_result.add_data(response)
        self.save_progress("⣸⡇")
        self.save_progress("⣿⣷")
        self.save_progress("⠙⣯⣳⣄⡀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀")
        self.save_progress("⠀⠉⠙⢯⣏⣳⣶⢶⡿⠟⠉⠉⡏⠉⠉⠏⠉⣉⡻⢾⢷⢤⣀⡀")
        self.save_progress("⠀⠀⠀⠀⠙⠛⠺⡿⣀⠀⠀⢀⣹⡤⠜⠿⢍⡁⠀⡎⠈⣆⠈⠉⣳⢶⡀")
        self.save_progress("⠀⠀⠀⠀⠀⠀⣰⡇⠈⢻⢯⡉⠀⢇⠀⠀⠀⣹⢾⠦⢤⣘⣆⡴⠁⠀⢙⡿⣄")
        self.save_progress("⠀⠀⠀⠀⠀⠀⢹⡷⡄⢸⠀⠈⠳⣜⡆⣠⠞⠁⠀⣇⢀⡴⠋⢯⠓⠒⣼⡆⠈⣻⣆")
        self.save_progress("⠀⠀⠀⠀⠀⢀⡾⣇⠙⣾⣤⠤⠒⠒⡟⠲⢤⣀⣠⢾⡋⠀⠀⢈⠷⡏⠁⠙⢦⡇⠈⣳⣦")
        self.save_progress("⠀⠀⠀⠀⣠⢿⠃⣸⡞⠁⢻⣍⣳⣶⡇⠀⠀⣸⢯⠀⣷⣴⣖⣁⠀⠙⣆⡀⢸⣡⠞⢱⠙⢧⡀")
        self.save_progress("⠀⠀⠀⡿⠓⣾⠞⠁⠀⢀⡼⠁⣰⠃⠀⠀⢰⣧⣸⡼⠁⠰⢷⡌⠙⡏⠉⢙⣿⠁⠠⣯⡤⠤⢿⠆")
        self.save_progress("⠀⠀⢴⣧⣀⣏⠀⠀⠀⠘⢯⠉⣿⡀⠀⠀⢸⣠⢺⠁⠀⠀⠘⣟⢦⣻⠀⢾⡝⡆⣰⡇⣹⣷⣻⡀")
        self.save_progress("⠀⠀⠀⠻⣼⣉⠷⢶⠀⠀⠘⣾⣈⣧⡄⠀⢾⡥⣼⣄⣀⠀⠀⢸⣦⠻⡷⢤⡝⣿⣏⣷⣃⠹⣍⡷")
        self.save_progress("⠀⠀⠀⠀⠋⠉⠉⠉⠀⠀⠀⠉⠳⣭⣟⣻⠀⢳⣤⣞⣛⣇⠀⠀⠈⠳⠿⠥⠽⠆⠀⠉⠉⠉⠛")
        self.save_progress("Successfully Connected to SPECTEROPS BLOODHOUND ENTERPRISE")
        return action_result.set_status(phantom.APP_SUCCESS)

    def _get_available_types_for_domain(self, domain_id, action_result):
        # Fetch available types for the domain
        self.save_progress(f"Fetch available types for the domain ID: {domain_id}")
        endpoint = f"/api/v2/domains/{domain_id}/available-types"
        # Do not fail the poll action if one domain has no types metadata.
        types_result = ActionResult(dict())
        ret_val, path_ids_response = self._request("GET", endpoint, types_result)

        if phantom.is_fail(ret_val) or not path_ids_response:
            self.save_progress(f"Failed to fetch types for Domain ID: {domain_id}, skipping domain")
            return []
        # Here, types is a list of strings
        types = path_ids_response.get("data") or []
        self.debug_print(f"Fetched Types for Domain ID {domain_id}: {types}")
        self.save_progress(f"The domain with ID {domain_id} has {len(types)} types in total")
        return types

    def _fetch_finding_details_by_pages(self, domain_id, finding_type, skip, limit, action_result):
        # Using the finding_type directly as it's a string now
        self.debug_print(f"Fetching findings for domain id {domain_id} and type {finding_type} for current page")
        self.debug_print(f"Fetch {limit} finding by skipping {skip} findings")
        findings_endpoint = f"/api/v2/domains/{domain_id}/details?finding={finding_type}&skip={skip}&limit={limit}"
        details_result = ActionResult(dict())
        ret_val, details_response = self._request("GET", findings_endpoint, details_result)
        if phantom.is_fail(ret_val):
            self.save_progress(f"Failed to fetch findings for Finding Type: {finding_type} in Domain ID: {domain_id}")
            return phantom.APP_ERROR, {}
        return ret_val, details_response or {}

    def _fetch_all_findings_information(self, domain_id, finding_type, action_result):
        self.save_progress(f"Fetching ALL the findings for domain id {domain_id} and type {finding_type}")
        all_findings_for_type = []
        skip = 0
        limit = 10
        while True:
            ret_val, details_response = self._fetch_finding_details_by_pages(domain_id, finding_type, skip, limit, action_result)
            if phantom.is_fail(ret_val):
                self.save_progress(f"Failed to fetch findings for Finding Type: {finding_type} in Domain ID: {domain_id}")
                return all_findings_for_type
            data = details_response.get("data", [])
            if len(data) == 0:
                break
            all_findings_for_type.extend(data)
            skip = skip + len(data)
            self.debug_print(f"Fetched {details_response.get('count', len(data))} findings in this page")

        self.save_progress(f"Successfully fetched total {len(all_findings_for_type)} findings for domain id {domain_id} and type {finding_type}")
        return all_findings_for_type

    def _get_cef_type(self, field_name):
        self.debug_print("Get the CEF type for the fields, as per it's name")
        # Following are all the possible field types, we have only mapped a few out of those
        # ( "vault id", "file name", "file path", "hash", "host name", "ip", "mac address",
        #  "md5", "port", "process name", "sha1", "sha256", "sha512", "url" )
        field_name_to_type_map = {"domain": "domain", "email": "user id"}
        return field_name_to_type_map.get(field_name)

    def _create_cef_field_and_types_for_principal(self, props):
        self.debug_print("Creating the CEF fields and types for the Principal")
        cef = {}
        cef_types = {}
        for key in props:
            cef[key] = props[key]
            field_type = self._get_cef_type(key)
            if field_type:
                cef_types[key] = [field_type]
        return cef, cef_types

    def _modify_principal_label(self, data, text):
        if isinstance(data, dict):  # Check if data is a dictionary
            if text == "FromPrincipal":
                if data.get("Finding", "").startswith("LargeDefault"):
                    return "Group"
                else:
                    return "Non Tier Zero Principal"

            elif text == "ToPrincipal":
                if data.get("Finding", "").startswith("LargeDefault"):
                    return "Principal"
                else:
                    return "Tier Zero Principal"

        return "User"

    def _build_principal_artifact(self, finding, kind_key, id_key, props_key, label_key):
        if kind_key not in finding:
            return None
        props = finding.get(props_key) or {}
        if not isinstance(props, dict):
            props = {}
        source_id = finding.get(id_key)
        name = props.get("name") or source_id
        if not source_id or not name:
            self.debug_print(f"Skipping artifact for {kind_key}; missing id or name")
            return None
        cef, cef_types = self._create_cef_field_and_types_for_principal(props)
        return {
            "source_data_identifier": source_id,
            "name": name,
            "description": props.get("description", f"{label_key} with name {name}"),
            "type": finding.get(kind_key),
            "label": self._modify_principal_label(finding, label_key),
            "cef": cef,
            "cef_types": cef_types,
        }

    def _create_principle_artifact_details(self, finding):
        self.debug_print("Creating the artifact details")
        return self._build_principal_artifact(finding, "PrincipalKind", "Principal", "Props", "Principal")

    def _create_to_principle_artifact_details(self, finding):
        self.debug_print("Creating the artifact details for ToPrincipal")
        return self._build_principal_artifact(finding, "ToPrincipalKind", "ToPrincipal", "ToPrincipalProps", "ToPrincipal")

    def _create_from_principle_artifact_details(self, finding):
        self.debug_print("Creating the artifact details for From Principal")
        return self._build_principal_artifact(finding, "FromPrincipalKind", "FromPrincipal", "FromPrincipalProps", "FromPrincipal")

    def _get_artifacts_dict_for_finding(self, finding):
        self.debug_print(f"Building finding artifacts for the Finding type {finding.get('Finding')}")
        artifacts = [
            self._create_principle_artifact_details(finding),
            self._create_from_principle_artifact_details(finding),
            self._create_to_principle_artifact_details(finding),
        ]
        return [artifact for artifact in artifacts if artifact]

    def _convert_risk_to_severity(self, risk):
        try:
            risk_value = float(risk)
        except (TypeError, ValueError):
            return "low"
        severity = "low"
        if risk_value > 33.33:
            severity = "medium"
        if risk_value > 66.66:
            severity = "high"
        return severity

    def _get_finding_severity(self, finding, finding_type):
        if "Principal" in finding or str(finding_type).startswith("LargeDefaultGroups"):
            risk = finding.get("ImpactPercentage", 0)
        else:
            risk = finding.get("ExposurePercentage", finding.get("ImpactPercentage", 0))
        if risk is None:
            risk = 0
        try:
            return float(risk) * 100
        except (TypeError, ValueError):
            return 0

    def _get_finding_title(self, path_id, action_result):
        if not hasattr(self, "_title_cache"):
            self._title_cache = {}

        if path_id in self._title_cache:
            return self._title_cache[path_id]

        endpoint = f"/api/v2/assets/findings/{path_id}/title.md"
        # Use a throwaway result so a missing title.md does not fail the poll action.
        title_result = ActionResult(dict())
        ret_val, path_title = self._request("GET", endpoint, title_result)

        if phantom.is_fail(ret_val) or path_title is None:
            self.debug_print(f"Finding title unavailable for path_id: {path_id}, defaulting to empty string")
            self.save_progress(f"Finding title not available for {path_id}, using empty title")
            self._title_cache[path_id] = ""
            return ""

        title = path_title.strip() if isinstance(path_title, str) else ""
        self._title_cache[path_id] = title
        return title

    def _get_container_dict_for_finding(self, finding, domain_name, action_result):
        finding_id = finding.get("id", "")
        finding_type = finding.get("Finding", "")
        path_title = self._get_finding_title(finding_type, action_result) or ""
        self.debug_print(f"Building container for finding {finding['id']}")
        # Build the container JSON
        container_json = {}
        container_json["name"] = f"{domain_name} : {path_title} : {finding_id}"
        container_json["data"] = finding
        container_json["description"] = finding_type
        container_json["source_data_identifier"] = f"{domain_name}:{path_title}:{finding_id}"
        container_json["severity"] = self._convert_risk_to_severity(finding["severity"])

        self.debug_print(f"Create artifacts for the the finding id: {finding['id']}")
        if self._does_container_exist_for_finding(f"{domain_name}:{path_title}:{finding_id}"):
            container_json["artifacts"] = []
        else:
            container_json["artifacts"] = self._get_artifacts_dict_for_finding(finding)

        return container_json

    def _does_container_exist_for_finding(self, source_data_identifier):
        url = f'{self.get_phantom_base_url()}rest/container?_filter_source_data_identifier="{source_data_identifier}"&_filter_asset={self.get_asset_id()}'
        existing_container_id = False

        try:
            r = requests.get(url, verify=False, timeout=DEFAULT_REQUEST_TIMEOUT)  # nosemgrep
            resp_json = r.json()
        except Exception as e:
            err = self._get_error_message_from_exception(e)
            self.debug_print(f"Unable to query container: {err}")
            return False

        if resp_json.get("count", 0) <= 0:
            self.debug_print("No container matched, creating a new one.")
            return False

        try:
            existing_container_id = resp_json.get("data", [])[0]["id"]
        except Exception as e:
            err = self._get_error_message_from_exception(e)
            self.debug_print(f"Container results are not proper: {err}")
            return False

        return existing_container_id

    def _update_container_for_attack_finding(self, existing_container_id, container):
        # First, update the container without updating any artifacts
        try:
            self.debug_print(f"Updating container with id {existing_container_id}")
            update_json = container.copy()
            del update_json["artifacts"]
            url = f"{self.get_phantom_base_url()}rest/container/{existing_container_id}"
            r = requests.post(url, json=update_json, verify=False, timeout=DEFAULT_REQUEST_TIMEOUT)  # nosemgrep
            resp_json = r.json()

            for artifact in container["artifacts"]:
                self._save_or_update_artifact(existing_container_id, artifact)
            if r.status_code != 200 or resp_json.get("failed"):
                self.debug_print(
                    "Error while updating the container. Error is: ",
                    resp_json.get("failed"),
                )
                return False
        except Exception as e:
            self.debug_print(f"Error occurred while updating the container. {e}")
            return False

        return True

    def _ingest_finding(self, finding, domain_name, action_result):
        finding_id = finding.get("id")
        try:
            container = self._get_container_dict_for_finding(finding, domain_name, action_result)
        except Exception as e:
            self.debug_print(f"Skipping finding {finding_id}; failed to build container: {e}")
            self.save_progress(f"Skipping finding {finding_id}; failed to build container")
            return False

        container["artifacts"] = [artifact for artifact in container.get("artifacts") or [] if artifact]
        existing_container_id = self._does_container_exist_for_finding(container["source_data_identifier"])
        is_new_container_created = False
        try:
            if not existing_container_id:
                self.debug_print(f"Saving container for Finding with id {finding_id}")
                success = self.save_container(container)
                is_new_container_created = True
            else:
                success = self._update_container_for_attack_finding(existing_container_id, container)
                is_new_container_created = False
        except Exception as e:
            self.debug_print(f"Skipping finding {finding_id}; failed to save container: {e}")
            self.save_progress(f"Skipping finding {finding_id}; failed to save container")
            return False

        if not success:
            self.debug_print(f"Skipping finding {finding_id}; container save returned failure")
            self.save_progress(f"Skipping finding {finding_id}; container save failed")
            return False

        self.num_artifacts += len(container["artifacts"])
        return is_new_container_created

    def _get_artifact(self, source_data_identifier, container_id):
        url = f'{self.get_phantom_base_url()}rest/artifact?_filter_source_data_identifier="{source_data_identifier}"&_filter_container_id={container_id}&sort=id&order=desc'
        try:
            r = requests.get(url, verify=False, timeout=60)  # nosemgrep
            resp_json = r.json()
        except Exception as e:
            err = self._get_error_message_from_exception(e)
            self.debug_print(f"Exception when querying for artifact ID: {err}")
            return None

        if resp_json.get("count", 0) <= 0:
            self.debug_print(f"No artifact matched the source_data_identifier {source_data_identifier} and container id {container_id}")
            return None

        try:
            return resp_json.get("data", [])[0]
        except Exception as e:
            err = self._get_error_message_from_exception(e)
            self.debug_print(f"Exception when parsing artifact results: {err}")
            return None

    def _save_or_update_artifact(self, container_id, artifact):
        if not artifact or not artifact.get("source_data_identifier"):
            return
        existing_artifact = self._get_artifact(artifact["source_data_identifier"], container_id)
        if existing_artifact:
            # We have an existing artifact. Update it.
            artifact["container_id"] = existing_artifact["container"]
            artifact["id"] = existing_artifact["id"]
            self.debug_print(f"Updating artifact {artifact['name']}", artifact)
            self.save_artifacts([artifact])
        else:
            # This is a new artifact. Save it directly.
            self.debug_print(f"Saving new artifact {artifact['name']}", artifact)
            artifact["container_id"] = container_id
            self.save_artifact(artifact)

    def _handle_on_poll(self, param):
        self.debug_print(f"In action handler for: {self.get_action_identifier()}")
        self.save_progress("Polling the attack path details from SpecterOps BloodHound")
        max_container_limit = param.get(phantom.APP_JSON_CONTAINER_COUNT)
        max_artifact_limit = param.get(phantom.APP_JSON_ARTIFACT_COUNT)
        self.num_artifacts = 0

        # Add an action result object to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Fetch available domains
        ret_val, response = self._request("GET", "/api/v2/available-domains", action_result)
        self.save_progress("Getting the available domains from SpecterOps BloodHound")

        if phantom.is_fail(ret_val):
            self.save_progress("Failed to fetch available-domains")
            return action_result.get_status()

        # Extract the list of domains
        domains = response["data"]
        if not domains:
            self.save_progress("No domains found in response")
            return action_result.set_status(phantom.APP_ERROR, "No domains found in response")
        self.save_progress(f"Found {len(domains)} available domains")

        container_count = 0
        repeated_container_count = 0
        self.debug_print("Loop through each domain")
        max_limit_reached = False
        for domain in domains:
            domain_id = domain["id"]
            domain_name = domain["name"]
            types = self._get_available_types_for_domain(domain_id, action_result) or []

            # Find path findings for each type in the domain
            for finding_type in types:
                # Using the finding_type directly as it's a string now
                all_findings_for_type = self._fetch_all_findings_information(domain_id, finding_type, action_result) or []

                for single_finding in all_findings_for_type:
                    single_finding["severity"] = self._get_finding_severity(single_finding, finding_type)

                    is_new_container_created = self._ingest_finding(single_finding, domain_name, action_result)
                    if is_new_container_created:
                        container_count += 1
                    else:
                        repeated_container_count += 1
                    # Check if the max container limit is reached
                    max_limit_reached = (max_container_limit is not None and container_count >= max_container_limit) or (
                        max_artifact_limit is not None and self.num_artifacts >= max_artifact_limit
                    )
                    if max_limit_reached:
                        if max_artifact_limit is not None and self.num_artifacts > max_artifact_limit:
                            self.save_progress(
                                f"{self.num_artifacts - max_artifact_limit} extra artifacts is created to maintain correct container details"
                            )
                        break
                if max_limit_reached:
                    break
            if max_limit_reached:
                break

        self.save_progress(f"Finished poll by fetching {container_count} attack paths from {len(domains)} available domains")
        if repeated_container_count > 0:
            self.save_progress(f"{repeated_container_count} number of findings were repeated")
        return action_result.set_status(
            phantom.APP_SUCCESS,
            f"Found {container_count} findings from {len(domains)} available domains",
        )

    def _handle_fetch_asset_information(self, param):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")
        action_result = self.add_action_result(ActionResult(dict(param)))

        object_id = quote(param.get("object_id", ""), safe="")
        if not object_id:
            return action_result.set_status(phantom.APP_SUCCESS, "Object Id not available")

        ret_val, response = self._request("GET", f"/api/v2/search?q={object_id}", action_result)
        if phantom.is_fail(ret_val):
            if self._is_http_not_found(action_result):
                return action_result.set_status(phantom.APP_SUCCESS, "Object Id not available")
            return action_result.get_status()

        search_data = (response or {}).get("data") or []
        if not search_data:
            return action_result.set_status(phantom.APP_SUCCESS, "Object Id not available")

        search_hit = search_data[0] if isinstance(search_data[0], dict) else {}
        obj_type = search_hit.get("type") or ""
        primary_response = self._fetch_primary_response(object_id, obj_type, action_result)
        if phantom.is_fail(action_result.get_status()):
            if self._is_http_not_found(action_result):
                return action_result.set_status(phantom.APP_SUCCESS, "Node is missing")
            return action_result.get_status()

        if not isinstance(primary_response, dict) or not primary_response.get("data"):
            return action_result.set_status(phantom.APP_SUCCESS, "Node is missing")

        if obj_type.startswith("AZ"):
            self._handle_azure_types(object_id, obj_type, primary_response, action_result)
            if phantom.is_fail(action_result.get_status()):
                return action_result.get_status()

        action_result.add_data(primary_response)
        return action_result.set_status(phantom.APP_SUCCESS)

    def _fetch_primary_response(self, object_id, obj_type, action_result):
        """Fetch the primary response based on the object type."""
        if obj_type in DIRECTORY_TYPES:
            api_path = f"/api/v2/{obj_type.lower()}s/{object_id}"
        elif obj_type in AZURE_TYPES:
            api_path = f"/api/v2/azure/{self._get_azure_type_path(obj_type)}?object_id={object_id}&counts=false"
        else:
            api_path = f"/api/v2/base/{object_id}"

        return self._call_api(api_path, action_result)

    def _get_azure_type_path(self, obj_type):
        """Return the API path type for Azure object types."""
        if obj_type == "AZServicePrincipal":
            return "service-principals"
        elif obj_type == "AZApp":
            return "applications"
        return (obj_type[2:] + "s").lower()

    def _handle_azure_types(self, object_id, obj_type, primary_response, action_result):
        """Handle additional Azure-specific processing."""
        if obj_type == "AZTenant":
            self._process_az_tenant(object_id, primary_response, action_result)
        else:
            related_types = AZURE_RELATED_TYPES.get(obj_type, {})
            for related_type, mapping_key in related_types.items():
                self._update_primary_response(
                    primary_response,
                    object_id,
                    obj_type,
                    related_type,
                    mapping_key,
                    action_result,
                )

    def _process_az_tenant(self, object_id, primary_response, action_result):
        """Process Azure Tenant-specific logic."""
        descendent_count = 0
        inbound_control_count = 0

        for rel_type in AZ_TENANT_RELATED_TYPES:
            api_path = f"/api/v2/azure/tenants?object_id={object_id}&related_entity_type={rel_type}&skip=0&limit=128"
            secondary_response = self._call_api(api_path, action_result)

            if secondary_response and "count" in secondary_response:
                if rel_type == "inbound-control":
                    inbound_control_count = secondary_response["count"]
                else:
                    descendent_count += secondary_response["count"]
            else:
                action_result.append_to_message(f"Failed to fetch data for related type: {rel_type}")

        data = primary_response.setdefault("data", {})
        if not isinstance(data, dict):
            return
        data["inbound_object_control"] = inbound_control_count
        data["descendents"] = {"descendent_counts": descendent_count}

    def _update_primary_response(
        self,
        primary_response,
        object_id,
        obj_type,
        related_type,
        mapping_key,
        action_result,
    ):
        """Update the primary response with data from related types."""
        api_path = (
            f"/api/v2/azure/{self._get_azure_type_path(obj_type)}?object_id={object_id}&related_entity_type={related_type}&skip=0&limit=128"
        )
        secondary_response = self._call_api(api_path, action_result)
        if not secondary_response or "count" not in secondary_response:
            action_result.append_to_message(f"Failed to fetch data for related type: {related_type}")
            return

        count_value = secondary_response["count"]
        data = primary_response.setdefault("data", {})
        if isinstance(data, dict):
            data[mapping_key] = count_value

    def _http_status_code(self, action_result):
        """Best-effort HTTP status from a request ActionResult."""
        if hasattr(action_result, "get_debug_data"):
            debug = action_result.get_debug_data() or {}
            candidates = debug if isinstance(debug, list) else [debug]
            for item in candidates:
                if not isinstance(item, dict):
                    continue
                status = item.get("r_status_code")
                try:
                    return int(status)
                except (TypeError, ValueError):
                    continue
        message = action_result.get_message() or ""
        marker = "Status Code: "
        if marker in message:
            rest = message.split(marker, 1)[1]
            digits = ""
            for ch in rest:
                if ch.isdigit():
                    digits += ch
                else:
                    break
            if digits:
                return int(digits)
        return None

    def _is_http_not_found(self, action_result):
        """Return True when a failed request was an HTTP 404."""
        return self._http_status_code(action_result) == 404 or "Status Code: 404" in (action_result.get_message() or "")

    def _call_api(self, path, action_result):
        """Utility function to make an API call.

        HTTP 404 is treated as missing data and does not fail the parent action.
        Other errors (auth, rate limit, 5xx) are propagated as APP_ERROR.
        """
        api_result = ActionResult(dict())
        ret_val, response = self._request("GET", path, api_result)
        if phantom.is_fail(ret_val):
            message = api_result.get_message() or f"Failed to fetch data for API: {path}"
            if self._is_http_not_found(api_result):
                action_result.append_to_message(message)
                return None
            action_result.set_status(phantom.APP_ERROR, message)
            return None
        return response

    def _handle_does_path_exist(self, param):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")
        action_result = self.add_action_result(ActionResult(dict(param)))
        start_node = quote(param.get("start_node", ""), safe="")
        end_node = quote(param.get("end_node", ""), safe="")
        endpoint = f"/api/v2/graphs/shortest-path?start_node={start_node}&end_node={end_node}"
        ret_val, _response = self._request("GET", endpoint, action_result)
        if ret_val:
            action_result.add_data({"response": True})
        else:
            action_result.add_data({"response": False})
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_get_object_id(self, param):
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")
        action_result = self.add_action_result(ActionResult(dict(param)))
        original_name = param.get("name") or ""
        if not original_name:
            return action_result.set_status(phantom.APP_SUCCESS, "Name not available")
        name = quote(original_name, safe="")
        _ret_val, response = self._request("GET", f"/api/v2/search?q={name}", action_result)
        data = response["data"]
        if data:
            exact_match = next(
                (item["objectid"] for item in data if item["name"].strip() == original_name),
                None,
            )
            if exact_match:
                action_result.add_data({"object_id": exact_match})
                return action_result.set_status(phantom.APP_SUCCESS)
            else:
                return action_result.set_status(phantom.APP_SUCCESS, "Exact match not found")
        else:
            return action_result.set_status(phantom.APP_SUCCESS, "Object Id not available")

    def handle_action(self, param):
        ret_val = phantom.APP_SUCCESS
        action_id = self.get_action_identifier()

        if action_id == "on_poll":
            ret_val = self._handle_on_poll(param)

        if action_id == "fetch_asset_information":
            ret_val = self._handle_fetch_asset_information(param)

        if action_id == "does_path_exist":
            ret_val = self._handle_does_path_exist(param)

        if action_id == "get_object_id":
            ret_val = self._handle_get_object_id(param)

        if action_id == "test_connectivity":
            ret_val = self._handle_test_connectivity(param)

        return ret_val

    def initialize(self):
        self._state = self.load_state()
        config = self.get_config()

        self._base_url = config.get("bloodhound_base_url")
        self._token_key = config.get("token_key")
        self._token_id = config.get("token_id")
        self._start_date = config.get("historical_poll_time_range")
        self._end_date = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        return phantom.APP_SUCCESS

    def finalize(self):
        self.save_state(self._state)
        return phantom.APP_SUCCESS


def main():
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("-c", "--config", required=True, help="Config file path")
    args = argparser.parse_args()

    connector = SpecteropsbloodhoundConnector()
    connector.initialize()
    connector.handle_action({"config": args.config})
    connector.finalize()


if __name__ == "__main__":
    main()
