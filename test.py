from db import add_candidate, get_candidates, update_candidate_status

# 1. Add a second candidate
new_candidate = add_candidate(
    full_name="Sarah Connor",
    email="sarah.connor@example.com",
    role="Frontend Developer"
)
print("Added candidate:", new_candidate)

# 2. Update Alex Smith (id=2) to 'interviewing'
updated = update_candidate_status(candidate_id=2, new_status="interviewing")
print("Updated status:", updated)

# 3. List all current candidates
print("\nCurrent Pipeline:")
for c in get_candidates():
    print(f"- [{c['id']}] {c['full_name']} | {c['role']} | Status: {c['status']}")