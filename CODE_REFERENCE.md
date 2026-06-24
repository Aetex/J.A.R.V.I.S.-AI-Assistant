# UI Redesign - Code Reference Guide

## Quick Reference: What Was Added

### 1. New CSS Animations

```css
/* Menu Button Pulsing Glow */
@keyframes menuButtonGlow {
    0% { box-shadow: 0 0 0px rgba(0, 255, 0, 0); }
    50% { box-shadow: 0 0 8px rgba(0, 255, 0, 0.4); }
    100% { box-shadow: 0 0 0px rgba(0, 255, 0, 0); }
}

/* Dropdown Menu Expansion */
@keyframes menuDropdown {
    from {
        opacity: 0;
        transform: translateY(-10px) scaleY(0.8);
    }
    to {
        opacity: 1;
        transform: translateY(0) scaleY(1);
    }
}

/* Update Overlay Fade-In */
@keyframes overlayFadeIn {
    from {
        opacity: 0;
        backdrop-filter: blur(0px);
    }
    to {
        opacity: 1;
        backdrop-filter: blur(5px);
    }
}
```

### 2. Header Button Styling

```css
.header-btn {
    background: none;
    border: 1px solid #00f6ff;
    color: #00f6ff;
    cursor: pointer;
    font-size: 0.6rem;
    padding: 4px 8px;
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 1px;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    position: relative;
    overflow: hidden;
}

.header-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: rgba(0, 246, 255, 0.1);
    transition: left 0.3s ease;
    z-index: -1;
}

.header-btn:hover::before {
    left: 0;
}

.header-btn:hover {
    box-shadow: 0 0 12px rgba(0, 246, 255, 0.6), 
                inset 0 0 8px rgba(0, 246, 255, 0.1);
    transform: translateY(-2px);
    border-color: rgba(0, 246, 255, 0.95);
}
```

### 3. Menu Button (Green) Specific

```css
.menu-toggle-btn {
    border-color: #00ff00;
    color: #00ff00;
    animation: menuButtonGlow 2s ease-in-out infinite;
}

.menu-toggle-btn::before {
    background: rgba(0, 255, 0, 0.1);
}

.menu-toggle-btn:hover {
    box-shadow: 0 0 12px rgba(0, 255, 0, 0.6), 
                inset 0 0 8px rgba(0, 255, 0, 0.1);
    border-color: rgba(0, 255, 0, 0.95);
}

.menu-toggle-btn.active {
    background: rgba(0, 255, 0, 0.1);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.7), 
                inset 0 0 10px rgba(0, 255, 0, 0.2);
}
```

### 4. Dropdown Menu Styling

```css
.action-menu {
    position: absolute;
    top: 100%;
    right: 0;
    background: rgba(10, 20, 30, 0.95);
    border: 1px solid rgba(0, 246, 255, 0.3);
    border-radius: 5px;
    margin-top: 5px;
    min-width: 180px;
    box-shadow: 0 0 20px rgba(0, 246, 255, 0.3), 
                inset 0 0 10px rgba(0, 246, 255, 0.05);
    z-index: 100;
    backdrop-filter: blur(10px);
    overflow: hidden;
}

.action-menu.hidden {
    display: none;
    opacity: 0;
    transform: translateY(-10px) scaleY(0.9);
}

.action-menu.visible {
    display: flex;
    flex-direction: column;
    animation: menuDropdown 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}
```

### 5. Menu Items Styling

```css
.menu-item {
    background: none;
    border: none;
    border-bottom: 1px solid rgba(0, 246, 255, 0.1);
    color: #00f6ff;
    padding: 12px 15px;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.7rem;
    letter-spacing: 1px;
    cursor: pointer;
    text-align: left;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.menu-item::before {
    content: '';
    position: absolute;
    left: -100%;
    top: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, rgba(0, 246, 255, 0.1), 
                                        rgba(0, 246, 255, 0.2));
    transition: left 0.3s ease;
    z-index: -1;
}

.menu-item:hover::before {
    left: 0;
}

.menu-item:hover {
    color: #fff;
    text-shadow: 0 0 10px rgba(0, 246, 255, 0.6);
    padding-left: 20px;
}
```

### 6. Update Item (Green Color)

```css
.update-item {
    color: #00ff00;
    border-bottom-color: rgba(0, 255, 0, 0.1);
}

.update-item::before {
    background: linear-gradient(90deg, rgba(0, 255, 0, 0.1), 
                                        rgba(0, 255, 0, 0.2));
}

.update-item:hover {
    color: #fff;
    text-shadow: 0 0 10px rgba(0, 255, 0, 0.6);
}
```

### 7. Exit Button (Red Color)

