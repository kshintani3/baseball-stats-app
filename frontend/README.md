# NPB Stats Frontend

A modern Next.js frontend application for displaying Japanese Professional Baseball (NPB) statistics.

## Features

- **Dashboard**: Overview of top batters, pitchers, and team standings
- **Batter Rankings**: Searchable and filterable batter statistics
- **Pitcher Rankings**: Pitcher performance rankings with role filtering
- **Team Standings**: Team rankings and statistics
- **Player Details**: Individual player statistics across multiple seasons with charts
- **Player Comparison**: Compare up to 4 players side-by-side

## Technology Stack

- **Framework**: Next.js 14.2.0
- **UI**: React 18.2.0
- **Styling**: Tailwind CSS 3
- **Charts**: Recharts 2.10.0
- **Language**: TypeScript 5

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Install dependencies:

```bash
npm install
```

2. Configure the API endpoint:

Create a `.env.local` file based on `.env.example`:

```bash
cp .env.example .env.local
```

Edit `.env.local` and set the API URL:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── layout.tsx           # Root layout with navbar
│   ├── page.tsx             # Dashboard
│   ├── batters/             # Batter rankings
│   ├── pitchers/            # Pitcher rankings
│   ├── teams/               # Team standings and rankings
│   ├── players/[id]/        # Player detail page
│   ├── compare/             # Player comparison
│   └── globals.css          # Global styles
├── components/              # Reusable React components
│   ├── Navbar.tsx          # Navigation sidebar
│   ├── RankingTable.tsx    # Data table component
│   ├── SeasonSelector.tsx  # Season dropdown
│   ├── StatSelector.tsx    # Stat definition dropdown
│   ├── TeamFilter.tsx      # Team filter dropdown
│   ├── PlayerCard.tsx      # Player info card
│   └── StatsChart.tsx      # Recharts wrapper
├── lib/                     # Utilities
│   └── api.ts              # API client functions
├── types/                   # TypeScript types
│   └── index.ts            # Type definitions
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
└── postcss.config.js
```

## API Integration

The frontend connects to a backend API at the URL specified in `NEXT_PUBLIC_API_URL`. The API client (`lib/api.ts`) provides typed functions for all endpoints:

- `fetchBatterRankings()` - Batter statistics rankings
- `fetchPitcherRankings()` - Pitcher statistics rankings
- `fetchTeamRankings()` - Team statistics rankings
- `fetchPlayer()` - Individual player information
- `fetchPlayerStats()` - Player statistics across seasons
- `fetchComparePlayers()` - Compare multiple players
- `fetchStatDefinitions()` - Available statistics metadata
- `fetchSeasons()` - Available seasons
- `fetchTeams()` - Team list
- `fetchTeamStandings()` - Team standings

## Features Details

### Dashboard
- Year/season selector
- Top 5 batter preview
- Top 5 pitcher preview
- Team standings preview
- Quick navigation cards

### Batter Rankings
- Stat selector with automatic decimal precision
- Team filter
- Minimum plate appearances filter
- Sortable table with pagination
- Limit selector (20/50/100 items)
- Player links to detail pages

### Pitcher Rankings
- Same filters as batters
- Additional role filter (All/Starter/Reliever)
- Minimum innings pitched filter
- Role-specific statistics

### Team Pages
- Toggle between standings and rankings views
- Full season statistics
- Games back calculation
- Win/Loss/Tie display
- Team statistics comparisons

### Player Detail
- Player header with all information
- Season selector
- Statistics charts (line charts with seasonal progression)
- Detailed stats grid for selected season
- Full season history table
- Compare button for multi-player comparison

### Player Comparison
- Add/remove up to 4 players
- Season-specific comparison
- Bar chart visualization
- Side-by-side statistics table
- Player info cards

## Styling

The application uses a dark theme with:
- Dark gray background (#111827)
- Gray card backgrounds (#1f2937)
- Blue accent colors (#3b82f6)
- Japanese language throughout
- Responsive design for all screen sizes
- Hover effects and smooth transitions

## Internationalization

All UI text is in Japanese (日本語):
- Navigation labels
- Page titles
- Form labels
- Error messages
- Button text

## Error Handling

- API errors are caught and displayed to users
- Loading states for all async operations
- Fallback UI when data is unavailable
- Clear error messages in Japanese

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Server-side rendering with Next.js
- Optimized images and assets
- Code splitting for faster page loads
- Tailwind CSS for minimal CSS output
- Recharts for efficient chart rendering

## License

Proprietary - NPB Stats
