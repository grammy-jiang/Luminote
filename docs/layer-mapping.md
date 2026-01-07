# Tech Stack Layer Mapping (Step 2.2)

This document maps atomic features from [atomic-features.md](atomic-features.md)
to implementation layers following Step 2.2 of the
[github-issue-creation-methodology.md](github-issue-creation-methodology.md).

## Overview

Each atomic feature will be implemented across one or more layers:

- **Backend:** FastAPI services, endpoints, and database operations
- **Frontend:** Svelte components, stores, and utilities
- **Infrastructure:** Docker, CI/CD, deployment configurations
- **Testing:** Unit tests, integration tests, E2E tests
- **Documentation:** API docs, architecture docs, user guides

______________________________________________________________________

## Phase 1 Feature Mapping

### Feature 1: Dual-Pane Translation with Progressive, Block-Level Rendering

14 atomic features across all layers

| Atomic Feature                  | Backend | Frontend | Infrastructure | Testing | Documentation |
| ------------------------------- | ------- | -------- | -------------- | ------- | ------------- |
| 1.1: Translation API Endpoint   | ✅      | —        | —              | ✅      | ✅            |
| 1.2: Translation Service        | ✅      | —        | —              | ✅      | —             |
| 1.3: Content Extraction Service | ✅      | —        | —              | ✅      | —             |
| 1.4: Extraction Endpoint        | ✅      | —        | —              | ✅      | ✅            |
| 1.5: Dual-Pane Layout           | —       | ✅       | —              | ✅      | —             |
| 1.6: Draggable Divider          | —       | ✅       | —              | ✅      | —             |
| 1.7: Skeleton Loading           | —       | ✅       | —              | ✅      | —             |
| 1.8: Source Pane Display        | —       | ✅       | —              | ✅      | —             |
| 1.9: Translation Pane Display   | —       | ✅       | —              | ✅      | —             |
| 1.10: Streaming Endpoint        | ✅      | —        | —              | ✅      | ✅            |
| 1.11: Progressive Rendering     | —       | ✅       | —              | ✅      | —             |
| 1.12: Hover Highlighting        | —       | ✅       | —              | ✅      | —             |
| 1.13: Click Navigation          | —       | ✅       | —              | ✅      | —             |
| 1.14: Keyboard Navigation       | —       | ✅       | —              | ✅      | —             |

**Layer Summary:**

- Backend: 5 features (endpoints, services)
- Frontend: 7 features (components, interactions)
- Infrastructure: 0 features (uses Phase 0)
- Testing: 14 features (100% coverage)
- Documentation: 3 features (API docs)

______________________________________________________________________

### Feature 2: Reader-Mode Extraction from Most Public URLs

5 atomic features

| Atomic Feature                       | Backend | Frontend | Infrastructure | Testing | Documentation |
| ------------------------------------ | ------- | -------- | -------------- | ------- | ------------- |
| 2.1: Extraction Endpoint             | —       | —        | —              | —       | —             |
| 2.2: News Article Support            | ✅      | —        | —              | ✅      | ✅            |
| 2.3: Blog Post Support               | ✅      | —        | —              | ✅      | ✅            |
| 2.4: Technical Documentation Support | ✅      | —        | —              | ✅      | ✅            |
| 2.5: Content Caching                 | ✅      | —        | —              | ✅      | —             |

**Layer Summary:**

- Backend: 4 features (content parsing, caching)
- Frontend: 0 features (uses existing extraction UI)
- Infrastructure: 0 features
- Testing: 4 features
- Documentation: 3 features (content type guides)

______________________________________________________________________

### Feature 3: BYOK Configuration

4 atomic features

| Atomic Feature                | Backend | Frontend | Infrastructure | Testing | Documentation |
| ----------------------------- | ------- | -------- | -------------- | ------- | ------------- |
| 3.1: Configuration Validation | ✅      | —        | —              | ✅      | ✅            |
| 3.2: Configuration Store      | —       | ✅       | —              | ✅      | —             |
| 3.3: Configuration Panel      | —       | ✅       | —              | ✅      | —             |
| 3.4: Settings Page            | —       | ✅       | —              | ✅      | —             |

