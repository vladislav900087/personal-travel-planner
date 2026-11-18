Personal Travel Planner — Project Guide

1. Product

We are building a web application for people who plan trips independently.

The application helps users organize:

* Trips and destinations.
* Daily itineraries.
* Places to visit.
* Travel budgets and expenses.
* Tickets, bookings and travel documents.
* Collaborative trip planning.

We do not sell tickets or hotel reservations.

2. Target users

People who travel alone, with a partner, or with friends.

The first version focuses on individual trip planning. We will validate the product with real users before expanding it.

3. Business model

Freemium subscription.

Free

* Up to 3 active trips.
* Trip and destination management.
* Daily itineraries.
* Saved places.
* Basic budget and expense tracking.
* Limited document storage.

Plus — proposed pricing

* 1,490 KZT/month.
* 11,900 KZT/year.

Plus includes:

* Unlimited trips.
* Collaborative planning.
* PDF export.
* Extended document storage.
* Additional planning features.

Prices and limits are hypotheses. Validate demand before implementing payments.

4. Technology stack

Backend:

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy 2
* Alembic
* Pydantic
* Pytest
* HTTPX

Frontend:

* Next.js
* React
* TypeScript
* Tailwind CSS
* shadcn/ui

Infrastructure:

* Docker Compose
* GitHub Actions
* Ruff
* Redis and Celery when background processing is needed
* S3-compatible file storage when document uploads are implemented

Maps:

* Leaflet
* OpenStreetMap

Use a modular monolith. Do not introduce microservices.

5. Architecture

Use pragmatic layered architecture.

Suggested backend structure:

* api/ — HTTP routes and dependencies.
* application/ — use cases and business workflows.
* domain/ — core business rules and entities.
* infrastructure/ — database, external services and storage.
* models/ — SQLAlchemy persistence models.
* schemas/ — Pydantic request and response schemas.
* core/ — configuration, security and shared infrastructure.
* tasks/ — background jobs.
* tests/ — unit, integration and API tests.

Keep dependencies directed inward. Domain logic must not depend on FastAPI or database implementation details.

Do not create unnecessary abstractions. Architecture must help us change the product safely.

6. Core domain

Initial entities:

* User
* Trip
* Destination
* ItineraryDay
* ItineraryItem
* SavedPlace
* Expense
* Document

Later entities:

* TripMember
* Subscription
* Payment
* Notification

Define relationships and ownership carefully. A user must never access another user’s private trip data.

7. Engineering principles

KISS: choose the simplest solution that works.

DRY: avoid duplicated business logic. Do not create abstractions for code used only once without a good reason.

SOLID: apply principles where they improve separation and maintainability.

Security: validate input, protect user data, hash passwords securely, enforce authorization on the backend, and never expose secrets.

Testing: test expected behavior, edge cases, permissions and data isolation. Do not chase coverage numbers.

Code quality: type hints, clear names, small focused functions, useful errors and readable code.

8. Git workflow

* main is always deployable.
* Create a feature branch for each task.
* Use meaningful commits.
* Open a Pull Request.
* Run tests and review changes.
* Merge only after approval.
* Delete completed feature branches.

Commit prefixes:

* feat:
* fix:
* test:
* refactor:
* docs:
* chore:
* ci:

Never force-push or rewrite history without an explicit reason.

9. Development roadmap

1. Product discovery and requirements.
2. Repository and project foundation.
3. Database design and migrations.
4. Authentication and authorization.
5. Trip management.
6. Destinations and itinerary planning.
7. Saved places and map integration.
8. Budgets and expenses.
9. Frontend integration and polish.
10. Document storage and PDF export.
11. Collaborative planning.
12. Notifications and background tasks.
13. Subscription and billing.
14. Security review and production deployment.
15. Beta testing and user feedback.

Do not implement future stages prematurely.

10. AI collaboration

AI may write code, tests, configuration, documentation and UI.

Before each feature:

1. Explain the user problem.
2. Explain the proposed solution.
3. List affected components.
4. Identify risks.
5. Wait for approval when requirements or architecture are unclear.

After each feature:

1. Summarize changed files.
2. Explain important decisions.
3. Report tests and their results.
4. List known limitations.
5. Explain what the developer should understand.

Never claim tests passed unless they were actually executed.

11. Learning principles

The developer does not need to type every line manually.

The developer must understand:

* What a component does.
* How data moves through the application.
* Where business rules live.
* How authorization works.
* How to investigate and fix errors.
* How to verify behavior with tests.

Do not require memorization or manual rewriting for practice.

Explain unfamiliar concepts in simple language. Teach through real project tasks.

12. Definition of Done

A feature is complete when:

* Its requirements are met.
* Backend and frontend work together where applicable.
* Authorization is enforced.
* Relevant tests pass.
* No known critical errors remain.
* Changes are reviewed.
* Documentation is updated when necessary.
* The feature is merged through the agreed Git workflow.
