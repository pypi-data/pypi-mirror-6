import unittest
from getpass import getpass
from korail import Korail, KorailError


class TestKorail(unittest.TestCase):

    korail = Korail()

    def test_0_login(self):
        user_id = raw_input("ID: ")
        password = getpass()
        phone_signing = raw_input("Use Phone Signing? (y/N) ").lower() == 'y'
        rv = self.korail.login(user_id, password, phone_signing)
        self.assertEqual(rv, True)

    def test_1_search_ktx(self):
        from datetime import datetime
        dep = '0001'
        arr = '0015'
        train_type = '00'
        date = datetime.strftime(datetime.now(), '%Y%m%d')
        time = datetime.strftime(datetime.now(), '%H%M%S')

        try:
            trains = self.korail.search_train(dep, arr, date, time, train_type)
        except KorailError as e:
            self.fail(e.message.encode('utf-8'))

        for train in trains:
            if train.train_type != '00' and train.train_type != '07':
                self.fail('Non-KTX train(%s) is included in search result.' %
                          train.train_type)

    def test_2_search_reserve(self):
        from datetime import datetime
        dep = '0001'
        arr = '0015'
        date = datetime.strftime(datetime.now(), '%Y%m%d')
        time = datetime.strftime(datetime.now(), '%H%M%S')

        try:
            trains = self.korail.search_train(dep, arr, date, time)
        except KorailError as e:
            self.fail(e.message.encode('utf-8'))

        tickets_count = len(self.korail.tickets())

        try:
            self.korail.reserve(trains[-1])
        except KorailError as e:
            self.fail(e.message.encode('utf-8'))

        tickets = self.korail.tickets()
        self.assertEqual(len(tickets), tickets_count + 1)

    def test_4_cancel_all(self):
        tickets = self.korail.tickets()
        for ticket in tickets:
            self.korail.cancel_ticket(ticket)
        tickets = self.korail.tickets()
        self.assertEqual(len(tickets), 0)


if __name__ == '__main__':
    unittest.main()
