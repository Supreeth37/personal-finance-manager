password = request.form['password']
confirm = request.form['confirm_password']
if password != confirm:
    flash("Passwords do not match!", "danger")
    return redirect(url_for('register'))
