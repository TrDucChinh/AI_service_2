# Plan Implementation AI Pipeline cho Hệ thống E‑Commerce (User Behavior → RNN/LSTM/biLSTM → KB Graph → RAG)

## 🎯 Mục tiêu
Triển khai pipeline gồm 4 phần chính:

1. Sinh dataset `data_user500.csv`
2. Train model dự đoán hành vi user bằng:
   - RNN
   - LSTM
   - biLSTM
3. Xây dựng Knowledge Graph bằng Neo4j
4. Triển khai RAG Chatbot dựa trên Knowledge Graph
5. Tích hợp vào hệ thống E‑commerce hiện tại

Đặc biệt:

➡ Model training chạy trên Google Colab
➡ Project local chỉ load best_model

---

# Tổng kiến trúc hệ thống

```
User Behavior Data
        ↓
Sequence Processing
        ↓
Train RNN / LSTM / biLSTM (Colab)
        ↓
Select best_model
        ↓
Export .pt
        ↓
Deploy vào backend
        ↓
Predict behavior realtime
        ↓
Push vào Knowledge Graph
        ↓
RAG Chatbot query graph
```

---

# PHẦN 1 — Sinh dataset data_user500.csv

## Schema dataset

```
user_id
product_id
action
(timestamp)
```

### action gồm:

```
view
click
add_to_cart
purchase
search
wishlist
remove_cart
checkout
```

## Script generate dataset

Folder đề xuất:

```
data_pipeline/
    generate_behavior_dataset.py
```

Dataset output:

```
data/data_user500.csv
```

Logic generate:

- 500 users
- mỗi user 20–80 events
- timestamp sequential
- simulate realistic behavior funnel

Ví dụ pipeline behavior:

```
view → click → add_to_cart → checkout → purchase
```

---

# PHẦN 2 — Training Models trên Google Colab

⚠ Không train local

Train trên Colab rồi export best_model

## Folder structure (Colab)

```
colab_training/
    dataset_loader.py
    preprocessing.py
    rnn_model.py
    lstm_model.py
    bilstm_model.py
    train.py
    evaluate.py
```

---

# Data preprocessing pipeline

Steps:

### Step 1
Encode categorical

```
user_id
product_id
action
```

### Step 2
Sequence window

Example

```
view → click → add_to_cart
predict next action
```

window size:

```
5
```

---

# Model architecture

## Model 1

```
RNN
```

## Model 2

```
LSTM
```

## Model 3

```
biLSTM
```

Loss:

```
CrossEntropyLoss
```

Optimizer:

```
Adam
```

Evaluation metrics:

```
Accuracy
Precision
Recall
F1-score
```

---

# Visualization cần generate

Export plots:

```
training_loss.png
accuracy.png
confusion_matrix.png
model_compare.png
```

---

# Model selection strategy

Chọn best_model theo:

```
Highest F1-score
```

Export:

```
best_model.pt
label_encoder.pkl
config.json
```

Upload vào:

```
project_root/ml_models/
```

---

# PHẦN 3 — Backend inference service

Folder structure:

```
backend/
    ml/
        inference.py
        predictor.py
        loader.py
```

Predict flow:

```
User events
    ↓
Convert sequence
    ↓
Load encoder
    ↓
Load best_model
    ↓
Predict next action
```

Return example:

```
{
  predicted_action: add_to_cart
}
```

---

# PHẦN 4 — Knowledge Graph (Neo4j)

Schema graph

Nodes:

```
User
Product
Action
Session
```

Relationships:

```
(User)-[:VIEWED]->(Product)
(User)-[:CLICKED]->(Product)
(User)-[:ADDED_TO_CART]->(Product)
(User)-[:PURCHASED]->(Product)
```

---

# Neo4j integration service

Folder:

```
backend/kg/
    neo4j_client.py
    graph_builder.py
    queries.py
```

Example query

```
MATCH (u:User)-[:CLICKED]->(p)
RETURN p
LIMIT 10
```

---

# PHẦN 5 — Build RAG Chatbot

Pipeline

```
User question
    ↓
Embedding
    ↓
Query Neo4j
    ↓
Retrieve subgraph
    ↓
Context builder
    ↓
LLM generate answer
```

---

# Suggested tech stack cho RAG

```
Neo4j
LangChain
OpenAI / Gemini
FastAPI
```

---

# Chatbot use cases

Example questions

```
User nào hay mua laptop?
Product nào được click nhiều nhất?
User A đã xem những gì?
```

---

# PHẦN 6 — Integration vào hệ thống E‑commerce hiện tại

Frontend hiển thị

## Feature 1

```
User behavior timeline
```

Example

```
view → click → add_to_cart
```

---

## Feature 2

Realtime prediction

Example

```
Suggested next action:
add_to_cart
```

---

## Feature 3

Chatbot UI riêng

Không dùng ChatGPT UI

Custom:

```
React
Flutter
Android XML
```

---

# PHẦN 7 — Deployment architecture

```
Frontend
    ↓
Backend API
    ↓
ML inference service
    ↓
Neo4j graph DB
    ↓
RAG chatbot service
```

---

# PHẦN 8 — Roadmap implementation theo sprint

## Sprint 1

Generate dataset

Deliverables:

```
data_user500.csv
EDA notebook
```

---

## Sprint 2

Train models trên Colab

Deliverables:

```
RNN
LSTM
biLSTM
metrics compare
best_model.pt
```

---

## Sprint 3

Deploy inference API

Deliverables:

```
/predict-next-action
```

---

## Sprint 4

Build Neo4j Knowledge Graph

Deliverables:

```
Graph schema
Cypher queries
Graph builder service
```

---

## Sprint 5

Build RAG chatbot

Deliverables:

```
Retriever
Prompt template
Graph query adapter
Chat API
```

---

## Sprint 6

Frontend integration

Deliverables:

```
Behavior dashboard
Prediction panel
Chatbot UI
```

---

# PHẦN 9 — Checklist nghiệm thu

Dataset

```
500 users
8 actions
realistic timestamps
```

Models

```
trained
compared
visualized
best_model selected
```

Graph

```
nodes created
relations correct
queries working
```

Chatbot

```
answer đúng theo graph
response realtime
```

Integration

```
prediction realtime
chatbot hoạt động
behavior tracking hiển thị
```

