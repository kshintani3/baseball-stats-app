# Quick Start Guide

## Installation & Setup (5 minutes)

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure API endpoint**
   ```bash
   cp .env.example .env.local
   # Edit .env.local and set NEXT_PUBLIC_API_URL
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open browser**
   - Navigate to http://localhost:3000
   - The app should load with the navbar on the left

## Features Overview

### Dashboard (/)
- Overview of top batters and pitchers
- Team standings preview
- Quick navigation to other sections
- Season selector

### Batter Rankings (/batters)
- Filter by season, team, stat type
- Minimum plate appearances filter
- Sortable table with pagination
- Click player names to view details

### Pitcher Rankings (/pitchers)
- Similar to batter rankings
- Additional "Role" filter (Starter/Reliever)
- Minimum innings pitched filter

### Teams (/teams)
- Toggle between "Standings" and "Rankings" views
- Full season standings with win/loss/tie
- Team statistics rankings

### Player Detail (/players/[id])
- Complete player information
- Season-specific statistics
- Line chart showing stat progression
- All-time statistics table
- "Compare" button to add to comparison

### Player Comparison (/compare)
- Add up to 4 players by ID
- Season selector
- Side-by-side statistics table
- Bar chart comparing main stat
- Player info cards

## API Integration

The app connects to the backend API (default: http://localhost:8000)

Key endpoints used:
- `GET /api/rankings/batters` - Batter rankings
- `GET /api/rankings/pitchers` - Pitcher rankings
- `GET /api/rankings/teams` - Team rankings
- `GET /api/standings` - Team standings
- `GET /api/players/{id}` - Player info
- `GET /api/players/{id}/stats` - Player stats
- `GET /api/compare` - Compare players
- `GET /api/meta/stats` - Available statistics
- `GET /api/meta/seasons` - Available seasons
- `GET /api/meta/teams` - Team list

## Development

### File Structure
```
frontend/
├── app/              # Pages (Next.js App Router)
├── components/       # Reusable components
├── lib/             # API client & utilities
├── types/           # TypeScript types
└── [config files]
```

### Adding a New Page
1. Create a new folder in `app/` directory
2. Add `page.tsx` file
3. Use existing components (SeasonSelector, RankingTable, etc.)

### Modifying Styles
- Tailwind CSS is configured
- Edit `app/globals.css` for global styles
- Use utility classes in components

### API Calls
- All API calls in `lib/api.ts`
- Functions are fully typed with TypeScript
- Error handling built-in

## Troubleshooting

### Port 3000 already in use
```bash
npm run dev -- -p 3001
```

### API connection errors
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Ensure backend is running at the specified URL
- Check browser console for detailed errors

### Build errors
```bash
npm run build
# Check for TypeScript errors
```

### Clear cache
```bash
rm -rf .next
npm run dev
```

## Browser DevTools

- Use React Developer Tools extension for component debugging
- Check Network tab to monitor API calls
- Console shows any JavaScript errors

## Deployment

### Build for production
```bash
npm run build
npm start
```

### Environment variables for production
Create `.env.local` with production API URL:
```
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## Performance Tips

- Stats pages use pagination (20/50/100 items)
- Recharts handles large datasets efficiently
- Dark theme reduces eye strain
- Responsive design works on all devices

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions

## Need Help?

- Check console for errors: F12 → Console
- Review API responses: F12 → Network
- Read component documentation in code comments

---

Enjoy exploring NPB statistics!
