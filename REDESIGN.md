# REDESIGN — Match ICAIRE Website Design

## ICAIRE Design System (from icaire.org)

### Fonts
- **Primary:** Poppins (Google Fonts) — weights 400, 500, 600, 700
- **Body:** Inter (Google Fonts) — weights 300, 400, 500, 600, 700
- **Arabic:** Cairo (Google Fonts) — weights 400, 700
- Import: `https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap`
- Also: `https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap`

### Color Palette
- **Primary Dark Green:** #1A5C3A (hero overlay, headers)
- **Deeper Green:** #0D3D2A (darker sections, footer)
- **Accent Mint Green:** #4DC88E (highlights, accent text, buttons)
- **Text White:** #FFFFFF
- **Text Soft White:** rgba(255,255,255,0.85)
- **Background Light:** #F8FAFC or white
- **Text Dark (on light bg):** #1E293B
- **Text Muted:** #64748B
- **Border:** #E2E8F0
- **Card BG:** #FFFFFF with subtle shadow

### Hero Section
- Full-viewport hero with a lighthouse image background
- Heavy green overlay: rgba(20, 90, 60, 0.75) gradient
- Green tint from lighter (#2D7A50 at top) to darker (#0D3D2A at bottom)
- Text centered, bold Poppins
- "Artificial Intelligence" line in italic + accent mint green (#4DC88E)
- Tagline in lighter weight

### Navigation
- Transparent nav bar overlaying hero
- Logo(s) left, nav links right
- White text, Poppins medium ~14px
- No background

### Cards
- White background (#FFFFFF)
- Border-radius: 8-10px
- Box-shadow: 0 2px 8px rgba(0,0,0,0.15)
- Padding: generous (~24px)

### Buttons
- Primary: #4DC88E background, white text, border-radius 6-8px
- Secondary/Ghost: transparent bg, white border, white text

### Section Design
- Dark green sections alternate with light/white sections
- Section headings: Poppins SemiBold/Bold, white on dark, dark on light
- Generous spacing between sections

### Partner Logos
- Small white rounded-rect cards containing logos
- In a horizontal row

### Overall Aesthetic
- Moody, institutional, professional
- Green monochrome theme
- Minimal UI chrome
- Lighthouse metaphor ("International Lighthouse for AI")
- Bilingual English/Arabic support

## Task
Rebuild index.html to match this EXACT design system. Keep all the existing data and sections from the current dashboard (status tracker, country cards, comparison table, radar chart, gap analysis, sources). But restyle EVERYTHING to look like it belongs on icaire.org:

1. Use the same fonts (Poppins, Inter, Cairo)
2. Use the same green color palette (not blue/teal)
3. Hero section: dark green gradient background (no need for lighthouse image, just the green gradient), centered title
4. Navigation: transparent, minimal, matching ICAIRE style
5. Cards: white with subtle shadow on green or light sections
6. Alternate between dark green sections and light sections
7. Accent color #4DC88E for highlights, charts, interactive elements
8. Chart.js colors should use the green palette
9. Status badges: use greens and appropriate secondary colors
10. Footer: dark green with white text
11. Overall feel: institutional, UNESCO-grade, professional

Keep data.json unchanged — just restyle the HTML/CSS completely.
