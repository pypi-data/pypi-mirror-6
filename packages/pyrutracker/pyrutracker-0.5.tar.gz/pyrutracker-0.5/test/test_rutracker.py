#!/usr/bin/env python
# coding=utf-8

import unittest
import sys
import os
import string
from collections import OrderedDict
from datetime import datetime
sys.path.append("..")

import bs4
from pyrutracker import common


class TestRuTracker(unittest.TestCase):

    def get_doc(self, file_path):
        path = os.path.join(os.path.dirname(__file__), file_path)
        return bs4.BeautifulSoup(open(path, 'r'))

    def test_clear_text(self):
        s = "text example"
        self.assertEqual(
            s, common.clear_text(string.whitespace + s + string.whitespace))

    def test_categories(self):
        categories = ['Новости', 'Вопросы по форуму и трекеру',
                      'Кино, Видео и ТВ', 'Документалистика и юмор',
                      'Спорт', 'Сериалы', 'Книги и журналы',
                      'Обучение иностранным языкам', 'Обучающее видео',
                      'Аудиокниги', 'Все по авто и мото', 'Музыка',
                      'Популярная музыка', 'Джазовая и Блюзовая музыка',
                      'Рок-музыка', 'Электронная музыка', 'Игры',
                      'Программы и Дизайн', 'Мобильные устройства', 'Apple',
                      'Медицина и здоровье', 'Разное',
                      'Обсуждения, встречи, общение']

        for category in common.categories(self.get_doc("html/main.html")):
            self.assertTrue(category.title.encode('utf-8') in categories)

    def test_pages(self):
        doc = self.get_doc("html/pages-no.html")
        self.assertEqual(1, len(list(common.pages(doc))))

        doc = self.get_doc("html/pages-normal.html")
        self.assertEqual(12, len(list(common.pages(doc))))

        doc = self.get_doc("html/pages-two.html")
        self.assertEqual(2, len(list(common.pages(doc))))

    def test_headers(self):
        doc = self.get_doc("html/subforums.html")
        headers = common.get_headers(doc)
        self.assertEqual(headers, (u'Зарубежное кино',))

    def test_headers2(self):
        doc = self.get_doc("html/topic.html")
        headers = common.get_headers(doc)
        self.assertEqual(headers, (u'Зарубежное кино', u'Фильмы до 1990 года'))

    def test_subforums(self):
        doc = self.get_doc("html/subforums.html")
        subforums = list(common.subforums(doc))
        self.assertEqual(22, len(subforums))
        self.assertEqual(subforums[-1].date, datetime(2013, 9, 21, 23, 57))

    def test_subforums_without_date(self):
        doc = self.get_doc("html/main.html")
        subforums = list(common.subforums(doc))
        self.assertEqual(subforums[3].date, None)

    def test_topics(self):
        doc = self.get_doc("html/subforums.html")
        topics = list(common.topics(doc))
        self.assertEqual(13, len(topics))
        n = -3
        self.assertEqual(
            topics[n].title.encode('utf-8'), "Мебиус / Moebius (Ким Ки-Дук / Kim Ki-duk) [2013, Южная Корея, драма, немое кино, HDRip]")
        self.assertEqual(topics[n].url,
                         "http://rutracker.org/forum/viewtopic.php?t=4541293")
        self.assertEqual(topics[n].size.encode('utf-8'), '1.03 GB')
        self.assertEqual(topics[n].date, datetime(2013, 9, 22, 3, 2))

    def test_page_items(self):
        doc = self.get_doc("html/subforums.html")
        items = list(common.page_items(doc))
        self.assertEqual(35, len(items))
        subforums = filter(
            lambda item: isinstance(
                item,
                common.Subforum),
            items)
        topics = filter(lambda item: isinstance(item, common.Topic), items)
        self.assertEqual(22, len(subforums))
        self.assertEqual(13, len(topics))

    def test_topic_description(self):
        doc = self.get_doc("html/topic.html")
        descr = common.topic_description(doc)
        result = OrderedDict([
            (u'Название', u'Детская игра 2 / Child’s Play 2'),
            (u'Страна', u'США'),
            (u'Жанр', u'ужасы, триллер, детектив'),
            (u'Год выпуска', u'1990'),
            (u'Продолжительность', u'01:23:50'),
            (u'Перевод', u'Студийный (одноголосый закадровый) Tycoon'),
            (u'Перевод 2', u'Авторский (одноголосый закадровый) Горчаков'),
            (u'Cубтитры', u'нет'),
            (u'Оригинальная аудиодорожка', u'английский'),
            (u'Режиссер', u'Джон Лафия / John Lafia'),
            (u'В ролях',
             u'Алекс Винсент, Дженни Агаттер, Геррит Грэм, Кристин Элиз, Грейс Забриски, Брэд Дуриф'),
            (u'Описание',
             u'Энди — мальчик, в которого Чаки пытался вселиться в первой серии — попадает к приёмным родителям (родная мать мальчика была признана душевнобольной). Ему до сих пор снятся кошмары о Чаки. Между тем, фирма-производитель рыжих игрушечных пупсов, дабы избежать дурной репутации (в силу событий, произошедших в фильме-оригинале), восстанавливает куклу Чаки из её «останков», найденных на «месте происшествия». Так фирма пытается доказать, что реальной опасности кукла не имеет. Но получилось наоборот… Теперь Энди вновь предстоит столкнуться с маленьким, но очень опасным, пластмассовым монстром, который все ещё намерен овладеть телом мальчика…'),
            (u'Автор рипа', u'msltel'),
            (u'Качество видео', u'BDRip (Blu-Ray Remux/1080p)'),
            (u'Формат видео', u'AVI'),
            (u'Видео',
             u'720x384 (1.85:1) 23.976fps XviD 1 900 Kbps 0.287 bit/pixel'),
            (u'Аудио 1', u'Dolby AC3 48000Hz stereo 192kbps'),
            (u'Аудио 2', u'Dolby AC3 48000Hz stereo 192kbps'),
            (u'Аудио 3', u'Dolby AC3 48000Hz stereo 192kbps')
        ])
        self.assertEqual(result, descr)

    def test_topic_description2(self):
        doc = self.get_doc("html/topic2.html")
        descr = common.topic_description(doc)
        result = OrderedDict([
            (u'Название',
             u'Укротитель медведей / Bjornetaemmeren / The Bear Tamer'),
            (u'Год выпуска', u'1912'),
            (u'Страна', u'Дания'),
            (u'Жанр', u'драма, немое кино'),
            (u'Продолжительность', u'00:40:29'),
            (u'Перевод', u'Субтитры'),
            (u'Русские субтитры', u'есть'),
            (u'Режиссер', u'Альфред Линд / Alfred Lind'),
            (u'В ролях',
             u'Альфред Линд, Лили Бек, Петер Фьельструп, Хольгер-Мадсен'),
            (u'Описание',
             u'К бродячему цирку присоединяется укротитель вместе со своим питомцем – дрессированным медведем. Через некоторое время он женится на актрисе этого цирка – заклинательнице змей. Но поступает заманчивое предложение его жене работать в варьете. Слава и поклонники настолько вскружили ей голову, что муж - укротитель медведей - вынужден действовать…'),
            (u'В 1912 г. режиссер Альфред Линд снял фильм «Бродячий цирк», который пользовался настолько большой популярностью в не только в странах Скандинавии но и в Европе (кстати и в России тоже), что в том же году, по горячим следам, Линд решил снять сиквел',
             u'«Укротитель медведей».'),
            (u'imdb.com User Rating', u'7,7/10'),
            (u'Качество', u'DVDRip'),
            (u'Формат', u'AVI'),
            (u'Видео кодек', u'XviD'),
            (u'Аудио кодек', u'MP3'),
            (u'Видео', u'720 х 544, 25 fps, ~1483 kbps Xvid'),
            (u'Аудио', u'44.100 kHz, MPEG Layer 3, 2 ch, ~128.00 kbps avg')
        ])
        self.assertEqual(result, descr)

    def test_blocked(self):
        doc = self.get_doc("html/page-blocked.html")
        self.assertTrue(common.is_blocked(doc))

    def test_blocked_raises(self):
        self.assertRaises(common.PageBlocked,
                          common.html_from_url, "html/page-blocked.html")

if __name__ == '__main__':
    unittest.main()
