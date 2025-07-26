# Miscrits: World of Creatures - Automation Bot

An intelligent automation bot for farming and battling in the Steam game "Miscrits: World of Creatures". This bot can automatically farm specific objects, engage in battles, capture target Miscrits, and handle post-battle training sequences.

## Features

### 🎯 **Auto-Farming**
- Automatically clicks on farming objects (seashells, rocks, trees, etc.)
- Respects 20-second cooldown timers
- Detects and collects reward drops (potions, gold)
- Handles "Okay" button popups

### ⚔️ **Battle Automation**
- Detects when battles start using OCR
- Reads enemy Miscrit names and capture percentages
- Implements intelligent capture logic (85%+ chance for target Miscrits)
- Uses hardcoded attack moves for non-target encounters
- Tracks encounter statistics persistently

### 🏆 **Post-Battle Training**
- Detects "ready to train" opportunities
- Executes platinum training sequences automatically
- Handles complex multi-step training workflows
- Manages training UI interactions

### 🔧 **Smart Detection**
- **OCR (Optical Character Recognition)** for dynamic text
- **Template Matching** for static UI elements
- **Fuzzy String Matching** for robust text comparison
- **Persistent State Management** across program runs

## Prerequisites

### System Requirements
- **Windows 10/11**
- **Python 3.8+**
- **Conda** (recommended for environment management)

### Required Software
1. **Tesseract OCR** - Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
2. **Python packages** (see requirements.txt)

## Installation

