Personal Travel Planner — Product Requirements Document
Version: 0.3 Status: Draft Target release: 31 March 2027
1. Product Overview
Personal Travel Planner is a B2C web application for independently planning multi-city and multi-country trips.
It combines destinations, itineraries, places, budgets, expenses and travel documents in one application.
The MVP supports individual trip planning. Collaboration is postponed.
2. Target Audience
* Solo travelers.
* Couples.
* Groups of friends.
3. MVP Features
1. Authentication and user profiles.
2. Trip management.
3. Multiple destinations per trip.
4. Daily itineraries and activities.
5. Place search using a map/API and manual place creation.
6. Budget planning and expense tracking.
7. Multiple currencies and exchange-rate conversion.
8. Travel document management.
Documents support PDF/image uploads and external links.
Out of scope: collaboration, booking services, AI itinerary generation, subscriptions and advanced analytics.
4. Technology Stack
Backend: Python, FastAPI, PostgreSQL, SQLAlchemy 2, Alembic, Pydantic.
Frontend: Next.js, React, TypeScript, Tailwind CSS, shadcn/ui.
Testing: Pytest, HTTPX.
Infrastructure: Docker Compose, GitHub Actions, Ruff.
Background jobs: Celery and Redis.
Architecture: modular monolith. Avoid microservices and premature abstractions.
5. Database Models and Relationships
The following is the proposed initial database design.
User
* id (UUID)
* email
* hashed_password
* is_active
* created_at
Relationships:
* User 1 → N Trips
* User 1 → N RefreshTokens
RefreshToken
* id
* user_id
* token_hash
* expires_at
* revoked_at
Relationship: N → 1 User.
Trip
* id
* user_id
* title
* description
* start_date
* end_date
* primary_currency
* created_at
* updated_at
Relationships:
* Trip 1 → N Destinations
* Trip 1 → N ItineraryDays
* Trip 1 → N SavedPlaces
* Trip 1 → 1 TripBudget
* Trip 1 → N Expenses
* Trip 1 → N Documents
Destination
* id
* trip_id
* city
* country
* country_code
* arrival_date
* departure_date
* position
Relationship: N → 1 Trip.
ItineraryDay
* id
* trip_id
* date
* notes
Relationships:
* N → 1 Trip
* 1 → N Activities
Activity
* id
* itinerary_day_id
* saved_place_id (nullable)
* title
* description
* start_time
* end_time
* position
Relationships:
* N → 1 ItineraryDay
* N → 0..1 SavedPlace
SavedPlace
* id
* trip_id
* destination_id (nullable)
* name
* description
* address
* latitude
* longitude
* provider
* external_place_id
Relationships:
* N → 1 Trip
* N → 0..1 Destination
* 1 → N Activities
TripBudget
* id
* trip_id
* planned_amount
Relationship: 1 → 1 Trip. Uses the trip’s primary currency.
Expense
* id
* trip_id
* destination_id (nullable)
* title
* amount
* currency
* exchange_rate_used
* converted_amount
* expense_date
* category
* notes
* created_at
Relationships:
* N → 1 Trip
* N → 0..1 Destination
Store original amounts and the conversion rate used. Use Decimal/Numeric for monetary values.
CurrencyRate
* id
* base_currency
* target_currency
* rate
* provider
* updated_at
Purpose: cache exchange rates and support automatic conversion and manual adjustments.
Document
* id
* trip_id
* title
* document_type
* storage_type
* file_key (nullable)
* external_url (nullable)
* original_filename (nullable)
* mime_type (nullable)
* expiry_date (nullable)
* created_at
Relationship: N → 1 Trip.
Document types: ticket, booking, insurance, visa, other.
Storage types: uploaded file or external link.
Store files in private object storage; PostgreSQL stores metadata and file references.
Database Rules
* UUID primary keys.
* Foreign keys and appropriate indexes.
* Explicit deletion/cascade rules.
* Timezone-aware timestamps.
* Database constraints for important invariants.
* Every trip operation must verify ownership.
* Private documents must never be publicly accessible.
6. API Endpoints
All endpoints use the /api/v1 prefix.
Authentication
* POST /auth/register
* POST /auth/login
* POST /auth/refresh
* POST /auth/logout
* GET /auth/me
Trips
* GET /trips
* POST /trips
* GET /trips/{trip_id}
* PATCH /trips/{trip_id}
* DELETE /trips/{trip_id}
Destinations
* GET /trips/{trip_id}/destinations
* POST /trips/{trip_id}/destinations
* PATCH /destinations/{destination_id}
* DELETE /destinations/{destination_id}
Itinerary
* GET /trips/{trip_id}/itinerary
* POST /trips/{trip_id}/days
* PATCH /itinerary/days/{day_id}
* DELETE /itinerary/days/{day_id}
* POST /itinerary/days/{day_id}/activities
* PATCH /itinerary/activities/{activity_id}
* DELETE /itinerary/activities/{activity_id}
* PATCH /itinerary/days/{day_id}/activities/reorder
Places
* GET /places/search
* GET /trips/{trip_id}/places
* POST /trips/{trip_id}/places
* PATCH /places/{place_id}
* DELETE /places/{place_id}
External place search must use a provider adapter.
Budget and Expenses
* GET /trips/{trip_id}/budget
* PUT /trips/{trip_id}/budget
* GET /trips/{trip_id}/expenses
* POST /trips/{trip_id}/expenses
* PATCH /expenses/{expense_id}
* DELETE /expenses/{expense_id}
* GET /currencies/rates
Documents
* GET /trips/{trip_id}/documents
* POST /trips/{trip_id}/documents/upload
* POST /trips/{trip_id}/documents/link
* GET /documents/{document_id}
* DELETE /documents/{document_id}
All endpoints require validation, authorization, consistent error responses and automated tests.
7. Celery Tasks
Use Celery and Redis for background processing.
Initial task:
sync_exchange_rates
* Fetch exchange rates from the selected provider.
* Update CurrencyRate records.
* Run periodically, approximately once per day.
* Retry temporary failures.
* Log errors.
Use Celery Beat for scheduling.
Other background tasks are postponed until required by an approved feature.
8. Implementation Roadmap
Implement features in this order:
Phase 1 — Foundation
* Create repository and project structure.
* Configure FastAPI, Next.js and PostgreSQL.
* Configure Docker Compose and environment variables.
* Set up Ruff, Pytest and GitHub Actions.
Phase 2 — Database and Authentication
* Implement User and RefreshToken.
* Create migrations.
* Implement registration, login, refresh, logout and current-user endpoint.
* Add tests.
Phase 3 — Trip Management
* Implement Trip model and CRUD.
* Validate dates and currency.
* Enforce ownership.
* Add tests.
Phase 4 — Destinations
* Implement Destination model and CRUD.
* Support multiple destinations and ordering.
* Add date validation and tests.
Phase 5 — Itinerary
* Implement ItineraryDay and Activity.
* Add daily plans and activity CRUD.
* Support activity ordering.
* Add tests.
Phase 6 — Places
* Select map and place-search provider.
* Implement provider adapter.
* Implement SavedPlace CRUD and external search.
* Add tests.
Phase 7 — Budget and Currency
* Implement TripBudget and Expense.
* Support multiple currencies.
* Integrate exchange-rate API.
* Implement manual rate adjustment and conversion snapshots.
* Add Celery, Redis and periodic rate synchronization.
* Add calculation tests.
Phase 8 — Documents
* Select object storage provider.
* Implement Document model.
* Add file uploads and external links.
* Validate file types, sizes and access permissions.
* Add tests.
Phase 9 — Frontend
* Authentication screens.
* Dashboard and trip management.
* Destinations and itinerary.
* Map and saved places.
* Budget and expenses.
* Document management.
* Loading, empty and error states.
Phase 10 — Production
* Security and permissions review.
* Full test suite.
* Production deployment.
* Logging, backups and monitoring.
* Documentation.
Phase 11 — Beta
* Invite initial users.
* Collect feedback.
* Fix critical issues.
* Evaluate the MVP before adding paid features.
9. Engineering Requirements
* Use feature branches and Pull Requests.
* Every meaningful feature needs automated tests.
* Database changes require Alembic migrations.
* Review code before merging into main.
* Never merge without user approval.
* Keep business logic separate from API routes.
* Avoid unnecessary abstractions.
* Do not claim tests pass without running them.
10. Open Technical Decisions
These must be resolved before implementing the relevant features:
* Map and place-search provider.
* Exchange-rate API provider.
* Object storage provider.
* Authentication token strategy and security details.
* File upload limits and validation rules.
* Final database constraints and deletion behavior.
11. Definition of Done
A feature is complete when:
* Requirements are implemented.
* Migrations are included when needed.
* Validation and authorization work.
* Automated tests pass.
* Linting passes.
* API documentation is updated.
* Changes are reviewed and approved.
