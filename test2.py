import csv
from flask import Flask, jsonify, request, render_template, redirect, url_for, make_response

app = Flask(__name__)


with open('templates/Testing.csv') as f:
    reader = csv.reader(f)
    values = next(reader)
    values = values[:len(values ) -1]

print(values)

@app.route('/', methods=['GET'])
def page_show():
    print(values)
    return render_template('includes/default.html', values=values)

@app.route('/result', methods=['POST'])
def identify():
    selected_values = []
    if request.form['value' ] !='' and request.form['value'] not in selected_values:
        for value in values:
            selected_values.append(request.form['values'])

    disease = result.input_check(selected_values)
    return render_template('identify.html', values=values, results=results)


if __name__ == '__main__':

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=6666, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='localhost', port=port)
