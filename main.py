from cProfile import label

from flask import Flask, render_template
from flask_wtf import FlaskForm
from  wtforms import FloatField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

app = Flask(__name__)

class Base(DeclarativeBase):
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///countries.db"

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Country(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    info: Mapped[str] = mapped_column(String(250))

    def __repr__(self):
        return f'<Country {self.name}>'


app.secret_key = "secret_key"

with app.app_context():
    db.create_all()

with app.app_context():
    names_result = db.session.execute(db.select(Country.name).order_by(Country.name))
    all_names = names_result.scalars().all()

all_names.insert(0, "-- No Country Selected --")


class PriceForm(FlaskForm):
    price = FloatField(label="Price of the meal: ", validators=[DataRequired()])
    tip = FloatField(label="Tip %: ", validators=[DataRequired()])
    count = SubmitField(label="Count!")

class CountryForm(FlaskForm):
    country = SelectField(
        label="Country: ", choices=all_names, render_kw={"style": "width: 30ch"})
    check = SubmitField(label="Check")

def get_country_info(country_name):
    if country_name != "-- No Country Selected --":
        with app.app_context():
            country = db.session.execute(db.select(Country).where(Country.name == country_name)).scalar()
            country = country.__dict__
            return country["info"]
    else:
        return ""

@app.route('/', methods=["GET", "POST"])
def home():
    tip = ""
    country_info = ""
    price_form = PriceForm()
    country_form = CountryForm()
    if price_form.validate_on_submit():
        tip = price_form.price.data * 0.01 * price_form.tip.data
    if country_form.validate_on_submit():
        country_info = get_country_info(country_form.country.data)

    return render_template("index.html", tip=tip, price_form=price_form, country_form=country_form,
                           country_info=country_info)


if __name__ == "__main__":
    app.run(debug=True)