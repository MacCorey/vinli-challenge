# Vinli QA Challenge
# Corey McKenzie
# corey.mckenzie@gmail.com

# Notes:
# 1. Rather than just assert for each error, I've collected the errors to report at the end. This allows us to see
# multiple failures rather than having to fix each one before the next test can run.
# 2. There is a lot left to test, but time did not permit. I've added some TODOs. Normally I'd also log to the console
# or tag the test with "pending."
# 3. I'd normally have a framework to handle login and common functionality then break the tests into separate files.

import json
import logging
import time
import unittest
from http import HTTPStatus

import requests

BASE_URL = 'https://qa-api-challenge.herokuapp.com'
ENROLL = '/api/v1/vehicles/{vehicleId}/odometer-alerts/_enroll'
REPORT = BASE_URL + '/api/v1/odometer-alerts'
RESERVED_VEHICLE_ID = '123'


class VinliTests:

    def __init__(self):
        start_time = time.perf_counter()
        self.errors = []
        self.test_enroll()
        self.test_unenroll()
        self.test_report()
        assert len(self.errors) == 0, f'There were {len(self.errors)} failures: {self.errors}'
        logging.info(f'Test completed successfully in {time.perf_counter() - start_time} seconds.')

    def test_enroll(self) -> None:
        good_values = ['0', '1', '02', '10', '0010', '100', '1000', '65530']
        bad_values = ['', '1.1', 'invalid', '\0', '-1', '100000000']

        for vehicle_id in good_values:
            req = self.enroll(vehicle_id, HTTPStatus.CREATED)
            json_data = json.loads(req.text)
            enrollment = json_data.get('enrollment')
            response_vehicle_id = enrollment.get('vehicleId')
            if response_vehicle_id != vehicle_id:
                self.log_and_append(
                    f'Added vehicleId: {vehicle_id}, but response contained vehicleId: {response_vehicle_id}.')
            if not enrollment.get('enrolled'):
                self.log_and_append(f'Enrolled was not true for {vehicle_id}.')
            # Should unenroll each vehicle
        # TODO: Ask if NOT_FOUND is the right status code for invalid vehicleIds.
        for vehicle_id in bad_values:
            self.enroll(vehicle_id, HTTPStatus.NOT_FOUND)
        # TODO: Ask if FORBIDDEN is the right status code for duplicates.
        for vehicle_id in good_values:
            self.enroll(vehicle_id, HTTPStatus.FORBIDDEN, 'Duplicates should be rejected.')
        # Should unenroll any invalids that got added.

    # This is not comprehensive due to time constraints.
    def test_unenroll(self) -> None:
        self.enroll(RESERVED_VEHICLE_ID, HTTPStatus.CREATED)
        self.enroll(RESERVED_VEHICLE_ID, HTTPStatus.NO_CONTENT, False, 'Unable to unenroll added vehicle.')
        # TODO: Ask if NOT_FOUND Is correct
        self.enroll(RESERVED_VEHICLE_ID, HTTPStatus.NOT_FOUND, False, 'Should not be able to unenroll vehicle twice.')

        # Add tests of invalid IDs

    # Due to time constraints this is not comprehensive.
    def test_report(self):
        fields = ['id', 'vehicleId', 'status', 'mileage', 'completedDate']

        def missing_item(item: str) -> None:
            self.log_and_append(f'Report: "alerts" is missing "{item}" for vehicleId: {RESERVED_VEHICLE_ID}.')

        # Enroll a car so we have some data.
        self.enroll(RESERVED_VEHICLE_ID, HTTPStatus.CREATED)
        req = requests.get(REPORT)
        json_data = json.loads(req.text)
        if 'alerts' not in json_data:
            self.log_and_append('"alerts" not in report.')
        else:
            for entry in json_data.get('alerts'):
                for field in fields:
                    if field not in entry:
                        missing_item(field)

                # Should check id is valid and same on multiple runs.
                # Should check vehicleIds match those added
                # Should check mileage never decreases

        # clean up
        self.enroll(RESERVED_VEHICLE_ID, HTTPStatus.NO_CONTENT, False, 'Unable to unenroll added vehicle.')

    def enroll(self, vehicle_id: str, expected: int, should_enroll: bool = True, logging_details: str = '') -> requests:
        if should_enroll:
            req = requests.post(self.make_url(ENROLL, vehicle_id))
        else:
            req = requests.delete(self.make_url(ENROLL, vehicle_id))
        if req.status_code != expected:
            self.log_and_append(
                f'Expected status code {expected} for vehicleId: {vehicle_id}. Got {req.status_code}. {logging_details}')
        return req

    @staticmethod
    def make_url(endpoint: str, vehicle_id: str) -> str:
        return BASE_URL + endpoint.replace('{vehicleId}', vehicle_id)

    def log_and_append(self, message: str) -> None:
        logging.warning(message)
        self.errors.append(message)


class TestVinliQAChallenge(unittest.TestCase):
    def test(self):
        return VinliTests()

    test.db = True
    test.group = ['Assortment', 'AsstBuild', 'AddToAsst', 'DataAddSub']


if __name__ == '__main__':
    VinliTests()
