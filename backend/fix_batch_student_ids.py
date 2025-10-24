#!/usr/bin/env python3
"""
Fix all batch student_ids arrays to match student membership
"""
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db
from bson import ObjectId

def print_batch_report(bid, batch, correct_ids, old_ids):
    print(f"Batch {bid}: {batch.get('name','')}\n  Correct students: {len(correct_ids)}  |  Was: {len(old_ids)}")
    added = set(correct_ids) - set(old_ids)
    removed = set(old_ids) - set(correct_ids)
    if added:
        print(f"    Added: {added}")
    if removed:
        print(f"    Removed: {removed}")

async def fix_batch_student_ids():
    await init_db()
    db = await get_db()

    batches = await db.batches.find({}).to_list(length=None)
    all_students = await db.users.find({"role":"student"}).to_list(length=None)

    batch_id_to_students = {}
    for student in all_students:
        bid = student.get("batch_id")
        if bid:
            bid_str = str(bid)
            sid_str = str(student["_id"])
            batch_id_to_students.setdefault(bid_str, []).append(sid_str)

    for batch in batches:
        bid = str(batch["_id"])
        correct_ids = batch_id_to_students.get(bid, [])
        old_ids = batch.get("student_ids",[])
        # Set the array to exactly the correct set
        await db.batches.update_one({"_id":batch["_id"]}, {"$set":{"student_ids":correct_ids}})
        print_batch_report(bid, batch, correct_ids, old_ids)
    print(f"DONE: Synced all batches.")

if __name__ == "__main__":
    asyncio.run(fix_batch_student_ids())
