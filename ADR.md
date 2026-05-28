# Architectual Design Records

## ADR-001: Use seperate models such as "species, "location", "Recording", and "AnomalyFlag"

**Status:** Accepted

### Context:
The app needs to manage multiple concepts such as animal, species, recording locations, uploaded audio recordings, and anomaly reports. Therefore a descion needed to be made on whether to store the information inside one large model or into seperate specific classes

### Alternatives Considered:
**Option 1: Store the information in a single large model**

Pros:
    -Faster to scaffold initially
    -fewer files

Cons:
    -Harder to maintain
    -Repeated information
    -Poor object-oriented decomposition


### Decision
The app will use seperate models for Species, Location, Recording, and AnomalyFlag

### Rationale
This option was chosen as seperating the models will improve its maintainablity and its object-oriented decomposition. This alighns with Django's design philosophies of explicit is better than implicit. it also allows reusable data models and possibly reduces the redundancy of the data

### Code Reference
- 'Assessment_2/blog_app/models.py:17-37'
- 'Assessment_2/blog_app/models.py:40-44'
- 'Assessment_2/blog_app/models.py:47-66'
- 'Assessment_2/blog_app/models.py:89-105'

### Consequences

Pros:
    -Better encapsulation
    -reduced redundancy
    -Easier extension and querying
    -better scalability

Cons:
    -More relationships to define and manage

---

## ADR-002: Species model design

**Status:** Accepted

### Context:
The app requires a way to store species information such as common names, scientific names, and conservation status. This data must be reusable across multiple recordings


### Alternatives Considered:
**Option 1: store species name as plain text in recoding model**

Pros:
    - Simple Implemeentation

Cons:
    - Data Duplication and inconsistency

**Option 2:Use an external API (no local storage)**

Pros:
    - Up-to-date data

Cons:
    - Requires internet and is more complex

### Decision
A Species model was created to  store species data to avoid duplication

### Rationale
This model was created as it allows the entity data to be reusable across multiple recordings. The other options were either too complex for the task or would lead to redundant data. By creating the model this way it follows Django's design prinicple of consistency. This also supports efficient querying and filtering of species and conservation status.

### Code Reference
- 'Assessment_2/blog_app/models.py:17-37'

### Consequences

Pros:
    - Improved data consistency
    - Easier filtering and querying of animal data

Cons:
    - Requires managing relationships with ForeignKey

## ADR-003: AnomalyFlag Model for recording validations

**Status:** Accepted

### Context:
The Application requires a way to flag recordings with issues such as incorrect/missing data, or incoherent noise and be able to flag them showing who flagged it and why 


### Alternatives Considered:
**Option 1:A single boolean field in Recording Model**

Pros:
    -Easy to implement

Cons:
    - Cannot store multiple flags or details 

### Decision
A seperate AnomalyFlag model was created which allows multiple flags per recoding, which allows the tracking of the type of flag, the description of the flag and the user who flagged the recording

### Rationale
A dedicated model was created as it allows for more detailed information such as detailed reports and tracking the user. A single boolean field in the recording model would have been insufficient in capturing the level of detail for this task.

### Code Reference
- 'Assessment_2/blog_app/models.py:89-105'

### Consequences

Pros:
    - Supports multiple flags per recording
    - Allows details and tracking

---

## ADR-004: Use of ForeignKey relationships

**Status:** Accepted

### Context:
Each recording traces back to one user, one species, and one location, and each anomaly flag belongs to one recording linking back to one user. Therefore the app needs a way to represent one-to-many relationships

### Alternatives Considered:
**Option 1: Store related names as text/integer fields**

Pros:
    - Simplier to implement

Cons:
    - Risk of inconsistent data
    - Harder to ORM query
    - No referential integrity

### Decision
ForeignKey fields were used to to connect a recording with the data of the species and user, and connects an anomaly flag with a recording and user

### Rationale
Foreign Keys were used as these relationships are one-to-many. it also improves data integrity and makes ORM queries cleaner.

