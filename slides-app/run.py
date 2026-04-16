from app import create_app
from random import randint
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=randint(5000, 9999))
