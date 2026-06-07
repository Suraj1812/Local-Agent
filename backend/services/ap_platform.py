from __future__ import annotations

from math import isclose
from typing import Any, Dict, List


TOLERANCE_AMOUNT = 25.0
TOLERANCE_PERCENT = 0.02


VENDORS = [
    {
        "id": "ven-1001",
        "name": "Northwind Logistics",
        "erp_id": "SAP-V1001",
        "risk": "low",
        "payment_terms": "Net 30",
        "default_gl": "6100 Freight & Logistics",
        "bank_status": "verified",
    },
    {
        "id": "ven-1017",
        "name": "Acme Components",
        "erp_id": "NS-ACME-17",
        "risk": "medium",
        "payment_terms": "Net 45",
        "default_gl": "5200 Raw Materials",
        "bank_status": "verified",
    },
    {
        "id": "ven-1042",
        "name": "Bluepeak Cloud",
        "erp_id": "QBO-BP-42",
        "risk": "low",
        "payment_terms": "Due on receipt",
        "default_gl": "6900 Cloud Infrastructure",
        "bank_status": "verified",
    },
]

PURCHASE_ORDERS = [
    {
        "id": "po-88021",
        "po_number": "PO-88021",
        "vendor_id": "ven-1001",
        "status": "open",
        "currency": "USD",
        "total": 18450.0,
        "lines": [
            {"sku": "FRT-LTL", "description": "LTL freight lanes", "quantity": 30, "unit_price": 615.0}
        ],
    },
    {
        "id": "po-88022",
        "po_number": "PO-88022",
        "vendor_id": "ven-1017",
        "status": "open",
        "currency": "USD",
        "total": 40750.0,
        "lines": [
            {"sku": "CMP-A12", "description": "Controller boards", "quantity": 500, "unit_price": 42.5},
            {"sku": "CMP-B77", "description": "Sensor housings", "quantity": 1000, "unit_price": 19.5},
        ],
    },
    {
        "id": "po-88023",
        "po_number": "PO-88023",
        "vendor_id": "ven-1042",
        "status": "blanket",
        "currency": "USD",
        "total": 12600.0,
        "lines": [
            {"sku": "CLOUD-COMPUTE", "description": "Compute usage", "quantity": 12, "unit_price": 1050.0}
        ],
    },
]

GOODS_RECEIPTS = [
    {"id": "grn-7001", "po_number": "PO-88021", "received_quantity": 30, "status": "received"},
    {"id": "grn-7002", "po_number": "PO-88022", "received_quantity": 1460, "status": "partial"},
    {"id": "grn-7003", "po_number": "PO-88023", "received_quantity": 12, "status": "received"},
]

INVOICES = [
    {
        "id": "inv-90031",
        "invoice_number": "INV-2026-0842",
        "vendor_id": "ven-1001",
        "vendor": "Northwind Logistics",
        "po_number": "PO-88021",
        "currency": "USD",
        "amount": 18450.0,
        "status": "matched",
        "match_type": "3-way",
        "risk": "low",
        "confidence": 0.97,
        "due_date": "2026-06-29",
        "erp": "SAP",
    },
    {
        "id": "inv-90032",
        "invoice_number": "AC-55219",
        "vendor_id": "ven-1017",
        "vendor": "Acme Components",
        "po_number": "PO-88022",
        "currency": "USD",
        "amount": 41720.0,
        "status": "exception",
        "match_type": "3-way",
        "risk": "medium",
        "confidence": 0.81,
        "due_date": "2026-07-12",
        "erp": "NetSuite",
    },
    {
        "id": "inv-90033",
        "invoice_number": "BP-2026-06",
        "vendor_id": "ven-1042",
        "vendor": "Bluepeak Cloud",
        "po_number": "PO-88023",
        "currency": "USD",
        "amount": 12600.0,
        "status": "ready_to_post",
        "match_type": "2-way",
        "risk": "low",
        "confidence": 0.94,
        "due_date": "2026-06-08",
        "erp": "QuickBooks",
    },
]

EXCEPTIONS = [
    {
        "id": "exc-2401",
        "invoice_id": "inv-90032",
        "type": "price_variance",
        "severity": "high",
        "owner": "AP Manager",
        "summary": "Invoice exceeds PO by 2.38% and received quantity is short.",
        "next_action": "Route to procurement owner for variance approval.",
    },
    {
        "id": "exc-2402",
        "invoice_id": "inv-90032",
        "type": "receipt_gap",
        "severity": "medium",
        "owner": "Receiving",
        "summary": "Goods receipt quantity is below invoiced quantity.",
        "next_action": "Request receiving confirmation or vendor credit memo.",
    },
]

