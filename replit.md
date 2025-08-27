# Overview

This is a comprehensive legal case management system built in Arabic for the Yemeni legal system. The application serves multiple user types including judges, lawyers, clients, and law students. It provides functionality for case management, court directory, lawyer directory, document templates, calendar scheduling, and comprehensive reporting. The system is designed to digitize and streamline legal processes in Yemen with support for Arabic language and RTL (right-to-left) text direction.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **UI Framework**: Bootstrap 5 with RTL support for Arabic layout
- **JavaScript**: Vanilla JavaScript with Bootstrap components, FullCalendar for scheduling
- **CSS**: Custom styles optimized for Arabic text and RTL layout
- **Icons**: Font Awesome icon library

## Backend Architecture
- **Web Framework**: Flask with modular blueprint structure
- **Authentication**: Flask-Login for session management with role-based access control
- **Form Handling**: Flask-WTF with WTForms for form validation and CSRF protection
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy integration
- **File Uploads**: Werkzeug utilities for secure file handling
- **Security**: Password hashing, proxy fix middleware for deployment

## Data Storage Solutions
- **Primary Database**: SQLite for development (configurable via DATABASE_URL environment variable)
- **Database Models**: User management, court directory, case management, appointments, documents, lawyer profiles
- **File Storage**: Local filesystem with organized upload directories
- **Session Storage**: Flask sessions with configurable secret key

## Authentication and Authorization
- **User Roles**: Admin, judge, lawyer, client, student with role-based permissions
- **Session Management**: Flask-Login with user loader functionality
- **Password Security**: Werkzeug password hashing with salt
- **Access Control**: Route-level protection based on user roles and authentication status

## Core Modules
- **Case Management**: Complete lifecycle management from creation to closure
- **Court Directory**: Comprehensive database of Yemeni courts with location services
- **Lawyer Directory**: Professional profiles with specializations and ratings
- **Document Templates**: Legal document generation with customizable templates
- **Calendar System**: Appointment scheduling with conflict detection
- **Reporting Dashboard**: Analytics and performance metrics
- **Client Portal**: Self-service interface for case tracking and document access

## Design Patterns
- **MVC Pattern**: Clear separation between models, views, and controllers
- **Factory Pattern**: Application factory for configuration management
- **Form Objects**: Dedicated form classes for validation and rendering
- **Template Inheritance**: Base template with extensible blocks for consistent UI
- **Utility Functions**: Centralized helper functions for common operations

# External Dependencies

## Python Packages
- **Flask**: Core web framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering
- **Werkzeug**: WSGI utilities and security functions

## Frontend Libraries
- **Bootstrap 5**: UI framework with RTL support
- **Font Awesome**: Icon library
- **FullCalendar**: Calendar and scheduling component
- **Chart.js**: Data visualization for reports

## Database Configuration
- **SQLite**: Default development database
- **PostgreSQL**: Production-ready option via DATABASE_URL configuration
- **Connection Pooling**: Configured for production deployment with pool recycling

## Deployment Dependencies
- **ProxyFix**: Werkzeug middleware for handling proxy headers
- **Environment Variables**: Configuration via environment for security and deployment flexibility
- **File Upload Handling**: Configurable upload directories with size limits

## Localization Support
- **Arabic Language**: Native Arabic text support throughout the interface
- **RTL Layout**: Right-to-left text direction for proper Arabic display
- **Date Formatting**: Arabic date formatting utilities
- **Cultural Adaptations**: Yemeni legal system specific terminology and processes