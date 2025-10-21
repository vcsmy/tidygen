# Freelancers App - Community Edition

## Overview

The Freelancers app is a **Community Edition exclusive** feature that enables individual domestic cleaners and contractors to register, manage their profiles, and receive gig assignments through the TidyGen ERP platform.

## Features

### Core Functionality
- **Freelancer Registration**: Individual contractors can register and create detailed profiles
- **Profile Management**: Complete profile management with personal info, skills, and availability
- **Document Verification**: Upload and verify identity documents, certifications, and insurance
- **Availability Scheduling**: Set and manage availability for different days and time slots
- **Skill Management**: Add and manage cleaning skills and certifications
- **Review System**: Client reviews and ratings for freelancers

### Web3 Integration
- **Wallet Connection**: Blockchain wallet integration for payments
- **Blockchain Verification**: Verified freelancer status on blockchain
- **NFT Badges**: Achievement badges as NFTs for milestones

## Models

### Freelancer
The main model representing an individual contractor/cleaner:
- Personal information and contact details
- Service areas and travel distance preferences
- Cleaning specializations and skills
- Availability schedule and status
- Performance metrics (rating, completion rate)
- Financial information (hourly rates, payment methods)
- Web3 integration (wallet address, blockchain verification)
- Verification status and background checks

### FreelancerDocument
Handles document uploads and verification:
- Document types (ID, passport, certifications, insurance)
- File management and verification status
- Expiry date tracking

### FreelancerAvailability
Manages freelancer availability:
- Day-of-week scheduling
- Time slot availability
- Recurring vs specific date availability

### FreelancerSkill
Defines available skills and their categories:
- Skill categorization (cleaning, maintenance, specialized)
- Certification requirements

### FreelancerSkillAssignment
Links freelancers to their skills:
- Proficiency levels (beginner to expert)
- Years of experience
- Certification details

### FreelancerReview
Client reviews and ratings:
- Multi-criteria ratings (quality, punctuality, communication, professionalism)
- Review comments and recommendations
- Job reference tracking

## API Endpoints

### Freelancer Management
- `GET/POST /api/v1/freelancers/` - List/create freelancers
- `GET/PUT/PATCH/DELETE /api/v1/freelancers/{id}/` - Freelancer details
- `GET /api/v1/freelancers/me/` - Current user's freelancer profile

### Availability Management
- `GET/POST /api/v1/freelancers/{id}/availability/` - Manage availability
- `GET/PUT/DELETE /api/v1/freelancers/{id}/availability/{slot_id}/` - Specific availability

### Document Management
- `GET/POST /api/v1/freelancers/{id}/documents/` - Document management
- `PUT /api/v1/freelancers/{id}/documents/{doc_id}/verify/` - Verify documents (staff only)

### Skills Management
- `GET /api/v1/freelancers/{id}/skills/` - Freelancer's skills
- `POST /api/v1/freelancers/{id}/skills/` - Assign skills
- `GET /api/v1/freelancers/skills/` - Available skills

### Reviews
- `GET/POST /api/v1/freelancers/{id}/reviews/` - Reviews for freelancer

### Search and Statistics
- `GET /api/v1/freelancers/search/` - Search freelancers
- `GET /api/v1/freelancers/{id}/stats/` - Freelancer statistics

## Usage

### Registration Flow
1. User creates account in the system
2. User applies to become a freelancer
3. Upload required documents (ID, background check, insurance)
4. Staff reviews and verifies documents
5. Freelancer profile is activated

### Profile Management
- Freelancers can update their personal information
- Set availability schedules for different days
- Add/remove skills and certifications
- Upload and manage documents
- Update payment preferences

### Job Assignment (Future Integration)
This app provides the foundation for gig-based job assignment that will be integrated with the `gig_management` and `contractor_payments` apps.

## Permissions

- **Read Access**: All authenticated users can view freelancer profiles
- **Write Access**: Only freelancer owners can modify their profiles
- **Document Verification**: Only staff members can verify documents
- **Review Creation**: Authenticated users can create reviews

## Security Features

- Background check requirements
- Document verification workflow
- Insurance validation
- Blockchain-based verification
- Comprehensive audit trails

## Future Enhancements

This app is designed to work with upcoming modules:
- **Gig Management**: Job posting and assignment system
- **Contractor Payments**: Escrow and payment processing
- **Freelancer Web3**: Advanced blockchain features and NFT badges

## Community Edition Benefits

This feature differentiates the Community Edition by providing:
- Individual contractor support (not available in commercial version)
- Gig-based economy for domestic cleaners
- Decentralized reputation system
- Web3-powered transparency and security
