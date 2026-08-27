---
last_mapped: 2026-08-27
---

# CONVENTIONS.md — Code Style & Patterns

## HTML Structure Convention

Every `code.html` follows this consistent structure:

```html
<!DOCTYPE html>
<html class="light" lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Screen Title]</title>
  
  <!-- 1. Tailwind CDN -->
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  
  <!-- 2. Material Symbols (often duplicated) -->
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:..." rel="stylesheet">
  
  <!-- 3. Inter font -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700" rel="stylesheet">
  
  <!-- 4. Inline Tailwind config (same block duplicated across all pages) -->
  <script id="tailwind-config">
    tailwind.config = { darkMode: "class", theme: { extend: { ... } } }
  </script>
  
  <!-- 5. Optional: page-specific <style> block for CSS not achievable via Tailwind -->
</head>
<body class="bg-[surface] text-[on-surface] ...">
  <!-- content -->
  <script>/* minimal JS */</script>
</body>
</html>
```

## Tailwind Usage Patterns

### Color Token Usage
Colors from the design system are used as Tailwind utility classes:
```html
<div class="bg-primary-container text-on-primary border-outline-variant">
<span class="text-on-surface-variant">
<div class="bg-surface-container-high">
```

### Typography Scale Classes
Typography uses custom fontSize utilities from Tailwind config:
```html
<h1 class="font-headline-lg text-headline-lg font-bold">
<p class="font-body-md text-body-md">
<span class="font-label-sm text-label-sm uppercase tracking-wider">
```
> Note: Both `font-[scale]` and `text-[scale]` are applied — `font-*` sets fontFamily, `text-*` sets fontSize.

### Layout Patterns
```html
<!-- Sidebar layout (interior pages) -->
<nav class="w-[260px] h-screen fixed left-0 top-0 ...">
<div class="ml-[260px] flex-1 flex flex-col h-screen overflow-hidden">

<!-- Split login layout -->
<section class="hidden lg:block w-1/2 relative bg-primary">   <!-- hero -->
<section class="w-full lg:w-1/2 flex items-center justify-center"> <!-- form -->
```

### Interactive States
```html
<!-- Hover/active micro-animations -->
class="hover:bg-surface-container-highest hover:text-on-surface 
       transition-colors duration-150 scale-100 active:scale-[0.98]"

<!-- Focus rings (accessibility) -->
class="focus:ring-2 focus:ring-primary focus:border-primary outline-none"
```

### Navigation Active State
```html
<!-- Active nav item -->
class="text-primary font-bold border-r-4 border-primary bg-surface-container-high"

<!-- Inactive nav item -->
class="text-on-surface-variant hover:bg-surface-container-highest hover:text-on-surface"
```

### Status Chips / Badges
```html
<!-- Error/Critical -->
<span class="bg-error-container text-on-error-container px-2 py-1 rounded uppercase">
<!-- Success/Active -->
<span class="bg-secondary-container text-on-secondary-container ...">
<!-- Neutral info -->
<span class="bg-surface-container-high text-on-surface border border-outline-variant ...">
```

## Icon Usage

Material Symbols Outlined used consistently:
```html
<span class="material-symbols-outlined">dashboard</span>
<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">map</span>
<span class="material-symbols-outlined text-[20px]">lock_person</span>
```

- Size controlled via `text-[Npx]` utility or inherits from parent
- Fill state toggled via `font-variation-settings` inline style for active icons
- `data-icon="..."` attribute used for semantic identification (navigation items)

## JavaScript Conventions

Pages use minimal inline JavaScript only:
```html
<script>
  // Common pattern: set current date dynamically
  document.getElementById('current-date').textContent = 
    new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
</script>
```

No external JS libraries. No module system. No event delegation patterns — interactions are CSS-driven (hover, focus).

## Naming Conventions

- **IDs:** descriptive lowercase with hyphens (`id="email"`, `id="password"`, `id="current-date"`, `id="tailwind-config"`)
- **CSS classes:** Tailwind utilities only — no custom class names created
- **Inline styles:** Only used for `font-variation-settings` on Material Symbols for FILL state
- **HTML attributes:** `data-icon="..."` on Material Symbol spans for icon identification

## Page Title Convention

```
[Screen Name] - [System/Product Name]
```
Examples:
- `Login - National Marine Oil Spill Monitoring System`
- `Maritime Intel - Command Dashboard`
- `Oil Spill Detection - Maritime Intel`
- `Evidence Dossier - INC-2026-001 | Geospatial Investigation Platform`
