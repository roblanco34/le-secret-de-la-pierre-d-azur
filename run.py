# dev only, do not use in production

from pierre_azur import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)