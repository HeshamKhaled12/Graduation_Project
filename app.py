from flask import Flask, render_template, url_for, redirect, request, jsonify, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import cv2
import numpy as np
from ultralytics import YOLO
from io import BytesIO
from chatbot import chat_with_drone_bot


app= Flask(__name__)
model_path = "d:\\Project\\test 2-5\\Grad Project\\models\\best (6).pt"
model = YOLO(model_path)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///d:\\Project\\test 2-5\\Grad Project\\database.db'
app.config['SECRET_KEY'] = 'keykeykey'
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={'placeholder': "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={'placeholder': "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():  # Ensure the form has been submitted and is valid
        user = User.query.filter_by(username=form.username.data).first()  # Find the user by username
        if user and bcrypt.check_password_hash(user.password, form.password.data):  # Check if user exists and password matches
            login_user(user)  # Log the user in
            return redirect(url_for('home'))  # Redirect to the dashboard
        else:
            return "Invalid username or password"  # Handle invalid credentials

    return render_template('login.html', form=form)    


@app.route('/home', methods=["GET", "POST"])
@login_required
def home():
    return render_template('home.html')

@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))


    return render_template('register.html', form=form)

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Reading the image
        img = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)

        # Running YOLO model on the image
        results = model(img)  # Perform detection with YOLO

        # Processing results
        result_image = results[0].plot()  # Image with annotations

        # Encode the processed image
        _, img_encoded = cv2.imencode('.jpg', result_image)
        response = img_encoded.tobytes()

        # Create a BytesIO stream to send the image
        image_stream = BytesIO(response)
        
        # Send the image back as a response
        return send_file(image_stream, mimetype='image/jpeg')
    
    # If it's a GET request, return the prediction page
    return render_template('predict.html')


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    bot_response = chat_with_drone_bot(user_message)
    return jsonify({"response": bot_response})


if __name__ == '__main__':
    app.run(debug=True)