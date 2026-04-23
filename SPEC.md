# PathAI — Complete Build Instructions for VS Code Copilot
> Paste this entire document into Copilot Chat (or break it into sections per feature).
> Every section is self-contained and actionable.

---

## 0. MASTER CONTEXT — Read this first

You are building **PathAI** — an autonomous AI-powered job search platform.

**Core concept:** Users upload their resume once. PathAI handles everything else —
finding jobs, tailoring resumes per role, sending recruiter outreach messages,
auto-applying to matched jobs overnight, and coaching through interviews. Users
pay nothing upfront; a one-time success fee (1% of CTC, capped at ₹15,000) is
collected 60 days after hire.

**Design philosophy:**
- Every screen should feel like a premium productivity tool — think Linear, Notion, Vercel dashboard
- Dark-first design with a clean light mode toggle
- Micro-animations on every meaningful state change (not decorative)
- No clutter. Every UI element either shows progress or enables action.
- Mobile responsive — job seekers are on phones

**North star metric for every feature:** Does this get users hired faster?

---

## 1. TECH STACK

### Frontend
```
Framework:     Next.js 14 (App Router)
Language:      TypeScript (strict mode)
Styling:       Tailwind CSS + shadcn/ui components
Animations:    Framer Motion
State:         Zustand (global) + React Query (server state)
Forms:         React Hook Form + Zod validation
Charts:        Recharts
Icons:         Lucide React
Fonts:         Geist (Inter-like, modern) + DM Serif Display for headings
```

### Backend
```
Framework:     FastAPI (Python 3.11+)
Task Queue:    Celery + Redis
Database:      PostgreSQL (Supabase)
ORM:           SQLAlchemy 2.0 + Alembic migrations
Auth:          Supabase Auth (JWT)
File Storage:  Supabase Storage (resume PDFs)
AI:            Anthropic Claude API (claude-sonnet-4-5)
Scraping:      Playwright + Apify SDK
Email:         Resend API
Payments:      Razorpay
```

### Infrastructure
```
Deployment:    Railway (backend) + Vercel (frontend)
CI/CD:         GitHub Actions
Monitoring:    Sentry
Env:           .env.local (frontend) + .env (backend)
```

---

## 2. PROJECT STRUCTURE

```
pathai/
├── frontend/                          # Next.js app
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx             # Sidebar + top nav
│   │   │   ├── page.tsx               # Dashboard home
│   │   │   ├── jobs/page.tsx          # Job matches
│   │   │   ├── applications/page.tsx  # Kanban tracker
│   │   │   ├── resume/page.tsx        # Resume builder
│   │   │   ├── outreach/page.tsx      # Recruiter messages
│   │   │   ├── interviews/page.tsx    # Interview prep
│   │   │   ├── profile/page.tsx       # User profile + settings
│   │   │   └── microsite/page.tsx     # Live profile microsite
│   │   ├── [username]/page.tsx        # Public microsite
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/                        # shadcn components
│   │   ├── dashboard/                 # Dashboard-specific
│   │   ├── jobs/                      # Job card, filters
│   │   ├── resume/                    # Resume editor
│   │   └── shared/                    # Reusable
│   ├── lib/
│   │   ├── api.ts                     # API client (axios)
│   │   ├── auth.ts                    # Auth helpers
│   │   ├── utils.ts
│   │   └── store/                     # Zustand stores
│   └── types/                         # TypeScript interfaces
│
└── backend/                           # FastAPI app
    ├── app/
    │   ├── main.py
    │   ├── api/
    │   │   ├── routes/
    │   │   │   ├── auth.py
    │   │   │   ├── resume.py
    │   │   │   ├── jobs.py
    │   │   │   ├── applications.py
    │   │   │   ├── outreach.py
    │   │   │   ├── interviews.py
    │   │   │   └── payments.py
    │   │   └── deps.py                # Auth dependency injection
    │   ├── core/
    │   │   ├── config.py              # Settings (pydantic-settings)
    │   │   └── security.py
    │   ├── models/                    # SQLAlchemy models
    │   ├── schemas/                   # Pydantic schemas
    │   ├── services/                  # Business logic
    │   │   ├── ai_service.py          # Claude API calls
    │   │   ├── job_scraper.py         # Playwright scraping
    │   │   ├── resume_parser.py       # PDF parsing
    │   │   ├── outreach_service.py    # Recruiter messaging
    │   │   └── payment_service.py     # Razorpay
    │   ├── tasks/                     # Celery tasks
    │   │   ├── apply_jobs.py
    │   │   ├── scrape_jobs.py
    │   │   └── send_outreach.py
    │   └── db/
    │       ├── session.py
    │       └── init_db.py
    ├── alembic/
    ├── requirements.txt
    └── Dockerfile
```

---

## 3. DATABASE SCHEMA

Create these tables in Supabase SQL editor or via Alembic migrations:

```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR UNIQUE NOT NULL,
  full_name VARCHAR,
  phone VARCHAR,
  linkedin_url VARCHAR,
  github_url VARCHAR,
  portfolio_url VARCHAR,
  avatar_url VARCHAR,
  career_readiness_score INTEGER DEFAULT 0,
  total_applications INTEGER DEFAULT 0,
  total_interviews INTEGER DEFAULT 0,
  is_passive_mode BOOLEAN DEFAULT FALSE,
  passive_mode_threshold INTEGER DEFAULT 85,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Resumes
CREATE TABLE resumes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  file_url VARCHAR,
  raw_text TEXT,
  parsed_json JSONB,           -- structured skills, experience, education
  career_dna JSONB,            -- AI-extracted strengths, keywords, persona
  is_primary BOOLEAN DEFAULT TRUE,
  version INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Skills (extracted from resume)
CREATE TABLE user_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  skill_name VARCHAR NOT NULL,
  proficiency VARCHAR,         -- beginner/intermediate/expert
  years_experience FLOAT,
  source VARCHAR DEFAULT 'resume'
);

-- Jobs
CREATE TABLE jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  external_id VARCHAR,
  title VARCHAR NOT NULL,
  company VARCHAR NOT NULL,
  company_logo_url VARCHAR,
  location VARCHAR,
  job_type VARCHAR,            -- full-time/contract/remote
  salary_min BIGINT,
  salary_max BIGINT,
  description TEXT,
  requirements TEXT,
  apply_url VARCHAR,
  source VARCHAR,              -- linkedin/naukri/indeed/company_page
  posted_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ,
  ghost_score INTEGER DEFAULT 50,     -- 0=ghost, 100=very real
  company_health_score INTEGER DEFAULT 50,
  is_fresh BOOLEAN DEFAULT TRUE,
  scraped_at TIMESTAMPTZ DEFAULT NOW(),
  raw_data JSONB
);

-- Job Matches (per user)
CREATE TABLE job_matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
  match_score INTEGER NOT NULL,       -- 0-100
  match_reasons JSONB,                -- why it matched
  is_dismissed BOOLEAN DEFAULT FALSE,
  is_saved BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, job_id)
);

-- Applications
CREATE TABLE applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
  status VARCHAR DEFAULT 'applied',   -- applied/viewed/interviewing/offer/rejected/ghosted
  applied_at TIMESTAMPTZ DEFAULT NOW(),
  applied_via VARCHAR,                -- pathai_auto/manual/referral
  tailored_resume_url VARCHAR,
  cover_letter TEXT,
  notes TEXT,
  follow_up_count INTEGER DEFAULT 0,
  last_follow_up_at TIMESTAMPTZ,
  interview_date TIMESTAMPTZ,
  offer_amount BIGINT,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Outreach Messages
CREATE TABLE outreach_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  job_id UUID REFERENCES jobs(id),
  application_id UUID REFERENCES applications(id),
  recipient_name VARCHAR,
  recipient_title VARCHAR,
  recipient_linkedin VARCHAR,
  recipient_email VARCHAR,
  message_type VARCHAR,         -- connection_request/linkedin_message/email
  message_text TEXT,
  status VARCHAR DEFAULT 'draft', -- draft/sent/opened/replied
  sent_at TIMESTAMPTZ,
  replied_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Interview Intel (crowdsourced)
CREATE TABLE interview_intel (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company VARCHAR NOT NULL,
  role_level VARCHAR,
  interview_type VARCHAR,       -- technical/behavioral/system_design/case
  questions JSONB,              -- array of {question, frequency, tips}
  interviewer_name VARCHAR,
  process_description TEXT,
  difficulty INTEGER,           -- 1-5
  outcome VARCHAR,              -- got_offer/rejected/withdrew
  submitted_by UUID REFERENCES users(id),
  verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Success Fees / Payments
CREATE TABLE success_fees (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  application_id UUID REFERENCES applications(id),
  offer_ctc BIGINT NOT NULL,
  fee_amount BIGINT NOT NULL,
  fee_percentage FLOAT DEFAULT 1.0,
  status VARCHAR DEFAULT 'pending',   -- pending/due/paid/waived/disputed
  hire_confirmed_at TIMESTAMPTZ,
  payment_due_at TIMESTAMPTZ,         -- hire_confirmed_at + 60 days
  paid_at TIMESTAMPTZ,
  razorpay_order_id VARCHAR,
  razorpay_payment_id VARCHAR,
  dispute_reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 4. ENVIRONMENT VARIABLES

### Frontend `.env.local`
```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Backend `.env`
```bash
DATABASE_URL=postgresql://user:pass@host:5432/pathai
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
SUPABASE_STORAGE_BUCKET=resumes
ANTHROPIC_API_KEY=sk-ant-...
RAZORPAY_KEY_ID=rzp_test_...
RAZORPAY_KEY_SECRET=...
RESEND_API_KEY=re_...
REDIS_URL=redis://localhost:6379
APIFY_API_TOKEN=apify_api_...
SECRET_KEY=your_jwt_secret
FRONTEND_URL=http://localhost:3000
```

---

## 5. DESIGN SYSTEM (Tailwind config + tokens)