JOURNAL_ENTRIES = [
    {
        "id": "je-3001",
        "invoice_id": "inv-90031",
        "status": "posted",
        "erp": "SAP",
        "lines": [
            {"account": "6100", "debit": 18450.0, "credit": 0.0},
            {"account": "2000", "debit": 0.0, "credit": 18450.0},
        ],
    },
    {
        "id": "je-3002",
        "invoice_id": "inv-90033",
        "status": "draft",
        "erp": "QuickBooks",
        "lines": [
            {"account": "6900", "debit": 12600.0, "credit": 0.0},
            {"account": "2000", "debit": 0.0, "credit": 12600.0},
        ],
    },
]

FINANCE_AGENTS = [
    {
        "name": "Finance Agent",
        "status": "online",
        "focus": "Coordinates AP policy, approvals, and close readiness.",
        "last_run": "2 min ago",
    },
    {
        "name": "Invoice Agent",
        "status": "online",
        "focus": "Extracts invoice header, line items, tax, payment terms, and GL hints.",
        "last_run": "4 min ago",
    },
    {
        "name": "Matching Agent",
        "status": "reviewing",
        "focus": "Runs 2-way and 3-way matching against PO and goods receipt records.",
        "last_run": "1 min ago",
    },
    {
        "name": "Exception Agent",
        "status": "online",
        "focus": "Detects variances, duplicates, missing receipts, vendor risk, and policy gaps.",
        "last_run": "1 min ago",
    },
    {
        "name": "Reconciliation Agent",
        "status": "online",
        "focus": "Reconciles AP subledger, accruals, payments, and vendor statements.",
        "last_run": "8 min ago",
    },
    {
        "name": "ERP Integration Agent",
        "status": "online",
        "focus": "Prepares posting payloads for SAP, NetSuite, Dynamics, and QuickBooks.",
        "last_run": "3 min ago",
    },
    {
        "name": "Audit Agent",
        "status": "online",
        "focus": "Creates traceable evidence for every AI and finance workflow decision.",
        "last_run": "30 sec ago",
    },
    {
        "name": "Reporting Agent",
        "status": "online",
        "focus": "Summarizes cash exposure, cycle time, exception backlog, and automation rate.",
        "last_run": "5 min ago",
    },
    {
        "name": "Workflow Agent",
        "status": "online",
        "focus": "Routes approvals using amount, entity, department, and segregation rules.",
        "last_run": "2 min ago",
    },
]


def ap_overview() -> Dict[str, Any]:
    invoice_total = sum(invoice["amount"] for invoice in INVOICES)
    matched = [invoice for invoice in INVOICES if invoice["status"] in {"matched", "ready_to_post"}]
    exceptions = [invoice for invoice in INVOICES if invoice["status"] == "exception"]
    return {
        "metrics": {
            "invoice_volume": len(INVOICES),
            "payable_exposure": invoice_total,
            "straight_through_rate": round(len(matched) / len(INVOICES) * 100, 1),
            "match_accuracy": 94.6,
            "exceptions_open": len(exceptions),
            "avg_cycle_time_hours": 5.8,
            "erp_sync_ready": len([invoice for invoice in INVOICES if invoice["status"] == "ready_to_post"]),
        },
        "systems": ["SAP", "Oracle NetSuite", "Microsoft Dynamics", "QuickBooks"],
        "modules": [
            "Invoice Upload",
            "Invoice OCR",
            "Vendor Management",
            "Purchase Orders",
            "Goods Receipts",
            "Invoice Matching",
            "Exception Center",
            "Approval Workflows",
            "Journal Entries",
            "ERP Sync",
            "Audit Logs",
            "Analytics Dashboard",
            "Agent Monitoring",
        ],
        "invoices": INVOICES,
        "exceptions": EXCEPTIONS,
        "journal_entries": JOURNAL_ENTRIES,
        "agents": FINANCE_AGENTS,
    }


def list_ap_invoices() -> List[Dict[str, Any]]:
    return INVOICES


def list_finance_agents() -> List[Dict[str, Any]]:
    return FINANCE_AGENTS


