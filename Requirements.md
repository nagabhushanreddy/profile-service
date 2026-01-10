# Multi-Finance User Application
## Profile Service - Requirements Document (OpenAPI-Compliant)

---

## 1. Overview

This document defines the functional and non-functional requirements for the **Profile Service** - a comprehensive user profile and Know Your Customer (KYC) management system for the Multi-Finance User Web Application built using a **microservices REST architecture**.

The service manages customer personal information, addresses, contact details, financial profile data, KYC status, consent tracking, profile documents (photos, identity proofs), and bank-side profile enrichment with maker-checker controls. All APIs must be OpenAPI 3.x compliant.

### Core Responsibility
- **Profile Management**: Customer profile creation, retrieval, and updates
- **Address Management**: Multiple addresses with type classification (residential, office, correspondence)
- **KYC Lifecycle**: KYC status tracking and verification workflows
- **Document Management**: Profile-related documents via document-service integration
- **Consent Management**: Track customer consents and preferences
- **Profile Audit**: Immutable audit trail of profile changes
- **Bank-Side Enrichment**: Risk officers, credit officers can enrich profiles with maker-checker controls

---

## 2. Architecture Principles

- Microservices with **single responsibility**
- **Database-per-service or use entity-service** for shared metadata
- REST APIs with **OpenAPI 3.0+**
- Stateless services
- JWT-based security with authz-service enforcement (default deny)
- Field-level access control and masking for PII (Personally Identifiable Information)
- Audit-first: all profile modifications logged immutably
- Layered architecture: Routes → Services → Clients → External Systems
- Reuse shared utilities via utils-service; shared metadata via entity-service
- Maker-checker pattern for bank-side profile enrichment updates

---

## 3. Features

- **Customer Profile**: Comprehensive profile data (name, DOB, gender, occupation, marital status, PAN, Aadhaar)
- **Address Management**: Multiple address records with types (residential, office, correspondence) and verification status
- **Contact Details**: Phone, email, alternative phone with verification
- **Financial Profile**: Income, occupation, employer details, bank account info (for disbursal)
- **KYC Status Tracking**: Identity verification, address verification, income verification, document verification milestones
- **Document Upload**: Profile documents (profile photo, identity proofs, address proofs) via document-service
- **Consent Management**: Track product consents, regulatory consents, marketing preferences
- **Profile Masking**: PII masking for API responses based on caller role/permissions
- **Self-Service Updates**: Customer can update own profile fields (mutable fields)
- **Bank-Side Profile Enrichment**: Risk scoring, credit grading, background verification (maker-checker)
- **Profile Completeness**: Track profile completion percentage and missing data
- **Verification Status**: Track verification status per profile section
- **Audit Trail**: Immutable history of all profile changes with actor, timestamp, before/after values
- **Multi-Tenant Isolation**: Strong tenant and data isolation
- **Rate Limiting**: Configurable limits per user/tenant to prevent abuse
- **Entity Service Integration**: Centralized profile metadata storage and retrieval
- **Document Service Integration**: Secure upload/retrieval of profile documents
- **AuthZ Integration**: Role-based access control and field-level permissions
- **Utils Integration**: Shared logging, configuration, correlation IDs
- **OpenAPI Documentation**: Auto-generated interactive documentation
- **Type Safety**: Full Pydantic schema validation

---

## 4. Technology Stack

- **Language**: Python 3.10+
- **Framework**: FastAPI (async, OpenAPI-native)
- **Data Validation**: Pydantic
- **Persistence**: Postgres (or via entity-service); Redis for caching and profile snapshots
- **Image Processing**: Pillow (for profile photo validation/resizing) - optional
- **Logging**: Structured JSON logs via utils-service
- **Testing**: pytest with coverage reporting
- **Server**: Uvicorn ASGI

---

## 5. Core APIs / Endpoints

### 5.1 Health Check
- `GET /health` - Service health and readiness
- `GET /healthz` - Kubernetes liveness probe

### 5.2 Profile Management

#### Get Own Profile
**Endpoint**: `GET /api/v1/profiles/me`

**Request Requirements:**
- Must include JWT token in Authorization header
- Must optionally include fields query parameter to specify requested fields
- Must optionally include include_masked flag (default false for privacy)

