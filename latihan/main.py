from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

# Untuk membuat secret key untuk ekstra proteksi
app.secret_key = 'your secret key'

# koneksi database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_penjualan'

# Inisialisasi MySQL
mysql = MySQL(app)



@app.route('/login/', methods=['GET', 'POST'])
def login():
    # massange untuk jika dibutuhkan ditampilan awal
    msg = ''
    # mengecek  "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # membuat variables untuk diakses
        username = request.form['username']
        password = request.form['password']
    # mengecek jika ada akun yang sama
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM USER WHERE USERNAME = %s AND PASSWORD = %s', (username, password,))
        # mengambil satu data record dan return result
        account = cursor.fetchone()
        # jika account exists di accounts tabel di luar database
        if account:
            # Membuat session data, bisa di akses ke semua route
            session['loggedin'] = True
            session['nama'] = account['nama']
            session['username'] = account['username']
            # Redirect ke home page
            # return 'Logged in successfully!' 
            # DIGANTI DENGAN DAN LANGSUNG MASUK HOME
            return redirect(url_for('home'))
        else:
            # jika password salah
            msg = 'Incorrect username/password!'
    return render_template('login/index.html', msg=msg)

# LOGOUT
@app.route('/logout')
def logout():
    # Remove session data, Untuk mengelurkan fungsi session / logout data
    session.pop('loggedin', None)
    session.pop('nama', None)
    session.pop('username', None)
    session.pop('nik', None)
    # Redirect to login page
    return redirect(url_for('login'))


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''    # massange untuk jika dibutuhkan ditampilan awal
    if request.method == 'POST':   # mengecek jika "username", "password" and "email" POST requests exist (user submitted form) # and 'id' in request.form and 'nama' in request.form and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        id = request.form['id']   # Create variables for easy access
        nama = request.form['nama']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM USER WHERE USERNAME = % s', (username, ))
        account = cursor.fetchone()
        if account:   #cek kalau akun sudah pernah dipakai
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):  #untuk batasan email
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z]+', nama): #untuk batasan nama
            msg = 'Invalid Name !'
        elif not re.match(r'[A-Za-z0-9]+', username): #untuk batasan username
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not nama:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO USER VALUES (%s, %s, %s, %s, %s )',
                           (id, nama, username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('login/register.html', msg=msg)

    # elif request.method == 'POST':
    #     # Form is empty... (no POST data)
    #     msg = 'Please fill out the form!'
    # # Show registration form with message (if any)
    # return render_template('register.html', msg=msg)

# HOME
@app.route('/home')
def home():
    # Mengecek jika user login masuk ke halaman home
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('login/home.html', nama=session['nama'])
    # jika tidak login masuk ke halaman login awal
    return redirect(url_for('login'))


# PROFILE
@app.route('/profile')
def profile():
    # Mengecek jika user login
    if 'loggedin' in session:
        # select nama untuk mengetahui informasi profile
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM USER WHERE USERNAME = %s',
                       (session['username'],))
        account = cursor.fetchone()
        # jika sudah dapat data masuk ke arah profile dan membawa data user
        return render_template('login/profile.html', account=account)
    # jika user tidak login maka kembali ke tampilan awak 
    return redirect(url_for('login'))


# ---- BARANG ---- #

#  HOME BARANG
@app.route('/barang')
def barang():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM BARANG')
    results = cursor.fetchall()
    return render_template('masterBarang/barang.html', container=results)

# TAMBAH BARANG
@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        # Create variables for easy access
        nama = request.form['nama']
        harga = request.form['harga']
        stok = request.form['stok']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "INSERT INTO BARANG (nama_barang, harga,stok) VALUES (%s, %s, %s)"
        value = (nama, harga, stok)
        cursor.execute(sql, value)
        mysql.connection.commit()
        return redirect(url_for('barang'))
    else:
        # memakai modal di halaman yang sama
        return redirect(url_for('barang'))


#  EDIT BARANG
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        id_barang = request.form['id_barang']
        nama = request.form['nama']
        harga = request.form['harga']
        stok = request.form['stok']
        sql = "UPDATE barang SET nama_barang=%s, harga=%d, stok=%d WHERE id_barang=%s"
        val = (nama, harga, stok, id_barang)
        cursor.execute(sql, val)
        mysql.connection.commit()
        return redirect(url_for('barang'))
    else:
        return redirect(url_for('barang'))

#  HAPUS BARANG
@app.route('/hapus/<id_barang>', methods=['GET', 'POST'])
def hapus(id_barang):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM barang WHERE id_barang=%s', (id_barang,))
    mysql.connection.commit()
    return redirect(url_for('barang'))


# ---- SUPLIER ---- #

#  HOME SUPLIER
@app.route('/suplier')
def suplier():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM SUPPLIER')
    results = cursor.fetchall()
    return render_template('suplier/suplier.html', container=results )

#   TAMBAH SUPPLIER
@app.route('/tambah_Suplier', methods=['GET', 'POST'])
def tambahSuplier():
    if request.method == 'POST':
        # Create variables for easy access
        nama = request.form['nama']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "INSERT INTO SUPPLIER (nama_supplier) VALUES (%s)"
        value = (nama, )
        cursor.execute(sql, value)
        mysql.connection.commit()
        return redirect(url_for('suplier'))
    else:
        # memakai modal di halaman yang sama
        return redirect(url_for('suplier'))


#   EDIT SUPLIER
@app.route('/edit_suplier', methods=['GET', 'POST'])
def editSuplier():
    cursor = mysql.connection.cursor()
    # cursor.execute('SELECT * FROM barang WHERE id_barang=%s', ( id_barang, )) #ini kenapa harus pakai koma
    # data = cursor.fetchone()
    if request.method == 'POST':
        id_suplier = request.form['id_suplier']
        nama = request.form['nama']
        sql = "UPDATE SUPPLIER   SET nama_supplier=%s WHERE id_supplier=%s"
        val = (nama, id_suplier)
        cursor.execute(sql, val)
        mysql.connection.commit()
        return redirect(url_for('suplier'))
    else:
        return redirect(url_for('suplier'))

#  HAPUS SUPLIER
@app.route('/hapusSuplier/<id_suplier>', methods=['GET', 'POST'])
def hapusSuplier(id_suplier):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM SUPPLIER WHERE id_supplier=%s', (id_suplier,))
    mysql.connection.commit()
    return redirect(url_for('suplier'))


#  -------- PEMBELIAN ----------- #
@app.route('/pembelian', methods=['GET', 'POST'])
def pembelian():
    # if 'loggedin' in session:
        # return render_template('suplier/suplier.html', nama=session['nama'])
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM PEMBELIAN')
    results = cursor.fetchall()

    cursor.execute('SELECT * FROM barang')
    barang = cursor.fetchall()

    cursor.execute('SELECT * FROM supplier')
    suplier = cursor.fetchall()
    # return redirect(url_for('dropdown'), container=results)
    return render_template('pembelian/beli.html', container=results, barang=barang, suplier=suplier)



# @app.route('/dropdown', methods=['GET'])
# def dropdown():
#     cursor = mysql.connection.cursor()
#     cursor.execute('SELECT * FROM USER')
#     colours = cursor.fetchall()
#     return render_template('pembelian/beli.html', colours=colours)

if __name__ == "__main__":
    app.run()


if __name__ == "__main__":
    app.run(debug=True)
