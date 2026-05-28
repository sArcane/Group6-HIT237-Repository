# Project Brief: Listening to NT's Disappearing Animals

## Overview
The application being created is a Django-based web application designed to acoustically monitor the Northern Territories' endangered native species. Allowing researchers and users to upload, review and analyse audio recordings and data of the native speicies.

Continuing from the previous iteration the app has now been extended with user authentication, a service layer, structured exceptions handling, and a test suite.

## Problem context
The Northern Territory is facing an unprecedented convergence of environmental pressures, making biodiversity monitoring urgent and politically significant. Many of the NT's unique animal species are under stress. Acoustic monitoring of these species allows a scalable and non-invasive way to track these species across the Territory, where traditional methods are logistically prohibitive

## Architecture

The project uses Django models to represent the main data, including species, recordings, locations, and anomaly flags.

Custom QuerySets and managers are used to keep reusable database query logic close to the models.

Views handle web requests, form submissions, redirects, and rendering templates.

A service layer has been added in blog_app/services.py to handle important workflows such as submitting recordings, flagging recordings, and reviewing recordings. This keeps the views cleaner and makes the business logic easier to test.

Authentication and permission logic is handled using Django’s built-in authentication system and a central access policy in blog_app/authorization.py.

## Functional Requirements
Users should be able to log audio recordings of the species calls and include metrics and data such as, the date, location, species and confidence score of the recording. Users should also be able to view recent submissions on a timeline and be able to flag anomalies in a recording.

## Features
The app features:

- Species and recording management

- Recording list and detail pages

- Filtering recordings by species, confidence score, and flagged status

- User registration, login, and logout

- Authenticated recording submission

- Owner-based access to recordings

- Reviewer permissions for reviewing or managing flagged recordings

- Anomaly flagging for suspicious recordings

- Species analytics and recording statistics

- Structured exception classes for application errors

- Tests for models, services, views, permissions, and exceptions

## Testing

The project includes a test suite covering the main parts of the application. Tests are used to check model/queryset behaviour, service functions, views, permission boundaries, and custom exceptions.

This helps confirm that the application works correctly and that important access rules are enforced.

## Design Approach
- Django MTV architecture
- Object-oriented design with seperate models
- Reusable query logic
- User-focused templates
