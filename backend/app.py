from flask import Flask, jsonify, request, render_template

from db import init_db
import tasks

app = Flask(__name__)
init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health_check():
    return jsonify({
        "service": "Long Running Tasks API",
        "status": "ok",
        "version": "1.0.0"
    }), 200

@app.route("/tasks", methods=["GET"])
def list_tasks():
    status = request.args.get("status")
    all_tasks = tasks.get_all_tasks()
    if status:
        all_tasks = [t for t in all_tasks if t["status"] == status]
    return jsonify([{"task_id": t["id"], "status": t["status"]} for t in all_tasks])

@app.route("/tasks", methods=["POST"])
def new_task():
    task_id = tasks.create_task()
    return jsonify({"task_id": task_id}), 201

@app.route("/tasks/<task_id>/status", methods=["GET"])
def task_status(task_id):
    task = tasks.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"task_id": task["id"], "status": task["status"]})

@app.route("/tasks/<task_id>/result", methods=["GET"])
def task_result(task_id):
    task = tasks.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    response = {"task_id": task["id"], "status": task["status"]}

    if task["status"] == tasks.TaskStatus.SUCCESS:
        response["result"] = task["result"]
    elif task["status"] == tasks.TaskStatus.FAILURE:
        response["error"] = task["result"]
    elif task["status"] == tasks.TaskStatus.CANCELLED:
        response["error"] = "Task was cancelled"

    return jsonify(response)

@app.route("/tasks/<task_id>/status", methods=["PATCH"])
def cancel_task(task_id): # only cancellation is allowed currently
    success = tasks.cancel_task(task_id)
    if not success:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"task_id": task_id, "status": "CANCELLED"}), 200

@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    success = tasks.delete_task(task_id)
    if not success:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"task_id": task_id}), 200