"""MongoDB connection and collection accessors and in-memory mock fallback."""
import logging
import os
from typing import Optional, Any, Dict

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from config.settings import MONGODB_URI, MONGODB_DB_NAME

logger = logging.getLogger(__name__)

_client: Optional[MongoClient] = None
_db: Optional[Database] = None
_use_mock: Optional[bool] = None
_mock_collections: Dict[str, Any] = {}


class MockCollection:
    """In-memory fallback database collection matching pymongo signatures."""
    def __init__(self, name: str):
        self.name = name
        self.documents: Dict[str, Dict[str, Any]] = {}

    def insert_one(self, doc: dict) -> Any:
        from bson import ObjectId
        doc_copy = doc.copy()
        if "_id" not in doc_copy or doc_copy["_id"] is None:
            doc_copy["_id"] = ObjectId()
        doc["_id"] = doc_copy["_id"]
        
        self.documents[str(doc_copy["_id"])] = doc_copy
        
        class InsertOneResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        return InsertOneResult(doc_copy["_id"])

    def find_one(self, query: dict) -> Optional[dict]:
        from bson import ObjectId
        for doc in self.documents.values():
            match = True
            for k, v in query.items():
                if k == "_id":
                    val_str = str(v) if isinstance(v, ObjectId) else v
                    doc_val_str = str(doc.get("_id"))
                    if doc_val_str != val_str:
                        match = False
                        break
                elif doc.get(k) != v:
                    match = False
                    break
            if match:
                return doc.copy()
        return None

    def find(self, query: dict = None) -> Any:
        query = query or {}
        from bson import ObjectId
        results = []
        for doc in self.documents.values():
            match = True
            for k, v in query.items():
                if k == "_id":
                    val_str = str(v) if isinstance(v, ObjectId) else v
                    doc_val_str = str(doc.get("_id"))
                    if doc_val_str != val_str:
                        match = False
                        break
                elif doc.get(k) != v:
                    match = False
                    break
            if match:
                results.append(doc.copy())

        class MockCursor:
            def __init__(self, items):
                self.items = items
            def sort(self, key, direction=-1):
                try:
                    self.items.sort(key=lambda x: x.get(key), reverse=(direction == -1))
                except Exception:
                    pass
                return self
            def limit(self, count):
                self.items = self.items[:count]
                return self
            def __iter__(self):
                return iter(self.items)
        return MockCursor(results)

    def update_one(self, query: dict, update: dict) -> Any:
        from bson import ObjectId
        doc = self.find_one(query)
        modified_count = 0
        if doc:
            doc_id_str = str(doc["_id"])
            actual_doc = self.documents[doc_id_str]
            if "$set" in update:
                for k, v in update["$set"].items():
                    actual_doc[k] = v
                modified_count = 1
        
        class UpdateResult:
            def __init__(self, modified_count):
                self.modified_count = modified_count
        return UpdateResult(modified_count)


def get_client() -> MongoClient:
    """Return singleton MongoDB client."""
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
    return _client


def get_db() -> Database:
    """Return singleton database instance."""
    global _db
    if _db is None:
        _db = get_client()[MONGODB_DB_NAME]
    return _db


def get_collection(name: str) -> Any:
    """Get a named collection with automatic in-memory fallback."""
    global _use_mock
    if _use_mock is None:
        if check_connection():
            _use_mock = False
        else:
            logger.warning(
                "Starting in Offline/Mock mode. Data will be saved in-memory and "
                "will reset when the server restarts."
            )
            _use_mock = True

    if _use_mock:
        if name not in _mock_collections:
            _mock_collections[name] = MockCollection(name)
        return _mock_collections[name]
    
    return get_db()[name]


def check_connection() -> bool:
    """Verify MongoDB connectivity."""
    # If URI is default localhost/unset, immediately use mock without network delay
    if not MONGODB_URI or "localhost" in MONGODB_URI or "127.0.0.1" in MONGODB_URI:
        logger.info("Localhost/unset MongoDB URI detected; using in-memory database mock.")
        return False

    try:
        get_client().admin.command("ping")
        return True
    except Exception as exc:
        logger.warning("MongoDB connection failed: %s", exc)
        return False


# Collection names
COLLECTIONS = {
    "users": "users",
    "resumes": "resumes",
    "job_descriptions": "job_descriptions",
    "analyses": "analyses",
    "interview_preparations": "interview_preparations",
    "roadmaps": "roadmaps",
}
