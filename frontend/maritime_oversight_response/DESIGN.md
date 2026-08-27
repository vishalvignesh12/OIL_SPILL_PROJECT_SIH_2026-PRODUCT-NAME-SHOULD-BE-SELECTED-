---
name: Maritime Oversight & Response
colors:
  surface: '#fbf9f9'
  surface-dim: '#dbdad9'
  surface-bright: '#fbf9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f3f3'
  surface-container: '#efeded'
  surface-container-high: '#e9e8e7'
  surface-container-highest: '#e3e2e2'
  on-surface: '#1b1c1c'
  on-surface-variant: '#44474e'
  inverse-surface: '#303031'
  inverse-on-surface: '#f2f0f0'
  outline: '#74777f'
  outline-variant: '#c4c6cf'
  surface-tint: '#465f88'
  primary: '#000a1e'
  on-primary: '#ffffff'
  primary-container: '#002147'
  on-primary-container: '#708ab5'
  inverse-primary: '#aec7f6'
  secondary: '#096969'
  on-secondary: '#ffffff'
  secondary-container: '#a2f0ef'
  on-secondary-container: '#166f6f'
  tertiary: '#180500'
  on-tertiary: '#ffffff'
  tertiary-container: '#3d1500'
  on-tertiary-container: '#b97958'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d6e3ff'
  primary-fixed-dim: '#aec7f6'
  on-primary-fixed: '#001b3d'
  on-primary-fixed-variant: '#2d476f'
  secondary-fixed: '#a2f0ef'
  secondary-fixed-dim: '#86d4d3'
  on-secondary-fixed: '#002020'
  on-secondary-fixed-variant: '#004f4f'
  tertiary-fixed: '#ffdbcb'
  tertiary-fixed-dim: '#ffb691'
  on-tertiary-fixed: '#341100'
  on-tertiary-fixed-variant: '#6c391d'
  background: '#fbf9f9'
  on-background: '#1b1c1c'
  surface-variant: '#e3e2e2'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-lg:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
  container-max: 1440px
---

## Brand & Style

This design system is engineered for mission-critical oversight, environmental protection, and legal accountability. The brand personality is **authoritative, precise, and transparent**. It prioritizes utility and rapid information retrieval over aesthetic decoration, reflecting the gravity of national maritime security and ecological preservation.

The design style follows **Corporate Modernism with a focus on Information Density**. It utilizes a structured grid, high-contrast text, and a restrained color palette to ensure legibility in high-stress monitoring environments. Every interface element is designed to feel stable and institutional, avoiding transient design trends like glassmorphism or neomorphism in favor of clear, geometric clarity.

## Colors

The color palette is anchored by **Deep Navy (#002147)**, providing an institutional foundation that evokes the sea and governmental authority. **Muted Teal (#006666)** is used as a secondary functional color for maritime-specific data layers and navigation elements.

- **Primary:** Reserved for headers, primary actions, and brand identification.
- **Secondary:** Used for data categorization and contextual maritime highlights.
- **Neutrals:** A scale of grays from `#F5F5F5` for surface backgrounds to `#717171` for secondary text and borders.
- **Semantic Colors:** Critical for monitoring. Green, Amber, and Red are used strictly for status indicators (e.g., "Clear," "Potential Leak," "Confirmed Spill"). These colors must maintain a minimum contrast ratio of 4.5:1 against their backgrounds.

## Typography

The design system utilizes **Inter** for all levels of the hierarchy. Inter was selected for its exceptional legibility at small sizes, particularly in data-heavy tables and map tooltips.

- **Headlines:** Use Bold or Semi-Bold weights to create a strong visual anchor for report titles and dashboard sections.
- **Body Text:** Standardized at 16px for optimal readability of long-form reports. 
- **Labels:** Small labels use a higher font weight and slight tracking (letter-spacing) to ensure clarity when used in metadata badges or table headers.
- **Numbers:** When displaying coordinates or vessel IDs, use tabular lining figures to ensure vertical alignment in lists.

## Layout & Spacing

This design system uses a **12-column fixed grid** for desktop and a **fluid single-column grid** for mobile. The layout is designed to handle high-density information displays, such as satellite imagery side-by-side with vessel manifests.

- **Rhythm:** An 8px base unit (incremented by 4px for fine-tuning) governs all padding and margins.
- **Safe Areas:** Large internal margins (40px on desktop) are used to prevent visual clutter and maintain a "premium" institutional feel.
- **Breakpoints:**
  - Mobile: < 600px (4 columns, 16px margin)
  - Tablet: 600px - 1024px (8 columns, 24px margin)
  - Desktop: > 1024px (12 columns, 40px margin, 1440px max-width)

## Elevation & Depth

To maintain a government-grade aesthetic, depth is achieved through **low-contrast outlines and tonal layering** rather than heavy shadows.

- **Base Layer:** `#FFFFFF` for the primary work surface.
- **Navigation/Sidebars:** `#F5F5F5` to provide a subtle structural distinction from the main content.
- **Cards & Containers:** Use a 1px solid border in `#E0E0E0` (Light Gray). 
- **Shadows:** Reserved strictly for ephemeral elements like dropdown menus or modals. When used, shadows must be "Ambient": very diffused, 10% opacity, with 0px offset to suggest the element is floating just above the surface without casting a dramatic shadow.

## Shapes

The shape language is **structured and conservative**. Sharp corners suggest precision, while a very subtle 4px (`0.25rem`) radius is applied to interactive elements to prevent the UI from feeling aggressive.

- **Input Fields & Buttons:** 4px border-radius.
- **Cards & Modals:** 8px (`0.5rem`) border-radius.
- **Pill Shapes:** Strictly prohibited for functional buttons; reserved only for status "chips" or "tags" to distinguish them from interactive buttons.

## Components

### Buttons
- **Primary:** Solid `#002147` background, white text. No gradients. High-contrast focus state with a 2px offset ring.
- **Secondary:** Outline variant with `#002147` border and text. 
- **Destructive:** Solid `#D32F2F` for actions like "Delete Monitoring Zone."

### Input Fields
- **Styling:** Solid 1px border (`#717171`), white background. 
- **States:** Active/Focus state uses the Primary Navy color for the border (2px thickness). Labels are always persistent above the field; never use placeholder text as a label substitute.

### Cards
- **Construction:** White background, 1px Gray border, no shadow. 
- **Headers:** Use a subtle `#F5F5F5` background for card headers to separate metadata from the content body.

### Data Tables
- **Essential:** Tables are the core of this system. They must feature zebra-striping using `#F5F5F5` for every second row. 
- **Typography:** Use `label-md` for headers and `body-md` for row content.

### Monitoring Specifics
- **Status Chips:** Small, condensed text in all-caps (`label-sm`). Use semantic background tints with high-contrast text (e.g., Light Red background with Dark Red text for "Critical Spill").
- **Vessel Identifiers:** Displayed in a monospaced-adjacent style (utilizing Inter's tabular figures) for rapid visual scanning of numeric ID codes.