```css
.exit-btn {
    border-color: #ff4444;
    color: #ff4444;
}

.exit-btn::before {
    background: rgba(255, 68, 68, 0.1);
}

.exit-btn:hover {
    box-shadow: 0 0 12px rgba(255, 68, 68, 0.6), 
                inset 0 0 8px rgba(255, 68, 68, 0.1);
    border-color: rgba(255, 68, 68, 0.95);
}
```

---

## JavaScript Implementation

### Menu Toggle Logic

```javascript
const menuToggleBtn = document.getElementById('menu-toggle-btn');
const actionMenu = document.getElementById('action-menu');

menuToggleBtn.addEventListener('click', () => {
    const isHidden = actionMenu.classList.contains('hidden');
    
    if (isHidden) {
        actionMenu.classList.remove('hidden');
        actionMenu.classList.add('visible');
        menuToggleBtn.classList.add('active');
        menuToggleBtn.style.animation = 'none';
    } else {
        actionMenu.classList.remove('visible');
        actionMenu.classList.add('hidden');
        menuToggleBtn.classList.remove('active');
        menuToggleBtn.style.animation = '';
    }
});
```

### Auto-Close on Outside Click

```javascript
document.addEventListener('click', (e) => {
    if (!e.target.closest('.menu-toggle-wrapper')) {
        actionMenu.classList.remove('visible');
        actionMenu.classList.add('hidden');
        menuToggleBtn.classList.remove('active');
        menuToggleBtn.style.animation = '';
    }
});
```

### Update Button Handler

```javascript
document.getElementById('update-btn').addEventListener('click', async () => {
    // Close the menu when update is clicked
    actionMenu.classList.remove('visible');
    actionMenu.classList.add('hidden');
    menuToggleBtn.classList.remove('active');
    
    const overlay = document.getElementById('update-overlay');
    const statusText = document.getElementById('update-status-text');
    const progressBar = document.getElementById('update-progress-bar');
    
    overlay.style.display = 'flex';
    statusText.textContent = 'Initiating system update sequence...';
    progressBar.style.width = '10%';

    const success = await ipcRenderer.invoke('perform-update');

    if (!success) {
        statusText.textContent = 'Update sequence failed. Resuming standard operations.';
        progressBar.style.width = '0%';
        setTimeout(() => { 
            overlay.style.display = 'none';
        }, 3000);
    }
});
```

### Keys Button Handler

```javascript
document.getElementById('keys-btn').addEventListener('click', () => {
    // Close the menu when keys is clicked
    actionMenu.classList.remove('visible');
    actionMenu.classList.add('hidden');
    menuToggleBtn.classList.remove('active');
    openSetupOverlay();
});
```

---

## HTML Structure

### Button Layout

```html
<div class="panel-header">
    SYSTEM STATUS
    <div style="position: absolute; top: 10px; right: 15px; display: flex; gap: 5px; align-items: center;">
        <!-- EXIT Button -->
        <button id="exit-btn" class="header-btn exit-btn">EXIT</button>
        
        <!-- MINI Button -->
        <button id="mini-toggle" class="header-btn mini-btn">MINI</button>
        
        <!-- MENU with Dropdown -->
        <div class="menu-toggle-wrapper">
            <button id="menu-toggle-btn" class="header-btn menu-toggle-btn">MENU</button>
            <div id="action-menu" class="action-menu hidden">
                <button id="update-btn" class="menu-item update-item">Update System</button>
                <button id="keys-btn" class="menu-item keys-item">Configure Keys</button>
            </div>
        </div>
    </div>
</div>
```

---

## Animation Timing

| Animation | Duration | Easing | Purpose |
|-----------|----------|--------|---------|
| menuButtonGlow | 2.0s | ease-in-out | Continuous pulse on MENU button |
| menuDropdown | 0.4s | cubic-bezier(0.34, 1.56, 0.64, 1) | Menu expansion with bounce |
| header-btn:hover | 0.3s | cubic-bezier(0.25, 0.46, 0.45, 0.94) | Button lift effect |
| menu-item:hover | 0.3s | ease | Text slide and glow |
| overlayFadeIn | 0.5s | ease-out | Update overlay appearance |
| menu-item::before | 0.3s | ease | Background fill animation |

---

## Color Reference

| Element | Color | Use |
|---------|-------|-----|
| MENU Button | #00ff00 | Green glow, indicates updates |
| EXIT Button | #ff4444 | Red, indicates danger |
| MINI Button | #00f6ff | Cyan, standard UI color |
| Base Text | #00f6ff | Cyan glow |
| Update Item | #00ff00 | Green text in menu |
| Keys Item | #00f6ff | Cyan text in menu |
| Background | rgba(0, 246, 255, 0.1) | Subtle background fill |
| Shadow | rgba(0, 246, 255, 0.3-0.7) | Glow effects |

