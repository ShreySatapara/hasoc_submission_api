from app import app

@app.route('/')
def test2():
    return '<h1>server is running</h1>'


@app.route('/dashboard')
def test():
    return 'dashboard test'
