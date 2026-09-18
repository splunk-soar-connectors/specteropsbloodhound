**Unreleased**

* Migrate the app from Python 3.9 to Python 3.13 for Splunk SOAR 7.0.0 and later
* Update light and dark theme SVG logos
* Continue ingesting attack path findings during poll when finding title metadata is unavailable
* Treat a missing BloodHound node (HTTP 404) in fetch asset information as success with a Node is missing message; authentication, rate-limit, and server errors still fail the action