### `tailwind.config.ts`
```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#eef2ff",
          100: "#e0e7ff",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          900: "#1e1b4b",
        },
        surface: {
          DEFAULT: "#ffffff",
          secondary: "#f8f9fa",
          tertiary: "#f1f3f5",
          dark: "#0f0f11",
          "dark-secondary": "#1a1a1f",
          "dark-tertiary": "#222228",
        },
        ink: {
          primary: "#0f0f11",
          secondary: "#52525b",
          muted: "#a1a1aa",
          dark: "#ffffff",
          "dark-secondary": "#a1a1aa",
        },
        success: { light: "#d1fae5", DEFAULT: "#10b981", dark: "#065f46" },
        warning: { light: "#fef3c7", DEFAULT: "#f59e0b", dark: "#92400e" },
        danger:  { light: "#fee2e2", DEFAULT: "#ef4444", dark: "#991b1b" },
        info:    { light: "#dbeafe", DEFAULT: "#3b82f6", dark: "#1e40af" },
      },
      fontFamily: {
        sans:    ["Geist", "var(--font-geist-sans)", "system-ui", "sans-serif"],
        serif:   ["DM Serif Display", "Georgia", "serif"],
        mono:    ["Geist Mono", "monospace"],
      },
      borderRadius: {
        "4xl": "2rem",
      },
      animation: {
        "fade-in":    "fadeIn 0.3s ease-out",
        "slide-up":   "slideUp 0.3s ease-out",
        "slide-in":   "slideIn 0.25s ease-out",
        "pulse-soft": "pulseSoft 2s ease-in-out infinite",
      },
      keyframes: {
        fadeIn:    { from: { opacity: "0" }, to: { opacity: "1" } },
        slideUp:   { from: { opacity: "0", transform: "translateY(8px)" }, to: { opacity: "1", transform: "translateY(0)" } },
        slideIn:   { from: { opacity: "0", transform: "translateX(-8px)" }, to: { opacity: "1", transform: "translateX(0)" } },
        pulseSoft: { "0%,100%": { opacity: "1" }, "50%": { opacity: "0.6" } },
      },
      boxShadow: {
        card:     "0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)",
        "card-lg":"0 4px 16px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04)",
        glow:     "0 0 0 3px rgba(99, 102, 241, 0.15)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
```

### Global CSS tokens (`app/globals.css`)
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --bg:          255 255 255;
    --bg-2:        248 249 250;
    --bg-3:        241 243 245;
    --text:        15 15 17;
    --text-2:      82 82 91;
    --text-3:      161 161 170;
    --border:      228 228 231;
    --brand:       99 102 241;
    --radius:      0.625rem;
  }
  .dark {
    --bg:          15 15 17;
    --bg-2:        26 26 31;
    --bg-3:        34 34 40;
    --text:        250 250 250;
    --text-2:      161 161 170;
    --text-3:      82 82 91;
    --border:      39 39 45;
    --brand:       129 140 248;
  }

  * { border-color: rgb(var(--border)); }
  body {
    background: rgb(var(--bg));
    color: rgb(var(--text));
    font-feature-settings: "rlig" 1, "calt" 1, "ss01" 1;
    -webkit-font-smoothing: antialiased;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgb(var(--border)); border-radius: 99px; }
}

@layer utilities {
  .text-gradient {
    @apply bg-gradient-to-r from-brand-500 to-violet-500 bg-clip-text text-transparent;
  }
  .card {
    @apply bg-[rgb(var(--bg))] border border-[rgb(var(--border))] rounded-xl shadow-card;
  }
  .card-hover {
    @apply hover:border-brand-400/40 hover:shadow-card-lg transition-all duration-200;
  }
}
```

---

## 6. AUTHENTICATION PAGES

### Instructions for Copilot:
> Build `app/(auth)/signup/page.tsx` and `app/(auth)/login/page.tsx`

**Signup page requirements:**
- Split layout: left side = product value prop, right side = form
- Left side: dark background, large serif headline "Get hired. Pay nothing until you do.", animated stat cards showing "34 jobs applied overnight", "3 recruiter replies", "1 interview booked" as a live simulation
- Right side: clean form — Email, Full Name, Password, Phone (optional)
- Below form: checkbox "I agree that if PathAI facilitates my hire, I'll pay a success fee of 1% of my CTC (capped at ₹15,000), payable 60 days after joining." — must be checked to proceed
- Google OAuth button (Supabase)
- LinkedIn OAuth button (Supabase)
- On submit: call POST `/api/auth/register`, store JWT, redirect to `/onboarding`
- Framer Motion: form fields fade-in staggered with 50ms delay between each

**Login page requirements:**
- Minimal centered design
- Email + password fields
- "Forgot password" link
- Google + LinkedIn OAuth
- Link to signup

---

## 7. ONBOARDING FLOW

### Instructions for Copilot:
> Build `app/(onboarding)/page.tsx` as a multi-step wizard

**Step 1 — Resume upload:**
- Large dashed drop zone (drag & drop or click to upload)
- Accept: PDF, DOCX
- On upload: show animated parsing progress ("Extracting skills...", "Building your profile...", "Finding job matches...")
- Call POST `/api/resume/upload` which returns parsed profile
- Display extracted skills as tags for user to confirm/edit

**Step 2 — Career preferences:**
- Target roles (multi-select with search — e.g., "Data Engineer", "Senior SDE")
- Preferred locations (multi-select: Bangalore, Mumbai, Delhi, Remote, etc.)
- Min salary expectation (slider, ₹3L – ₹50L+)
- Open to: Full-time / Contract / Both
- Industries to avoid (optional exclusion list)

**Step 3 — Automation settings:**
- "Autopilot mode" toggle (default: ON)
- When to apply: slider from "Only manually approved jobs" → "Apply to all matches above 80%"
- Max applications per day: 2 / 5 / 10 / Unlimited
- Auto-send recruiter outreach: Yes / No / Ask me first
- "Speed apply" toggle: Apply within 5 minutes of fresh postings

**Step 4 — Success fee agreement:**
- Clean summary of how the fee works
- Show the math: "If you get hired at ₹15 LPA, you pay ₹15,000 after 60 days. That's 1 day's salary."
- Comparison table: PathAI ₹15,000 once vs Careerflow ₹1,499 × 6 months = ₹8,994 whether hired or not
- Large "Agree & Launch PathAI" CTA button

---

## 8. DASHBOARD LAYOUT

### Instructions for Copilot:
> Build `app/(dashboard)/layout.tsx`

**Sidebar (240px wide, collapsible to 60px):**
```
Logo (top-left)
────────────────
[icon] Dashboard
[icon] Job Matches        [badge: 12 new]
[icon] Applications       [badge: 8]
[icon] Resume
[icon] Outreach           [badge: 3 replies]
[icon] Interviews
[icon] My Microsite
────────────────
[icon] Settings
[icon] Profile
────────────────
Career Score card:
  "82 / 100"  ← animated number
  "↑ 4 this week"
