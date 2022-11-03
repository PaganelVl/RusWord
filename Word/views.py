from django.shortcuts import render
from django.template.response import TemplateResponse
import requests
from bs4 import BeautifulSoup
from transliterate import translit
from django import forms


class Form(forms.Form):
    word = forms.CharField(label='')


class Parse:
    def word_manage(self, fl):
        """

        Траслитерация слова
         и обозначения его первой буквы на латинице

        """
        self.FirstLetter = fl
        self.word = translit(self.word, 'ru', reversed=True)
        for i in self.word:
            if i == "'":
                self.word = self.word.replace(i, "")

    def parse(self, url):
        # Замена ё на е
        for i in self.word:
            if i == "ё":
                self.word = self.word.replace(i, "е")
        # Траслитерация слова и обозначения его первой буквы на латинице
        match self.word[0]:
            case "е":
                self.word_manage('ye')
            case "ж":
                self.word_manage('zh')
            case "й":
                self.word_manage('iy')
            case "ч":
                self.word_manage('ch')
            case "ш":
                self.word_manage('sh')
            case "щ":
                self.word_manage('sch')
            case "ъ":
                self.word = "tverdyi-znak"
                self.FirstLetter = "tznak"
            case "ы":
                self.word = "y"
                self.FirstLetter = "y"
            case "ь":
                self.word = "myagkii-znak"
                self.FirstLetter = "mznak"
            case "ю":
                self.word_manage('yu')
            case "я":
                self.word_manage('ya')
            case _:
                self.word_manage(str(self.word[0]))

        search_url = f'{url}/{self.FirstLetter}/{self.word}.html'
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'lxml')
        dic = soup.find_all('div', class_="found_word")
        res = ""

        for gloses in dic:
            res += gloses.p.text

        return res

    def __init__(self, word):
        self.word = word


def index(request):
    userform = Form()
    data = {"form": userform}

    return render(request, "index.html", data)


def result(request):
    word = request.POST.get("word")
    word = str(word)
    parse_dict = Parse(word)

    dictionaries = [
        ['Толковый словарь Даля', 'https://diclist.ru/slovar/dalya'],
        ['Толковый словарь Ожегова', 'https://diclist.ru/slovar/ozhegova'],
        ['Толковый словарь Ушакова', 'https://diclist.ru/slovar/ushakova'],
        ['Словарь Ефремовой', 'https://diclist.ru/slovar/efremovoy'],
        ['Энциклопедия Брокгауза и Ефрона', 'https://diclist.ru/slovar/dalya']
    ]

    for i in dictionaries:
        i.append(f'{parse_dict.parse(i[1])}')

    userform = Form()
    data = {'dict': dictionaries, 'word': word, "form": userform}

    return TemplateResponse(request, 'result.html', data)
