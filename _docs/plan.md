# Shared Household Chores Manager — Project Scope & Technical Plan

## 1. Project Overview & Vision
A streamlined, mobile-responsive Web App (PWA) designed for flatmates and roommates to manage shared household responsibilities with fairness, transparency, and minimal friction. 

The tool eliminates the awkwardness of chore delegation through automated round-robin rotations, built-in accountability nudges, vacation mode skip logic, chore swapping, and a shared essential supplies checklist.

---

## 2. Core Target Audience & Principles
* **Target Audience:** Roommates and flatmates sharing living spaces.
* **Core Principles:**
  * **Fairness First:** Transparent automated chore rotations so no single person bears an unfair burden.
  * **Low Friction:** Fast onboarding via invite codes/links with lightweight authentication (Google OAuth / Magic Link).
  * **Trust-Based Accountability:** Visual status indicators with friendly in-app nudges rather than invasive surveillance.
  * **Mobile-First UX:** Optimized for quick phone checkoffs and glanceable dashboard views.

---

## 3. Scope & Feature Specifications (MVP)

### A. Household Management & Access
* **Household Creation:** Any user can create a household and set house rules/name.
* **Invite Links & Codes:** 6-character shareable invite code and direct invite URL for frictionless onboarding.
* **Lightweight Authentication:** Google OAuth or Magic Link via Supabase Auth.
* **Member Profiles:** Name, avatar/initials, contact info, and active status.

### B. Automated Round-Robin Chore Engine
* **Chore Creation:** Title, description, area/category (Kitchen, Bathroom, Living Room, Trash), frequency (Daily, Weekly, Bi-weekly, Monthly).
* **Smart Rotation:** Chores automatically advance to the next roommate upon completion or cycle turnover.
* **Smart Skip (Vacation Mode):** If a roommate is marked "Away/On Vacation", the engine smoothly skips them in the rotation and resumes when they return.

### C. Dashboard & Visual Accountability
* **"My Chores" Tab:** Personalized view of tasks due today, upcoming, or overdue.
* **"Household Board" Tab:** Bird's-eye view of all house chores, who is responsible, and current status.
* **One-Click Checkoff:** Mark chores as complete with a single tap, recording completion timestamps and history.
* **In-App Gentle Nudge:** Roommates can send a pre-canned, polite in-app nudge badge for tasks that are overdue.

### D. Chore Swapping
* **Swap Requests:** If a roommate cannot complete a chore during their cycle, they can initiate a swap request with a specific flatmate.
* **Accept / Decline Workflow:** The target flatmate receives a notification badge to accept or decline the swap.
* **Auto-Reassignment:** Upon acceptance, the active assignment updates immediately without breaking the long-term rotation order.

### E. Vacation / Away Mode
* **Status Toggle:** Roommates can set their status to "Away" (with optional return date).
* **Automatic Rotation Bypass:** Active rotations bypass the away member until their status is restored to active.

### F. Shared Supplies Checklist
* **Low-Stock Tracker:** Simple status tracker for communal supplies (e.g., trash bags, dish soap, toilet paper, detergent).
* **Status Badges:** `In Stock`, `Running Low`, `Out of Stock`.
* **Claim to Restock:** Roommates can tap "I will buy this" when heading out for groceries.

---

## 4. Tech Stack & Architecture

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend Framework** | **Next.js 15 (App Router, React 19)** | Fast SSR/SSG, excellent SEO & performance, modern Server Actions. |
| **Styling & Icons** | **Tailwind CSS + Lucide React + Radix UI / Shadcn UI** | Rapid development, modern accessible UI, dark/light theme support. |
| **Language** | **TypeScript** | End-to-end type safety across client, server, and database queries. |
| **Backend & Database** | **Supabase (PostgreSQL)** | Managed Postgres, built-in Auth (Google OAuth/Magic Link), Row-Level Security (RLS), Realtime subscriptions. |
| **Platform Format** | **Responsive Web App (PWA)** | Works across iOS Safari, Android Chrome, and Desktop browsers with home-screen installability. |

---

## 5. Database Schema & Data Model

```
 ┌─────────────┐       ┌──────────────────────┐       ┌───────────────────┐
 │   profiles  │──────<│  household_members   │>──────│    households     │
 └─────────────┘       └──────────────────────┘       └───────────────────┘
        │                         │                             │
        │                         │                             │
        │                         ▼                             ▼
        │              ┌──────────────────────┐       ┌───────────────────┐
        │              │  chore_assignments   │>──────│      chores       │
        │              └──────────────────────┘       └───────────────────┘
        │                         │                             │
        │                         ▼                             │
        │              ┌──────────────────────┐                 │
        └─────────────<│     chore_swaps      │                 │
                       └──────────────────────┘                 │
                                                                ▼
                                                      ┌───────────────────┐
                                                      │     supplies      │
                                                      └───────────────────┘
```

### Table Definitions (PostgreSQL / Supabase DDL)

