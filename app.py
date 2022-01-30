from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from wtforms import FloatField, DecimalRangeField, SubmitField
from wtforms.validators import InputRequired
from compute import UAR, obiekt

import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mykey'
app.config['DEBUG'] = True

class MODEL(FlaskForm):
    default_value = [0.05, 0.05, 0.75, 1, 0, 2.5, 0.25, 10, 10, -10, 1]
    sample_time = DecimalRangeField('Okres próbkowania: ', default=default_value[0])
    differential_time = DecimalRangeField('Czas wyprzedzenia: ', default=default_value[1])
    integration_time = DecimalRangeField('Czas zdwojenia :', default=default_value[2])
    gain = DecimalRangeField('Wartość wzmocnienia regulatora: ', default=default_value[3])
    h_z = DecimalRangeField('Wartość zadana: ', default=default_value[4])
    A = FloatField('Pole powierzchni przekroju poprzecznego: ', default=default_value[5], validators=[InputRequired()])
    B = FloatField('Współczynnik wypływu: ', default=default_value[6], validators=[InputRequired()])
    h_max = FloatField('Maksymalny poziom substancji w zbiorniku: ', default=default_value[7], validators=[InputRequired()])
    u_max = FloatField('Maksymalna wartość sygnału sterującego: ', default=default_value[8], validators=[InputRequired()])
    u_min = FloatField('Minimalna wartość sygnału sterującego: ', default=default_value[9], validators=[InputRequired()])
    Q_d_max = FloatField('Maksymalne natężenie dopływu: ', default=default_value[10], validators=[InputRequired()])
    submit_all = SubmitField('Zatwierdź wszystko')

@app.route('/', methods = ["POST","GET"])
def index():

    form = MODEL(request.form)
    cost = UAR.costsController(obiekt)
    cost_fuzzy = UAR.costsControllerFuzzy(obiekt)
    quality = UAR.qualityController(obiekt)
    quality_fuzzy = UAR.qualityControllerFuzzy(obiekt)
    if request.method == "POST" and form.validate():
        with open('static/data/data.json', 'w') as f:
            json.dump(request.form, f)

    return render_template('view_pid_simulator.html', form=form, cost=cost,cost_fuzzy=cost_fuzzy, quality=quality,
                           quality_fuzzy=quality_fuzzy)

@app.route('/Generate_PID')
def SomeFunction():
    UAR.count(obiekt)
    UAR.FuzzyDisplay(obiekt)
    return "200"


if __name__ == '__main__':
    app.run()
