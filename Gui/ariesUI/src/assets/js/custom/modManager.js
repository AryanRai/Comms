const fs = require('fs');
const path = require('path');

const modManager = async () => {
  const modsDir = path.resolve(__dirname, '../ariesMods');
  const widgetList = [];

  try {
    // Check if directory exists before reading
    if (!fs.existsSync(modsDir)) {
      console.error(`Mods directory not found at: ${modsDir}`);
      return widgetList;
    }

    // Read all files/folders in the ariesMods directory
    const files = fs.readdirSync(modsDir);

    for (const file of files) {
      const modPath = path.join(modsDir, file);

      // Check if it's a directory and has a manifest.json
      if (fs.statSync(modPath).isDirectory() && fs.existsSync(path.join(modPath, 'manifest.json'))) {
        try {
          // Read the manifest
          const manifest = JSON.parse(fs.readFileSync(path.join(modPath, 'manifest.json')));
          
          // Check if manifest has widgets array
          if (Array.isArray(manifest.widgets)) {
            // Add each widget from the mod
            manifest.widgets.forEach(widget => {
              widgetList.push({
                name: widget.name,
                type: widget.type || 'widget',
                description: widget.description || '',
                component: widget.component || 'index.js',
                modName: manifest.name || file,
                modPath: modPath,
                cdn: manifest.cdn || widget.cdn || [],
                options: widget.options || {}
              });
            });
          } else {
            // Fallback for backwards compatibility - treat entire mod as single widget
            widgetList.push({
              name: manifest.name || file,
              type: manifest.type || 'widget',
              description: manifest.description || '',
              component: manifest.main || 'index.js',
              modName: manifest.name || file,
              modPath: modPath,
              cdn: manifest.cdn || [],
              options: manifest.options || {}
            });
          }
        } catch (error) {
          console.error(`Error loading mod ${file}:`, error);
        }
      }
    }
  } catch (error) {
    console.error('Error scanning mods directory:', error);
  }

  return widgetList;
};

export default modManager;