def _find_po(po_number: str) -> Dict[str, Any] | None:
    return next((po for po in PURCHASE_ORDERS if po["po_number"] == po_number), None)


def _find_grn(po_number: str) -> Dict[str, Any] | None:
    return next((receipt for receipt in GOODS_RECEIPTS if receipt["po_number"] == po_number), None)


def run_matching(payload: Dict[str, Any]) -> Dict[str, Any]:
    po_number = str(payload.get("po_number") or "PO-88022")
    amount = float(payload.get("amount") or 41720.0)
    vendor_id = str(payload.get("vendor_id") or "ven-1017")
    invoice_number = str(payload.get("invoice_number") or "AC-55219")

    po = _find_po(po_number)
    grn = _find_grn(po_number)
    checks = []
    exceptions = []
    score = 100

    if not po:
        return {
            "status": "exception",
            "score": 0,
            "checks": [{"name": "PO exists", "status": "failed"}],
            "exceptions": [{"type": "missing_po", "severity": "critical", "message": "Purchase order not found"}],
        }

    vendor_match = po["vendor_id"] == vendor_id
    checks.append({"name": "Vendor matches PO", "status": "passed" if vendor_match else "failed"})
    if not vendor_match:
        score -= 30
        exceptions.append({"type": "vendor_mismatch", "severity": "critical", "message": "Invoice vendor does not match PO"})

    amount_delta = amount - float(po["total"])
    amount_ok = abs(amount_delta) <= max(TOLERANCE_AMOUNT, float(po["total"]) * TOLERANCE_PERCENT)
    checks.append(
        {
            "name": "Amount within tolerance",
            "status": "passed" if amount_ok else "failed",
            "delta": round(amount_delta, 2),
        }
    )
    if not amount_ok:
        score -= 25
        exceptions.append(
            {
                "type": "price_variance",
                "severity": "high",
                "message": f"Invoice variance is {amount_delta:.2f} against PO total.",
            }
        )

    expected_quantity = sum(float(line["quantity"]) for line in po["lines"])
    received_quantity = float(grn["received_quantity"]) if grn else 0.0
    quantity_ok = grn is not None and (received_quantity >= expected_quantity or isclose(received_quantity, expected_quantity))
    checks.append({"name": "Goods receipt covers invoiced quantity", "status": "passed" if quantity_ok else "failed"})
    if not quantity_ok:
        score -= 20
        exceptions.append(
            {
                "type": "receipt_gap",
                "severity": "medium",
                "message": "Goods receipt is missing or does not cover the expected PO quantity.",
            }
        )

    duplicate = invoice_number in {invoice["invoice_number"] for invoice in INVOICES}
    checks.append({"name": "Duplicate invoice check", "status": "failed" if duplicate else "passed"})
    if duplicate:
        score -= 15
        exceptions.append({"type": "duplicate_invoice", "severity": "high", "message": "Invoice number already exists."})

    status = "auto_approved" if score >= 90 and not exceptions else "exception"
    return {
        "status": status,
        "score": max(score, 0),
        "match_type": "3-way" if grn else "2-way",
        "policy": {
            "amount_tolerance": TOLERANCE_AMOUNT,
            "percent_tolerance": TOLERANCE_PERCENT,
            "segregation_of_duties": "AI can recommend and draft postings; human approval required for exceptions.",
        },
        "checks": checks,
        "exceptions": exceptions,
        "recommendation": "Post to ERP" if status == "auto_approved" else "Route to exception workflow",
    }


def architecture_snapshot() -> Dict[str, Any]:
    return {
        "frontend": ["Next.js 15", "TypeScript", "Tailwind CSS", "shadcn-style primitives", "Vercel"],
        "backend": ["FastAPI", "Python", "SQLAlchemy", "PostgreSQL target", "Redis queue/cache target", "Railway"],
        "ai": ["Ollama", "DeepSeek-R1", "Llama 3", "Qwen", "local extraction and reasoning models"],
        "data_plane": ["Invoices", "Purchase Orders", "Goods Receipts", "Vendor Master", "ERP Ledgers"],
        "control_plane": ["Policy Engine", "Matching Engine", "Agent Orchestrator", "Audit Log", "Approval Workflow"],
        "erp_connectors": ["SAP", "Oracle NetSuite", "Microsoft Dynamics", "QuickBooks"],
    }