**Layer Summary:**

- Backend: 1 feature (validation)
- Frontend: 3 features (UI components, store)
- Infrastructure: 0 features
- Testing: 4 features
- Documentation: 1 feature (config guide)

______________________________________________________________________

### Feature 4: Clear Error Handling

6 atomic features

| Atomic Feature                      | Backend | Frontend | Infrastructure | Testing | Documentation |
| ----------------------------------- | ------- | -------- | -------------- | ------- | ------------- |
| 4.1: Error Response Standardization | ✅      | —        | —              | ✅      | ✅            |
| 4.2: URL Fetch Error Handling       | ✅      | —        | —              | ✅      | —             |
| 4.3: API Key Error Handling         | ✅      | —        | —              | ✅      | —             |
| 4.4: Error Toast Notifications      | —       | ✅       | —              | ✅      | —             |
| 4.5: Critical Error Modal           | —       | ✅       | —              | ✅      | —             |
| 4.6: Retry Logic with Countdown     | —       | ✅       | —              | ✅      | —             |

**Layer Summary:**

- Backend: 3 features (error handling)
- Frontend: 3 features (error UI)
- Infrastructure: 0 features
- Testing: 6 features
- Documentation: 1 feature (error guide)

______________________________________________________________________

### Feature 5: Block-Level Synchronization

3 atomic features

| Atomic Feature        | Backend | Frontend | Infrastructure | Testing | Documentation |
| --------------------- | ------- | -------- | -------------- | ------- | ------------- |
| 5.1: Block ID Mapping | —       | ✅       | —              | ✅      | —             |
| 5.2: Scroll Sync Mode | —       | ✅       | —              | ✅      | —             |
| 5.3: Touch Support    | —       | ✅       | —              | ✅      | —             |

**Layer Summary:**

- Backend: 0 features
- Frontend: 3 features (utilities, interactions)
- Infrastructure: 0 features
- Testing: 3 features
- Documentation: 0 features

______________________________________________________________________

## Phase 1 Summary by Layer

### Backend Layer

**Total: 13 atomic features**

1. 1.1: Translation API Endpoint
1. 1.2: Translation Service
1. 1.3: Content Extraction Service
1. 1.4: Extraction Endpoint
1. 1.10: Streaming Endpoint
1. 2.2: News Article Support
1. 2.3: Blog Post Support
1. 2.4: Technical Documentation Support
1. 2.5: Content Caching
1. 3.1: Configuration Validation
1. 4.1: Error Response Standardization
1. 4.2: URL Fetch Error Handling
1. 4.3: API Key Error Handling

**Estimated Backend Work:** ~8 hours across 13 features

**Frontend Layer** **Total: 15 atomic features**

1. 1.5: Dual-Pane Layout
1. 1.6: Draggable Divider
1. 1.7: Skeleton Loading
1. 1.8: Source Pane Display
1. 1.9: Translation Pane Display
1. 1.11: Progressive Rendering
1. 1.12: Hover Highlighting
1. 1.13: Click Navigation
1. 1.14: Keyboard Navigation
1. 3.2: Configuration Store
1. 3.3: Configuration Panel
1. 3.4: Settings Page
1. 4.4: Error Toast Notifications
1. 4.5: Critical Error Modal
1. 4.6: Retry Logic with Countdown
1. 5.1: Block ID Mapping
1. 5.2: Scroll Sync Mode
1. 5.3: Touch Support

**Estimated Frontend Work:** ~10 hours across 18 features

### Infrastructure Layer

**Total: 0 new atomic features for Phase 1**

All infrastructure set up in Phase 0 (Project setup)

### Testing Layer

**Total: 32 atomic features** (100% test coverage)

