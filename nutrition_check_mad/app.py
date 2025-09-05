from flask import Flask, render_template, request
from services.openfood_client import search_product, get_product

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form.get("product_name")
        results = search_product(query)
        return render_template("results.html", query=query, results=results)
    return render_template("index.html")


@app.route("/product/<barcode>")
def product_detail(barcode):
    product = get_product(barcode)
    return render_template("product.html", product=product)


if __name__ == "__main__":
    app.run(debug=True)
