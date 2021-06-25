from website import create_app

app = create_app("prod")

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
    # app.run(threaded=True)