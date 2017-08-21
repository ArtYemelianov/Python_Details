import requests, json


class Station:
    def __init__(self, id, name):
        """

        :param int id: Id of station
        :param str name:  Name of station
        """
        self.id = id
        self.name = name

    def values(self):
        return (self.id, self.name)

    def __str__(self):
        return str(self.values())

    def __repr__(self):
        return 'id: %d, name: %s' % (self.id, self.name)


class TrainRequest:
    URL = 'http://booking.uz.gov.ua/ru/purchase/search/'

    def __init__(self, **kwargs):
        '''

        :param Station start: A from station
        :param Station end: An end station

        '''
        self.station_from = kwargs['station_from']
        self.station_till = kwargs['station_till']
        self.date_dep = kwargs.get('date_dep', '15.08.2017')
        self.time_dep = kwargs.get('time_dep', '00:00')
        self.time_dep_till = kwargs.get('time_dep_till', '23:59')
        self.another_ec = kwargs.get('another_ec', '0')
        self.search = kwargs.get('search', '')
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.result = None
        """:type: requests.Response """

    def has_error(self):
        '''
        Checks request finished with an error or success
        :return: If error occurred - description of error. If success - None
        :rtype: str|None
        '''
        if not self.result:
            return "Request not done"
        else:
            if self.result.status_code != 200:
                return "Error status code %d" % self.result.status_code
            data = json.loads(self.result.text)
            ":type: dict"
            error = data.get('error', None)
            return error

    def get_data(self):
        '''
        Gets parsed data
        :return: If error occurred - description of error. If success - None
        :rtype: list of parsed response
        :rtype: list of TrainResponse

        '''
        ls = json.loads(self.result.text)['value']
        res = list()
        for item in ls:
            data = {}
            data['from'] = StationResponse(**item['from'])
            data['till'] = StationResponse(**item['till'])
            data['types'] = [TypeResponse(**x) for x in item['types']]
            data['num'] = item['num']
            data['model'] = item['model']
            data['category'] = item['category']
            data['travel_time'] = item['travel_time']
            data['station_id_from'] = self.station_from.id
            data['station_id_till'] = self.station_till.id
            res.append(TrainResponse(**data))
        return res

    def make_request(self, **kwargs):
        """
        Makes post request
        :param date_dep: str Date
        """
        date_dep = kwargs.get('date_dep', self.date_dep)
        body = "station_id_from={}" \
               "&station_id_till={}" \
               "&station_from=&station_till=" \
               "&date_dep={}" \
               "&time_dep=00:00&time_dep_till=&another_ec=0&search=".format(
            self.station_from.id,
            self.station_till.id,
            date_dep
        )
        self.result = requests.post(TrainRequest.URL, data=body, headers=self.headers)


class TrainResponse:
    def __init__(self, **kwargs):
        '''


        :param str num:  Number of train
        :param int model:  Model
        :param int category:  Category
        :param str travel_time: During of trip
        :param StationResponse station_from: A from station
        :param StationResponse station_till: A till station
        :param list of (TypeResponse) types: A list of types
        '''
        self.station_id_from = kwargs['station_id_from']
        self.station_id_till = kwargs['station_id_till']
        self.num = kwargs['num']
        self.model = kwargs['model']
        self.category = kwargs.get('category', None)
        self.travel_time = kwargs['travel_time']
        self.station_from = kwargs['from']
        self.station_till = kwargs['till']
        self.types = kwargs['types']

    def __repr__(self):
        return "{%s, %s, %s -> %s, %s}" % (self.num,
                                           self.travel_time,
                                           self.station_from,
                                           self.station_till,
                                           self.types)

    def __str__(self):
        return " num %s, " \
               "model %s, " \
               "category  %d, " \
               "travel_time %s " \
               "%s -> %s, %s}" % \
               (self.num,
                self.model,
                self.category,
                self.travel_time,
                self.station_from,
                self.station_till,
                self.types)


class StationResponse:
    """
    Structure that contains response request
    """

    def __init__(self, **kwargs):
        self.station = kwargs['station']
        self.date = kwargs['date']
        self.src_date = kwargs['src_date']

    def __repr__(self):
        return "{%s , %s}" % (self.station, self.src_date)


class TypeResponse:
    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.title = kwargs['title']
        self.letter = kwargs['letter']
        self.places = kwargs['places']

    def __repr__(self):
        return "{%s , %d}" % (self.title, self.places)


def request_station(name):
    url_station = 'http://booking.uz.gov.ua/ru/purchase/station'
    res = requests.get(url_station, params={'term': name})
    return res


def request_and_parse_station(name):
    res = request_station(name)
    if res.status_code != 200:
        return []
    titles = [Station(x['value'], x['title']) for x in json.loads(res.text)]
    return titles


def compose_coaches_body(station_from, station_till, train, coach_type, date):
    """
    Compose body for coaches request

    :param Station station_from: A from station
    :param Station station_till: A till station
    :param TrainResponse train: A train
    :return: dict
    """
    return "station_id_from={}" \
           "&station_id_till={}" \
           "&train={}" \
           "&coach_type={}" \
           "&date_dep={}" \
           "&round_trip=0" \
           "&another_ec=0".format(
        station_from,
        station_till,
        train,
        coach_type,
        date)


def encode_str(value):
    import ast
    return ast.literal_eval(str(value.encode())[1:].replace("\\x", '%'))


class CoachesRequest:
    URL = 'http://booking.uz.gov.ua/ru/purchase/coaches/'

    def __init__(self, train_response):
        '''

        :param TrainResponse train_response: Train response
        '''
        self.station_id_from = train_response.station_id_from
        self.types = [encode_str(x.id) for x in train_response.types]
        self.station_id_till = train_response.station_id_till
        self.train = encode_str(train_response.num)

        self.date_dep = train_response.station_from.date
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    def make_request(self, **kwargs):
        """
        Makes post request
        :param str train: Name of train
        :param str coach_type: Coach type
        :param int type_index: Index of type
        """
        train = kwargs.get('train', self.train)
        type_index = kwargs['type_index']
        coach_type = self.types[type_index]
        body = ('station_id_from={}' \
                '&station_id_till={}' \
                '&train={}' \
                '&coach_type={}' \
                '&date_dep={}' \
                '&round_trip=0' \
                '&another_ec=0').format(
            self.station_id_from,
            self.station_id_till,
            train,
            coach_type,
            self.date_dep,
        )
        self.result = requests.post(CoachesRequest.URL, data=body, headers=self.headers)
        return self.result
