ACTION_REL = {
    "view": "VIEWED",
    "click": "CLICKED",
    "add_to_cart": "ADDED_TO_CART",
    "purchase": "PURCHASED",
    "search": "SEARCHED",
    "wishlist": "WISHLISTED",
    "remove_cart": "REMOVED_FROM_CART",
    "checkout": "CHECKED_OUT",
}


def upsert_event_query(action):
    rel = ACTION_REL.get(action, "INTERACTED")
    return f"""
MERGE (u:User {{id: $user_id}})
MERGE (p:Product {{id: $product_id}})
MERGE (a:Action {{name: $action}})
MERGE (s:Session {{id: $session_id}})
SET s.last_seen = $timestamp
MERGE (u)-[:HAS_SESSION]->(s)
MERGE (u)-[r:{rel}]->(p)
SET r.timestamp = $timestamp
MERGE (u)-[:PERFORMED]->(a)
MERGE (s)-[:EVENT]->(a)
"""


TOP_CLICKED_PRODUCTS = """
MATCH (:User)-[r:CLICKED]->(p:Product)
RETURN p.id AS product_id, count(r) AS click_count
ORDER BY click_count DESC
LIMIT $limit
"""

FREQUENT_LAPTOP_BUYERS = """
MATCH (u:User)-[r:PURCHASED]->(p:Product)
WHERE toLower(coalesce(p.category, "laptop")) CONTAINS "laptop"
RETURN u.id AS user_id, count(r) AS purchases
ORDER BY purchases DESC
LIMIT $limit
"""

USER_VIEWED_PRODUCTS = """
MATCH (u:User {id: $user_id})-[:VIEWED]->(p:Product)
RETURN p.id AS product_id, count(*) AS views
ORDER BY views DESC
LIMIT $limit
"""