**Response Requirements:**
- Success Status: 200 OK
- Must return profile object with: id (UUID), user_id, name, DOB, gender, phone, email
- Must return marital_status, occupation, employer_name
- Must return identity fields: PAN, Aadhaar (partial, last 4 digits unless specific permission)
- Must return profile_completeness percentage
- Must return kyc_status summary
- Must return verification_status per section
- Must return updated_at timestamp
- Must mask sensitive fields based on caller role (e.g., customer sees own data, bank officer may see verification notes)

**Business Logic:**
- Apply PII masking based on caller's role and permissions via authz-service
- Cache profile data with short TTL (5 minutes) for performance
- Log profile access for audit
- Enforce tenant isolation

**Security:**
- JWT token required; fail closed if missing/invalid
- AuthZ check: caller must be profile owner or bank-side role with read permission
- No sensitive data in logs

---

#### Update Own Profile (Customer)
**Endpoint**: `PATCH /api/v1/profiles/me`

**Request Requirements:**
- Must include JWT token
- Must accept mutable fields: name (full, first, last), phone, email, marital_status, occupation, employer_name
- Must NOT allow update of identity fields (PAN, Aadhaar) or KYC-verified data without re-verification
- Must accept Idempotency-Key header for idempotent updates

**Response Requirements:**
- Success Status: 200 OK
- Must return updated profile
- Must include metadata: timestamp, correlation_id, update_source (customer_self)

**Business Logic:**
- Only profile owner (customer) may update own mutable profile fields
- Validate field format (phone international, email valid, names length limits)
- Lock verified fields (e.g., if KYC_VERIFIED, name locked unless explicit reverification requested)
- Create audit trail entry before/after comparison
- Invalidate profile cache on update
- Emit event for notification-service (profile updated)

**Security:**
- Enforce caller is profile owner via authz-service
- Rate limit updates (10 per hour per user)
- Validate and sanitize all inputs
- Log update with correlation ID

**Error Responses:**
- 400 Bad Request: Invalid field format
- 401 Unauthorized: Missing/invalid token
- 403 Forbidden: Insufficient permissions
- 409 Conflict: KYC-verified fields cannot be updated
- 422 Unprocessable Entity: Validation errors
- 429 Too Many Requests: Rate limit exceeded

---

#### Get Profile by ID (Bank-Side)
**Endpoint**: `GET /api/v1/profiles/{profile_id}`

**Request Requirements:**
- Must include JWT token
- Must include role claim with permission to view profiles

**Response Requirements:**
- Success Status: 200 OK
- Complete profile with enrichment data (risk score, credit grade, verification notes)

**Business Logic:**
- Enforce authz-service permission for profile_id access
- Include enrichment fields if caller is bank-side role
- Log access for audit trail

**Security:**
- AuthZ required; default deny
- No cross-tenant access
- Rate limit (100 per minute per user)

---

### 5.3 Address Management

#### Get Addresses
**Endpoint**: `GET /api/v1/profiles/me/addresses`

**Query Parameters:**
- type (optional: residential, office, correspondence)

**Response Requirements:**
- Success Status: 200 OK
- Must return array of address objects: id, type, address_line1, address_line2, city, state, postal_code, country, is_primary, verification_status, verified_at

**Business Logic:**
- Return only addresses belonging to profile owner
- Include verification status
- Sort by is_primary first, then by creation date

---

#### Add Address
**Endpoint**: `POST /api/v1/profiles/me/addresses`

**Request Requirements:**
- Must accept type (enum: residential, office, correspondence)
- Must accept address_line1 (required)
- Must accept address_line2 (optional)
- Must accept city, state, postal_code, country (required)
- Must accept is_primary (optional boolean)

**Response Requirements:**
- Success Status: 201 Created
- Must return address object with id and timestamps

**Business Logic:**
- Validate address format and postal code format per country
- If is_primary=true, unset other primary addresses
- Create audit entry
- Mark as unverified until KYC process validates
- Support up to 10 addresses per profile

**Security:**
- Only profile owner may add addresses
- Rate limit (20 adds per month per user)

---

#### Update Address
**Endpoint**: `PATCH /api/v1/profiles/me/addresses/{address_id}`