### Code Reference
- 'Assessment_2/blog_app/models.py:71-73'
- 'Assessment_2/blog_app/models.py:98-99'

### Consequences

Pros:
    - Better data integrity
    - Better queries and filter
    - Better navigation between related objects

---

## ADR-005: Centralised Query Logic Using Custom QuerySets, Managers, and View Mixins

**Status:** Accepted

### Context:
The application requires consistent and reusable query logic for retrieving recordings, applying filters and calculating quality. These queries are used across multiple views. Without centralisation, the query logic would be duplicated across views, therefore increasing maintenance, reducing consistency and potentially causing performance issues.

### Alternatives Considered:
**Option 1: Keep query logic in each view**

Pros:
    - Simple

Cons:
    - Duplacted logic across views
    - Harder to maintain/update

**Option 2: Use helper functions for query logic**

Pros:
    - Reduces duplication compared to option 1
    - Easier to reuse

Cons:
    - Not fully integrated with DJango QuerySet chaining
    - Less expressive
### Decision
Create custom QuerySets and managers in the models, keep query composition close to the model layer so that views operate on consistent data logic, implemented a reusable view mixin and used ORM optimisation technigues 

### Rationale
This option was chosen as query logic is inherently correlated to the data models and should not be duplicated across multiple views. By encapsulating the query behaviour inside the QuerySets and managers it allows that the data access is consistent, reusable and mainatainable.

The view mixins ensures that the views use the same query structure. Therefore avoiding duplication and meaning more consistent behaviour across the app.

The ORM optimisations reduces database queries and improves performance.

### Code Reference
- 'Assessment_2/blog_app/models.py:6-15'
- 'Assessment_2/blog_app/models.py:48-69'
- 'Assessment_2/blog_app/views.py:13-15'
- 'Assessment_2/blog_app/views.py:18-40'
- 'Assessment_2/blog_app/views.py:43-53'

### Consequences

Pros:
    - Reusable and testable query logic
    - Reduced N+1 query issues through ORM optimisation
    - Cleaner and more maintainable views
    - Consistent data access across multiple pages
    - Strong demonstration of Django QuerySet API usage

Cons:
    - Slightly more indirection than simple function-based views.
    - Analytics responses rely on ORM-generated SQL that should be profiled if dataset grows significantly.

---

## ADR-006: Activity Timeline

**Status:** Accepted

### Context:
The app needs a central page where users can view the submitted species recordings and be able to identify anomalies

**Option 1: Create a simple list to display recordings**

Pros:
    - Easy to implement

Cons:
    - Too simple
    - not expressive

### Decision
The recording_list.html template was created as a dashboard style activity timeline that shows the recordings with instant audio playback and shows flagged recordings

### Rationale
A dashboard layout allows users to efficiently access the information and recordings.

### Code Reference
- 'Assessment_2/blog_app/templates/recording_list.html

### Consequences

Pros:
    - Faster data review and anomaly detection
    - Improved usability for researchers

Cons:
    - More complex than a simple list

---

## ADR-007: Use of Django form rendering for recording submissions

**Status:** Accepted

### Context:
The app needs a form interface for users to submit new recordings with the animal data

### Decision
The recording_form.html template uses Django's form rendering instead of manually coding each input

### Rationale
Ensure consistency with teh frontend and backend validation rules, follows Django's DRY (Don’t Repeat Yourself) philosophy as it allows the html to remain skinny and ensures that the data is synced with the database

### Code Reference
- 'Assessment_2/blog_app/templates/recording_form.html'

### Consequences

Pros:
    - Cleaner and more maintainable forms
    - Consistent validation with models

Cons:
    - Less flexibility than fully custom HTML forms

---

## ADR-008: Research Detail View

**Status:** Accepted

### Context:
Researchers need a detailed page to review the recordings, anomalies, species data and metadata


### Decision
The recording_detail.html template provides the audio of a recording, its metadata, anomaly flags, and species details