```sql
-- 1. Profiles (Linked to Supabase Auth)
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Households
CREATE TABLE households (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    invite_code VARCHAR(8) UNIQUE NOT NULL,
    created_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Household Members (Join table with roles & vacation status)
CREATE TABLE household_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    role TEXT CHECK (role IN ('admin', 'member')) DEFAULT 'member',
    is_away BOOLEAN DEFAULT FALSE,
    away_until DATE,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (household_id, profile_id)
);

-- 4. Chores
CREATE TABLE chores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT DEFAULT 'general',
    frequency TEXT CHECK (frequency IN ('daily', 'weekly', 'biweekly', 'monthly')) NOT NULL,
    rotation_order UUID[] DEFAULT '{}', -- Array of household_members.id defining the fixed queue
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Chore Assignments (Active & historical task instances)
CREATE TABLE chore_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chore_id UUID NOT NULL REFERENCES chores(id) ON DELETE CASCADE,
    household_id UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    assigned_member_id UUID NOT NULL REFERENCES household_members(id) ON DELETE CASCADE,
    due_date DATE NOT NULL,
    status TEXT CHECK (status IN ('pending', 'completed', 'overdue', 'skipped')) DEFAULT 'pending',
    completed_at TIMESTAMPTZ,
    completed_by UUID REFERENCES profiles(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Chore Swaps
CREATE TABLE chore_swaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL REFERENCES chore_assignments(id) ON DELETE CASCADE,
    requester_member_id UUID NOT NULL REFERENCES household_members(id) ON DELETE CASCADE,
    target_member_id UUID NOT NULL REFERENCES household_members(id) ON DELETE CASCADE,
    status TEXT CHECK (status IN ('pending', 'accepted', 'declined', 'cancelled')) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. In-App Nudges
CREATE TABLE nudges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL REFERENCES chore_assignments(id) ON DELETE CASCADE,
    from_member_id UUID NOT NULL REFERENCES household_members(id) ON DELETE CASCADE,
    to_member_id UUID NOT NULL REFERENCES household_members(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Shared Supplies
CREATE TABLE supplies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    status TEXT CHECK (status IN ('in_stock', 'low', 'out_of_stock')) DEFAULT 'in_stock',
    claimed_by UUID REFERENCES household_members(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES profiles(id),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 6. Rotation & Skip Engine Logic

```
   [Chore Marked Completed] OR [Cycle Turnover Triggered]
                           │
                           ▼
              Fetch current member index in 
               `chores.rotation_order`
                           │
                           ▼
          Find next member index (index + 1) % length
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
      Is member Active?           Is member Away (`is_away = true`)?
             │                           │
             ▼                           ▼
     Assign Chore to Member      Skip & advance to next index
```

* **Swap Handling:** When a swap is accepted, only the current instance (`chore_assignments.assigned_member_id`) changes; the base sequence array (`chores.rotation_order`) remains intact for future cycles.

---

## 7. User Experience & Screen Structure

1. **Auth & Onboarding (`/login`, `/join`, `/create-household`):**
   * Google One-Tap or Magic link login.
   * Input 6-character code or auto-join via `/join/[code]`.
2. **Main Household Dashboard (`/dashboard`):**
   * **Header:** Household name, Member avatars (with Away indicators), Quick Add button.
   * **My Tasks Section:** High-priority cards for tasks assigned to the logged-in user with status badges (Due Today, Overdue, Completed).
   * **Household Overview:** Grid/list of all tasks with member assignments and rotation queues.
   * **Supplies Bar:** Glanceable widget showing items marked `Low` or `Out of Stock`.
3. **Chore Action Modal:**
   * Tap task card -> Mark Complete, Request Swap, or Send Polite Nudge.
4. **Supplies Hub (`/supplies`):**
   * Quick toggle between In Stock / Low / Out of Stock, with an "I'll grab this" action.
5. **Settings & Profile (`/settings`):**
   * Toggle Vacation/Away mode with optional end date.
   * Copy invite link, manage house members.

---

## 8. Implementation Roadmap

### Phase 1: Project Setup & Database Foundations
- [ ] Initialize Next.js 15 project with TypeScript, Tailwind CSS, and Shadcn UI components.
- [ ] Configure Supabase client & environment variables.
- [ ] Implement database migrations with Row-Level Security (RLS) policies.

### Phase 2: Authentication & Household Onboarding
- [ ] Supabase Auth integration (Google OAuth & Magic Link).
- [ ] Household creation & unique 6-character invite code generation.
- [ ] Household join flow via invite code / link.

### Phase 3: Core Chores & Round-Robin Rotation
- [ ] Chore creation, category grouping, and cycle intervals.
- [ ] Rotation assignment engine (including automatic away-mode skips).
- [ ] Interactive Dashboard with "My Chores" and "All Chores" views.
- [ ] One-click completion flow with history logging.

### Phase 4: Swapping, Nudges & Supplies
- [ ] Chore swap request & approval workflow.
- [ ] In-app polite nudge alert system.
- [ ] Shared supplies checklist with stock status toggles.

### Phase 5: Polish, PWA & Testing
- [ ] Mobile PWA manifest & service worker configuration.
- [ ] Optimistic UI updates for snappy mobile interactions.
- [ ] End-to-end user flow testing & deployment preparation.