**Response Requirements:**
- Success Status: 200 OK
- Must return updated address

**Business Logic:**
- Allow updates if address not yet verified
- If already verified, require re-verification or mark as unverified
- Log changes

---

#### Delete Address
**Endpoint**: `DELETE /api/v1/profiles/me/addresses/{address_id}`

**Response Requirements:**
- Success Status: 204 No Content

**Business Logic:**
- Soft delete (mark as deleted, keep audit trail)
- Cannot delete if marked as correspondence address in active loan

---

### 5.4 KYC Management

#### Get KYC Status
**Endpoint**: `GET /api/v1/profiles/me/kyc`

**Response Requirements:**
- Success Status: 200 OK
- Must return kyc_status (enum: pending, in_progress, verified, rejected, expired)
- Must return completed_checks array: identity_verified, address_verified, income_verified, document_verified
- Must return verification_dates for each check
- Must return rejection_reason if rejected
- Must return expiry_date if verified (with validity period)

**Business Logic:**
- Identity verified: PAN/Aadhaar verified
- Address verified: Address proof document verified
- Income verified: Income documentation reviewed
- Document verified: All required documents received and scanned clean
- Overall KYC status moves to VERIFIED only when all required checks complete

---

#### Initiate KYC (Customer)
**Endpoint**: `POST /api/v1/profiles/me/kyc/initiate`

**Request Requirements:**
- Optional: kyc_type (enum: standard, enhanced, legacy - default: standard)

**Response Requirements:**
- Success Status: 201 Created
- Must return kyc_id and required_documents list

**Business Logic:**
- Create KYC workflow
- List all required documents per kyc_type
- Generate document upload instructions
- Set status to in_progress

---

### 5.5 Profile Documents

#### Upload Profile Document
**Endpoint**: `POST /api/v1/profiles/me/documents`

**Request Requirements:**
- Must delegate file upload to document-service
- Must accept document_type (enum: profile_photo, aadhar, pan, passport, driving_license, utility_bill, bank_statement, others)
- Must accept metadata: issue_date (optional), expiry_date (optional)

**Response Requirements:**
- Success Status: 201 Created
- Must return document_id from document-service, type, verification_status, uploaded_at

**Business Logic:**
- Call document-service to upload file with virus scanning
- Store document type and metadata in profile service
- Link document to KYC workflow if part of KYC
- Mark for verification by bank officer
- Validate document type per KYC requirements

**Security:**
- Enforce document-service virus scanning
- Rate limit uploads (10 per day per user)
- Only owner may upload own documents

---

#### Get Profile Documents
**Endpoint**: `GET /api/v1/profiles/me/documents`

**Query Parameters:**
- document_type (optional filter)
- verification_status (optional filter)

**Response Requirements:**
- Success Status: 200 OK
- Must return array of documents with metadata, verification_status, verified_by, verified_at
- Must include pre-signed URL from document-service for download

---

#### Verify Document (Bank-Side)
**Endpoint**: `POST /api/v1/profiles/{profile_id}/documents/{document_id}/verify`

**Request Requirements:**
- Must include verification_result (enum: approved, rejected)
- Must include verification_notes (optional)
- Must include Maker-Checker-Id header (for maker-checker tracking)

**Response Requirements:**
- Success Status: 200 OK
- Must return verification result with verified_by, verified_at

**Business Logic:**
- Enforce role-based access (only authorized officers)
- Create marker-checker workflow: one officer submits verification (Maker), another reviews and approves (Checker)
- Lock document after both approve
- Create audit trail with both maker and checker details
- Update KYC status based on all documents verified

**Security:**
- Enforce maker-checker pattern: same officer cannot both make and check
- Require elevated permissions
- Log all verifications with reasons

---

### 5.6 Consent Management

#### Get Consents
**Endpoint**: `GET /api/v1/profiles/me/consents`

**Response Requirements:**
- Success Status: 200 OK
- Must return array of consents: type (enum), status (accepted/rejected), accepted_at, version

**Consent Types:**
- terms_and_conditions
- data_usage
- marketing_communication
- cibil_report_pull (for loan eligibility)

---

#### Accept/Reject Consent
**Endpoint**: `POST /api/v1/profiles/me/consents/{consent_type}`