### Rationale
Having a place that displays all of the information in one place allows users to make informed and educated decisions.

### Code Reference
- 'Assessment_2/blog_app/templates/recording_details.html'

### Consequences

Pros:
    - Encapsulates related data from multiple models to easily link models
    - Displays metadata, such as scientific names and conservation statuses to help researchers be informed in their decisions when flagging data.

Cons:
    - Complex template structure

---

## ADR-009: User Authentication and Object-Level Authorization Architecture

**Status:** Accepted

### Context:
The project requires controlled access to recordings, anomaly notes, and analytics data. The previous implementation allowed broad read access through list/detail pages and did not explicitly enforce model-level permissions for cross-user access.

### Threat Model and Security Risks:
- Insecure direct object references (IDOR): a user could attempt to access another user's recording by changing IDs in URLs.
- Sensitive data leakage: anomaly descriptions can include reviewer notes that should not be exposed to all authenticated users.
- Privilege escalation: general authenticated users should not automatically gain analytics visibility or reviewer capabilities.
- Weak observability for denied access: without explicit denial logging, abuse patterns are hard to detect during testing.

### Alternatives Considered:
**Option 1: Role checks only in templates**

Pros:
        - Fast to implement

Cons:
        - No backend enforcement
        - Vulnerable to direct URL access

**Option 2: Endpoint-level login only (no object scoping)**

Pros:
        - Basic access control

Cons:
        - Authenticated users can still enumerate other users' objects
        - No granular reviewer controls

### Decision
Implement a layered architecture across models, views, and middleware:
- Models define explicit custom permissions for cross-user viewing, review operations, and analytics access.
- Views enforce authentication and object-level queryset scoping via a dedicated policy module.
- Middleware audits authorization denials and adds conservative browser policy headers.

### Rationale
This architecture applies defense in depth:
- Model permissions provide a stable authorization vocabulary (`view_all_recordings`, `review_recordings`, `view_species_analytics`).
- View-layer policy enforces owner-based access by default and grants broader access only with explicit permissions.
- Middleware records denied requests for security review and supports threat-informed monitoring.

The approach is designed to minimize accidental data exposure while preserving clear paths for privileged reviewer workflows.

### Code Trace (Models -> Views -> Middleware)
- Models and permission definitions:
    - 'Assessment 2/blog_app/models.py'
    - 'Assessment 2/blog_app/migrations/0002_authorization_permissions.py'
- Authorization policy and object-level scoping:
    - 'Assessment 2/blog_app/authorization.py'
- Enforced in views (login + scoped queryset + permission checks):
    - 'Assessment 2/blog_app/views.py'
- Denial auditing and policy headers:
    - 'Assessment 2/blog_app/middleware.py'
- Middleware registration and auth defaults:
    - 'Assessment 2/project_blog/settings.py'

### Consequences

Pros:
        - Prevents cross-user recording access by default
        - Protects reviewer-only anomaly details and analytics data
        - Improves traceability of authorization denials
        - Provides clear, testable permission boundaries

Cons:
        - Additional complexity in permission setup and test fixtures
        - More explicit user onboarding needed to assign reviewer permissions

### Verification Evidence
- Focused authorization tests were added and validated:
    - 'Assessment 2/blog_app/test_authorization.py'
    - Coverage includes login requirement, owner-scoped queries, reviewer access, and analytics permission enforcement.

---

## ADR-010: Use of Service Layer for Recording Workflow

**Status:** Accepted

### Context:
As the application now needs to handle submitting recordings, flagging recordings, and reviewing flagged recordings. Flagging a recording would require creating an anomaly flag, updating the recording as flagged, finding the user that performed the action, then making sure the database is consistent. If the logic stays in the view it would make it the views to large, forgoing Django's skinny views philosophies

**Option 1: Keep Logic inside of the views**

Pros:
    - Simple to understand
    - Less files