### 1. Create Conda Environment
```bash
conda create -n miscrits-bot python=3.8
conda activate miscrits-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR
1. Download Tesseract for Windows from the [official repository](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install to a directory (e.g., `C:\Program Files\Tesseract-OCR`)
3. Add to PATH environment variable
4. Verify installation: `tesseract --version`

### 4. Prepare Reference Images
Create the following directory structure:
```
project_root/
├── reference_images/
│   ├── reference_image.png          # Your farming object
│   ├── Capture button.png
│   ├── It's your turn!.png
│   ├── first move card.png
│   ├── Continue.png
│   ├── potion drop.png
│   ├── gold drop.png
│   └── okay.png
├── screenshots/                     # Auto-created for debugging
└── Insert_images/                   # Alternative location for reference
```

## Configuration

### User Settings (autofarm.py)
Edit the settings at the top of `autofarm.py`:

```python
# =====================
# USER CONFIGURABLE SETTINGS
# =====================
TARGET_MISCRIT_NAME = 'Light Crickin'    # Your target Miscrit
PLATINUM_TRAINING = True                  # Enable/disable training
FARM_COOLDOWN = 20                       # Seconds between farming clicks
BATTLE_CHECK_WINDOW = 7                  # Seconds to check for battle
REFERENCE_OBJECT_PATH = 'Insert_images/reference_image.png'
# =====================
```

### Key Settings Explained

| Setting | Description | Default |
|---------|-------------|---------|
| `TARGET_MISCRIT_NAME` | Name of the Miscrit you're farming for | 'Light Crickin' |
| `PLATINUM_TRAINING` | Enable automatic platinum training after battles | True |
| `FARM_COOLDOWN` | Seconds to wait between farming clicks | 20 |
| `BATTLE_CHECK_WINDOW` | Seconds to check for battle after farming | 7 |

## Usage

### Basic Usage
1. **Start the game** and navigate to your farming location
2. **Arrange windows** - Game and IDE side-by-side recommended
3. **Run the bot**:
   ```bash
   python autofarm.py
   ```

### Advanced Usage
- **Stop the bot**: Press `Ctrl+C` for clean exit
- **Monitor progress**: Check console output for detailed logs
- **Debug issues**: Review screenshots in `screenshots/` directory

## How It Works

### Farming Loop
1. **Screenshot** the game screen
2. **Find farming object** using template matching
3. **Click object** and wait for interaction
4. **Check for battle** for 7 seconds
5. **Collect drops** if no battle detected
6. **Wait for cooldown** (20 seconds)
7. **Repeat**

### Battle Sequence
1. **Detect battle start** using OCR ("It's your turn!")
2. **Read enemy name** and capture percentage
3. **Decide action**:
   - **Capture** if target Miscrit + 85%+ chance
   - **Attack** otherwise (first move)
4. **Handle battle end** and continue button
5. **Check for training** opportunity
6. **Execute training** if enabled and available

### Training Sequence
1. **Detect "ready to train"** after battle
2. **Click Continue** button
3. **Navigate training UI** with hardcoded coordinates
4. **Complete training** and return to farming

## File Structure

```
Miscrits Automation/
├── autofarm.py              # Main farming script
├── battle_engine.py         # Battle automation logic
├── utils.py                 # Shared utility functions
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── reference_images/       # UI element templates
│   ├── reference_image.png
│   ├── Capture button.png
│   ├── It's your turn!.png
│   ├── Continue.png
│   ├── potion drop.png
│   ├── gold drop.png
│   └── okay.png
├── screenshots/            # Debug screenshots
│   ├── turn_card_area_farm.png
│   ├── enemy_name_area.png
│   ├── capture_percentage_area.png
│   └── ready_to_train_area.png
├── target_encounters.txt   # Persistent encounter counter
└── current_target.txt      # Current target Miscrit name
```

## Troubleshooting

### Common Issues

#### **"Reference image not found"**
- Ensure your farming object image is in the correct path
- Check file name matches `REFERENCE_OBJECT_PATH`
- Verify image is clear and cropped properly

#### **"Battle engine script not found"**
- Ensure `battle_engine.py` exists in the same directory
- Check file permissions

#### **OCR not working**
- Verify Tesseract is installed and in PATH
- Test with: `tesseract --version`
- Check screenshot quality and text clarity

#### **Bot not clicking correctly**
- Ensure game window is visible and not minimized
- Check screen resolution matches reference images
- Verify mouse coordinates are correct for your setup

#### **Battle detection issues**
- Review `screenshots/turn_card_area_farm.png`
- Check OCR results in console output
- Adjust `TURN_CARD_X, TURN_CARD_Y, TURN_CARD_W, TURN_CARD_H` if needed

### Debug Mode
The bot automatically saves debug screenshots:
- **Farming**: `screenshots/turn_card_area_farm.png`
- **Battle**: `screenshots/enemy_name_area.png`
- **Training**: `screenshots/ready_to_train_area.png`

Review these images to diagnose detection issues.

## Technical Details

### Technologies Used
- **Python 3.8+** - Main programming language
- **PyAutoGUI** - Mouse and keyboard automation
- **OpenCV (cv2)** - Image processing and template matching
- **Pillow (PIL)** - Image manipulation
- **Tesseract OCR** - Text recognition from screenshots
- **Pytesseract** - Python wrapper for Tesseract
- **Difflib** - Fuzzy string matching for OCR results

### Key Algorithms
1. **Template Matching** - Find UI elements by comparing reference images
2. **OCR + Fuzzy Matching** - Read text with tolerance for errors
3. **Persistent State** - Track encounters across program runs
4. **Responsive Detection** - Quick battle detection during cooldowns

### Performance Notes
- **Screenshot frequency**: Every 1 second during battle checks
- **OCR processing**: ~100-200ms per text region
- **Template matching**: ~50-100ms per template
- **Memory usage**: Minimal, screenshots are processed and discarded

## Safety and Ethics

### Important Notes
- **Use at your own risk** - Automation may violate game terms of service
- **Fair play** - Don't use to gain unfair advantages over other players
- **Respect cooldowns** - The bot respects game mechanics and timers
- **Educational purpose** - This project demonstrates automation techniques

### Recommendations
- **Test thoroughly** before extended use
- **Monitor performance** and adjust settings as needed
- **Backup saves** before using automation tools
- **Use responsibly** and in accordance with game policies

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Add docstrings to new functions
- Include error handling
- Test with different game scenarios

## License

This project is for educational purposes. Use responsibly and in accordance with the game's terms of service.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review debug screenshots in `screenshots/`
3. Check console output for error messages
4. Verify all prerequisites are installed correctly

---

**Happy Farming! 🎮** 