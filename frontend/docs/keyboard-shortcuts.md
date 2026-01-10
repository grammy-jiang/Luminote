# Keyboard Shortcuts

Luminote supports comprehensive keyboard navigation for power users who want to
navigate content without using a mouse.

## Block Navigation

### Within a Pane

- **Arrow Up** - Navigate to the previous block in the current pane
- **Arrow Down** - Navigate to the next block in the current pane
- **Home** - Jump to the first block in the current pane
- **End** - Jump to the last block in the current pane

### Between Panes

- **Tab** - Switch focus from left pane (Source) to right pane (Translation)
- **Shift + Tab** - Switch focus from right pane (Translation) to left pane
  (Source)

### Cross-Pane Navigation

- **Enter** or **Space** - When focused on a block, jump to the corresponding
  block in the other pane
  - From Source pane → Scrolls to matching block in Translation pane
  - From Translation pane → Scrolls to matching block in Source pane

## Pane Resizing

- **Ctrl + Arrow Left** - Decrease left pane width (increase right pane width)
- **Ctrl + Arrow Right** - Increase left pane width (decrease right pane width)

## Visual Feedback

- Focused blocks have a **blue outline** (`outline: 2px solid #3b82f6`)
- Navigated blocks have a **pulse animation** for visual feedback
- Highlighted blocks (from cross-pane navigation) have a **yellow background**
  with orange outline

## Accessibility Features

- All keyboard shortcuts prevent default browser behavior to avoid conflicts
- Screen reader announcements for cross-pane navigation
- ARIA labels for all interactive elements
- Semantic HTML structure (headings, lists, blockquotes, etc.)
- Keyboard focus indicators meet WCAG 2.1 standards

## Tips for Keyboard Users

1. **Start with Tab**: Press Tab to focus the left pane, then use Arrow keys to
   navigate blocks
1. **Jump Quickly**: Use Home/End to quickly reach the first or last block
1. **Cross-Reference**: Press Enter on a source block to see its translation
   instantly
1. **Adjust Layout**: Use Ctrl + Arrow keys to resize panes to your preference
1. **Sequential Navigation**: Navigate through all blocks using Arrow Down
   repeatedly

## Browser Compatibility

These keyboard shortcuts work in all modern browsers:

- Chrome/Edge (v90+)
- Firefox (v88+)
- Safari (v14+)

## Known Limitations

- Browser extensions or operating system shortcuts may conflict with some
  keyboard shortcuts
- Some screen readers may announce navigation differently depending on
  configuration
- In mobile browsers, keyboard shortcuts require an external keyboard
