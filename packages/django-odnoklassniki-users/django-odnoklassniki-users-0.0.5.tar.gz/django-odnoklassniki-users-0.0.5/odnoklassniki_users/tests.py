# -*- coding: utf-8 -*-
from django.test import TestCase
from models import User, USER_INFO_TIMEOUT_DAYS
from factories import UserFactory
from datetime import datetime, timedelta
import simplejson as json
import mock

USER1_ID = 561348705024
USER1_NAME = u'Евгений Дуров'

USER2_ID = 578592731938

def user_fetch_mock(**kwargs):
    ids = kwargs.get('uids').split(',')
    users = [User.objects.get(id=id) if User.objects.filter(id=id).count() == 1 else UserFactory(id=id) for id in ids]
    ids = [user.pk for user in users]
    return User.objects.filter(pk__in=ids)

class OdnoklassnikiUsersTest(TestCase):

    def test_refresh_user(self):

        instance = User.remote.fetch(ids=[USER1_ID])[0]
        self.assertEqual(instance.name, USER1_NAME)

        instance.name = 'temp'
        instance.save()
        self.assertEqual(instance.name, 'temp')

        instance.refresh()
        self.assertEqual(instance.name, USER1_NAME)

    def test_fetch_user(self):

        self.assertEqual(User.objects.count(), 0)

        users = User.remote.fetch(ids=[USER1_ID, USER2_ID])

        self.assertEqual(len(users), 2)
        self.assertEqual(User.objects.count(), 2)

        instance = users.get(id=USER1_ID)

        self.assertEqual(instance.id, USER1_ID)
        self.assertEqual(instance.name, USER1_NAME)
        self.assertTrue(isinstance(instance.registered_date, datetime))

    @mock.patch('odnoklassniki_api.models.OdnoklassnikiManager.fetch', side_effect=user_fetch_mock)
    def test_fetch_users_more_than_100(self, fetch):

        users = User.remote.fetch(ids=range(0, 150))

        self.assertEqual(len(users), 150)
        self.assertEqual(User.objects.count(), 150)

        self.assertEqual(len(fetch.mock_calls[0].call_list()[0][2]['uids'].split(',')), 100)
        self.assertEqual(len(fetch.mock_calls[1].call_list()[0][2]['uids'].split(',')), 50)

    @mock.patch('odnoklassniki_api.models.OdnoklassnikiManager.fetch', side_effect=user_fetch_mock)
    def test_fetching_expired_users(self, fetch):

        users = User.remote.fetch(ids=range(0, 50))

        # make all users fresh
        User.objects.all().update(fetched=datetime.now())
        # make 10 of them expired
        User.objects.filter(pk__lt=10).update(fetched=datetime.now() - timedelta(USER_INFO_TIMEOUT_DAYS + 1))

        users_new = User.remote.fetch(ids=range(0, 50), only_expired=True)

        self.assertEqual(len(fetch.mock_calls[0].call_list()[0][2]['uids'].split(',')), 50)
        self.assertEqual(len(fetch.mock_calls[1].call_list()[0][2]['uids'].split(',')), 10)
        self.assertEqual(users.count(), 50)
        self.assertEqual(users.count(), users_new.count())

    def test_parse_user(self):

        response = u'''[{
              "allows_anonym_access": true,
              "birthday": "05-11",
              "current_status": "собщество генерал шермон",
              "current_status_date": "2013-11-12 03:45:01",
              "current_status_id": "62725470887936",
              "first_name": "Евгений",
              "gender": "male",
              "has_email": false,
              "has_service_invisible": false,
              "last_name": "Дуров",
              "last_online": "2014-04-09 02:35:10",
              "locale": "r",
              "location": {"city": "Кемерово",
               "country": "RUSSIAN_FEDERATION",
               "countryCode": "RU"},
              "name": "Евгений Дуров",
              "photo_id": "508669228288",
              "pic1024x768": "http://uld1.mycdn.me/getImage?photoId=508669228288&photoType=3&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic128max": "http://usd1.mycdn.me/getImage?photoId=508669228288&photoType=2&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic128x128": "http://umd1.mycdn.me/getImage?photoId=508669228288&photoType=6&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic180min": "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=13&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic190x190": "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=5&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic240min": "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=14&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic320min": "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=15&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic50x50": "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=4&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic640x480": "http://uld1.mycdn.me/getImage?photoId=508669228288&photoType=0&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic_1": "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=4&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic_2": "http://usd1.mycdn.me/getImage?photoId=508669228288&photoType=2&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic_3": "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=5&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic_4": "http://uld1.mycdn.me/getImage?photoId=508669228288&photoType=0&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "pic_5": "http://umd1.mycdn.me/getImage?photoId=508669228288&photoType=6&viewToken=1gbG-ihJLgI5L_XujVV_6A",
              "private": false,
              "registered_date": "2012-11-05 14:13:53",
              "uid": "561348705024",
              "url_profile": "http://www.odnoklassniki.ru/profile/561348705024",
              "url_profile_mobile": "http://www.odnoklassniki.ru/profile/?st.application_key=CBAEBGLBEBABABABA&st.signature=d9867421a0017d9a08c17a206edf2730&st.reference_id=561348705024"}]'''

        instance = User()
        instance.parse(json.loads(response)[0])
        instance.save()

        self.assertEqual(instance.id, 561348705024)
        self.assertEqual(instance.name, u'Евгений Дуров')

        self.assertEqual(instance.allows_anonym_access, True)
        self.assertEqual(instance.birthday, "05-11")
        self.assertEqual(instance.current_status, u"собщество генерал шермон")
        self.assertEqual(instance.current_status_date, datetime(2013, 11, 12, 3, 45, 01))
        self.assertEqual(instance.current_status_id, 62725470887936)
        self.assertEqual(instance.first_name, u"Евгений")
        self.assertEqual(instance.gender, 2)
        self.assertEqual(instance.has_email, False)
        self.assertEqual(instance.has_service_invisible, False)
        self.assertEqual(instance.last_name, u"Дуров")
        self.assertEqual(instance.last_online, datetime(2014, 4, 9, 2, 35, 10))
        self.assertEqual(instance.locale, "r")
        self.assertEqual(instance.city, u"Кемерово")
        self.assertEqual(instance.country, "RUSSIAN_FEDERATION")
        self.assertEqual(instance.country_code, "RU")
        self.assertEqual(instance.name, u"Евгений Дуров")
        self.assertEqual(instance.photo_id, 508669228288)

        self.assertEqual(instance.pic1024x768, "http://uld1.mycdn.me/getImage?photoId=508669228288&photoType=3&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic128max, "http://usd1.mycdn.me/getImage?photoId=508669228288&photoType=2&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic128x128, "http://umd1.mycdn.me/getImage?photoId=508669228288&photoType=6&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic180min, "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=13&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic190x190, "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=5&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic240min, "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=14&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic320min, "http://itd0.mycdn.me/getImage?photoId=508669228288&photoType=15&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic50x50, "http://i500.mycdn.me/getImage?photoId=508669228288&photoType=4&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.pic640x480, "http://uld1.mycdn.me/getImage?photoId=508669228288&photoType=0&viewToken=1gbG-ihJLgI5L_XujVV_6A")
        self.assertEqual(instance.private, False)
        self.assertEqual(instance.registered_date, datetime(2012, 11, 5, 14, 13, 53))
        self.assertEqual(instance.url_profile, "http://www.odnoklassniki.ru/profile/561348705024")
        self.assertEqual(instance.url_profile_mobile, "http://www.odnoklassniki.ru/profile/?st.application_key=CBAEBGLBEBABABABA&st.signature=d9867421a0017d9a08c17a206edf2730&st.reference_id=561348705024")
