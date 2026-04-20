import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

ACTIONS = [
    "view",
    "click",
    "add_to_cart",
    "purchase",
    "search",
    "wishlist",
    "remove_cart",
    "checkout",
]

FUNNELS = [
    ["view", "click", "add_to_cart", "checkout", "purchase"],
    ["search", "view", "click"],
    ["view", "wishlist", "view", "click", "add_to_cart"],
    ["view", "click", "add_to_cart", "remove_cart", "view"],
]


def generate_dataset(output_path: Path, users: int = 500, min_events: int = 20, max_events: int = 80) -> None:
    random.seed(42)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["user_id", "product_id", "action", "timestamp"])
        writer.writeheader()

        for user_id in range(1, users + 1):
            event_count = random.randint(min_events, max_events)
            base_time = datetime.utcnow() - timedelta(days=random.randint(1, 90))
            current_time = base_time
            funnel = random.choice(FUNNELS)

            for idx in range(event_count):
                action = funnel[idx % len(funnel)] if idx < len(funnel) else random.choice(ACTIONS)
                current_time += timedelta(minutes=random.randint(1, 60))
                writer.writerow(
                    {
                        "user_id": user_id,
                        "product_id": random.randint(1, 1500),
                        "action": action,
                        "timestamp": current_time.isoformat(timespec="seconds") + "Z",
                    }
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic user behavior dataset.")
    parser.add_argument("--output", default="data/data_user500.csv")
    parser.add_argument("--users", type=int, default=500)
    parser.add_argument("--min-events", type=int, default=20)
    parser.add_argument("--max-events", type=int, default=80)
    args = parser.parse_args()

    generate_dataset(Path(args.output), args.users, args.min_events, args.max_events)
    print(f"Generated dataset at {args.output}")
