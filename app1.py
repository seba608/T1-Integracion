from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
import requests
import json
from octopus import Octopus

app = Flask(__name__)
Bootstrap(app)


def create_request(urls, buscar):
    data = []

    otto = Octopus(concurrency=20, auto_start=True, cache=True, expiration_in_seconds=50)

    def handle_url_response(url, response):
        if "Not found" == response.text:
            print ("URL Not Found: %s" % url)
        else:
            aux_dict = json.loads(response.text)
            if aux_dict["url"][-3] == '/':
                data.append((aux_dict[buscar], aux_dict["url"][-2]))
            else:
                data.append((aux_dict[buscar], aux_dict["url"][-3:-1]))

    for url in urls:
        otto.enqueue(url, handle_url_response)

    otto.wait()
    return data


@app.route("/")
def index():
    r = requests.get("https://swapi.co/api/films/")
    data = json.loads(r.text)
    return render_template("index.html", films=data['results'])


@app.route('/pelicula/<int:film_id>')
def mostrar_pelicula(film_id):
    r = requests.get("https://swapi.co/api/films/{}/".format(film_id))
    film = json.loads(r.text)

    personajes = create_request(film['characters'], 'name')
    planetas = create_request(film['planets'], 'name')
    naves = create_request(film['starships'], 'name')
    return render_template("pelicula.html", pelicula=film, personajes=personajes,
                           planetas=planetas, naves=naves)


@app.route('/personaje/<int:personaje_id>')
def mostrar_personaje(personaje_id):
    r = requests.get("https://swapi.co/api/people/{}/".format(personaje_id))
    character = json.loads(r.text)
    peliculas = create_request(character['films'], 'title')
    naves = create_request(character['starships'], 'name')
    return render_template("personaje.html", personaje=character, peliculas=peliculas,
                           naves=naves)


@app.route('/nave/<int:nave_id>')
def mostrar_nave(nave_id):
    r = requests.get("https://swapi.co/api/starships/{}/".format(nave_id))
    nave = json.loads(r.text)

    peliculas = create_request(nave['films'], 'title')
    pilots = create_request(nave['pilots'], 'name')
    return render_template("nave.html", variable=nave, peliculas=peliculas,
                           pilotos=pilots)


@app.route('/planeta/<int:planeta_id>')
def mostrar_planeta(planeta_id):
    r = requests.get("https://swapi.co/api/planets/{}/".format(planeta_id))
    planeta = json.loads(r.text)

    peliculas = create_request(planeta['films'], 'title')
    pilots = create_request(planeta['residents'], 'name')
    return render_template("planeta.html", variable=planeta, peliculas=peliculas,
                           pilotos=pilots)


@app.route('/search', methods=["POST", "GET"])
def search():
    if request.method == "POST":
        input = request.form['entrada']
        personajes = []
        naves = []
        planetas = []
        peliculas = []
        vars = ['people', 'starships', 'planets', 'films']
        for var in vars:
            r = requests.get('https://swapi.co/api/{}/?search={}'.format(var, input))
            aux = json.loads(r.text)

            if var == 'people':
                for elem in aux['results']:
                    if elem["url"][-3] == '/':
                        personajes.append((elem['name'], elem["url"][-2]))
                    else:
                        personajes.append((elem['name'], elem["url"][-3:-1]))

            elif var == 'starships':
                for elem in aux['results']:
                    if elem["url"][-3] == '/':
                        naves.append((elem['name'], elem["url"][-2]))
                    else:
                        naves.append((elem['name'], elem["url"][-3:-1]))

            elif var == 'planets':
                for elem in aux['results']:
                    if elem["url"][-3] == '/':
                        planetas.append((elem['name'], elem["url"][-2]))
                    else:
                        planetas.append((elem['name'], elem["url"][-3:-1]))

            else:
                for elem in aux['results']:
                    if elem["url"][-3] == '/':
                        peliculas.append((elem['title'], elem["url"][-2]))
                    else:
                        peliculas.append((elem['title'], elem["url"][-3:-1]))

        return render_template("search.html", personajes=personajes, peliculas=peliculas,
                               naves=naves, planetas=planetas)
    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
