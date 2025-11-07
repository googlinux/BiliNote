# BiliNote SaaS Frontend

Modern, responsive SaaS website for BiliNote - AI-powered video notes generation platform.

## 🚀 Features

- **Landing Page**: Beautiful, conversion-optimized landing page with:
  - Hero section with clear value proposition
  - Feature showcase
  - Pricing table (Free, Basic $9/mo, Pro $29/mo, Enterprise $99/mo)
  - FAQ section
  - CTA sections

- **Authentication Pages**: Login and Register pages (UI only, backend integration pending)

- **Responsive Design**: Mobile-first design that works perfectly on all devices

- **Dark Mode**: Automatic dark mode support based on system preferences

- **Modern Tech Stack**:
  - Next.js 16 (App Router)
  - React 19
  - TypeScript
  - Tailwind CSS v4
  - Shadcn UI components
  - Lucide Icons

## 🛠️ Development

### Prerequisites

- Node.js 18+
- pnpm (or npm/yarn)

### Getting Started

```bash
# Install dependencies
pnpm install

# Run development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start
```

The app will be available at `http://localhost:3000`

## 📁 Project Structure

```
saas-web/
├── app/                      # Next.js App Router pages
│   ├── auth/                # Authentication pages
│   │   ├── login/          # Login page
│   │   └── register/       # Register page
│   ├── page.tsx            # Landing page (home)
│   ├── layout.tsx          # Root layout
│   └── globals.css         # Global styles + Tailwind
├── components/
│   ├── landing/            # Landing page sections
│   │   ├── navbar.tsx
│   │   ├── hero-section.tsx
│   │   ├── features-section.tsx
│   │   ├── pricing-section.tsx
│   │   ├── faq-section.tsx
│   │   ├── cta-section.tsx
│   │   └── footer.tsx
│   └── ui/                 # Reusable UI components
│       └── button.tsx
├── lib/
│   └── utils.ts            # Utility functions
└── public/                 # Static assets
```

## 🎨 Design System

- **Colors**: Zinc-based color palette with dark mode support
- **Typography**: Geist Sans and Geist Mono fonts
- **Spacing**: Consistent spacing scale using Tailwind
- **Components**: Built with Radix UI primitives for accessibility

## 🌍 Global Features

- **English by default**: All content in English for global audience
- **USD pricing**: $9, $29, $99 pricing tiers
- **Stripe ready**: Designed for Stripe payment integration

## 📝 Next Steps

### Phase 1: Backend Integration (Pending)
- [ ] User authentication API (JWT)
- [ ] Database setup (PostgreSQL)
- [ ] User registration/login endpoints

### Phase 2: Dashboard (Pending)
- [ ] User dashboard layout
- [ ] Notes list and management
- [ ] Usage statistics
- [ ] Settings pages

### Phase 3: Payment Integration (Pending)
- [ ] Stripe checkout flow
- [ ] Subscription management
- [ ] Quota tracking
- [ ] Invoice history

### Phase 4: Core Features (Pending)
- [ ] Video note generation UI
- [ ] Markdown viewer/editor
- [ ] Export functionality
- [ ] API integration with backend

## 📄 License

MIT License - See main project for details

## 🔗 Links

- Main Repository: [BiliNote](https://github.com/JefferyHcool/BiliNote)
- Documentation: Coming soon
- API Docs: Coming soon

---

**Status**: 🚧 Phase 5 Complete - Landing Page Ready for Review