```

**Top navigation bar:**
- Breadcrumb (current page)
- Autopilot status badge: green dot "Autopilot: ON" or red "Paused"
- Notification bell (application status updates)
- Dark mode toggle
- Avatar dropdown

**Layout behavior:**
- Sidebar collapses to icon-only on md breakpoint
- Page content area has max-width 1200px, centered
- No horizontal scroll anywhere
- Smooth sidebar collapse animation (Framer Motion)

---

## 9. DASHBOARD HOME PAGE

### Instructions for Copilot:
> Build `app/(dashboard)/page.tsx`

**Section 1 — Hero greeting (top):**
- "Good morning, Shubh. Here's your job search overnight." (dynamic time + name)
- Animated counter cards in a 4-column grid:
  - "Applied last night" → number with clock icon
  - "New matches" → number with sparkle icon
  - "Recruiter replies" → number with chat icon
  - "Interviews scheduled" → number with calendar icon

**Section 2 — Activity feed (left, 65% width):**
- Timeline of PathAI's automated actions: "Applied to Senior Data Engineer at PhonePe • 2h ago", "Sent recruiter message to Priya Sharma at Razorpay • 4h ago", "New job match: Staff Engineer at Stripe (91% match) • 6h ago"
- Each item has company logo, job title, action type (apply/outreach/match), timestamp
- "View full activity" link at bottom

**Section 3 — Quick stats (right, 35% width):**
- "Applications this week" — mini bar chart (Recharts)
- "Response rate" — donut chart showing Applied / Replied / Interviews
- "Top matching skills" — horizontal bar showing your skills vs market demand

**Section 4 — Action queue (bottom):**
- Cards for items needing user action: "Interview at Stripe tomorrow — review prep deck", "Offer received from Flipkart — review now", "Follow up on Zomato application (8 days, no reply)"
- Each card has a clear CTA button

---

## 10. JOB MATCHES PAGE

### Instructions for Copilot:
> Build `app/(dashboard)/jobs/page.tsx`

**Layout:**
- Filters sidebar (left, 280px): Role, Location, Salary range, Job type, Company size, Min match score, Hide ghost jobs toggle
- Job cards grid (right): 2 columns on desktop, 1 on mobile

**Job Card component (`components/jobs/JobCard.tsx`):**
```tsx
interface JobCardProps {
  job: {
    id: string
    title: string
    company: string
    companyLogo?: string
    location: string
    salaryMin?: number
    salaryMax?: number
    matchScore: number          // 0-100
    ghostScore: number          // 0-100 (higher = more legit)
    companyHealthScore: number  // 0-100
    postedAt: string
    isFresh: boolean            // posted < 24h ago
    tags: string[]              // skills matched
  }
}
```

Card design:
- White/dark card with subtle border
- Top row: company logo (40px circle), company name, location, "Fresh" badge (green) if isFresh
- Job title (large, semibold)
- Salary range (if available)
- Match score: large colored number (green 80+, yellow 60-79, gray <60) with label "Match"
- Ghost score: small "Legitimacy" indicator — green/yellow/red dot + text
- Skill tags (3-4 shown, "+N more" overflow)
- Bottom row: "Apply with PathAI" primary button, "Save" icon button, "Dismiss" icon button
- On hover: slight elevation, "See why it matched" expands showing AI reasoning
- If autopilot already applied: show "Applied by PathAI • 3h ago" status badge instead of button

**Sorting:** Best match / Newest / Salary high-low / Company health

---

## 11. APPLICATIONS KANBAN PAGE

### Instructions for Copilot:
> Build `app/(dashboard)/applications/page.tsx`

Build a Kanban board with these columns (draggable cards via `@hello-pangea/dnd`):

```
Applied → Viewed → Interviewing → Offer → Hired
                                          Rejected (hidden by default, toggle to show)
                                          Ghosted (hidden by default)
