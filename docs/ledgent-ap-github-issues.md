# GitHub Issue Backlog

## Sprint 1: AP Platform Pivot

1. Build AP command center home screen
   - Metrics: invoice volume, payable exposure, straight-through rate, match accuracy
   - Invoice queue with status, ERP, match type, amount
   - Exception center
   - Finance agent monitor

2. Add AP backend domain endpoints
   - `GET /api/ap/overview`
   - `GET /api/ap/invoices`
   - `GET /api/ap/agents`
   - `POST /api/ap/matching/run`
   - `GET /api/ap/architecture`

3. Add AP database models
   - Organizations
   - Vendors
   - Invoices
   - Purchase Orders
   - Goods Receipts
   - Matching Results
   - Exceptions
   - Journal Entries
   - Approvals
   - Workflows
   - Agent Executions

4. Deploy AP version live
   - Push to GitHub
   - Deploy Vercel frontend
   - Deploy Railway backend with backend folder as root
   - Verify CORS, health, AP overview, matching, frontend hydration

## Sprint 2: Production Data Layer

5. Replace SQLite with PostgreSQL
   - Add Railway Postgres
   - Add database URL configuration
   - Keep local SQLite fallback for demos

6. Add Alembic migrations
   - Initial AP domain migration
   - Migration dry-run command
   - CI migration check

7. Add tenant-scoped CRUD APIs
   - Vendors
   - Purchase Orders
   - Goods Receipts
   - Invoices
   - Journal Entries

8. Add audit event writer
   - Append-only events
   - Actor, object, action, evidence, policy trace
   - Redact sensitive fields

## Sprint 3: Document Intelligence

9. Build invoice OCR worker
   - Accept PDF, DOCX, image, text
   - Extract text/tables
   - Persist extraction artifacts

10. Add invoice extraction schema
   - Vendor
   - Invoice number
   - PO number
   - Date and due date
   - Tax
   - Line items
   - Payment terms
   - Confidence scores

11. Build extraction review UI
   - Field-level confidence
   - Human corrections
   - Audit corrections

12. Add duplicate detection
   - Invoice number/vendor
   - Amount/date similarity
   - Document hash
   - Bank/remittance mismatch

## Sprint 4: Matching and Exceptions

13. Implement line-level 2-way matching
   - PO header checks
   - PO line amount checks
   - Tolerance policy

14. Implement line-level 3-way matching
   - PO line checks
   - Goods receipt quantity checks
   - Partial receipt handling

15. Build exception workflow engine
   - Open, assigned, waiting vendor, approved, rejected, resolved
   - Owner and SLA
   - Escalation

16. Build approval routing
   - Amount thresholds
   - Department/entity rules
   - Segregation of duties
   - Controller override

## Sprint 5: ERP Execution

17. Build ERP connector abstraction
   - Auth
   - Pull vendors/POs/receipts
   - Push bills/journals
   - Idempotency keys

18. Add QuickBooks sandbox connector
   - Vendor sync
   - Bill draft
   - Journal draft

19. Add NetSuite connector design
   - REST/SuiteTalk payload mapping
   - Subsidiary, department, class, location

20. Add ERP sync monitoring
   - Retry queue
   - Dead-letter queue
   - Error resolution UI

## Sprint 6: Enterprise Readiness

21. Add authentication and RBAC
   - AP Clerk
   - AP Manager
   - Controller
   - Auditor
   - ERP Admin

22. Add immutable audit log
   - Hash chaining
   - Export for auditors
   - No destructive edits

23. Add automated test suite
   - Matching unit tests
   - API tests
   - Browser tests
   - Connector contract tests

24. Add observability
   - Structured logs
   - Worker metrics
   - Agent execution traces
   - Alerting for failed syncs and SLA breaches