Every atomic feature includes:

- Unit tests
- Component/endpoint tests
- Integration tests where applicable
- E2E tests for UI workflows

**Estimated Testing Work:** Included in feature estimates (~5 hours)

### Documentation Layer

**Total: 8 atomic features**

1. 1.1: Translation API documentation
1. 1.4: Extraction API documentation
1. 1.10: Streaming API documentation
1. 2.2: News content type guide
1. 2.3: Blog content type guide
1. 2.4: Technical documentation type guide
1. 3.1: Configuration guide
1. 4.1: Error codes reference

**Estimated Documentation Work:** ~2 hours across 8 features

______________________________________________________________________

## Implementation Order by Layer

### Week 1: Backend Foundations (Infrastructure Phase 0)

Phase 0 infrastructure issues (before Phase 1)

### Week 2-3: Backend Core (Backend Layer)

**Priority Order:**

1. 1.1: Translation API Endpoint
1. 1.2: Translation Service
1. 1.3: Content Extraction Service
1. 1.4: Extraction Endpoint
1. 3.1: Configuration Validation

**Rationale:** These enable all other backend features and UI

### Week 3-4: Backend Advanced (Backend Layer)

**Priority Order:** 6. 4.1: Error Response Standardization 7. 4.2: URL Fetch
Error Handling 8. 4.3: API Key Error Handling 9. 2.2-2.5: Content type support +
caching 10. 1.10: Streaming Endpoint

### Week 5-6: Frontend Components (Frontend Layer)

**Priority Order:**

1. 1.5: Dual-Pane Layout (foundation)
1. 1.6: Draggable Divider (builds on 1.5)
1. 1.7: Skeleton Loading (enhancement)
1. 1.8: Source Pane Display (builds on 1.5)
1. 1.9: Translation Pane Display (builds on 1.5)
1. 3.2: Configuration Store (supports 3.3, 3.4)
1. 3.3: Configuration Panel (builds on 3.2)
1. 3.4: Settings Page (builds on 3.3)

**Rationale:** Build layout first, then add features that depend on it

### Week 7: Frontend Integration (Frontend Layer)

**Priority Order:** 9. 1.11: Progressive Rendering (connects backend 1.10) 10.
1.12: Hover Highlighting (enhancement) 11. 1.13: Click Navigation (builds on
1.12) 12. 1.14: Keyboard Navigation (enhancement) 13. 5.1: Block ID Mapping
(supports 1.12-1.14) 14. 5.2: Scroll Sync Mode (enhancement)

### Week 8: Frontend Polish (Frontend Layer)

**Priority Order:** 15. 4.4: Error Toast Notifications 16. 4.5: Critical Error
Modal 17. 4.6: Retry Logic with Countdown 18. 5.3: Touch Support

______________________________________________________________________

## Dependency Graph by Layer

### Backend Dependencies

```
1.2 (Translation Service) depends on:
  └─ 1.1 (Translation API Endpoint)
     └─ 3.1 (Configuration Validation)

1.4 (Extraction Endpoint) depends on:
  └─ 1.3 (Content Extraction Service)

1.10 (Streaming Endpoint) depends on:
  └─ 1.2 (Translation Service)

2.2-2.4 (Content Type Support) depends on:
  └─ 1.3 (Content Extraction Service)

2.5 (Caching) depends on:
  └─ 1.4 (Extraction Endpoint)

4.2-4.3 (Error Handling) depends on:
  └─ 4.1 (Error Response Standardization)
```

### Frontend Dependencies