**Request Requirements:**
- Must accept decision (enum: accept, reject)
- Must accept version (consent document version)

**Response Requirements:**
- Success Status: 200 OK
- Must return consent with new status and timestamp

**Business Logic:**
- Store consent acceptance with timestamp and version
- Some consents mandatory for loan eligibility (CIBIL, terms)
- Log all consent changes

---

### 5.7 Profile Enrichment (Bank-Side, Maker-Checker)

#### Add Risk Score and Credit Grade
**Endpoint**: `POST /api/v1/profiles/{profile_id}/enrichment`

**Request Requirements:**
- Must include risk_score (numeric, 1-100)
- Must include risk_grade (enum: low, medium, high, very_high)
- Must include credit_grade (enum: A, B, C, D, E)
- Must include background_check_result (enum: clear, review, flag)
- Must include verification_notes (optional)
- Must include Maker-Checker-Id for tracking (Maker's request)

**Response Requirements:**
- Success Status: 201 Created (if first submission as Maker) or 200 OK (if Checker approval)
- Must return enrichment object with status: pending_checker_review or approved

**Business Logic:**
- Maker submits enrichment data
- System flags for Checker review
- Checker reviews and approves/rejects
- On approval, update profile with enrichment data
- On rejection, return to Maker with feedback
- Create audit trail with both Maker and Checker signatures

**Maker-Checker Rules:**
- Same officer cannot be both Maker and Checker
- Checker must be same or higher rank than Maker
- SLA: Checker must review within 24 hours
- If rejected, Maker can resubmit with corrections

**Security:**
- Enforce role-based access (only bank officers)
- Require explicit permissions for enrichment
- Log all submissions with reasons
- Immutable audit trail

---

#### Review Enrichment (Checker)
**Endpoint**: `POST /api/v1/profiles/{profile_id}/enrichment/{enrichment_id}/review`

**Request Requirements:**
- Must include decision (enum: approve, reject)
- Must include checker_notes (optional)
- Must include Checker-Id for tracking

**Response Requirements:**
- Success Status: 200 OK
- Must return enrichment with decision and checker details

---

### 5.8 Audit & Activity

#### Get Profile Audit Trail
**Endpoint**: `GET /api/v1/profiles/me/audit`

**Query Parameters:**
- from_date, to_date (optional date range)
- action_type (optional filter: create, update, verify, enrich)
- limit, offset (for pagination)

**Response Requirements:**
- Success Status: 200 OK
- Must return array of audit entries: id, action, actor_id, actor_role, timestamp, from_value, to_value, reason, correlation_id

**Business Logic:**
- Enforce same user can only see own audit
- Bank officers may see audit for profiles they manage
- Immutable, append-only audit trail

---

### 5.9 Profile Completeness

#### Get Profile Completeness
**Endpoint**: `GET /api/v1/profiles/me/completeness`

**Response Requirements:**
- Success Status: 200 OK
- Must return overall_completeness percentage
- Must return field_completeness object: personal_info %, address_info %, kyc_info %, documents_info %
- Must return missing_fields array (list of fields needed for KYC/loan eligibility)

**Business Logic:**
- Calculate based on presence of required fields
- Weight fields by importance (name=critical, occupation=important)
- Suggest missing fields to customer

---

### 5.10 Admin/Reference Data

#### Get Profile Status Enum Values
**Endpoint**: `GET /api/v1/reference/profile-statuses`

#### Get KYC Status Enum Values
**Endpoint**: `GET /api/v1/reference/kyc-statuses`

#### Get Address Types
**Endpoint**: `GET /api/v1/reference/address-types`

---

## 6. Data Model Requirements (Descriptive)

**Profile Schema:**
- id (UUID), user_id (entity-service ref), tenant_id (UUID)
- Personal data: first_name, last_name, full_name, date_of_birth, gender, marital_status
- Identity: PAN (pan_id), Aadhaar (aadhaar_id, masked), passport_id (optional)
- Occupation: occupation_type, employer_name, employer_id, job_title, annual_income (optional), employment_status
- Contact: phone (primary, verified), email (primary, verified), alternative_phone (optional)
- Financial: salary_account_number (for disbursal), salary_account_ifsc, bank_name
- KYC: kyc_status, kyc_id (linked workflow), completed_at, verified_at, expiry_at (renewal date)
- Profile completeness: completeness_percentage, last_updated_at
- Verification: identity_verified_at, address_verified_at, income_verified_at, document_verified_at
- Enrichment: risk_score, risk_grade, credit_grade, background_check_status, enriched_at, enriched_by (officer_id)
- Audit: created_at, created_by (user_id), updated_at, updated_by (user_id), deleted_at (soft delete)

**Address Schema:**
- id (UUID), profile_id (ref), type (enum), is_primary (boolean)
- address_line1, address_line2, city, state, postal_code, country
- verification_status, verified_at, verified_by
- created_at, updated_at

**KYC Workflow Schema:**
- id (UUID), profile_id (ref), kyc_type, status, required_documents array
- completed_checks: identity_verified, address_verified, income_verified, document_verified
- verification_timestamps, rejection_reason, expiry_date
- created_at, updated_at

**Document Link Schema:**
- id (UUID), profile_id, document_id (document-service ref), document_type, verification_status, verified_by, verified_at
- created_at

**Consent Schema:**
- id (UUID), profile_id, consent_type, status, accepted_at, consent_version
- created_at

**Enrichment Schema:**
- id (UUID), profile_id, risk_score, risk_grade, credit_grade, background_check_result
- maker_id, maker_notes, maker_submitted_at
- checker_id, checker_notes, checker_decision, checker_reviewed_at
- status (pending_review, approved, rejected), created_at

**Audit Entry Schema:**
- id (UUID), profile_id, action (create/update/verify/enrich), actor_id, actor_role
- from_value (before), to_value (after), field_name, reason
- timestamp, correlation_id

---

## 7. Business Logic & Rules

### 7.1 Profile Creation
- Triggered on user registration via auth-service
- Auto-populate from auth-service claims where available (email, phone)
- Set initial kyc_status to pending
- Create empty addresses list
- Set completeness to 0%

### 7.2 Self-Service Updates (Customer)
- Customer can update: name, phone, email, marital_status, occupation, employer_name
- Cannot update identity fields (PAN, Aadhaar) once verified
- Cannot update previously verified fields without re-verification
- Each update creates audit entry with before/after
- Updates trigger profile re-cache

### 7.3 KYC Workflow
- Initiated by customer or bank-initiated
- Standard KYC: identity + address + document verification
- Enhanced KYC: add income verification (for loans > threshold amount)
- Legacy KYC: manual verification only
- Status flow: pending → in_progress → verified/rejected
- Verified status valid for 1 year; flag for renewal after 11 months

### 7.4 Address Management
- Support up to 10 addresses per profile
- One primary address (residential)
- One correspondence address for mail
- Verified status required for loan eligibility
- Cannot delete if in use in active loan/application

### 7.5 Document Verification
- All documents must pass virus scan (document-service)
- Verification required before KYC completion
- Required documents per KYC type defined in config
- Expiry dates checked; flag for renewal if expiring

### 7.6 Maker-Checker for Enrichment
- Only bank officers with explicit role may enrich profiles
- Maker: submits risk score, credit grade, background check
- Checker: independent review and approval/rejection
- Same officer cannot be both Maker and Checker
- Checker has 24 hours SLA for review
- Rejected enrichments return to Maker with feedback
- All decisions logged immutably

### 7.7 PII Masking
- Customer sees full data
- Bank officers (loan officers, risk officers) see full data (if permission granted)
- Other roles: Aadhaar last 4 digits only, PAN partially masked
- API respects authz-service permissions for field-level access

### 7.8 Consent Tracking
- Track customer acceptance of each consent type with version
- Mandatory consents: terms_and_conditions, cibil_report_pull (for loans)
- Optional: marketing_communication
- Cannot proceed with loan without mandatory consents
- Consent changes tracked in audit

### 7.9 Profile Completeness
- Calculated based on required fields per use case
- Personal info (50%): name, DOB, gender
- Address info (20%): primary address verified
- KYC info (20%): KYC status verified
- Documents (10%): all required documents verified
- Suggest missing fields to customer via UI

### 7.10 Ownership & Tenancy
- Customer can only access own profile
- Bank officers access profiles for their assigned customers (via loan applications)
- Strict tenant isolation; no cross-tenant access
- authz-service enforces all access control rules

---

## 8. Security Requirements

### 8.1 Authentication
- JWT validation from auth-service
- Token claims include user_id, tenant_id, role
- API key support for service-to-service (optional)

### 8.2 Authorization
- All endpoints protected by JWT requirement
- AuthZ checks via authz-service (default deny model)
- Field-level access control: some fields visible only to bank roles
- PII masking applied based on caller permissions
- Ownership enforced: customer can only update own profile

### 8.3 Data Protection
- No sensitive data in logs (PAN, Aadhaar, account numbers)
- Sensitive fields masked in API responses unless explicitly authorized
- Personal data encrypted at rest (handled by database)
- Secure document upload via document-service with virus scanning

### 8.4 Audit & Immutability
- All profile changes logged with actor, timestamp, before/after values
- Append-only audit trail; no deletion/modification of audit entries
- Soft deletes preserve audit history
- Correlation IDs propagated to audit entries for tracing

### 8.5 Maker-Checker
- Separate actor IDs for Maker and Checker
- Same officer cannot fulfill both roles
- Decision audit includes both actors and their notes

### 8.6 Rate Limiting
- Update profile: 10 per hour per user
- Add address: 20 per month per user
- Upload document: 10 per day per user
- Protect against abuse

### 8.7 Input Validation
- Strict validation of all inputs (phone, email, postal codes, date formats)
- Phone format validation per country
- Email validation before update
- Sanitize free-text fields to prevent injection
- File type validation delegated to document-service

---

## 9. Performance Requirements

### 9.1 Latency
- P95 latency for profile read (GET /profiles/me): <150ms
- P95 latency for profile update (PATCH /profiles/me): <250ms
- P95 latency for KYC status check: <100ms
- P95 latency for address list: <120ms

### 9.2 Throughput
- Support 500 concurrent profile operations
- Queries: 10,000 per second sustained

### 9.3 Caching
- Profile cache TTL: 5 minutes (invalidated on update)
- Address list cache TTL: 10 minutes
- KYC status cache TTL: 2 minutes (frequently changing)

### 9.4 Pagination
- Default limit: 50; max: 100
- Support offset/cursor-based pagination

---

## 10. Error Handling

### 10.1 Standard Error Response
- success: false (boolean)
- error object: code (ERROR_CODE), message (human-readable), details (optional)
- data: null
- metadata: timestamp (ISO 8601), correlation_id (UUID)

### 10.2 Error Codes
- INVALID_REQUEST: Malformed request
- UNAUTHORIZED: Missing/invalid JWT
- FORBIDDEN: Insufficient permissions
- NOT_FOUND: Profile/address/document not found
- CONFLICT: Profile locked or KYC-verified field update attempted
- UNPROCESSABLE_ENTITY: Validation errors (field-level)
- IDENTITY_UNVERIFIED: Identity not verified for operation
- KYC_UNVERIFIED: KYC not verified for loan eligibility
- DOCUMENT_MISSING: Required document not provided
- DOCUMENT_VERIFICATION_FAILED: Document rejected in verification
- MAKER_CHECKER_INVALID: Same officer cannot be maker and checker
- RATE_LIMITED: Too many requests
- ENTITY_SERVICE_ERROR: Metadata persistence failure
- DOCUMENT_SERVICE_ERROR: File upload/retrieval failure
- AUTHZ_SERVICE_ERROR: Authorization check failed

---

## 11. External Service Integration

### 11.1 Entity Service
**Purpose**: Store and query profile metadata in canonical form

**Operations:**
- Create user profile entity
- Query profile by user_id
- Update profile attributes
- Store addresses, documents, consent records

**Error Handling:**
- Retry transient failures (3 attempts, exponential backoff)
- Return error to client on persistent failures
- Log integration errors with correlation ID

### 11.2 Document Service
**Purpose**: Secure file storage and virus scanning for profile documents

**Operations:**
- Upload profile document (profile photo, identity proofs)
- Retrieve document metadata and pre-signed URL
- Soft delete document

**Error Handling:**
- Handle virus scan failure (quarantine document)
- Retry transient failures
- If document-service down, queue documents for later verification

### 11.3 AuthZ Service
**Purpose**: Role-based access control and field-level permissions

**Operations:**
- Check if caller can read profile
- Check if caller can update specific profile fields
- Check if caller can perform enrichment
- Fetch caller's role and permissions

**Error Handling:**
- Fail closed (deny access) on authz-service error
- Cache authorization decisions (short TTL: 30 seconds)
- Log all authorization failures

### 11.4 Utils Service
**Purpose**: Shared logging and configuration

**Operations:**
- Initialize structured logging
- Use pre-configured logger instance
- Get configuration (via environment or config files)

---

## 12. Testing Requirements

### 12.1 Unit Tests
- Profile CRUD operations
- Address validation and management
- KYC status transitions
- Consent acceptance/rejection
- Profile completeness calculations
- Maker-checker logic (same officer cannot both make and check)
- PII masking for different roles
- Idempotency for updates
- Minimum 80% code coverage

### 12.2 Integration Tests
- Profile creation flow (auth-service trigger)
- Document upload and verification (document-service integration)
- AuthZ enforcement (authz-service integration)
- Maker-checker workflow with both approval and rejection paths
- Audit trail immutability
- Entity-service metadata persistence
- Profile cache invalidation on updates
- Address verification workflow

### 12.3 Security Tests
- JWT validation (expired, invalid, missing)
- Field-level access control (customer vs. bank officer)
- PII masking in API responses
- Cross-tenant access prevention
- Maker-checker enforcement (same officer validation)
- Rate limiting enforcement
- Sensitive data not in logs

### 12.4 Performance Tests
- Load test profile reads (500 concurrent)
- Load test profile updates
- Cache hit rate validation
- Pagination performance under load

---

## 13. Configuration Requirements

### 13.1 Application Settings
- Service name: profile-service
- Version and environment tracking
- Server host, port (default: 8006), workers

### 13.2 Security Configuration
- JWT settings: secret key, algorithm (HS256)
- AuthZ-service endpoint, timeout (5s), retry attempts (2)
- API key header name (X-API-Key)

### 13.3 Caching Configuration
- Profile cache TTL (default: 5 minutes)
- Address list cache TTL (default: 10 minutes)
- KYC status cache TTL (default: 2 minutes)
- Redis endpoint (or in-memory fallback)

### 13.4 Business Configuration
- KYC required fields per kyc_type
- Required documents per product type
- Profile completeness weights
- Maker-checker SLA (default: 24 hours)
- Consent versions and mandatory types

### 13.5 External Services Configuration
- Entity-service: base URL, timeout (10s), retry attempts (3)
- Document-service: base URL, timeout (10s), retry attempts (3)
- AuthZ-service: base URL, timeout (5s), retry attempts (2)
- Notification-service: base URL, timeout (5s) - for profile update notifications

### 13.6 Logging Configuration
- Log level (INFO default), JSON format, stdout output
- Sensitive field masking in logs (PAN, Aadhaar, account numbers)

### 13.7 Rate Limiting Configuration
- Profile updates: 10 per hour per user
- Address adds: 20 per month per user
- Document uploads: 10 per day per user

---

## 14. Deployment

### 14.1 Container
- Docker image with Python 3.10+ and all dependencies
- Health check endpoint: `/healthz`
- Readiness probe: `/health`
- Liveness probe: `/healthz`

### 14.2 Kubernetes
- Minimum 2 replicas for HA
- Resource limits: CPU 1 core, Memory 1GB
- Resource requests: CPU 500m, Memory 512MB
- HPA based on CPU > 70% or latency > 300ms
- Persistent connections to Redis (if used)

### 14.3 Service Discovery
- Service name: `profile-service`
- Port: 8006
- Protocol: HTTP

### 14.4 Database
- Postgres or entity-service for metadata
- Schema migrations with rollback capability
- Indexes on: profile_id, user_id, tenant_id, kyc_status

---

## 15. OpenAPI Requirements

### 15.1 OpenAPI Specification
- Version: OpenAPI 3.0.3
- Title: Profile Service API
- Version: 1.0.0
- Base Path: `/api/v1`

### 15.2 Security Schemes
- **BearerAuth**: HTTP bearer token authentication with JWT format
- **ApiKeyAuth**: API key passed in X-API-Key header for service-to-service

### 15.3 Request/Response Headers
- X-Correlation-Id: Request correlation ID for tracing
- Idempotency-Key: For idempotent updates
- ETag: For cache validation

### 15.4 Documentation
- Interactive Swagger UI at `/docs`
- ReDoc documentation at `/redoc`
- OpenAPI JSON at `/openapi.json`

---

## 16. Monitoring & Observability

### 16.1 Metrics
- Request rate, latency (P50, P95, P99), error rate per endpoint
- Profile reads/writes per minute
- Cache hit rate
- Maker-checker approval/rejection ratio
- Document verification success rate
- AuthZ check latency
- Entity-service and document-service integration latency

### 16.2 Logs
- Structured JSON logs with correlation_id, user_id, tenant_id, action
- Log all profile updates with before/after field values
- Log all document verifications with decision
- Log all maker-checker actions
- Log all authz checks and decisions
- Mask sensitive data (PAN, Aadhaar, account numbers) in logs

### 16.3 Tracing
- Propagate correlation IDs to all downstream calls
- Trace profile reads, updates, document verification
- Trace maker-checker workflow steps
- Trace authz-service and entity-service calls

### 16.4 Alerts
- High error rate (> 5% of requests)
- AuthZ failures (possible attack)
- Entity-service integration failures
- Document-service integration failures
- Cache performance degradation
- SLA breaches for maker-checker review

---

## 17. Project Structure (Logical, No Code)

Root entrypoint main.py with FastAPI app initialization, lifespan events, middleware setup.

app/ package containing:
- config.py: Configuration loading from environment and YAML
- middleware.py: Request context, JWT extraction, correlation ID management, error handling
- cache.py: Profile, address, KYC status caching with TTL management
- models/: Pydantic schemas for requests, responses, and domain entities (Profile, Address, KYC, Document, Consent, Enrichment, Audit)
- routes/: API endpoint handlers organized by feature (health, profiles, addresses, kyc, documents, consents, enrichment, audit)
- services/: Business logic layer
  - profile_service: Profile CRUD, completeness calculation, PII masking
  - address_service: Address management, verification workflow
  - kyc_service: KYC status tracking, workflow orchestration
  - document_service: Document integration, verification workflow
  - consent_service: Consent acceptance, tracking
  - enrichment_service: Maker-checker logic, risk/credit scoring
  - audit_service: Immutable audit trail management
  - validation_service: Field validation, format checks
- clients/: External service HTTP clients
  - entity_service: Profile metadata persistence
  - document_service: File upload/retrieval
  - authz_service: Authorization checks
  - (future) notification_service: Status change notifications

tests/: Unit and integration tests with conftest.py, test fixtures, reports directory for junit/coverage

storage/: None (profiles stored in entity-service or database)

config/: YAML files for app and logging configuration

requirements.txt and requirements-dev.txt: Dependencies

Standards:
- Each directory with Python code MUST have __init__.py
- Use absolute imports: from app.services import ProfileService
- Export commonly used classes in __init__.py files
- Follow layered architecture: Routes → Services → Clients → External Systems
- Keep routes thin (validation + delegation only)
- Business logic in services layer
- External integrations in clients layer
- Use from utils import logger for logging
- Use from utils import init_app_logging for initialization

---

## 18. Future Enhancements

### 18.1 Advanced Features (Phase 2)
- Biometric profile verification (facial recognition for profile photo)
- Social media profile verification
- Alternative identity documents support (GSTIN, business registration for business accounts)
- Household member profiles (for joint applications)
- Co-borrower management
- Profile verification via video KYC
- Digital signature capture for consents

### 18.2 Analytics & Insights (Phase 2)
- Profile completion trends per customer segment
- KYC rejection reasons analysis
- Document verification time analytics
- Maker-checker decision distribution analysis
- Risk score distribution and trends

### 18.3 Integration Enhancements (Phase 2)
- Real-time credit bureau integration for scoring
- Background verification service integration
- Income verification via third-party APIs
- Automated PAN/Aadhaar verification

---

**End of Document**
