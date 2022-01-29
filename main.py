from flask import Flask, Response
from flask_restful import Api, Resource, reqparse, abort, request
import datetime
from urllib.parse import parse_qs
import json
from wiki import getWiki

app = Flask(__name__)
api = Api(app)

languages = {
    "he": {
        'title': 'מיוחד:חיפוש',
        'url': 'https://he.wikipedia.org/w/index.php'
    },
    "en": {
        'title': 'Special:Search',
        'url': 'https://en.wikipedia.org/w/index.php'
    },
    "es": {
        'title': 'Especial:Buscar',
        'url': 'https://es.wikipedia.org/w/index.php'
    },
    "ru": {
        'title': 'Служебная:Поиск',
        'url': 'https://ru.wikipedia.org/w/index.php'
    }
}


class Wiki(Resource):
    def get(self):
        query = parse_qs(request.query_string.decode())
        article, num, lan = query.get("article"), query.get("par"), query.get("lan")
        if article is None or num is None:
            return Response(response="Bad Request", status=404, mimetype="application/json")
        article = str(article[0])
        num = str(num[0])
        if not num.isdigit():
            if num == "all":
                num = 10000
            else:
                return Response(response="Bad Number", status=400, mimetype="application/json")
        else:
            num = int(num)
        if lan is None:
            lan = "en"
        else:
            lan = str(lan[0])
            if languages.get(lan) is None:
                return Response(response="Language Not Found", status=400, mimetype="application/json")
        try:
            page = getWiki(article, num, lan)
        except Exception:
            return Response(response="Not Found", status=404, mimetype="application/json")
        r = Response(response=page, status=200)
        return r

    def post(self):
        data = parse_qs(request.get_data().decode())
        if data == {}:
            try:
                data = json.loads(request.get_data().decode())
            except json.decoder.JSONDecodeError:
                return Response(response="Bad request", status=400, mimetype="application/json")
        try:
            article, num = data.get("article"), data.get("par")
            if type(article) == list:
                article = article[0]
            if type(num) == list:
                num = num[0]

            if data.get("lan") is None:
                lan = "en"
            else:
                lan = data.get("lan")
                if type(lan) == list:
                    lan = lan[0]
            if num != "all":
                num = int(num)
            else:
                num = 10000

        except Exception:
            return Response(response="Bad request", status=400, mimetype="application/json")
        try:
            page = getWiki(article, num, lan)
        except Exception:
            return Response(response="Bad articles", status=400, mimetype="application/json")

        r = Response(response=page, status=200)
        return r


api.add_resource(Wiki, "/")
if __name__ == "__main__":
    app.run(debug=False)