```
1.6 (Draggable Divider) depends on:
  └─ 1.5 (Dual-Pane Layout)

1.8 (Source Pane) depends on:
  └─ 1.5 (Dual-Pane Layout)

1.9 (Translation Pane) depends on:
  └─ 1.5 (Dual-Pane Layout)

1.11 (Progressive Rendering) depends on:
  ├─ 1.5 (Dual-Pane Layout)
  ├─ 1.8 (Source Pane)
  ├─ 1.9 (Translation Pane)
  └─ Backend 1.10 (Streaming Endpoint)

1.12 (Hover Highlighting) depends on:
  ├─ 1.8 (Source Pane)
  └─ 1.9 (Translation Pane)

1.13 (Click Navigation) depends on:
  └─ 1.12 (Hover Highlighting)

1.14 (Keyboard Navigation) depends on:
  └─ 1.13 (Click Navigation)

3.2 (Config Store) has no dependencies

3.3 (Config Panel) depends on:
  └─ 3.2 (Config Store)

3.4 (Settings Page) depends on:
  ├─ 3.3 (Config Panel)
  └─ Backend 3.1 (Configuration Validation)

5.1 (Block ID Mapping) depends on:
  ├─ 1.8 (Source Pane)
  └─ 1.9 (Translation Pane)

5.2 (Scroll Sync) depends on:
  ├─ 1.5 (Dual-Pane Layout)
  └─ 5.1 (Block ID Mapping)

5.3 (Touch Support) depends on:
  ├─ 1.12 (Hover Highlighting)
  └─ 1.13 (Click Navigation)

4.4-4.6 (Error UI) depends on:
  └─ Backend 4.1 (Error Response Standardization)
```

### Cross-Layer Dependencies

```
Frontend 1.11 (Progressive Rendering) depends on:
  └─ Backend 1.10 (Streaming Endpoint)

Frontend 3.3-3.4 (Config UI) depends on:
  └─ Backend 3.1 (Configuration Validation)

Frontend 4.4-4.6 (Error UI) depends on:
  └─ Backend 4.1 (Error Response Format)

Frontend 5.1-5.3 (Sync Features) depends on:
  └─ Backend 1.4 (Extraction Endpoint - for block IDs)
```

______________________________________________________________________

## Test Strategy by Layer

### Backend Testing

- **Unit Tests:** Service methods with mocked dependencies
- **Integration Tests:** API endpoints with test database/providers
- **Provider Tests:** Real API key testing (optional, with test keys)
- **Error Tests:** All error paths covered

### Frontend Testing

- **Unit Tests:** Store logic, utility functions
- **Component Tests:** Vitest + svelte testing library
- **Interaction Tests:** Click, hover, keyboard events
- **Integration Tests:** Component combinations

### Testing Coverage Target

- **Backend:** 85% code coverage
- **Frontend:** 80% component coverage
- **Critical Paths:** 100% coverage (error handling, data flow)

______________________________________________________________________

## Documentation Strategy by Layer

### API Documentation

- **Endpoint docs** for each backend feature
- **Request/response schemas** (OpenAPI/Swagger)
- **Error codes reference**
- **Code examples** for each endpoint

### Architecture Documentation

- ADRs already created in [adr/](adr/)
- Layer mapping in this document
- Implementation sequence in
  [implementation-sequence.md](implementation-sequence.md)

### User Documentation

- Configuration guide (for BYOK)
- Error messages guide
- Troubleshooting section

______________________________________________________________________

## Copilot Readiness Checklist

Each atomic feature is ready for Copilot assignment when:

- ✅ Acceptance criteria clearly defined
- ✅ Dependencies mapped
- ✅ File locations specified
- ✅ Test requirements listed
- ✅ Relevant ADRs referenced
- ✅ Code examples provided (where applicable)

**Status:** All 32 Phase 1 atomic features meet these criteria

______________________________________________________________________

## References

- [atomic-features.md](atomic-features.md) - Detailed atomic feature
  specifications
- [feature-dependency-analysis.md](feature-dependency-analysis.md) - High-level
  feature dependencies
- [adr/](adr/) - Architecture Decision Records
- [infrastructure-requirements.md](infrastructure-requirements.md) - Phase 0
  setup
- [implementation-sequence.md](implementation-sequence.md) - Detailed weekly
  batches
