from src.flask_setup import app

if __name__ == '__main__':
    #app.run(debug=True) # local testing
    app.run(debug=False, host="0.0.0.0", port=9691)
