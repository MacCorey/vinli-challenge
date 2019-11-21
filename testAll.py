import logging
import unittest
import time
from http import HTTPStatus
import requests
import json

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

    def test_enroll(self):
        good_values = ['0', '1', '02', '10', '0010', '100', '1000', '65530']
        bad_values = ['', 'invalid', '\0', '-1', '100000000']

        for vehicle_id in good_values:
            self.enroll(vehicle_id, HTTPStatus.CREATED)
        # TODO: Ask if NOT_FOUND is the right status code for invalid vehicleIds.
        for vehicle_id in bad_values:
            self.enroll(vehicle_id, HTTPStatus.NOT_FOUND)
        # TODO: Ask if FORBIDDEN is the right status code for duplicates.
        for vehicle_id in good_values:
            self.enroll(vehicle_id, HTTPStatus.FORBIDDEN, 'Duplicates should be rejected.')

    # This is not comprehensive due to time constraints.
    def test_unenroll(self):
        self.enroll(RESERVED_VEHICLE_ID, HTTPStatus.CREATED)
        self.enroll(RESERVED_VEHICLE_ID, HTTPStatus.NO_CONTENT, False, 'Unable to unenroll added vehicle.')
        # TODO: Ask if NOT_FOUND Is correct
        self.enroll('123', HTTPStatus.NOT_FOUND, False, 'Should not be able to unenroll vehicle twice.')

    # Due to time constraints this is not as comprehensive as it should be.
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

        # clean up
        self.enroll(RESERVED_VEHICLE_ID, HTTPStatus.NO_CONTENT, False, 'Unable to unenroll added vehicle.')

    def enroll(self, vehicle_id: str, expected: int, should_enroll: bool = True, logging_details: str = ''):
        if should_enroll:
            req = requests.post(self.make_url(ENROLL, vehicle_id))
        else:
            req = requests.delete(self.make_url(ENROLL, vehicle_id))
        if req.status_code != expected:
            self.log_and_append(f'Expected status code {expected} for vehicleId: {vehicle_id}. Got {req.status_code}. {logging_details}')

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
