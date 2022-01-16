from src.flask_setup import app

if __name__ == '__main__':
    #app.run(debug=True) # local testing
    app.run(host="0.0.0.0")