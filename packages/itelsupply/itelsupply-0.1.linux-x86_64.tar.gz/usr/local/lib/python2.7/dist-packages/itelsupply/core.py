import requests

API_URL = "http://api.itelsupply.no/"

class ITelSupply(object):
    """
    Usage:
    i_tel_supply = ITelSupply('telephone_number')
    i_tel_supply.data.json()
    """

    def __init__(self, number, *args, **kwargs):
        self.number = number

        self.request = kwargs.get('request', 'get')
        self.response = kwargs.get('response', 'json')
        self.application = kwargs.get('application', 'cccs')
        self.call = kwargs.get('call', 'search')
        self.message = kwargs.get('message', '%20')
        self.price = kwargs.get('price', '0')
        self.returnurl = kwargs.get('returnurl', False)

        print self._get_data()


    def _get_data(self):
        payload = {
            'request': self.request,
            'response': self.response,
            'application': self.application,
            'call': self.call,
            'price': self.price,
                            'number': self.number,
        }

        if self.call == 'sendsms':
            payload['message'] = self.message

        if self.returnurl:
            payload['returnurl'] = self.returnurl

        self.data = requests.get('%s' % (API_URL), params=payload)
        return self.data.status_code

