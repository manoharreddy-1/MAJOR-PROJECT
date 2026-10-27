"""Tests for MockCollection fallback database."""
import pytest
from bson import ObjectId
from database.mongodb import MockCollection


class TestMockCollection:
    def test_insert_and_find_one(self):
        coll = MockCollection("test")
        doc = {"name": "Test User", "role": "Developer"}
        
        result = coll.insert_one(doc)
        assert isinstance(result.inserted_id, ObjectId)
        assert "_id" in doc
        assert doc["_id"] == result.inserted_id
        
        found = coll.find_one({"_id": doc["_id"]})
        assert found is not None
        assert found["name"] == "Test User"
        assert found["role"] == "Developer"

    def test_find_multiple(self):
        coll = MockCollection("test")
        coll.insert_one({"role": "ML Engineer", "created_at": 10})
        coll.insert_one({"role": "ML Engineer", "created_at": 20})
        coll.insert_one({"role": "Backend Developer", "created_at": 30})
        
        # Find matching
        cursor = coll.find({"role": "ML Engineer"})
        items = list(cursor)
        assert len(items) == 2
        
        # Sorting
        sorted_cursor = coll.find({"role": "ML Engineer"}).sort("created_at", -1)
        sorted_items = list(sorted_cursor)
        assert sorted_items[0]["created_at"] == 20
        assert sorted_items[1]["created_at"] == 10
        
        # Limiting
        limited_cursor = coll.find({"role": "ML Engineer"}).sort("created_at", 1).limit(1)
        limited_items = list(limited_cursor)
        assert len(limited_items) == 1
        assert limited_items[0]["created_at"] == 10

    def test_update_one(self):
        coll = MockCollection("test")
        doc = {"title": "Junior Developer", "skills": ["Python"]}
        result = coll.insert_one(doc)
        
        update_result = coll.update_one(
            {"_id": result.inserted_id},
            {"$set": {"title": "Senior Developer", "skills": ["Python", "Docker"]}}
        )
        
        assert update_result.modified_count == 1
        
        updated = coll.find_one({"_id": result.inserted_id})
        assert updated["title"] == "Senior Developer"
        assert "Docker" in updated["skills"]
