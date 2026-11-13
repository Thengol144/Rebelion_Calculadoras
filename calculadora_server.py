from flask import Flask, request, jsonify
import math
import statistics

app = Flask(__name__)

# Formato de calculadora = {"id": identificador, "valor": valor_numerico}
calculadoras = {}


@app.route("/api/v1/calculadoras", methods=["POST"])
def add_calculadora():    

    if not request.is_json:
        return {"error": "La peticion debe ser JSON"}, 415

    data = request.get_json()

    if "id" not in data or not isinstance(data["id"], int):
        return {"error": "Falta el campo 'id' o no es un numero valido"}, 400

    if data["id"] not in calculadoras:
        calculadoras[data["id"]] = {"id": data["id"], "valor": 0}
        return calculadoras[data["id"]], 201

    return jsonify(calculadoras[data["id"]]), 200


@app.route("/api/v1/calculadoras/<int:id>", methods=["GET"])
def get_calculadora(id):

    if id in calculadoras:
        return jsonify(calculadoras[id]), 200
    return {"error": "Calculadora no encontrada"}, 404


@app.route("/api/v1/calculadoras/<int:id>/add", methods=["POST"])
def add(id):

    if id not in calculadoras:
        return {"error": "Calculadora no encontrada"}, 404

    if not request.is_json:
        return {"error": "La peticion debe ser JSON"}, 415

    data = request.get_json()

    if "valor" not in data or not isinstance(data["valor"], (int, float)):
        return {"error": "Falta el campo 'valor' o no es un numero valido"}, 400

    calculadoras[id]["valor"] += data["valor"]

    return jsonify({"op": "add", "valor": calculadoras[id]["valor"]}), 200


@app.route("/api/v1/calculadoras/<int:id>/sub", methods=["POST"])
def sub(id):

    if id not in calculadoras:
        return {"error": "Calculadora no encontrada"}, 404

    if not request.is_json:
        return {"error": "La peticion debe ser JSON"}, 415

    data = request.get_json()

    if "valor" not in data or not isinstance(data["valor"], (int, float)):
        return {"error": "Falta el campo 'valor' o no es un numero valido"}, 400

    calculadoras[id]["valor"] -= data["valor"]

    return jsonify({"op": "sub", "valor": calculadoras[id]["valor"]}), 200


@app.route("/api/v1/calculadoras/<int:id>/div", methods=["POST"])
def div(id):

    if id not in calculadoras:
        return {"error": "Calculadora no encontrada"}, 404

    if not request.is_json:
        return {"error": "La peticion debe ser JSON"}, 415

    data = request.get_json()

    if "valor" not in data or not isinstance(data["valor"], (int, float)):
        return {"error": "Falta el campo 'valor' o no es un numero valido"}, 400

    if data["valor"] == 0:
        return {"error": "No se puede dividir entre cero"}, 400

       
    calculadoras[id]["valor"] /= data["valor"]
    

    return jsonify({"op": "div", "valor": calculadoras[id]["valor"]}), 200


@app.route("/api/v1/calculadoras/<int:id>/mult", methods=["POST"])
def mult(id):

    if id not in calculadoras:
        return {"error": "Calculadora no encontrada"}, 404

    if not request.is_json:
        return {"error": "La peticion debe ser JSON"}, 415

    data = request.get_json()

    if "valor" not in data or not isinstance(data["valor"], (int, float)):
        return {"error": "Falta el campo 'valor' o no es un numero valido"}, 400

    calculadoras[id]["valor"] *= data["valor"]

    return jsonify({"op": "mult", "valor": calculadoras[id]["valor"]}), 200    


@app.route("/api/v1/calculadoras/<int:id>/sqrt", methods=["POST"])
def sqrt(id):

    if id not in calculadoras:
        return {"error": "Calculadora no encontrada"}, 404

    if calculadoras[id]["valor"] < 0:
            return {"error": "No se puede calcular la raiz cuadrada de un numero negativo"}, 400
    
    calculadoras[id]["valor"] = math.sqrt(calculadoras[id]["valor"])

    return jsonify({"op": "sqrt", "valor": calculadoras[id]["valor"]}), 200  


@app.route("/api/v1/calculadoras/<int:id>/mean", methods=["POST"])
def mean(id):

    if id not in calculadoras:
        return {"error": "Calculadora no encontrada"}, 404
    
    if not request.is_json:
        return {"error": "La peticion debe ser JSON"}, 415 

    data = request.get_json()

    if "valores" not in data or not isinstance(data["valores"], list) or not all(isinstance(x, (int, float)) for x in data["valores"]):
        return {"error": "Falta el campo 'valores' o no son numeros validos"}, 400

    calculadoras[id]["valor"] = statistics.mean(data["valores"])

    return jsonify({"op": "mean", "valor": calculadoras[id]["valor"]}), 200


@app.route("/api/v1/calculadoras/<int:id>/std", methods=["POST"])
def std(id):

    if id not in calculadoras:
        return {"error": "Calculadora no encontrada"}, 404    

    if not request.is_json:
        return {"error": "La peticion debe ser JSON"}, 415 

    data = request.get_json()

    if "valores" not in data or not isinstance(data["valores"], list) or not all(isinstance(x, (int, float)) for x in data["valores"]):
        return {"error": "Falta el campo 'valores' o no son numeros validos"}, 400

    calculadoras[id]["valor"] = statistics.stdev(data["valores"])

    return jsonify({"op": "std", "valor": calculadoras[id]["valor"]}), 200   


@app.route("/api/v1/calculadoras/<int:id>/reset", methods=["POST"])
def reset(id):
  
    if id not in calculadoras:
        return {"error": "Calculadora no encontrada"}, 404

    calculadoras[id]["valor"] = 0
    return jsonify({"op": "reset", "valor": calculadoras[id]["valor"]}), 200
