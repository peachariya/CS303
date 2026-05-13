"""
บริการวิเคราะห์เครือข่ายบัญชีม้า (Money Mule Network Analysis)
ใช้ NetworkX สร้างกราฟทิศทาง (Directed Graph) และตรวจจับบัญชีที่เป็นศูนย์กลาง
"""

from typing import List
from collections import defaultdict
import networkx as nx
from app.models.schemas import Transaction, NodeInfo, EdgeInfo, GraphAnalyzeResponse


# -------------------------------------------------------
# Thresholds สำหรับการตรวจจับบัญชีม้า
# -------------------------------------------------------
HUB_DEGREE_THRESHOLD = 3        # รับโอนจาก >= 3 บัญชี และโอนออกหลายบัญชี
RAPID_PASSTHROUGH_RATIO = 0.80  # โอนออกมากกว่า 80% ของที่รับมา = ผ่านทาง
MIN_TRANSACTION_FLAG = 3        # ต้องมีธุรกรรม >= 3 ครั้ง ถึงจะ flag


def build_graph(transactions: List[Transaction]) -> nx.DiGraph:
    """สร้าง Directed Graph จาก transaction list"""
    G = nx.DiGraph()

    for tx in transactions:
        src = tx.from_account
        dst = tx.to_account
        amt = tx.amount
        ts  = tx.timestamp

        G.add_edge(src, dst, amount=amt, timestamp=ts)

        # สะสม attributes บน node
        for node in [src, dst]:
            if node not in G.nodes:
                G.add_node(node)
            if "total_received" not in G.nodes[node]:
                G.nodes[node]["total_received"] = 0.0
                G.nodes[node]["total_sent"] = 0.0
                G.nodes[node]["tx_count"] = 0

        G.nodes[dst]["total_received"] = G.nodes[dst].get("total_received", 0) + amt
        G.nodes[src]["total_sent"]     = G.nodes[src].get("total_sent", 0) + amt
        G.nodes[src]["tx_count"]       = G.nodes[src].get("tx_count", 0) + 1
        G.nodes[dst]["tx_count"]       = G.nodes[dst].get("tx_count", 0) + 1

    return G


def compute_node_risk(G: nx.DiGraph, node: str) -> float:
    """คำนวณ risk score ของแต่ละ node"""
    data = G.nodes[node]
    score = 0.0

    in_deg  = G.in_degree(node)   # จำนวนบัญชีที่โอนเข้า
    out_deg = G.out_degree(node)  # จำนวนบัญชีที่โอนออก
    received = data.get("total_received", 0)
    sent     = data.get("total_sent", 0)
    tx_count = data.get("tx_count", 0)

    # 1. รับเงินจากหลายแหล่งและโอนออกหลายที่ (Hub pattern)
    if in_deg >= HUB_DEGREE_THRESHOLD and out_deg >= 2:
        score += 0.40

    # 2. Rapid passthrough — รับมาแล้วโอนออกเกือบหมด
    if received > 0:
        passthrough_ratio = sent / received
        if passthrough_ratio >= RAPID_PASSTHROUGH_RATIO:
            score += 0.35

    # 3. ธุรกรรมถี่ผิดปกติ
    if tx_count >= 10:
        score += 0.15
    elif tx_count >= 5:
        score += 0.08

    # 4. รับเงินแล้วไม่มีประวัติโอนออก (ปลายทางสุดท้าย = น่าสนใจ)
    if received > 0 and sent == 0 and in_deg >= 2:
        score += 0.20

    return min(score, 1.0)


def detect_mule_accounts(G: nx.DiGraph) -> tuple[list, list]:
    """
    ตรวจจับบัญชีม้าและ hub accounts
    คืน: (suspected_mules, hub_accounts)
    """
    suspected_mules = []
    hub_accounts    = []

    for node in G.nodes:
        data = G.nodes[node]
        in_deg  = G.in_degree(node)
        out_deg = G.out_degree(node)
        received = data.get("total_received", 0)
        sent     = data.get("total_sent", 0)
        tx_count = data.get("tx_count", 0)

        if tx_count < MIN_TRANSACTION_FLAG:
            continue

        # Hub: รับจากหลายบัญชี + โอนออกหลายบัญชี
        if in_deg >= HUB_DEGREE_THRESHOLD and out_deg >= 2:
            hub_accounts.append(node)

        # Mule: passthrough สูง หรือเป็น hub
        if received > 0:
            ratio = sent / received
            if ratio >= RAPID_PASSTHROUGH_RATIO or node in hub_accounts:
                suspected_mules.append(node)

    return list(set(suspected_mules)), list(set(hub_accounts))


def analyze_graph(transactions: List[Transaction]) -> GraphAnalyzeResponse:
    """วิเคราะห์เครือข่ายธุรกรรมและคืนผลลัพธ์สำหรับ Frontend"""
    G = build_graph(transactions)
    suspected_mules, hub_accounts = detect_mule_accounts(G)

    nodes = []
    for node in G.nodes:
        data = G.nodes[node]
        risk = compute_node_risk(G, node)
        nodes.append(NodeInfo(
            id=node,
            risk_score=round(risk, 3),
            total_received=round(data.get("total_received", 0), 2),
            total_sent=round(data.get("total_sent", 0), 2),
            transaction_count=data.get("tx_count", 0),
            is_hub=(node in hub_accounts),
        ))

    edges = []
    for src, dst, edge_data in G.edges(data=True):
        edges.append(EdgeInfo(
            source=src,
            target=dst,
            amount=edge_data.get("amount", 0),
            timestamp=edge_data.get("timestamp", ""),
        ))

    return GraphAnalyzeResponse(
        nodes=nodes,
        edges=edges,
        suspected_mule_accounts=suspected_mules,
        hub_accounts=hub_accounts,
    )
