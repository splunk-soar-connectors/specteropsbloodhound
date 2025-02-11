#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------
# Phantom sample App Connector python file
# -----------------------------------------

# Phantom App imports
import phantom.app as phantom
from phantom.action_result import ActionResult
from phantom.base_connector import BaseConnector

import hmac
import hashlib
import base64
import requests
import datetime
from typing import Optional

from specteropsbloodhound_consts import *


class RetVal(tuple):

    def __new__(cls, val1, val2=None):
        return tuple.__new__(RetVal, (val1, val2))


class SpecteropsbloodhoundConnector(BaseConnector):

    def __init__(self):
        super(SpecteropsbloodhoundConnector, self).__init__()
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
                phantom.APP_ERROR, "Empty response and no information in the header"
            ), None
        )

    def _process_html_response(self, response, action_result):
        status_code = response.status_code
        try:
            error_text = response.text
        except:
            error_text = "Cannot parse error details"

        message = f"Status Code: {status_code}. Data from server:\n{error_text}\n"
        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_json_response(self, r, action_result):
        try:
            resp_json = r.json()
        except Exception as e:
            return RetVal(
                action_result.set_status(
                    phantom.APP_ERROR, f"Unable to parse JSON response. Error: {str(e)}"
                ), None
            )

        if 200 <= r.status_code < 399:
            return RetVal(phantom.APP_SUCCESS, resp_json)

        message = f"Error from server. Status Code: {r.status_code} Data from server: {r.text.replace(u'{', '{{').replace(u'}', '}}')}"
        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_response(self, r, action_result):
        self.debug_print(f"Processing response: Status Code {r.status_code}")
        self.debug_print(f"Response Text: {r.text[:500]}")  # Log first 500 chars

        if hasattr(action_result, 'add_debug_data'):
            action_result.add_debug_data({'r_status_code': r.status_code})
            action_result.add_debug_data({'r_text': r.text})
            action_result.add_debug_data({'r_headers': r.headers})

        if 'json' in r.headers.get('Content-Type', ''):
            return self._process_json_response(r, action_result)
        if 'html' in r.headers.get('Content-Type', ''):
            return self._process_html_response(r, action_result)
        if not r.text:
            return self._process_empty_response(r, action_result)
        else:
            return RetVal(phantom.APP_SUCCESS, r.text)

    def _request(self, method: str, uri: str, action_result, body: Optional[bytes] = None) -> RetVal:
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
                    "Signature": base64.b64encode(digester.digest()),
                    "Content-Type": "application/json",
                },
                data=body,
            )
        except Exception as e:
            return RetVal(
                action_result.set_status(
                    phantom.APP_ERROR, f"Error Connecting to server. Details: {str(e)}"
                ), None
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
        self.save_progress("⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀")
        self.save_progress("⠘⢿⣿⣿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀")
        self.save_progress("⠀⠈⢿⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣶⣦⣤⣄⣀⠀")
        self.save_progress("⠀⠀⠈⠻⣿⣿⣦⣤⣄⣤⣠⣠⣀⣴⣾⣿⣦⡀⠀⠀⠉⠙⠛⠻⣿⣿⡿⠁")
        self.save_progress("⠀⠀⠀⠀⠈⠙⠻⠿⠿⠿⠿⠿⠿⣿⣿⣿⣿⠇⠀⠀⠀⠀⢀⣾⣿⡟⠁⠀")
        self.save_progress("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠹⠏⠁⠀⠀⠀⠀⠀⣾⣿⡿⠀⠀⠀")
        self.save_progress("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⣶⣶⣆⠀⠀⠀⠀⠀⠀⣀⣠⣾⣿⡟⠀⠀⠀⠀")
        self.save_progress("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣧⠀⠀⣰⣾⣿⣿⠿⠟⠋⠀⠀⠀⠀⠀")
        self.save_progress("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣧⣼⣿⡿⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀")
        self.save_progress("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀")
        self.save_progress("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀")
        self.save_progress("Successfully Connected to SPECTEROPS BLOODHOUND ENTERPRISE")
        return action_result.set_status(phantom.APP_SUCCESS)


    def _get_available_types_for_domain(self, domain_id, action_result):
        # Fetch available types for the domain
        self.save_progress(f"Fetch available types for the domain ID: {domain_id}")
        endpoint = f'/api/v2/domains/{domain_id}/available-types'
        ret_val, path_ids_response = self._request('GET', endpoint, action_result)

        if phantom.is_fail(ret_val):
            return action_result.set_status(
                phantom.APP_ERROR,
                f"Failed to fetch types for Domain ID: {domain_id}"
            )
        # Here, types is a list of strings
        types = path_ids_response['data']
        self.debug_print(f"Fetched Types for Domain ID {domain_id}: {types}")
        self.save_progress(f"The domain with ID {domain_id} has {len(types)} types in total")
        return types

    def _fetch_finding_details_by_pages(self, domain_id, finding_type, skip, limit, action_result):
        # Using the finding_type directly as it's a string now
        self.debug_print(
            f"Fetching findings for domain id {domain_id} and type {finding_type} for current page"
        )
        self.debug_print(f"Fetch {limit} finding by skipping {skip} findings")
        findings_endpoint = (
            f"/api/v2/domains/{domain_id}/details?"
            f"finding={finding_type}&skip={skip}&limit={limit}"
        )
        ret_val, details_response = self._request('GET', findings_endpoint, action_result)
        if phantom.is_fail(ret_val):
            self.save_progress(
            f"Failed to fetch findings for Finding Type: {finding_type} in Domain ID: {domain_id}"
            )
            return
        return ret_val, details_response

    def _fetch_all_findings_information(self, domain_id, finding_type, action_result):
        self.save_progress(f"Fetching ALL the findings for domain id {domain_id} and type {finding_type}")
        all_findings_for_type = []
        skip = 0
        limit = 10
        while True:
            ret_val, details_response = self._fetch_finding_details_by_pages(domain_id, finding_type, skip, limit, action_result)
            if phantom.is_fail(ret_val):
                self.save_progress(f"Failed to fetch findings for Finding Type: {finding_type} in Domain ID: {domain_id}")
                return
            data = details_response.get('data', [])
            if len(data) == 0:
                break
            all_findings_for_type.extend(data)
            skip = skip + len(details_response['data'])
            self.debug_print(f"Fetched {details_response['count']} findings in this page")

        self.save_progress(f"Successfully fetched total {len(all_findings_for_type)} findings for domain id {domain_id} and type {finding_type}")
        return all_findings_for_type

    def _fetch_severity_for_attack_path_type(self, domain_id, finding_type, action_result):
        self.save_progress(f"Fetching severity for the domain ID {domain_id} and type {finding_type}")
        findings_endpoint = f'/api/v2/domains/{domain_id}/sparkline?finding={finding_type}&sort_by=updated_at'
        ret_val, sparklines_response = self._request('GET', findings_endpoint, action_result)
        if phantom.is_fail(ret_val):
            self.save_progress(f"Failed to fetch sparklines for Finding Type: {finding_type} in Domain ID: {domain_id}")
            return
        num_sparklines = len(sparklines_response['data'])
        self.debug_print(f"Found {len(sparklines_response['data'])} sparklines")
        self.debug_print("Fetch the Composite Risk from the last sparkline")
        composite_risk = sparklines_response['data'][num_sparklines-1]['CompositeRisk']
        self.debug_print(f"Fetched composite risk for finding type {finding_type} as {composite_risk}")

        return composite_risk

    def _get_cef_type(self, field_name):
        self.debug_print("Get the CEF type for the fields, as per it's name")
        # Following are all the possible field types, we have only mapped a few out of those
        # ( "vault id", "file name", "file path", "hash", "host name", "ip", "mac address",
        #  "md5", "port", "process name", "sha1", "sha256", "sha512", "url" )
        field_name_to_type_map = {
            "domain": "domain",
            "email": "user id"
        }
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

    def _modify_principal_label(self,data, text):
        if isinstance(data, dict):  # Check if data is a dictionary
            if text == 'FromPrincipal':
                if data.get('Finding', '').startswith('LargeDefault'):
                    return 'Group'
                else:
                    return 'Non Tier Zero Principal'

            elif text == 'ToPrincipal':
                if data.get('Finding', '').startswith('LargeDefault'):
                    return 'Principal'
                else:
                    return 'Tier Zero Principal'

        return 'User'

    def _create_principle_artifact_details(self, finding):
        self.debug_print("Creating the artifact details")
        principal_artifact_details = None
        if "PrincipalKind" in finding:
            cef, cef_types = self._create_cef_field_and_types_for_principal(finding['Props'])
            principal_artifact_details = {
                "source_data_identifier": finding['Principal'],
                "name": finding['Props']['name'],
                "description": finding['Props'].get('description', f"Principal with name {finding['Props']['name']}"),
                "type": finding['PrincipalKind'],
                "label": self._modify_principal_label(finding,"Principal"),
                "cef": cef,
                "cef_types": cef_types
            }
        return principal_artifact_details

    def _create_to_principle_artifact_details(self, finding):
        self.debug_print("Creating the artifact details for ToPrincipal")
        principal_artifact_details = None
        if "ToPrincipalKind" in finding:
            cef, cef_types = self._create_cef_field_and_types_for_principal(finding['ToPrincipalProps'])
            principal_artifact_details = {
                "source_data_identifier": finding['ToPrincipal'],
                "name": finding['ToPrincipalProps']['name'],
                "description": finding['ToPrincipalProps'].get('description', f"ToPrincipal of with name {finding['ToPrincipalProps']['name']}"),
                "type": finding['ToPrincipalKind'],
                "label": self._modify_principal_label(finding,"ToPrincipal"),
                "cef": cef,
                "cef_types": cef_types
            }

        return principal_artifact_details

    def _create_from_principle_artifact_details(self, finding):
        self.debug_print("Creating the artifact details for From Principal")
        principal_artifact_details = None
        if "FromPrincipalKind" in finding:
            cef, cef_types = self._create_cef_field_and_types_for_principal(finding['FromPrincipalProps'])
            principal_artifact_details = {
                "source_data_identifier": finding['FromPrincipal'],
                "name": finding['FromPrincipalProps']['name'],
                "description": finding['FromPrincipalProps'].get('description', f"FromPrincipal of with name {finding['FromPrincipalProps']['name']}"),
                "type": finding['FromPrincipalKind'],
                "label": self._modify_principal_label(finding,"FromPrincipal"),
                "cef": cef,
                "cef_types": cef_types
            }

        return principal_artifact_details


    def _get_artifacts_dict_for_finding(self, finding):
        self.debug_print(f"Building finding artifacts for the Finding type {finding['Finding']}")

        artifacts = []
        if "PrincipalKind" in finding:
            artifacts.append(self._create_principle_artifact_details(finding))
        if "FromPrincipalKind" in finding:
            artifacts.append(self._create_to_principle_artifact_details(finding))
        if "ToPrincipalKind" in finding:
            artifacts.append(self._create_from_principle_artifact_details(finding))

        return artifacts

    def _convert_risk_to_severity(self, composite_risk):
        severity = 'low'
        if composite_risk > 33.33:
            severity = 'medium'
        if composite_risk > 66.66:
            severity = 'high'
        return severity

    def _get_finding_title(self, path_id, action_result):
        if not hasattr(self, '_title_cache'):
            self._title_cache = {}

        if path_id in self._title_cache:
            return self._title_cache[path_id]

        endpoint = f'/api/v2/assets/findings/{path_id}/title.md'
        ret_val, path_title = self._request('GET', endpoint, action_result)

        if phantom.is_fail(ret_val):
            action_result.set_status(phantom.APP_ERROR, f"Failed to fetch finding title for path_id: {path_id}")
            return None

        self._title_cache[path_id] = path_title.strip()

        return path_title

    def _get_container_dict_for_finding(self, finding, domain_name, action_result):
        finding_id = finding["id"]
        finding_type = finding["Finding"]
        path_title = self._get_finding_title(finding_type,action_result)
        self.debug_print(f"Building container for finding {finding['id']}")
        # Build the container JSON
        container_json = {}
        container_json["name"] = f'{domain_name} : {path_title} : {finding_id}'
        container_json["data"] = finding
        container_json["description"] = finding_type
        container_json["source_data_identifier"] = f'{domain_name}:{path_title.strip()}:{finding_id}'
        container_json["severity"] = self._convert_risk_to_severity(finding['composite_risk'])

        self.debug_print(f"Create artifacts for the the finding id: {finding['id']}")
        if self._does_container_exist_for_finding(f'{domain_name}:{path_title.strip()}:{finding_id}'):
            container_json["artifacts"] = []
        else:
            container_json["artifacts"] = self._get_artifacts_dict_for_finding(finding)

        return container_json

    def _does_container_exist_for_finding(self, source_data_identifier):
        url = '{0}rest/container?_filter_source_data_identifier="{1}"&_filter_asset={2}'.format(
            self.get_phantom_base_url(),
            source_data_identifier, self.get_asset_id()
        )
        existing_container_id = False

        try:
            r = requests.get(url, verify=False, timeout=DEFAULT_REQUEST_TIMEOUT)  # nosemgrep
            resp_json = r.json()
        except Exception as e:
            err = self._get_error_message_from_exception(e)
            self.debug_print("Unable to query container: {0}".format(err))
            return False

        if resp_json.get("count", 0) <= 0:
            self.debug_print("No container matched, creating a new one.")
            return False

        try:
            existing_container_id = resp_json.get('data', [])[0]['id']
        except Exception as e:
            err = self._get_error_message_from_exception(e)
            self.debug_print("Container results are not proper: {0}".format(err))
            return False

        return existing_container_id

    def _update_container_for_attack_finding(self, existing_container_id, container):
        # First, update the container without updating any artifacts
        try:
            self.debug_print(f"Updating container with id {existing_container_id}")
            update_json = container.copy()
            del update_json["artifacts"]
            url = '{0}rest/container/{1}'.format(self.get_phantom_base_url(), existing_container_id)
            r = requests.post(url, json=update_json, verify=False, timeout=DEFAULT_REQUEST_TIMEOUT)  # nosemgrep
            resp_json = r.json()

            for artifact in container["artifacts"]:
                self._save_or_update_artifact(existing_container_id, artifact)
            if r.status_code != 200 or resp_json.get('failed'):
                self.debug_print("Error while updating the container. Error is: ", resp_json.get('failed'))
                return False
        except Exception as e:
            self.debug_print("Error occurred while updating the container. {}".format(e))
            return False

        return True

    def _ingest_finding(self, finding, domain_name, action_result):
        finding_id = finding["id"]
        success = phantom.APP_ERROR
        container = self._get_container_dict_for_finding(finding,domain_name,action_result)
        existing_container_id = self._does_container_exist_for_finding(container["source_data_identifier"])
        is_new_container_created = False
        if not existing_container_id:
            # Container does not exist. Go ahead and save it
            self.debug_print(f"Saving container for Finding with id {finding_id}")
            success = self.save_container(container)
            is_new_container_created = True
        else:
            # Container exists, which means this Finding has been ingested before. Update it.
            success = self._update_container_for_attack_finding(existing_container_id, container)
            is_new_container_created = False
        self.num_artifacts += len(container["artifacts"])
        return is_new_container_created if success else phantom.APP_ERROR

    def _get_artifact(self, source_data_identifier, container_id):
        url = '{0}rest/artifact?_filter_source_data_identifier="{1}"&_filter_container_id={2}&sort=id&order=desc'.format(
                        self.get_phantom_base_url(), source_data_identifier, container_id)
        try:
            r = requests.get(url, verify=False, timeout=60)  # nosemgrep
            resp_json = r.json()
        except Exception as e:
            err = self._get_error_message_from_exception(e)
            self.debug_print("Exception when querying for artifact ID: {0}".format(err))
            return None

        if resp_json.get('count', 0) <= 0:
            self.debug_print(
                "No artifact matched the source_data_identifier {0} and container id {1}".format(
                    source_data_identifier,
                    container_id
                )
            )
            return None

        try:
            return resp_json.get('data', [])[0]
        except Exception as e:
            err = self._get_error_message_from_exception(e)
            self.debug_print("Exception when parsing artifact results: {0}".format(err))
            return None


    def _save_or_update_artifact(self, container_id, artifact):
        existing_artifact = self._get_artifact(artifact["source_data_identifier"], container_id)
        if existing_artifact:
            # We have an existing artifact. Update it.
            artifact["container_id"] = existing_artifact["container"]
            artifact["id"] = existing_artifact["id"]
            self.debug_print('Updating artifact {0}'.format(artifact["name"]), artifact)
            self.save_artifacts([artifact])
        else:
            # This is a new artifact. Save it directly.
            self.debug_print('Saving new artifact {0}'.format(artifact["name"]), artifact)
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
        ret_val, response = self._request('GET', '/api/v2/available-domains', action_result)
        self.save_progress("Getting the available domains from SpecterOps BloodHound")

        if phantom.is_fail(ret_val):
            self.save_progress("Failed to fetch available-domains")
            return action_result.get_status()

        # Extract the list of domains
        domains = response['data']
        if not domains:
            self.save_progress("No domains found in response")
            return action_result.set_status(phantom.APP_ERROR, "No domains found in response")
        self.save_progress(f"Found {len(domains)} available domains")

        container_count = 0
        repeated_container_count = 0
        self.debug_print("Loop through each domain")
        max_limit_reached = False
        for domain in domains:
            domain_id = domain['id']
            domain_name = domain['name']
            types = self._get_available_types_for_domain(domain_id, action_result)

            # Find path findings for each type in the domain
            for finding_type in types:
                # Using the finding_type directly as it's a string now
                all_findings_for_type = self._fetch_all_findings_information(domain_id, finding_type, action_result)
                composite_risk = self._fetch_severity_for_attack_path_type(domain_id, finding_type, action_result)
                
                self.debug_print(f"Add Composite Risk value {composite_risk} to each finding")
                for single_finding in all_findings_for_type:
                    single_finding['composite_risk'] = composite_risk
                    is_new_container_created = self._ingest_finding(single_finding, domain_name, action_result)
                    if is_new_container_created:
                        container_count+=1
                    else:
                        repeated_container_count+=1
                    # Check if the max container limit is reached
                    max_limit_reached = (max_container_limit is not None and container_count >= max_container_limit) or \
                        (max_artifact_limit is not None and self.num_artifacts >= max_artifact_limit)
                    if max_limit_reached:
                        if max_artifact_limit is not None and self.num_artifacts > max_artifact_limit:
                            self.save_progress(f'{self.num_artifacts-max_artifact_limit} extra artifacts is created to maintain correct container details')
                        break
                if max_limit_reached:
                    break
            if max_limit_reached:
                break
        
        self.save_progress(f"Finished poll by fetching {container_count} attack paths from {len(domains)} available domains")
        if repeated_container_count > 0:
            self.save_progress(f"{repeated_container_count} number of findings were repeated")
        return action_result.set_status(phantom.APP_SUCCESS, f"Found {container_count} findings from {len(domains)} available domains")

    def _handle_fetch_asset_information(self, param):
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))
        action_result = self.add_action_result(ActionResult(dict(param)))

        object_id = param.get('object_id')
        ret_val, response = self._request('GET', f'/api/v2/search?q={object_id}', action_result)
        if not response['data']:
            return action_result.set_status(phantom.APP_SUCCESS, "Object Id not available")

        obj_type = response['data'][0]['type']
        primary_response = self._fetch_primary_response(object_id, obj_type, action_result)

        if not primary_response:
            return action_result.set_status(phantom.APP_ERROR, "Failed to fetch primary response")

        if obj_type.startswith('AZ'):
            self._handle_azure_types(object_id, obj_type, primary_response, action_result)

        action_result.add_data(primary_response)
        return action_result.set_status(phantom.APP_SUCCESS)

    def _fetch_primary_response(self, object_id, obj_type, action_result):
        """Fetch the primary response based on the object type."""
        if obj_type in DIRECTORY_TYPES:
            api_path = f'/api/v2/{obj_type.lower()}s/{object_id}'
        elif obj_type in AZURE_TYPES:
            api_path = f'/api/v2/azure/{self._get_azure_type_path(obj_type)}?object_id={object_id}&counts=false'
        else:
            api_path = f'/api/v2/base/{object_id}'

        return self._call_api(api_path, action_result)

    def _get_azure_type_path(self, obj_type):
        """Return the API path type for Azure object types."""
        if obj_type == 'AZServicePrincipal':
            return 'service-principals'
        elif obj_type == 'AZApp':
            return 'applications'
        return (obj_type[2:] + "s").lower()

    def _handle_azure_types(self, object_id, obj_type, primary_response, action_result):
        """Handle additional Azure-specific processing."""
        if obj_type == 'AZTenant':
            self._process_az_tenant(object_id, primary_response, action_result)
        else:
            related_types = AZURE_RELATED_TYPES.get(obj_type, {})
            for related_type, mapping_key in related_types.items():
                self._update_primary_response(primary_response, object_id, obj_type, related_type, mapping_key, action_result)

    def _process_az_tenant(self, object_id, primary_response, action_result):
        """Process Azure Tenant-specific logic."""
        descendent_count = 0
        inbound_control_count = 0

        for rel_type in AZ_TENANT_RELATED_TYPES:
            api_path = f'/api/v2/azure/tenants?object_id={object_id}&related_entity_type={rel_type}&skip=0&limit=128'
            secondary_response = self._call_api(api_path, action_result)

            if secondary_response and 'count' in secondary_response:
                if rel_type == 'inbound-control':
                    inbound_control_count = secondary_response['count']
                else:
                    descendent_count += secondary_response['count']
            else:
                action_result.append_to_message(f"Failed to fetch data for related type: {rel_type}")

        primary_response['data']['inbound_object_control'] = inbound_control_count
        primary_response['data']['descendents'] = {'descendent_counts': descendent_count}

    def _update_primary_response(self, primary_response, object_id, obj_type, related_type, mapping_key, action_result):
        """Update the primary response with data from related types."""
        api_path = f'/api/v2/azure/{self._get_azure_type_path(obj_type)}?object_id={object_id}&related_entity_type={related_type}&skip=0&limit=128'
        secondary_response = self._call_api(api_path, action_result)
        if not secondary_response or 'count' not in secondary_response:
            action_result.append_to_message(f"Failed to fetch data for related type: {related_type}")
            return

        count_value = secondary_response['count']
        primary_response['data'][mapping_key] = count_value

    def _call_api(self, path, action_result):
        """Utility function to make an API call."""
        ret_val, response = self._request('GET', path, action_result)
        if not ret_val:
            action_result.append_to_message(f"Failed to fetch data for API: {path}")
            return None
        return response
    
    def _handle_does_path_exist(self, param):
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))
        action_result = self.add_action_result(ActionResult(dict(param)))
        start_node = param.get('start_node')
        end_node = param.get('end_node')
        endpoint = f'/api/v2/graphs/shortest-path?start_node={start_node}&end_node={end_node}'
        ret_val, response = self._request('GET', endpoint, action_result)
        if ret_val==True:
            action_result.add_data({'response': True})
        else:
            action_result.add_data({'response': False})
        return action_result.set_status(phantom.APP_SUCCESS)


    def _handle_get_object_id(self, param):
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))
        action_result = self.add_action_result(ActionResult(dict(param)))
        name = param.get('name').replace(" ", "%20")
        ret_val, response = self._request('GET', f'/api/v2/search?q={name}', action_result)
        data = response['data']
        if data:
            exact_match = next((item['objectid'] for item in data if item['name'].strip() == param.get('name')), None)
            if exact_match :
                action_result.add_data({'object_id':exact_match})
                return action_result.set_status(phantom.APP_SUCCESS)
            else:
                return action_result.set_status(phantom.APP_SUCCESS, f'Exact match not found')
        else:
            return action_result.set_status(phantom.APP_SUCCESS, f'Object Id not available')


    def handle_action(self, param):
        ret_val = phantom.APP_SUCCESS
        action_id = self.get_action_identifier()

        if action_id == 'on_poll':
            ret_val = self._handle_on_poll(param)

        if action_id == 'fetch_asset_information':
            ret_val = self._handle_fetch_asset_information(param)

        if action_id == 'does_path_exist':
            ret_val = self._handle_does_path_exist(param)

        if action_id == 'get_object_id':
            ret_val = self._handle_get_object_id(param)

        if action_id == 'test_connectivity':
            ret_val = self._handle_test_connectivity(param)

        return ret_val

    def initialize(self):
        self._state = self.load_state()
        config = self.get_config()

        self._base_url = config.get('bloodhound_base_url')
        self._token_key = config.get('token_key')
        self._token_id = config.get('token_id')
        self._start_date = config.get('historical_poll_time_range')
        self._end_date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        return phantom.APP_SUCCESS

    def finalize(self):
        self.save_state(self._state)
        return phantom.APP_SUCCESS

def main():
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-c', '--config', required=True, help='Config file path')
    args = argparser.parse_args()

    connector = SpecteropsbloodhoundConnector()
    connector.initialize()
    connector.handle_action({"config": args.config})
    connector.finalize()

if __name__ == '__main__':
    main()
