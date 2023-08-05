import requests
import xmltodict


class CareerBuilder:
    base_api_url = 'http://api.careerbuilder.com/v1/'

    def __init__(self, developer_key):
        self.developer_key = developer_key

    def _api_call(self, url, **kwargs):
        url = self.base_api_url + url
        payload = {
            'DeveloperKey': self.developer_key,
        }
        payload = dict(payload.items() + kwargs.items())
        resp = requests.get(url, params=payload)
        xml = resp.text
        return xmltodict.parse(xml)

    def application(self, job_id, **kwargs):
        kwargs['JobDID'] = job_id
        return self._api_call('appliation/blank', **kwargs)

    def categories(self, **kwargs):
        return self._api_call('categories', **kwargs)

    def education_codes(self, **kwargs):
        return self._api_call('educationscodes', **kwargs)

    def employee_types(self, **kwargs):
        return self._api_call('employeetypes', **kwargs)

    def job(self, job_id, **kwargs):
        kwargs['DID'] = job_id
        return self._api_call('job', **kwargs)

    def job_search(self, **kwargs):
        return self._api_call('jobsearch', **kwargs)

    def recommendations(self, job_id, **kwargs):
        kwargs['JobDID'] = job_id
        return self._api_call('recommendations/forjob', **kwargs)