Cons:
    - Views become fat
    - more difficult to test
    - May be duplicated logic
    - Harder to maintain

**Option 2: Use function-based services (chosen)**

Pros:
    - Keeps views skinny
    - Encapsulates workflow in a dedicated service module
    - easier to test
    - better readability

Cons:
    - Adds another layer to the app
    - Could become disorganised

**Option 3 Use Class-based services**

Pros:
    - Groups related services in a class
    - Encapsulates workflow in a dedicated service module
    - easier to test
    - better readability

Cons:
    - Too complex for scope of the app

### Decision
A function-based service layer was created to handle the actions of submitting recordings, flagging recordings and reviewing recordings. This function later contains functions such as submit_recording(), flag_recording(), and review_recording().

This makes it so that the views are still responsible for handling HTTP requests, forms, redirects adn redering templates, while the service layer is responsible for the actions that would involve multiple models or updates to the database.

### Rationale
A function-based service layer was created due to the app needing more functionality. Using this layer improves the separation of concerns while keeping the code simple for the current scope of the project. it also allows the vies to remain focused on HTTP requests while the service layers handle reusable logic.

### Code Reference
- Assessment_2/blog_app/services.py

- Assessment_2/blog_app/services.py: submit_recording()

- Assessment_2/blog_app/services.py: flag_recording()

- Assessment_2/blog_app/services.py: review_recording()

- Assessment_2/blog_app/views.py

- Assessment_2/blog_app/models.py


### Consequences

Pros:
    - Keeps views skinny
    - makes testing the added functions easier
    - reduces duplicated logic
    - Clear seperation between views, services, models and Querysets

Cons:
    - Adds an extra layer to the app
    - function based service could be insufficient if the app grows larger

---

## ADR-011: Exception Handling for Application Errors

**Status:** Accepted

### Context:
The application is now more complex now with added features, such as users being able to submit recordings, flag recordings and review the recordings. all these features can fail for reasons such as, missing recordings, invalid speices or location data, invalid form input, failed file uploads, and permission issues. 

Without structured exception handling, errors may be handled inconsistently, therefore a decsision needed to be made on how the app should handle specific errors while still working with Django's build-in form, validation, and permission handling.

**Option 1: Only use generic python exception handling**

Pros:
    - Simple to implement
    - No extra file or classes

Cons:
    - Non-descriptive error types
    - More difficulty analysing application failiure
    - More difficulty testing specific failiure scenarios
    - Does not provide error codes

**Option 2: Use only Django built-in exceptions**

Pros:
    - Integrates naturally with Django views, forms, and permissions
    - Certain terms are already understood by Django
    - Simple and reliable

Cons:
    - Some error cases still may be represented too generally
    - Does not fully describe the projects domain errors

**Option 3: Create a custom exception hierarchy for application-specific errors (chosen)**

Pros:
    - Gives clear names to domain errors
    - Supports structerd error codes and details
    - makes exception behaviour easier to test directly
    - Scalable
    - Improves documentation of expected failure cases

Cons:
    - Adds more classes

### Decision
A custom exception hierarchy was added to represent application-specific errors. A base exception was created "BlogAppExceptions" then specific exception groups were created for different parts of the applications, each of these exceptions can store a readable message, error code and a Http status code with additional details. The application still uses Django exceptions such as ValidationError and PermissionDenied in the service and views.

### Rationale
This option was chosen as the project neded clearer and more testable error handling. With the addition of the new layers and feature more failiure cases woould appear. The custom exception hierarchy gives the app a place to define these errors, further supporting the separation of concerns. Django's built-in exceptions are still used as PermissionDenied and ValidationError are already understood by Django.

### Code Reference
- Assessment 2/blog_app/exceptions.py

- Assessment 2/blog_app/exceptions.py: BlogAppException

- Assessment 2/blog_app/exceptions.py: RecordingNotFound

- Assessment 2/blog_app/exceptions.py: RecordingValidationError

- Assessment 2/blog_app/exceptions.py: InvalidConfidenceScore

