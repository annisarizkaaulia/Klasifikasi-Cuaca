from flask import Flask, render_template, request, flash
from flask_mysqldb import MySQL
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras

app = Flask(__name__)
# session
app.secret_key = 'your_secret_key_here'
# db
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cuaca'
mysql = MySQL(app)


model = tf.keras.models.load_model("model.h5")  # model
class_names = ["Cerah", "Berawan", "Hujan"]  # to convert class


# PAGE USER
@app.route("/")
def index():
    # get data form
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM master_cuaca")
    data = cursor.fetchall()
    cursor.close()
    return render_template("pages/index.html", data=data)  # page index


# PAGE LOGIN
@app.route("/login")
def login():
    return render_template("pages/login.html")  # page login


# PAGE REGISTER
@app.route("/register")
def register():
    return render_template("pages/register.html")  # page register


# PAGE ADMIN
@app.route("/home")
def home():
    return render_template("pages/home.html")  # page home


# DATA WEATHER ADMIN
@app.route("/datatable")
def datatable():
    # get data form
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM master_cuaca")
    data = cursor.fetchall()
    cursor.close()
    return render_template("pages/datatable.html", data=data)  # page datatable


@ app.route("/deletecuaca/<int:id_cuaca>", methods=['POST'])
def deletecuaca(id_cuaca):
    # delete data
    cursor = mysql.connection.cursor()
    cursor.execute(
        "DELETE FROM master_cuaca WHERE id_cuaca = (%s)", (id_cuaca,))
    mysql.connection.commit()
    cursor.close()
    return render_template("pages/datatable.html")  # page formdata


# FORM WEATHER ADMIN
@ app.route("/formdata")
def formdata():
    return render_template("pages/formdata.html")  # page formdata


@app.route("/editcuaca/<int:id_cuaca>", methods=['GET'])
def editcuaca(id_cuaca):
    # get edit data
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT * FROM master_cuaca WHERE id_cuaca = (%s)", (id_cuaca,))
    data = cursor.fetchall()
    cursor.close()
    # page edit data form
    return render_template("pages/editformdata.html", data=data)


@ app.route("/updatedata/<int:id_cuaca>", methods=['POST'])
def updatedata(id_cuaca):
    # insert data form
    arah_angin = float(request.form['arah_angin'])
    kecepatan_angin = float(request.form['kecepatan_angin'])
    jarak_pandang = float(request.form['jarak_pandang'])
    suhu = float(request.form['suhu'])
    titik_embun = float(request.form['titik_embun'])
    tekanan_udara = float(request.form['tekanan_udara'])
    data = {'arah_angin': [arah_angin],
            'kecepatan_angin': [kecepatan_angin],
            'jarak_pandang': [jarak_pandang],
            'suhu': [suhu],
            'titik_embun': [titik_embun],
            'tekanan_udara': [tekanan_udara]}

    df = pd.DataFrame(data)
    prediction = model.predict(df)
    predicted_index = np.argmax(prediction)
    cuaca = class_names[predicted_index]

    cursor = mysql.connection.cursor()
    cursor.execute(
        """UPDATE master_cuaca SET 
        arah_angin=%s, kecepatan_angin=%s, jarak_pandang=%s, suhu=%s, titik_embun=%s, tekanan_udara=%s, cuaca=%s WHERE id_cuaca = %s""",
        (arah_angin, kecepatan_angin, jarak_pandang, suhu, titik_embun, tekanan_udara, cuaca, id_cuaca))
    mysql.connection.commit()
    cursor.close()
    flash('Data has been updated successfully', 'success')
    # page formdata predict
    return render_template("pages/formdata.html", cuaca=cuaca, arah_angin=arah_angin,
                           kecepatan_angin=kecepatan_angin, jarak_pandang=jarak_pandang,
                           suhu=suhu, titik_embun=titik_embun, tekanan_udara=tekanan_udara)


@ app.route("/predict", methods=['POST'])
def predict():
    # insert data form
    arah_angin = float(request.form['arah_angin'])
    kecepatan_angin = float(request.form['kecepatan_angin'])
    jarak_pandang = float(request.form['jarak_pandang'])
    suhu = float(request.form['suhu'])
    titik_embun = float(request.form['titik_embun'])
    tekanan_udara = float(request.form['tekanan_udara'])
    data = {'arah_angin': [arah_angin],
            'kecepatan_angin': [kecepatan_angin],
            'jarak_pandang': [jarak_pandang],
            'suhu': [suhu],
            'titik_embun': [titik_embun],
            'tekanan_udara': [tekanan_udara]}

    df = pd.DataFrame(data)
    prediction = model.predict(df)
    predicted_index = np.argmax(prediction)
    cuaca = class_names[predicted_index]

    cursor = mysql.connection.cursor()
    cursor.execute(
        """INSERT INTO
        master_cuaca (arah_angin, kecepatan_angin, jarak_pandang,
                      suhu, titik_embun, tekanan_udara, cuaca)
        VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (arah_angin, kecepatan_angin, jarak_pandang, suhu, titik_embun, tekanan_udara, cuaca))
    # db.commit()
    mysql.connection.commit()
    cursor.close()
    flash('Data has been saved successfully', 'success')
    # page formdata predict
    return render_template("pages/formdata.html", cuaca=cuaca, arah_angin=arah_angin,
                           kecepatan_angin=kecepatan_angin, jarak_pandang=jarak_pandang,
                           suhu=suhu, titik_embun=titik_embun, tekanan_udara=tekanan_udara)


if __name__ == "__main__":
    app.run(debug=True, port=8005)
