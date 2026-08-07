import os, requests, json
from flask import Flask, request, jsonify
from models import SessionLocal, SavedImage, init_db
from flask_cors import CORS
from dotenv import load_dotenv
import redis
import logging
from datetime import datetime
from sqlalchemy import text

# Load environment variables
load_dotenv()  # load .env in dev
init_db()

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://frontend-8a61091935-images-gallery.apps.ir-central1.arvancaas.ir",
            "https://frontend-8a61091935-images-gallery.apps.ir-central1.arvancaas.ir/",  # safe fallback
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration from Environment Variables
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL = int(os.getenv("CACHE_TTL", 300))  # Default 5 minutes

# Initialize Redis client
try:
    redis_client = redis.from_url(REDIS_URL)
    redis_client.ping()  # Test connection
    app.logger.info("Successfully connected to Redis")
except redis.ConnectionError as e:
    app.logger.error(f"Failed to connect to Redis: {e}")
    redis_client = None  # App will work without cache, but log errors

OPENVERSE_API_URL = "https://api.openverse.engineering/v1/images/"

@app.route("/health")
def health():
    """Health check endpoint for load balancers"""
    db_ok = True
    cache_ok = redis_client is not None
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        db_ok = False
        app.logger.error(f"Database health check failed: {e}")

    status = {
        "status": "ok" if (db_ok and cache_ok) else "degraded",
        "db": "ok" if db_ok else "error",
        "cache": "ok" if cache_ok else "error"
    }
    return jsonify(status), 200 if db_ok else 503

@app.route("/api/search")
def search():
    app.logger.info(f"Received search request: {request.url}")
    app.logger.info(f"Headers: {dict(request.headers)}")
    q = request.args.get("q", "").strip().lower()
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "20") 

    if not q:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    # Create a unique cache key for this query and page
    cache_key = f"search:{q}:{page}:{per_page}"

    # Check Redis cache first
    if redis_client:
        try:
            cached_result = redis_client.get(cache_key)
            if cached_result:
                app.logger.info(f"Cache HIT for key: {cache_key}")
                return jsonify(json.loads(cached_result))
        except redis.RedisError as e:
            app.logger.error(f"Redis error on get: {e}")

    # If not in cache, call Openverse API
    params = {"q": q, "page": page, "page_size": per_page}

    try:
        r = requests.get(OPENVERSE_API_URL, params=params, timeout=10)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Openverse API error", "details": str(e)}), 502

    data = r.json()
    # Simplify response for frontend
    results = []
    for item in data.get("results", []):
        # Openverse uses different field names than Unsplash
        results.append({
            "unsplash_id": item.get("id"),
            "thumb": item.get("thumbnail"),
            "full": item.get("url"),
            "alt": item.get("title") or ""
        })

    response_data = {"results": results, "total": data.get("result_count", 0)}

    # Cache the successful response in Redis
    if redis_client:
        try:
            redis_client.setex(cache_key, CACHE_TTL, json.dumps(response_data))
            app.logger.info(f"Cached results for key: {cache_key}")
        except redis.RedisError as e:
            app.logger.error(f"Redis error on setex: {e}")

    return jsonify(response_data)

@app.route("/api/save", methods=["POST"])
def save_image():
    payload = request.json or {}
    unsplash_id = payload.get("unsplash_id")
    thumb = payload.get("thumb")
    full = payload.get("full")
    alt = payload.get("alt", "")

    if not unsplash_id or not thumb or not full:
        return jsonify({"error": "Missing required fields: unsplash_id, thumb, full"}), 400

    db = SessionLocal()
    try:
        # Avoid duplicates by unsplash_id
        existing = db.query(SavedImage).filter_by(unsplash_id=unsplash_id).first()
        if existing:
            return jsonify({"saved": True, "id": existing.id, "message": "Already saved"}), 200

        obj = SavedImage(unsplash_id=unsplash_id, thumb=thumb, full=full, alt=alt)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return jsonify({"saved": True, "id": obj.id}), 201
    except Exception as e:
        db.rollback()
        app.logger.error(f"Error saving image: {e}")
        return jsonify({"error": "Failed to save image"}), 500
    finally:
        db.close()

@app.route("/api/saved")
def list_saved():
    db = SessionLocal()
    try:
        items = db.query(SavedImage).order_by(SavedImage.created_at.desc()).all()
        
        out = []
        for i in items:
            item_data = {
                "id": i.id,
                "unsplash_id": i.unsplash_id,
                "thumb": i.thumb,
                "full": i.full,
                "alt": i.alt,
                "created_at": i.created_at.isoformat()
            }
            out.append(item_data)
            
        return jsonify({"items": out})
    except Exception as e:
        app.logger.error(f"Error fetching saved images: {e}")
        return jsonify({"error": "Failed to fetch saved images"}), 500
    finally:
        db.close()
        
@app.route("/api/saved/<int:image_id>", methods=["DELETE"])
def delete_saved_image(image_id):
    db = SessionLocal()
    try:
        image = db.query(SavedImage).filter(SavedImage.id == image_id).first()
        if not image:
            return jsonify({"error": "Image not found"}), 404
            
        db.delete(image)
        db.commit()
        return jsonify({"message": "Image deleted successfully"}), 200
    except Exception as e:
        db.rollback()
        app.logger.error(f"Error deleting image: {e}")
        return jsonify({"error": "Failed to delete image"}), 500
    finally:
        db.close()

@app.route("/api/test")
def test_endpoint():
    return jsonify({"message": "Backend is working!", "timestamp": datetime.now().isoformat()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
