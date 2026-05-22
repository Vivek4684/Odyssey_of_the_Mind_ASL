# Odyssey of the Mind - ASL Performance App

A mobile-friendly web app that provides American Sign Language (ASL) video interpretation for the Odyssey of the Mind final performance. Audience members who are deaf or hard of hearing can scan a QR code to access the ASL videos on their phones.

## How It Works

1. **Generate a QR code** pointing to the hosted URL of this app
2. **Print the QR code** and display it at the performance venue
3. **Audience members scan** the QR code with their phone camera
4. **They watch ASL videos** synced with the performance story scenes

## Setup Instructions

### 1. Add Your Story Content

Edit `story-data.js` to update the story text for each scene:

```javascript
{
    title: "Scene 1: Your Title",
    text: `<p>Your story text here...</p>`,
    video: "videos/scene1.mp4"
}
```

### 2. Add ASL Videos

1. Record ASL interpretation videos for each scene
2. Save them as MP4 files in the `videos/` folder
3. Name them to match the references in `story-data.js` (e.g., `scene1.mp4`, `scene2.mp4`, etc.)

### 3. Host the App

**Option A: GitHub Pages (Free & Easy)**
1. Push this repo to GitHub
2. Go to Settings > Pages
3. Set source to "main" branch
4. Your app will be live at `https://yourusername.github.io/repo-name/`

**Option B: Netlify/Vercel**
1. Connect your GitHub repo
2. Deploy automatically

### 4. Generate QR Code

Once hosted, generate a QR code for your URL:
- Use [QR Code Generator](https://www.qrcode-monkey.com/)
- Or any free QR code tool
- Print it large enough to scan from 3-5 feet away (minimum 2x2 inches)

## File Structure

```
├── index.html          # Main HTML page
├── styles.css          # All styling (mobile-first responsive)
├── app.js              # Application logic & navigation
├── story-data.js       # Story content & video references (EDIT THIS)
├── videos/             # Place ASL video files here
│   ├── scene1.mp4
│   ├── scene2.mp4
│   └── ...
└── README.md           # This file
```

## Features

- Mobile-first responsive design (optimized for phone scanning)
- Scene-by-scene navigation with swipe gestures
- Video player with controls
- Keyboard navigation (arrow keys)
- Accessible design with high contrast support
- No dependencies - pure HTML/CSS/JS
- Works offline once loaded

## Tips for ASL Videos

- Record in good lighting with a plain background
- Keep the signer centered and visible from waist up
- Use landscape orientation (16:9)
- Keep videos under 2 minutes per scene for quick loading
- Use MP4 format with H.264 codec for best compatibility

## QR Code Placement Tips

- Place QR codes at audience seating level
- Include a brief text label: "Scan for ASL interpretation"
- Test the QR code from various distances before the show
- Have a backup URL written below the QR code
