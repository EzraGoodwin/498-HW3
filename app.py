from flask import Flask, jsonify, request
from pymongo import MongoClient
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern
import os

app = Flask(__name__)

MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://hw3user:p1Z7R7fhuZCF6wcJ@hw3-cluster.mongodb.net/?retryWrites=true&w=majority"
)

client = MongoClient(MONGO_URI)
db = client["ev_db"]
base_collection = db["vehicles"]


def _str_id(inserted_id):
    """Return inserted _id as a plain string."""
    return str(inserted_id)


# Fast but Unsafe Write
@app.route("/insert-fast", methods=["POST"])
def insert_fast():
    record = request.get_json(force=True)
    if not record:
        return jsonify({"error": "Empty or invalid JSON body"}), 400

    col = base_collection.with_options(write_concern=WriteConcern(w=1))
    result = col.insert_one(record)
    return jsonify({"inserted_id": _str_id(result.inserted_id)}), 201


#Highly Durable Write
@app.route("/insert-safe", methods=["POST"])
def insert_safe():
    record = request.get_json(force=True)
    if not record:
        return jsonify({"error": "Empty or invalid JSON body"}), 400

    col = base_collection.with_options(write_concern=WriteConcern(w="majority"))
    result = col.insert_one(record)
    return jsonify({"inserted_id": _str_id(result.inserted_id)}), 201


#Strongly Consistent Read
@app.route("/count-tesla-primary", methods=["GET"])
def count_tesla_primary():
    col = base_collection.with_options(read_preference=ReadPreference.PRIMARY)
    count = col.count_documents({"Make": {"$regex": "^Tesla$", "$options": "i"}})
    return jsonify({"count": count}), 200


# Eventually Consistent Analytical Read
@app.route("/count-bmw-secondary", methods=["GET"])
def count_bmw_secondary():

    col = base_collection.with_options(
        read_preference=ReadPreference.SECONDARY_PREFERRED
    )
    count = col.count_documents({"Make": {"$regex": "^BMW$", "$options": "i"}})
    return jsonify({"count": count}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
