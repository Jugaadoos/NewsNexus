# AI News Hub - System Architecture Overview

> **Note:** Audience-specific derivative; canonical technical truth lives in `docs/product-foundation.md` and `docs/08-technical-design-document-tdd.md`.

## Overview

AI News Hub is a comprehensive news platform built with Streamlit that provides personalized news consumption through AI-powered features. The platform integrates multiple AI agents for content curation, blockchain-based review systems, geographic content filtering, and sophisticated user engagement tracking.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based web application
- **UI Components**: Custom components for news cards, map interfaces, and theme management
- **Responsive Design**: Wide layout with sidebar navigation and tabbed interfaces
- **Real-time Updates**: Dynamic content rendering with session state management

### Backend Architecture
- **Language**: Python 3.x
- **Database**: Environment-specific runtime policy (PostgreSQL for preprod/prod; SQLite fallback for local/dev when `DATABASE_URL` is unset) with SQLAlchemy ORM
- **AI Integration**: OpenAI GPT-4o for content analysis and generation
- **Async Processing**: AI agents running on asyncio for concurrent operations
- **Modular Design**: Service-oriented architecture with separate modules for distinct functionalities

### Data Storage Solutions
- **Primary Database**: PostgreSQL for user data, articles, analytics, and system records in preprod/prod; SQLite fallback in local/dev when `DATABASE_URL` is unset
- **Session Storage**: Streamlit session state for user preferences and temporary data
- **Blockchain Records**: Local blockchain simulation for review verification
- **File Storage**: Base64 encoding for images and media content

### Authentication and Authorization
- **Password Security**: PBKDF2 hashing with salted passwords
- **Role-Based Access**: Multiple user roles (reader, reviewer, editor, creator, journalist, publishing_partner, affiliate, admin)
- **Session Management**: Custom session handling with timeout controls
- **Multi-factor Authentication**: OTP integration for enhanced security

### External Service Integrations
- **AI Services**: OpenAI API for content processing and analysis
- **Payment Processing**: Stripe integration for subscriptions and payments
- **Geolocation**: IP-based location services and geocoding
- **News Sources**: RSS feed aggregation from major news outlets
- **Maps**: Geographic visualization and location-based content filtering

## Key Components

### AI Agent System
- **News Agent**: Automated news fetching and processing
- **Review Agent**: Content verification and quality assessment
- **Content Agent**: Summary generation and editorial opinions
- **Orchestrator**: Manages agent workflows and coordination

### Content Management
- **News Aggregator**: RSS feed processing and content extraction
- **AI Services**: Sentiment analysis, summarization, and categorization
- **Blockchain Review**: Decentralized content verification system
- **Geographic Services**: Location-based content filtering and mapping

### User Experience
- **Personalization**: AI-driven content recommendations
- **Color Psychology**: Dynamic theming based on content sentiment
- **Multi-tier Subscriptions**: Flexible pricing and feature access
- **Advertisement System**: Targeted ad placement with user preferences

### Analytics and Monitoring
- **User Analytics**: Comprehensive tracking of engagement metrics
- **Content Analytics**: Performance monitoring and trend analysis
- **Revenue Analytics**: Subscription and affiliate tracking
- **Geographic Analytics**: Location-based usage patterns

## Data Flow

1. **Content Ingestion**: RSS feeds → News Aggregator → AI Processing → Database Storage
2. **User Interaction**: User Request → Authentication → Personalization → Content Delivery
3. **AI Processing**: Content → Sentiment Analysis → Categorization → Review System
4. **Analytics Pipeline**: User Actions → Event Tracking → Analytics Processing → Dashboard Updates

## External Dependencies

### Core Services
- **OpenAI API**: Content analysis and generation
- **PostgreSQL**: Required primary data storage in preprod/prod
- **Stripe**: Payment processing
- **Geolocation APIs**: Location services

### Optional Integrations
- **Zoho Suite**: CRM and business management
- **PayPal**: Alternative payment processing
- **Google Maps**: Enhanced geographic features
- **Web3 Libraries**: Blockchain functionality

## Deployment Strategy

### Development Environment
- **Local Development**: Streamlit development server
- **Database**: PostgreSQL if `DATABASE_URL` is provided; otherwise SQLite fallback for local/dev
- **Environment Variables**: Configuration through .env files

### Production Deployment
- **Platform**: Replit or cloud hosting
- **Database**: Managed PostgreSQL service
- **Scaling**: Horizontal scaling through load balancing
- **Monitoring**: Comprehensive logging and error tracking

## Changelog

Changelog:
- July 04, 2025. Initial setup
- February 10, 2026. Stabilized core agent runtime: fixed DB session lifecycle, added SQLite default, added AI offline fallback mode, added one-cycle orchestrator/core runner, and resolved syntax errors that blocked compilation.

## Database mode selection (canonical policy)

Use the same runtime policy across all environments to avoid configuration drift:
- **preprod/prod:** `DATABASE_URL` must be set to a PostgreSQL connection string.
- **local/dev fallback:** if `DATABASE_URL` is unset, the app defaults to SQLite (`sqlite:///newsnexus.db`) via `database/connection.py`.
- **expected environment variables:** keep `DATABASE_URL` as the primary selector; keep `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD` populated for platform/tooling compatibility through `config.py`.

Rationale: one explicit policy reduces ambiguity, keeps local onboarding simple, and prevents environment-specific behavior mismatches during deployment.

## User Preferences

Preferred communication style: Simple, everyday language.
