# Gig Management App - Community Edition

## Overview

The Gig Management app is a **Community Edition exclusive** feature that handles job posting, application management, and assignment tracking for the freelancer ecosystem. It integrates seamlessly with the Freelancers app to create a complete gig economy platform.

## Features

### Core Functionality
- **Job Posting**: Clients and companies can post cleaning and maintenance jobs
- **Application Management**: Freelancers can apply to jobs with cover letters and proposals
- **Job Assignment**: Job owners can review applications and assign freelancers
- **Milestone Tracking**: Progress tracking with customizable milestones
- **Photo Documentation**: Before/during/after photos for job verification
- **Messaging System**: In-app communication between clients and freelancers
- **Review System**: Bi-directional reviews for completed jobs

### Job Management
- **Job Categories**: Organized job categories with default pricing
- **Flexible Pricing**: Support for hourly, fixed-price, and performance-based payments
- **Scheduling**: Preferred start/end dates with actual time tracking
- **Service Types**: Different cleaning types and property classifications
- **Skill Requirements**: Job-specific skill and certification requirements
- **Web3 Integration**: Blockchain job verification and NFT badges

## Models

### GigCategory
Job categories for organization and default pricing:
- Category names and descriptions with icons/colors
- Default hourly rate ranges for pricing guidance
- Active/inactive status for category management

### GigJob
Main job posting model with comprehensive details:
- **Job Information**: Title, description, category, status, priority
- **Client Details**: Client type (individual/corporate), contact info
- **Location**: Full address for service delivery
- **Service Details**: Service type, property details, requirements
- **Scheduling**: Preferred and actual start/end dates
- **Pricing**: Hourly rates, fixed prices, payment methods
- **Assignment**: Assigned freelancer and assignment tracking
- **Web3**: Smart contract addresses and blockchain transaction hashes

### GigApplication
Freelancer applications for jobs:
- Cover letters and proposed rates
- Estimated completion times and availability
- Application status tracking (submitted, reviewing, accepted, rejected)
- Review workflow with notes and reviewer information

### JobMilestone
Progress tracking milestones:
- Milestone types (start, progress, quality check, completion, payment)
- Expected and actual completion dates
- Quality scoring and notes
- Payment triggers for milestone-based payments
- Web3 milestone hash tracking

### JobPhoto
Documentation photos for jobs:
- Photo types (before, during, after, quality check, issues)
- GPS coordinates and metadata
- Photo hash for Web3 authenticity verification
- Milestone association for organized documentation

### JobMessage
Communication system for jobs:
- Message types (general, questions, updates, issues, requirements, feedback)
- Subject and content with attachment support
- Read status tracking for message management

### JobReview
Review system for completed jobs:
- Multi-criteria ratings (overall, quality, timeliness, communication, professionalism)
- Review titles, comments, and recommendations
- Response capability for two-way communication

## API Endpoints

### Job Management
- `GET/POST /api/v1/gig-management/jobs/` - List/create jobs
- `GET/PUT/PATCH/DELETE /api/v1/gig-management/jobs/{id}/` - Job details
- `GET /api/v1/gig-management/jobs/search/` - Search jobs
- `GET /api/v1/gig-management/jobs/{id}/stats/` - Job statistics

### Categories
- `GET /api/v1/gig-management/categories/` - List job categories

### Applications
- `GET/POST /api/v1/gig-management/jobs/{job_id}/applications/` - Job applications
- `GET/PUT/DELETE /api/v1/gig-management/jobs/{job_id}/applications/{id}/` - Application details
- `POST /api/v1/gig-management/jobs/{job_id}/applications/{id}/assign/` - Assign freelancer

### Milestones & Progress
- `GET/POST /api/v1/gig-management/jobs/{job_id}/milestones/` - Job milestones
- `GET/PUT/DELETE /api/v1/gig-management/jobs/{job_id}/milestones/{id}/` - Milestone details

### Photo Documentation
- `GET/POST /api/v1/gig-management/jobs/{job_id}/photos/` - Job photos

### Communication
- `GET/POST /api/v1/gig-management/jobs/{job_id}/messages/` - Job messages

### Reviews
- `GET/POST /api/v1/gig-management/jobs/{job_id}/reviews/` - Job reviews

## Workflow

### Job Posting Flow
1. Client creates job with details (title, description, location, pricing)
2. Job is published and visible to eligible freelancers
3. Freelancers apply with cover letters and proposed rates
4. Client reviews applications and selects freelancer
5. Job status changes to "assigned" and work begins

### Job Execution Flow
1. Freelancer starts job and milestone tracking begins
2. Photos and progress updates are documented
3. Client and freelancer communicate via messaging system
4. Quality checks and milestone completions are tracked
5. Job completion triggers review opportunity

### Payment Flow
- Milestones can trigger payments at completion
- Web3 integration supports crypto payments
- Traditional payment methods also supported
- Escrow system integration for secure transactions

## Permissions

- **Job Creation**: Authenticated users can create jobs
- **Job Viewing**: Published jobs visible to all, assigned jobs limited to participants
- **Application Management**: Job owners and assigned freelancers can manage applications
- **Milestone Management**: Job participants can create and update milestones
- **Photo Upload**: Job participants can upload documentation photos
- **Messaging**: Job participants can send messages
- **Reviews**: Job participants can leave reviews after completion

## Integration

### With Freelancers App
- Seamless freelancer profile linking
- Skill matching based on job requirements
- Availability scheduling integration
- Performance tracking and ratings

### With Web3 Integration
- Smart contract deployment for job agreements
- Blockchain transaction tracking
- NFT badge creation for job completion
- Decentralized verification system

## Future Enhancements

This app is designed to integrate with:
- **Contractor Payments**: Escrow and payment processing
- **Freelancer Web3**: Advanced blockchain features
- **Analytics**: Job performance and market analysis
- **Mobile Apps**: React Native/Futter integration for field workers

## Security Features

- Comprehensive permission system
- Job privacy controls
- Secure file upload handling
- Web3 transaction verification
- Audit trail for all job activities

This gig management system provides the foundation for a complete freelance cleaning and maintenance marketplace within the TidyGen ERP platform.