```

**Column header:** Column name + count badge

**Application Card:**
- Company logo + name
- Job title
- Applied date + "X days ago"
- Applied via: "PathAI Auto" badge (brand color) or "Manual" (gray)
- Last action: "Follow-up sent 2d ago"
- Quick action buttons: "Add note", "Log interview", "Mark offer"

**Right-side detail panel** (slides in when card clicked):
- Full job description
- Timeline of all PathAI actions for this application
- Cover letter used (expandable)
- Tailored resume used (link)
- Outreach messages sent (expandable)
- Notes (editable textarea)
- Next action selector: Schedule follow-up / Log interview / Mark offer / Archive

**Stats bar above board:**
- Total active: N | Response rate: N% | Avg days to reply: N | Interviews this month: N

---

## 12. RESUME PAGE

### Instructions for Copilot:
> Build `app/(dashboard)/resume/page.tsx`

**Left panel — Resume editor (60%):**
- Sections: Summary, Experience (add/edit/delete roles), Education, Skills, Projects, Certifications
- Each field is inline-editable (click to edit, auto-save)
- AI enhance button per section: "✨ Rewrite with AI" → calls POST `/api/resume/enhance-section` with section content + job context
- Bullet point improver: select a bullet → "Improve this bullet" → AI rewrites with metrics/action verbs

**Right panel — Live preview (40%):**
- Real-time PDF-style preview as user edits
- ATS Score meter: 0-100 with color (red/yellow/green)
- Score breakdown: Keywords matched, Action verbs, Measurable results, Length, Formatting
- "Optimize for specific job" button: paste JD → AI tailors the full resume
- Download PDF button

**Versions section (below editor):**
- List of all AI-tailored versions created for specific jobs
- Each shows: company name, tailored date, ATS score, "Use as base" option

---

## 13. OUTREACH PAGE

### Instructions for Copilot:
> Build `app/(dashboard)/outreach/page.tsx`

**Left: Message list**
- Tabs: All / Pending / Sent / Replied
- Each row: recipient name, title, company, message type, status (sent/read/replied), sent date
- Color-coded status dots

**Right: Compose panel**
- Input: LinkedIn URL of target person
- Auto-fills: name, title, company (via scraping)
- Message type selector: LinkedIn connection note (300 chars) / LinkedIn message / Email
- AI generates message based on: user's profile + target person's role + specific job
- Preview with char count
- Edit freely before sending
- Send now / Schedule for best time (AI recommends weekday 9-11am)

**Reply handling:**
- When recruiter replies to a LinkedIn message/email, it shows up in a "Replies" section
- AI suggests response: "Would you like me to suggest a reply?"

**Sequence builder (premium):**
- Day 0: Connection request
- Day 3: Follow-up message if no reply
- Day 7: Secondary follow-up with proof of interest
- Visual timeline showing where each outreach is in its sequence

---

## 14. INTERVIEW PREP PAGE

### Instructions for Copilot:
> Build `app/(dashboard)/interviews/page.tsx`

**Upcoming interviews section (top):**
- Interview cards with: company, role, date/time, interview type (HR/Tech/System Design)
- "Prep now" button opens prep deck

**Prep deck (modal or slide-out panel):**
Generated fresh for each company + role combination:
1. "Company snapshot" — recent news, product, culture, Glassdoor rating
2. "Why they're interviewing for this role" — AI deduction from JD
3. "Likely questions" — pulled from interview intel DB + AI generation
   - Behavioral: STAR story prompts
   - Technical: Based on JD requirements
   - Role-specific: Based on company stack/domain
4. "Your STAR stories" — AI extracts 5-6 stories from user's resume, pre-formatted
5. "Questions to ask them" — 8 smart questions tailored to the company

**AI mock interview (bottom section):**
- Select: interview type + difficulty
- Chat interface where AI plays interviewer
- User answers in text or voice (Web Speech API)
- After each answer: AI scores (1-5) + gives specific feedback
- End of session: overall score + strengths + improvement areas

**Post-interview debrief (triggered 72h after interview date):**
- Short form: How did it go? What questions were asked? (text + select)
- Submitted data enriches the interview intel database
- User gets +50 "PathAI Points" for contributing

---

## 15. PUBLIC MICROSITE PAGE

### Instructions for Copilot:
> Build `app/[username]/page.tsx` (public, no auth)

This is each user's live shareable profile — sent to recruiters instead of a PDF.

**Design:** Premium, portfolio-feel. Dark background with subtle texture.

**Sections:**
1. **Hero:** Full name, current/target role, location, "Open to opportunities" badge, contact buttons (LinkedIn, Email, Download Resume)
2. **In brief:** 3-4 sentence AI-written professional pitch, tailored to the job it was shared for (pass `?role=sde&company=stripe` query params)
3. **Career highlights:** 3 big wins/stats extracted from resume ("Reduced pipeline latency by 40%", "Led team of 8 engineers", "Built system processing 2M events/day")
4. **Top skills:** Visual skill bars or tags, grouped by category
5. **Work history:** Clean timeline (not a PDF list)
6. **Featured project:** 1 highlighted project with tech stack + outcome
7. **Contact CTA:** "Schedule a call" → Calendly/Google Meet link

**Share mechanism:** `/dashboard/microsite` page lets user copy their link, customize their pitch, and see how many recruiters viewed it.

---

## 16. BACKEND — CORE SERVICES

### Instructions for Copilot:
> Build `backend/app/services/ai_service.py`

```python
"""
All Claude API calls. Every function takes structured input and returns structured output.
Use claude-sonnet-4-5 for all calls.
Use streaming for long generations (resume rewrite, cover letters).
"""

import anthropic
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

async def parse_resume(raw_text: str) -> dict:
    """
    Extract structured data from raw resume text.
    Returns: {
      skills: [{name, proficiency, years}],
      experience: [{company, title, start, end, bullets}],
      education: [{institution, degree, year}],
      career_dna: {top_strengths, keywords, seniority_level, domains},
      readiness_score: int (0-100)
    }
    """

async def match_job_to_resume(resume_json: dict, job: dict) -> dict:
    """
    Score how well a resume matches a job.
    Returns: {
      score: int (0-100),
      matching_skills: [str],
      missing_skills: [str],
      match_reasons: [str],
      concerns: [str]
    }
    """

