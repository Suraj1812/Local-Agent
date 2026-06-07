from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, default="Local User")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(160), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    messages = relationship("Message", back_populates="conversation", cascade="all, delete")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    conversation = relationship("Conversation", back_populates="messages")


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(32), nullable=False)
    key = Column(String(220), nullable=False)
    value = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    goal = Column(Text, nullable=False)
    title = Column(String(260), nullable=False)
    priority = Column(String(32), nullable=False, default="medium")
    status = Column(String(32), nullable=False, default="pending")
    result = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    level = Column(String(32), nullable=False, default="info")
    action = Column(String(120), nullable=False)
    detail = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(260), nullable=False)
    mime_type = Column(String(120), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AppSetting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, default=1)
    model = Column(String(120), nullable=False, default="llama3")
    temperature = Column(Float, nullable=False, default=0.4)
    memory_limit = Column(Integer, nullable=False, default=20)
    theme = Column(String(32), nullable=False, default="light")
    tools_enabled_json = Column(Text, nullable=False, default="{}")
    agent_config_json = Column(Text, nullable=False, default="{}")
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False)
    erp_system = Column(String(80), nullable=False, default="NetSuite")
    base_currency = Column(String(8), nullable=False, default="USD")
    policy_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(180), nullable=False)
    erp_vendor_id = Column(String(120), nullable=False)
    tax_id = Column(String(80), nullable=True)
    payment_terms = Column(String(80), nullable=False, default="Net 30")
    default_gl_account = Column(String(80), nullable=True)
    bank_fingerprint = Column(String(160), nullable=True)
    risk_level = Column(String(32), nullable=False, default="low")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    po_number = Column(String(80), nullable=False, index=True)
    status = Column(String(40), nullable=False, default="open")
    currency = Column(String(8), nullable=False, default="USD")
    total_amount = Column(Float, nullable=False, default=0)
    lines_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class GoodsReceipt(Base):
    __tablename__ = "goods_receipts"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    receipt_number = Column(String(80), nullable=False, index=True)
    status = Column(String(40), nullable=False, default="received")
    received_quantity = Column(Float, nullable=False, default=0)
    lines_json = Column(Text, nullable=False, default="[]")
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Invoice(Base):
    __tablename__ = "ap_invoices"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True)
    invoice_number = Column(String(120), nullable=False, index=True)
    status = Column(String(40), nullable=False, default="received")
    currency = Column(String(8), nullable=False, default="USD")
    subtotal = Column(Float, nullable=False, default=0)
    tax_amount = Column(Float, nullable=False, default=0)
    total_amount = Column(Float, nullable=False, default=0)
    due_date = Column(DateTime(timezone=True), nullable=True)
    extraction_json = Column(Text, nullable=False, default="{}")
    lines_json = Column(Text, nullable=False, default="[]")
    confidence = Column(Float, nullable=False, default=0)
    duplicate_hash = Column(String(160), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class MatchingResult(Base):
    __tablename__ = "matching_results"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("ap_invoices.id"), nullable=False)
    match_type = Column(String(40), nullable=False)
    status = Column(String(40), nullable=False)
    score = Column(Float, nullable=False, default=0)
    checks_json = Column(Text, nullable=False, default="[]")
    exceptions_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ExceptionCase(Base):
    __tablename__ = "exception_cases"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("ap_invoices.id"), nullable=False)
    type = Column(String(80), nullable=False)
    severity = Column(String(40), nullable=False, default="medium")
    status = Column(String(40), nullable=False, default="open")
    owner = Column(String(120), nullable=True)
    detail = Column(Text, nullable=False)
    resolution_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("ap_invoices.id"), nullable=False)
    approver_role = Column(String(120), nullable=False)
    status = Column(String(40), nullable=False, default="pending")
    policy_reason = Column(Text, nullable=False)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("ap_invoices.id"), nullable=False)
    erp_system = Column(String(80), nullable=False)
    status = Column(String(40), nullable=False, default="draft")
    lines_json = Column(Text, nullable=False, default="[]")
    posted_reference = Column(String(160), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(160), nullable=False)
    status = Column(String(40), nullable=False, default="active")
    definition_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    agent_name = Column(String(120), nullable=False)
    object_type = Column(String(80), nullable=False)
    object_id = Column(String(120), nullable=False)
    status = Column(String(40), nullable=False, default="queued")
    input_json = Column(Text, nullable=False, default="{}")
    output_json = Column(Text, nullable=False, default="{}")
    policy_trace_json = Column(Text, nullable=False, default="[]")
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