- Assessment 2/blog_app/exceptions.py: SpeciesNotFound

- Assessment 2/blog_app/exceptions.py: LocationNotFound

- Assessment 2/blog_app/exceptions.py: InvalidFormData

- Assessment 2/blog_app/exceptions.py: FileUploadError

- Assessment 2/blog_app/services.py

- Assessment 2/blog_app/views.py

- Assessment 2/blog_app/test_exceptions.py

### Consequences

Pros:
    - Gives app clear structure for application specific errors
    - Makes errors easier to understand and document
    - Allows exceptions to include error codes, status codes, and extra details
    - Makes exceptions independently testable

Cons:
    - Adds another file
    - There is still the use of built-in Django exceptions

---

## ADR-012: Testing suite for models, service, views, permissions, and exceptions

**Status:** Accepted

### Context:
A testing suite needed to be made that covers the models, services, views and permissions as the app has grown. Testing is crucial now that many parts of the app depend on each other.

**Option 1: Manually test the application in the browser**

Pros:
    - Easy to do during development
    - Does not require writing test code
    - Useful for checking visual layout
Cons:
    - Easy to miss edge-cases
    - Does not prove service logic works independently
    - Does not demonstrate permissions
    - Unfitting for scope of the app

**Option 2: Use a layerd Django test suite (Chosen)**

Pros:
    - tests models. querysets, views, services, permissions, and exceptions
    - provides stronger evidence of working architecture
    - allows service functions to be tested independently
    - more explicit permission boundries

Cons:
    - takes longer to write and maintain
    - tests must be updated when business rules change

### Decision
A layered Django test suite was used, which covers different layers of the application such as models, querysets, services, views, autherisation and permissions, and exceptions.

### Rationale
This option was chosen as the app now contains serveral architectural layers, requiring a layered Django test suite, being able to test each layer independently is important as it allows us to verify that each layer works correctly

### Code Reference
- Assessment 2/blog_app/tests.py

- Assessment 2/blog_app/tests.py: RecordingQuerysetTests

- Assessment 2/blog_app/tests.py: RecordingViewTests

- Assessment 2/blog_app/tests.py: ServiceTests

- Assessment 2/blog_app/test_authorization.py

- Assessment 2/blog_app/test_authorization.py: AuthorizationArchitectureTests

- Assessment 2/blog_app/test_exceptions.py

### Consequences
Pros:
    - provides evidence that service layer works independently form the views
    - tests reusable queryset behaviours
    - tests custom exception hierarchy
    - makes application safer to change for further development

Cons:
    - more test files must be maintained
    - tests may fail if rules change without updating tests
    - some behaviours still may be better to test manually on a browser

---

## ADR-013: Addition of authenticated recording and review features

**Status:** Accepted

### Context:
A new feature was required to support a more realistic workflow where users can log in, submit recordings, flag suspicious or anomalous recordings, and allow reviewer-style users to managae or review flagged content

**Option 1: Add authenticated recording submissions and review workflows**

Pros:
    - extends on the original purpose of the app
    - Makes authentication meaningful as users can own submitted recordings
    - supports permission boundries between normal users and superusers
Cons:
    - requires changes in models, views, services, templates, permissions, and tests


### Decision
These features were added as they extend on the orignal purpose of the app, this now supports a more coherent workflow where users can interact with teh recordings, authenticated users can submit recordings, and super users can directly manage flagged recordings such as deleting them.

### Rationale
These features were added as they improve the functionality of the app

### Code Reference
- Assessment 2/accounts/templates/registration/login.html

- Assessment 2/accounts/templates/registration/register.html

- Assessment 2/accounts/views.py

- Assessment 2/accounts/views.py: RegisterView

### Consequences
Pros:
    - Feature growth from previous iteration
    - Give a purpose to authentication
    - gives service layer meaningful workflow to encapsulate

Cons:
    - increases complexity of the application
    - requires more carefule permission handling