async def tailor_resume(resume_json: dict, job: dict) -> dict:
    """
    Rewrite resume bullets and summary to match specific job.
    Returns modified resume_json with tailored content.
    Preserve truthfulness — only reframe, never fabricate.
    """

async def generate_cover_letter(resume_json: dict, job: dict, tone: str = "professional") -> str:
    """
    Generate a cover letter. NOT a template — genuinely specific to:
    - The exact role's requirements
    - The company's known culture/product
    - User's specific relevant experience
    Max 280 words. No "I am writing to apply for" openers.
    """

async def generate_recruiter_outreach(
    user_profile: dict,
    recruiter: dict,
    job: dict,
    message_type: str  # "connection_request" | "linkedin_message" | "email"
) -> str:
    """
    Generate personalized outreach. Rules:
    - Reference something specific about the recruiter's company/role
    - Lead with value, not ask
    - LinkedIn connection note: max 300 chars
    - LinkedIn message: max 1000 chars, conversational
    - Email: max 150 words, subject line included
    Never generic. Never "I hope this message finds you well."
    """

async def detect_ghost_job(job: dict, company_signals: dict) -> int:
    """
    Score job legitimacy 0-100.
    Input signals: days_since_posted, repost_count, company_headcount_trend,
    recent_layoffs, funding_status, glassdoor_interview_activity.
    Returns: ghost_score (0=definitely ghost, 100=definitely real)
    """

async def generate_interview_prep_deck(
    company: str, role: str, jd: str, user_resume: dict, intel: list
) -> dict:
    """
    Generate full interview prep deck.
    Returns: {
      company_snapshot: str,
      likely_questions: [{question, type, tips, sample_answer}],
      star_stories: [{situation, task, action, result, applicable_for}],
      questions_to_ask: [str],
      key_things_to_highlight: [str]
    }
    """

async def score_interview_answer(question: str, answer: str, role: str) -> dict:
    """
    Score a mock interview answer.
    Returns: {score: 1-5, feedback: str, what_was_good: [str], improve: [str]}
    """
