from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import datetime
from database import repository as rep, init_db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin


app = Flask(__name__)
app.secret_key = 'SDKFMQWE7R34F8QFNASDFQ9fdsjkfn3409jreg<>}{)()*&()}'+ str(datetime.now())

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'You must be authorized to view neccesary page'
login_manager.login_message_category = 'error'

connection, cursor = init_db.init_db() # initialized database and apply neccessary migrations
dbase = rep.DB(connection, cursor)

@login_manager.user_loader
def load_user(person_id):
    return UserLogin().FromDB(person_id, dbase)

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        person = dbase.get_person_by_login(request.form['login'])
        if person:
            if check_password_hash(person['password'], request.form['password']):
                remain = True if request.form.get('remain') else False
                login_user(UserLogin().create(person), remember=remain)
                return redirect(request.args.get('next') or url_for('mpage'))
            flash('Incorrect password', 'error')
        else:
            flash('Incorrect login', category='error')
    
    return render_template('authorization.html', dis='disabled')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You signed out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/registration', methods=['GET', 'POST'])
def registr():
    if request.method == 'POST':
        login = request.form['login']
        pswd = generate_password_hash(request.form['password_first'])
        if request.form['password_first'] != request.form['password_second']:
            flash('Passwords are not the same', category='error')
        elif dbase.write_record(table_name='person', person=login, 
                              password=pswd):
            flash('You are registered', category='success')
            return redirect(url_for('login'))
        flash('This login already exist', category='error')
    
    return render_template('registration.html', dis='disabled')

@app.route('/mpage_lim', methods=['POST'])
def mpage_lim():
    if dbase.update_lim(current_user.get_id(), 
                            request.form['type'], request.form['amount']):
        flash('Record was sent', category='success')
    else:
        flash('Limit cannot be updated', 'error')
    return redirect(url_for('mpage'))

@app.route('/home', methods=['GET', 'POST'])
@login_required
def mpage():
    pers = current_user.get_info()
    exp_am = 0
    for dict in dbase.get_records('expense', pers['person_id'], 30):
        exp_am += dict['amount']
    cred_am = 0
    for dict in dbase.get_records('credit', pers['person_id']):
        cred_am += dict['amount']
    inc_am = 0
    for dict in dbase.get_records('income', pers['person_id'], 30):
        inc_am += dict['amount']
    acc_am = 0
    for dict in dbase.get_records('account', pers['person_id']):
        acc_am += dict['amount']
    

    records = [{'cat_name' : 'expense', 'amount': exp_am, 'limit': pers['expense_lim']},
            {'cat_name' : 'credit', 'amount': cred_am, 'limit': pers['credit_lim']},
            {'cat_name' : 'income', 'amount': inc_am, 'limit': 0},
            {'cat_name' : 'account', 'amount': acc_am, 'limit': 0}]

    return render_template('main_page.html', records=records, lnk=0)

@app.route('/acc_parse', methods=['POST'])
def acc_parse():
    if request.form.get('delcheck'):
        if dbase.del_record('account', request.form['amount'], 
                            current_user.get_id(), acc_name=request.form['acc_name']):
            flash('Account has been deleted', 'success')
        else:
            flash("Account cannot be deleted", 'error')
    elif dbase.write_record('account', current_user.get_id(), 
                          amount=request.form['amount'], acc_name=request.form['acc_name']):
        flash('Account was added successfully', 'success')
    else:
        flash('Account cannot be added', 'error')

    return redirect(url_for('acc'))

@app.route('/accounts', methods=['POST', 'GET'])
@login_required
def acc():
    return render_template('accounts.html', 
                           records=dbase.get_records('account', current_user.get_id()), lnk=1)

@app.route('/inc_parse', methods=['POST'])
def inc_parse():
    date = request.form['date']
    amount = int(request.form['amount'])
    category = request.form['type']
    if datetime.strptime(date, "%Y-%m-%d") <= datetime.today():
        if request.form.get('delcheck'): # find out checkbox's condition
            if dbase.del_record('income', amount=amount, 
                                person_id=current_user.get_id(), date=date, category=category):
                flash('Record was deleted', category='success')
            else:
                flash('Wrong record for deleting', category='error')
        else:
            if dbase.write_record(table_name='income', amount=amount, 
                                    person_id=current_user.get_id(), date=date, category=category):
                flash('Record was sent', category='success')
            else:
                flash('Record cannot be inserted', category='error')
    else:
        flash('Date is greater than neccessary', category='error')
    
    return redirect(url_for('inc'))

@app.route('/income', methods=['GET', 'POST'])
@login_required
def inc():
    return render_template('income.html', 
                           records=dbase.get_records('income', current_user.get_id()), lnk=2)

@app.route('/cred_parse', methods=['POST'])
def cred_parse():
    if request.form.get('delcheck'):
        if dbase.del_record('credit', request.form['amount'], 
                            current_user.get_id(), category=request.form['type']):
            flash('Credit has been deleted', 'success')
        else:
            flash("Credit cannot be deleted", 'error')
    elif dbase.write_record('credit', current_user.get_id(), 
                          amount=request.form['amount'], category=request.form['type']):
        flash('Credit was added successfully', 'success')
    else:
        flash('Credit cannot be added', 'error')

    return redirect(url_for('cred'))

@app.route('/credits')
@login_required
def cred():
    return render_template('credits.html', 
                           records=dbase.get_records('credit', current_user.get_id()), lnk=4)

@app.route('/exp_parse', methods=['POST'])
def exp_parse():
    date = request.form['date']
    amount = int(request.form['amount'])
    category = request.form['type']
    if datetime.strptime(date, "%Y-%m-%d") <= datetime.today():
        if request.form.get('delcheck'): # find out checkbox's condition
            if dbase.del_record('expense', amount=amount, 
                                person_id=current_user.get_id(), date=date, category=category):
                flash('Record was deleted', category='success')
            else:
                flash('Wrong record for deleting', category='error')
        else:
            if dbase.write_record(table_name='expense', amount=amount, 
                                    person_id=current_user.get_id(), date=date, category=category):
                flash('Record was sent', category='success')
            else:
                flash('Record cannot be inserted', category='error')
    else:
        flash('Date is greater than neccessary', category='error')
    
    return redirect(url_for('exp'))

@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def exp():
    return render_template('expenses.html', 
                           records=dbase.get_records('expense', current_user.get_id()), lnk=3)

@app.errorhandler(404)
def pageNotFound(error):
    return render_template('404page.html', dis='disabled')

if __name__ == '__main__':
    app.run(debug=False)
    dbase.close()
