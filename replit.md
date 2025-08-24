# E-Library System

## Overview

This is a comprehensive digital library management system built with Flask that allows users to browse, search, and download books. The application features role-based access control with separate interfaces for regular users and administrators. Regular users can browse the library, search for books, and download content, while administrators have additional capabilities to manage books, users, categories, and view download analytics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templating with Flask
- **UI Framework**: Bootstrap 5 with dark theme support
- **CSS Framework**: Custom CSS with Bootstrap integration
- **JavaScript**: Vanilla JavaScript with Bootstrap components
- **Responsive Design**: Mobile-first approach with responsive layouts

### Backend Architecture
- **Web Framework**: Flask with modular structure
- **Authentication**: Flask-Login for session management
- **Form Handling**: Flask-WTF with WTForms for form validation
- **File Handling**: Werkzeug utilities for secure file uploads
- **Password Security**: Werkzeug password hashing

### Data Storage Solutions
- **ORM**: SQLAlchemy with Flask-SQLAlchemy integration
- **Database**: SQLite (default) with PostgreSQL support via DATABASE_URL
- **File Storage**: Local filesystem storage for uploaded books
- **Models**: User, Book, Category, and Download entities with proper relationships

### Authentication and Authorization
- **Session Management**: Flask-Login for user authentication
- **Password Hashing**: Werkzeug secure password hashing
- **Role-Based Access**: Admin and regular user roles with different permissions
- **Login Protection**: Route-level authentication decorators

### Application Structure
- **Factory Pattern**: Application factory with create_app() function
- **Blueprint Architecture**: Modular route organization (implied from structure)
- **Form Classes**: Separate form definitions with validation
- **Model Layer**: SQLAlchemy models with relationships
- **Static Assets**: CSS, JavaScript, and uploaded files organization

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering
- **Werkzeug**: WSGI utilities and security functions

### Frontend Dependencies
- **Bootstrap 5**: UI framework (CDN)
- **Font Awesome 6**: Icons library (CDN)
- **Bootstrap JavaScript**: Interactive components

### Database Support
- **SQLite**: Default database (built-in Python)
- **PostgreSQL**: Optional via DATABASE_URL environment variable
- **SQLAlchemy**: Database abstraction layer

### File Upload System
- **Local File Storage**: Books stored in uploads directory
- **File Security**: Werkzeug secure filename generation
- **File Size Limits**: 50MB maximum upload size

### Environment Configuration
- **Environment Variables**: SESSION_SECRET, DATABASE_URL
- **Proxy Support**: ProxyFix middleware for deployment
- **Upload Directory**: Configurable upload paths