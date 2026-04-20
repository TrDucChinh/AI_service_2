def _format_records(intent: str, records):
    if intent == "top_clicked_products":
        return [f"Product {r.get('product_id')}: {r.get('click_count')} clicks" for r in records]
    if intent == "frequent_laptop_buyers":
        return [f"User {r.get('user_id')}: {r.get('purchases')} laptop purchases" for r in records]
    if intent == "user_viewed":
        return [f"Product {r.get('product_id')}: {r.get('views')} views" for r in records]
    return [str(r) for r in records]


def build_prompt(question: str, intent: str, records):
    context_lines = _format_records(intent, records)
    context = "\n".join(context_lines) if context_lines else "No relevant graph records."
    return (
        "You are an e-commerce analyst assistant.\n"
        f"Intent: {intent}\n"
        f"Question: {question}\n"
        f"Graph context:\n{context}\n\n"
        "Answer based only on graph context. If context is empty, say data is insufficient."
    )


def build_context_answer(intent: str, records):
    if not records:
        return {
            "intent": intent,
            "answer": "Khong tim thay du lieu graph phu hop. Hay tiep tuc thu thap hanh vi nguoi dung de cai thien ket qua.",
            "context": [],
        }

    lines = _format_records(intent, records)

    return {"intent": intent, "answer": "\n".join(lines), "context": records}
