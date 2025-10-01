#!/bin/bash

# Convert the guide to a printable HTML file
pandoc COMPLETE_BEGINNERS_GUIDE.md \
  -o COMPLETE_BEGINNERS_GUIDE.html \
  --standalone \
  --toc \
  --toc-depth=3 \
  --metadata title="Complete Beginner's Guide to Django" \
  --css=pdf-style.css

echo "✅ HTML created: COMPLETE_BEGINNERS_GUIDE.html"
echo ""
echo "To create PDF:"
echo "1. Open COMPLETE_BEGINNERS_GUIDE.html in your browser"
echo "2. Press Cmd+P (or File → Print)"
echo "3. Select 'Save as PDF' as destination"
echo "4. Click 'Save'"
echo ""
echo "Your PDF will be ready!"
