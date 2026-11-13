import os
import random
import threading
import time
import requests
from flask import jsonify, request
from kazoo.client import KazooClient
from calculadora_server import app

NODE_ID = int(os.environ.get("NODE_ID", 1))
ZK_HOSTS = os.environ.get("ZK_HOSTS", "zookeeper1:2181,zookeeper2:2181,zookeeper3:2181")
FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))

es_lider = False
lider_actual = None
total_liderazgos_cluster = 0

metricas = {
    "peticiones_totales": 0,
    "peticiones_atendidas": 0,
    "demora_acumulada": 0.0,
    "liderazgos" : 0,
    "porcentaje_liderazgos": 0
}

@app.route("/api/v1/peticion/<int:calculadora_id>/<string:operacion>", methods=["POST"])
def peticion(calculadora_id, operacion):

    global es_lider, lider_actual, metricas

    if not request.is_json:
        return {"error": "La peticion debe ser JSON"}, 415

    data = request.get_json()
    metricas["peticiones_totales"] += 1

    if not es_lider:
        if not lider_actual or lider_actual == f"calc{NODE_ID}":
            return {"error": "Lider no disponible temporalmente para reenvio"}, 538
        
        try:
            url_lider = f"http://{lider_actual}:5000/api/v1/peticion/{calculadora_id}/{operacion}"
            response = requests.post(url_lider, json=data, timeout=5)
            return jsonify(response.json()), response.status_code
        except Exception as e:
            return jsonify({"error": f"Error al redirigir al líder: {str(e)}"}), 500

    tiempo_inicio = time.time()

    nodo_calculadora = (calculadora_id % 5) + 1
    calculadora_host = f"calc{nodo_calculadora}"

    url = f"http://{calculadora_host}:5000/api/v1/calculadoras/{calculadora_id}/{operacion}"

    try:

        requests.post(f"http://{calculadora_host}:5000/api/v1/calculadoras", json={"id": calculadora_id},)

        response = requests.post(url, json=data)
        metricas["peticiones_atendidas"] += 1
        metricas["demora_acumulada"] += time.time() - tiempo_inicio

        print(f"RESPUESTA DE {calculadora_host}\n", flush=True)

        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/peticion/<int:calculadora_id>", methods=["GET"])
def peticion_get(calculadora_id):

    global es_lider, lider_actual, metricas

    metricas["peticiones_totales"] += 1

    if not es_lider:
        if not lider_actual or lider_actual == f"calc{NODE_ID}":
            return {"error": "Lider no disponible temporalmente para reenvio"}, 538       
        try:
            url_lider = f"http://{lider_actual}:5000/api/v1/peticion/{calculadora_id}"
            response = requests.get(url_lider, timeout=5)
            return jsonify(response.json()), response.status_code
        except Exception as e:
            return jsonify({"error": f"Error al redirigir al líder: {str(e)}"}), 500

    tiempo_inicio = time.time()

    nodo_calculadora = (calculadora_id % 5) + 1
    calculadora_host = f"calc{nodo_calculadora}"

    url = f"http://{calculadora_host}:5000/api/v1/calculadoras/{calculadora_id}"

    try:

        response = requests.get(url)
        metricas["peticiones_atendidas"] += 1
        metricas["demora_acumulada"] += time.time() - tiempo_inicio

        print(f"RESPUESTA DE {calculadora_host}\n", flush=True)

        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/peticion/<int:calculadora_id>/reset", methods=["POST"])
def peticion_reset(calculadora_id):

    global es_lider, lider_actual, metricas

    metricas["peticiones_totales"] += 1

    if not es_lider:
        if not lider_actual or lider_actual == f"calc{NODE_ID}":
            return {"error": "Lider no disponible temporalmente para reenvio"}, 538       
        try:
            url_lider = f"http://{lider_actual}:5000/api/v1/peticion/{calculadora_id}/reset"
            response = requests.post(url_lider, timeout=5)
            return jsonify(response.json()), response.status_code
        except Exception as e:
            return jsonify({"error": f"Error al redirigir al líder: {str(e)}"}), 500

    tiempo_inicio = time.time()

    nodo_calculadora = (calculadora_id % 5) + 1
    calculadora_host = f"calc{nodo_calculadora}"

    url = f"http://{calculadora_host}:5000/api/v1/calculadoras/{calculadora_id}/reset"

    try:

        requests.post(f"http://{calculadora_host}:5000/api/v1/calculadoras", json={"id": calculadora_id},)
        
        response = requests.post(url)
        metricas["peticiones_atendidas"] += 1
        metricas["demora_acumulada"] += time.time() - tiempo_inicio

        print(f"RESPUESTA DE {calculadora_host}\n", flush=True)

        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/metricas", methods=["GET"])
def get_metricas():
    global es_lider, metricas
    return jsonify({"node_id": NODE_ID, "es_lider": es_lider, "metricas": metricas}), 200

def bucle_zookeeper():

    global es_lider, lider_actual, metricas, total_liderazgos_cluster

    time.sleep(10)

    def mi_funcion_watcher(event):
        pass

    while True:
        zk = None
        try:
            zk = KazooClient(hosts=ZK_HOSTS, timeout=60)
            zk.start()

            zk.ensure_path("/eleccion")

            mi_nombre_host = f"calc{NODE_ID}"
            node_path = zk.create("/eleccion/candidato_", value=mi_nombre_host.encode(), ephemeral=True, sequence=True)

            ultimo_lider = None

            while True:
                children = zk.get_children("/eleccion")
                children.sort()

                if children:
                    data_lider, _ = zk.get(f"/eleccion/{children[0]}")
                    lider_actual = data_lider.decode()

                    if lider_actual != ultimo_lider:
                        ultimo_lider = lider_actual
                        total_liderazgos_cluster += 1

                if node_path.endswith(children[0]):
                    
                    if not es_lider:
                        es_lider = True
                        metricas["liderazgos"] += 1
                        print(f"[NODO {NODE_ID}] ¡SOY EL LÍDER!", flush=True)

                    if total_liderazgos_cluster > 0:
                        metricas["porcentaje_liderazgos"] = round((metricas["liderazgos"] / total_liderazgos_cluster) * 100, 2)
                    else:
                        metricas["porcentaje_liderazgos"] = 0.0
                    
                    time.sleep(random.randint(15, 30))

                    print(f"[NODO {NODE_ID}] ¡AUTODESTRUCCIÓN DEL LÍDER!", flush=True)

                    zk.stop()
                    es_lider = False

                    time.sleep(random.randint(5, 10))

                    zk.start()

                    zk.ensure_path("/eleccion")
                    node_path = zk.create("/eleccion/candidato_", value=mi_nombre_host.encode(), ephemeral=True, sequence=True)

                else:
                    es_lider = False

                    if total_liderazgos_cluster > 0:
                        metricas["porcentaje_liderazgos"] = round((metricas["liderazgos"] / total_liderazgos_cluster) * 100, 2)
                    else:
                        metricas["porcentaje_liderazgos"] = 0.0

                    idx = children.index(node_path.split("/")[-1])
                    predecesor = children[idx - 1]
                    zk.exists(f"/eleccion/{predecesor}", watch=mi_funcion_watcher)
                    time.sleep(5)
            
        except Exception as e:
            print(F"[NODO {NODE_ID}] Error en conexión Zookeeper: {e}")
            es_lider = False
            if zk:
                try:
                    zk.stop()
                except:
                    pass
            time.sleep(5)


if __name__ == "__main__":
    t = threading.Thread(target=bucle_zookeeper, daemon=True)
    t.start()

    app.run(host="0.0.0.0", port=FLASK_PORT)