```

---

### Instructions for Copilot:
> Build `backend/app/services/resume_parser.py`

```python
"""
PDF/DOCX parsing pipeline.
1. Extract raw text using PyMuPDF (PDF) or python-docx (DOCX)
2. Store raw text in DB
3. Call ai_service.parse_resume() for structured extraction
4. Store parsed_json and career_dna in DB
5. Create user_skills records from extracted skills
"""
```

Dependencies: `pymupdf`, `python-docx`, `supabase-py`

---

### Instructions for Copilot:
> Build `backend/app/services/job_scraper.py`

```python
"""
Job scraping service. Runs as Celery periodic task every 2 hours.

Sources to scrape:
1. LinkedIn Jobs API (unofficial via RapidAPI)
2. Naukri.com (Playwright scraping)
3. Indeed India (Playwright scraping)
4. Company career pages (Apify actors for top 50 companies)

For each user with autopilot ON:
1. Get their preferences (roles, locations, salary)
2. Search each source
3. Deduplicate (check external_id)
4. Score ghost likelihood
5. Score company health
6. Match against user's resume (ai_service.match_job_to_resume)
7. Store matches above threshold (default 70)
8. If match > 85 AND speed_apply ON AND job posted < 2h ago: trigger auto-apply

Ghost score signals to check:
- Job posting age (older = more suspect)
- Company on layoffs.fyi? (check Apify actor)
- LinkedIn headcount trend (from LinkedIn company page scrape)
- Repost history in our DB
"""
```

---

### Instructions for Copilot:
> Build `backend/app/tasks/apply_jobs.py`

```python
"""
Celery task: auto_apply_job(user_id, job_id)

Pipeline:
1. Load user profile + primary resume
2. Load job details
3. ai_service.tailor_resume() → tailored resume JSON
4. Render tailored resume to PDF (use weasyprint or reportlab)
5. Upload tailored PDF to Supabase Storage
6. ai_service.generate_cover_letter()
7. Create Application record (status="applied", applied_via="pathai_auto")
8. If job has apply_url:
   a. Use Playwright to navigate to apply URL
   b. Detect form fields (label matching)
   c. Fill: name, email, phone, resume upload, cover letter
   d. Handle common ATS platforms: Greenhouse, Lever, Workday, iCIMS
   e. Submit (or flag for manual review if CAPTCHA)
9. Log activity entry
10. Schedule follow-up task for day 5 if no reply

Error handling:
- If Playwright fails (CAPTCHA, unusual form): mark as "needs_manual_apply", notify user
- Never submit if confidence < 80% form was filled correctly
- Always log what was submitted
"""
```

---

## 17. BACKEND — API ROUTES

### Instructions for Copilot:
> Build `backend/app/api/routes/jobs.py`

```python
GET    /api/jobs/matches          # Get matched jobs for current user (paginated, filterable)
GET    /api/jobs/{job_id}         # Get job details + why it matched
POST   /api/jobs/{job_id}/save    # Save job
POST   /api/jobs/{job_id}/dismiss # Dismiss job
POST   /api/jobs/{job_id}/apply   # Manually trigger PathAI apply
GET    /api/jobs/fresh            # Jobs posted < 6h, high match
```

### Instructions for Copilot:
> Build `backend/app/api/routes/applications.py`

```python
GET    /api/applications                    # All user applications
GET    /api/applications/kanban             # Grouped by status for kanban
PATCH  /api/applications/{id}/status        # Update status
PATCH  /api/applications/{id}/notes         # Update notes
POST   /api/applications/{id}/hire          # Mark as hired (triggers fee flow)
GET    /api/applications/stats              # Response rate, funnel stats
```

### Instructions for Copilot:
> Build `backend/app/api/routes/resume.py`

```python
POST   /api/resume/upload          # Upload PDF/DOCX → parse → return structured data
GET    /api/resume                 # Get current resume data
PATCH  /api/resume/section         # Update a resume section
POST   /api/resume/enhance-section # AI enhance a specific section
POST   /api/resume/tailor          # Tailor resume for specific job (returns new version)
GET    /api/resume/versions        # All tailored versions
GET    /api/resume/ats-score       # Calculate ATS score
POST   /api/resume/download        # Generate and download PDF
```

### Instructions for Copilot:
> Build `backend/app/api/routes/payments.py`

```python
POST   /api/payments/success-fee/initiate  # Create Razorpay order for success fee
POST   /api/payments/success-fee/verify    # Verify Razorpay payment signature
GET    /api/payments/success-fee/status    # Check fee status
POST   /api/payments/webhook               # Razorpay webhook handler
GET    /api/payments/history               # Payment history
```

---

## 18. FRONTEND — KEY COMPONENTS

### Instructions for Copilot:
> Build `components/shared/CareerScoreCard.tsx`

A circular progress indicator showing the user's Career Health Score (0–100).
- Animated SVG arc that fills based on score
- Color: red (<40), yellow (40-70), green (70+)
- Center: large score number + small "/ 100"
- Below circle: 4 micro-stats: "Applications: 34", "Replies: 8", "Interviews: 3", "Response rate: 23%"
- Trend indicator: "↑ 4 pts this week" in green

---

### Instructions for Copilot:
> Build `components/shared/AutopilotToggle.tsx`

A premium-looking toggle for enabling/disabling autopilot mode.
- Large pill toggle, animated with spring physics (Framer Motion)
- When ON: green glow, "Autopilot: Active" text, animated green pulse dot
- When OFF: gray, "Autopilot: Paused" text
- On toggle: optimistic UI update + PATCH `/api/users/autopilot`
- Tooltip on hover: "PathAI is applying to matched jobs overnight"

---

### Instructions for Copilot:
> Build `components/jobs/MatchReasonPopover.tsx`

A popover that appears on hover over a job card's match score.
- Shows: "Why 91% match?"
- List of matching skills with green checkmarks
- List of missing skills with gray circles
- AI-written 1-sentence reason: "Strong match on data engineering stack — your Iceberg and Kafka experience directly matches their requirements."
- "Gaps to address" section (if any)

---

### Instructions for Copilot:
> Build `components/dashboard/ActivityFeed.tsx`

Real-time activity feed showing PathAI's automated actions.

```typescript
interface Activity {
  id: string
  type: 'applied' | 'outreach_sent' | 'match_found' | 'reply_received' | 'interview_scheduled' | 'follow_up_sent'
  title: string
  company: string
  companyLogo?: string
  timestamp: string
  metadata: Record<string, string>
}
```

Design:
- Timeline with vertical line on left
- Each item has icon (colored by type), company logo, description, relative time
- "Applied" items show the tailored resume thumbnail on hover
- "Reply received" items have a green highlight and "View reply" CTA
- Infinite scroll with skeleton loading
- Subtle entrance animation (Framer Motion, staggered)

---

## 19. NOTIFICATIONS SYSTEM

### Instructions for Copilot:
> Build `components/shared/NotificationCenter.tsx`

Slide-over panel (from right) triggered by bell icon in top nav.

Notification types with distinct icons + colors:
- `match_found` — New job matched (blue, sparkle icon)
- `applied` — PathAI applied to a job (green, check icon)
- `reply_received` — Recruiter replied (yellow, chat icon)
- `interview_scheduled` — Interview confirmed (purple, calendar icon)
- `fee_due` — Success fee payment due in 3 days (amber, warning icon)
- `prep_ready` — Interview prep deck ready (blue, book icon)

Each notification:
- Company logo, description, relative time
- Mark as read on click
- Action button where applicable ("View reply", "Start prep", "Pay now")

Store notifications in Supabase Realtime for live updates.

---

## 20. SUCCESS FEE PAYMENT FLOW

### Instructions for Copilot:
> Build `app/(dashboard)/payment/success-fee/page.tsx`

Triggered when user marks themselves as hired.

**Step 1 — Hire confirmation:**
- "Congratulations on your new role at [Company]!" celebration animation (confetti)
- Upload offer letter (PDF)
- Confirm start date
- Confirm accepted CTC (pre-filled from application data)
- PathAI shows: "Here's what we did to help" — full activity log for this application

**Step 2 — Fee calculation:**
- Display: "Your success fee: ₹[amount]"
- Math breakdown: "[CTC] × 1% = [fee] (capped at ₹15,000)"
- "Due date: [start_date + 60 days]"
- Options: Pay now (₹500 discount) / Auto-pay on due date / Pay in 3 EMIs

**Step 3 — Razorpay checkout:**
- Pre-filled Razorpay modal
- On success: confetti, "Thank you — you're PathAI's success story #[N]"
- Add to public testimonials wall (with permission)

**Step 4 — Connector invite:**
- "You're in the door at [Company]. Help others like you."
- Invite to become a PathAI connector at their new company
- Explain: earn ₹500–2000 for every successful warm intro you facilitate

---

## 21. COPILOT BUILD COMMANDS

Use these as step-by-step prompts to build the product in sequence:

### Phase 1 — Foundation (Week 1-2)
```
1. "Set up Next.js 14 project with TypeScript, Tailwind, shadcn/ui. Use the config from section 5."
2. "Build the authentication pages as described in section 6. Use Supabase Auth."
3. "Build the database schema from section 3 using Supabase."
4. "Set up FastAPI backend with the structure from section 2. Include auth middleware using Supabase JWT verification."
5. "Build the onboarding flow from section 7."
6. "Build the dashboard layout with sidebar and top nav from section 8."
```

### Phase 2 — Core features (Week 3-4)
```
7. "Build the resume upload and parsing pipeline from section 16 (resume_parser.py + ai_service.parse_resume)."
8. "Build the job matches page and JobCard component from sections 10 and 18."
9. "Build the applications kanban board from section 11 using @hello-pangea/dnd."
10. "Build the resume editor page with AI enhance from section 12."
11. "Build the dashboard home page from section 9."
```

### Phase 3 — Automation (Week 5-6)
```
12. "Build the Celery task for job scraping from section 16 (job_scraper.py)."
13. "Build the auto-apply Celery task from section 16 (apply_jobs.py) with Playwright."
14. "Build the outreach page and AI message generation from section 13."
15. "Build the notification system from section 19 using Supabase Realtime."
16. "Build the activity feed component from section 18."
```

### Phase 4 — Revenue + polish (Week 7-8)
```
17. "Build the interview prep page with mock interview from section 14."
18. "Build the public microsite page from section 15."
19. "Build the success fee payment flow from section 20 using Razorpay."
20. "Add Framer Motion animations: staggered list reveals, page transitions, number counters."
21. "Implement dark mode with the CSS variables from section 5."
22. "Add Sentry error tracking and basic analytics events."
```

---

## 22. TESTING CHECKLIST

Before shipping each feature, verify:

**Auth flow:**
- [ ] Signup → email confirmation → onboarding redirect
- [ ] Login with email/password
- [ ] Login with Google OAuth
- [ ] JWT refresh works (no random logouts)

**Resume parsing:**
- [ ] PDF upload works (try 3 different resume formats)
- [ ] Skill extraction is accurate
- [ ] Career DNA is specific, not generic

**Job matching:**
- [ ] Matches are relevant (not random)
- [ ] Match score explanation makes sense
- [ ] Ghost score removes obvious dead postings
- [ ] Speed apply triggers within 5 min of fresh posting

**Applications kanban:**
- [ ] Drag and drop changes status in DB
- [ ] Detail panel shows full history
- [ ] Notes auto-save

**Outreach:**
- [ ] Messages are personalized (not templated)
- [ ] LinkedIn note stays under 300 chars
- [ ] Schedule timing works

**Payments:**
- [ ] Razorpay test mode works end-to-end
- [ ] Webhook correctly updates payment status
- [ ] 60-day timer triggers notification

---

## 23. PERFORMANCE REQUIREMENTS

- Dashboard initial load: < 1.5s (LCP)
- Job matches API: < 400ms (cached with Redis, 5-min TTL)
- Resume parse: < 8s (show progress animation)
- AI cover letter generate: < 6s (streaming, show typing animation)
- Kanban drag: 60fps (no layout thrash)
- All images: WebP, lazy loaded
- Use React.memo on JobCard and ApplicationCard (render in lists)
- Infinite scroll (not pagination) for jobs and activity feed

---

## 24. SECURITY REQUIREMENTS

- All API routes require valid Supabase JWT (`Authorization: Bearer <token>`)
- Users can only access their own data (enforce in every DB query with `user_id = current_user_id`)
- Resume files in Supabase Storage: private bucket, signed URLs with 1h expiry
- Razorpay signature verification on every webhook
- Rate limiting: 60 req/min per user on AI endpoints (Redis counter)
- Never log API keys, resume content, or personal data in server logs
- CORS: only allow `NEXT_PUBLIC_APP_URL`

---

## 25. SAMPLE DATA FOR DEVELOPMENT

```json
{
  "sample_user": {
    "name": "Rahul Sharma",
    "email": "rahul@example.com",
    "target_roles": ["Senior Data Engineer", "Staff Data Engineer"],
    "location": "Bangalore",
    "min_salary_lpa": 25
  },
  "sample_jobs": [
    {
      "title": "Senior Data Engineer",
      "company": "Razorpay",
      "location": "Bangalore",
      "salary_min": 3000000,
      "salary_max": 4500000,
      "ghost_score": 88,
      "company_health_score": 82,
      "tags": ["Apache Spark", "Kafka", "Python", "Airflow"]
    },
    {
      "title": "Staff Data Engineer",
      "company": "PhonePe",
      "location": "Bangalore / Remote",
      "salary_min": 4000000,
      "salary_max": 6000000,
      "ghost_score": 91,
      "company_health_score": 79,
      "tags": ["Spark", "Iceberg", "Scala", "dbt"]
    }
  ]
}
```

---

*This document is the single source of truth for PathAI's build.*
*Every section is independently usable as a Copilot prompt.*
*Build in the order shown in Section 21 for the fastest path to a working product.*

