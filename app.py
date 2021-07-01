from main import app

app.app_context().push()

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
    # app.run(threaded=True)