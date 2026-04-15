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
