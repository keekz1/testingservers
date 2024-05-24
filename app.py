from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from send_mail import send_mail

app = Flask(__name__)

ENV = 'prod'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://usrc7298c82cb23af01:bebf8213a01b1f373bb310882b9198d4@pg-204ff88c-0051-4c9d-ae39-434154fc072e.schematogo.us-east-1.antimony.io:17356/stgfc8bd0e91bb7'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Blackweb71323@localhost/Lexus'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Define the Feedback model
class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(200), unique=True)
    dealer = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())

    def __init__(self, customer, dealer, rating, comments):
        self.customer = customer
        self.dealer = dealer
        self.rating = rating
        self.comments = comments

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        customer = request.form['customer']
        dealer = request.form['dealer']
        rating = request.form['rating']
        comments = request.form['comments']

        # Check if required fields are filled
        if customer == '' or dealer == '':
            return render_template('index.html', message='Please enter required fields')

        # Check if feedback from this customer already exists
        if db.session.query(Feedback).filter(Feedback.customer == customer).count() == 0:
            # Create new Feedback instance and add to database
            data = Feedback(customer, dealer, rating, comments)
            db.session.add(data)
            db.session.commit()

            # Send email
            send_mail(customer, dealer, rating, comments)
            return render_template('success.html')
        else:
            return render_template('index.html', message='You have already submitted feedback')

if __name__ == '__main__':
    app.run()
