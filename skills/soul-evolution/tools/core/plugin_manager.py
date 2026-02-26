import os
import json
import importlib.util
import sys

class PluginManager:
    def __init__(self, workspace, plugins_dir):
        self.workspace = workspace
        self.plugins_dir = plugins_dir
        self.plugins = {}
        self.load_plugins()

    def load_plugins(self):
        if not os.path.exists(self.plugins_dir):
            return

        for entry in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, entry)
            manifest_path = os.path.join(plugin_path, "manifest.json")
            
            if os.path.isdir(plugin_path) and os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r") as f:
                        manifest = json.load(f)
                    
                    plugin_id = entry
                    manifest["id"] = plugin_id
                    manifest["path"] = plugin_path
                    
                    # Try to load backend logic if defined
                    backend_file = manifest.get("backend_file", "backend.py")
                    backend_path = os.path.join(plugin_path, backend_file)
                    
                    handler_module = None
                    if os.path.exists(backend_path):
                        spec = importlib.util.spec_from_file_location(f"plugin_{plugin_id}", backend_path)
                        handler_module = importlib.util.module_from_spec(spec)
                        sys.modules[f"plugin_{plugin_id}"] = handler_module
                        spec.loader.exec_module(handler_module)
                    
                    self.plugins[plugin_id] = {
                        "manifest": manifest,
                        "handler": handler_module
                    }
                    print(f"  ✓ Plugin loaded: {manifest.get('name', plugin_id)} (v{manifest.get('version', '1.0.0')})")
                except Exception as e:
                    print(f"  ✗ Failed to load plugin {entry}: {e}")

    def get_manifests(self):
        return [p["manifest"] for p in self.plugins.values()]

    def handle_api(self, handler, method):
        # Route format: /api/plugins/[plugin_id]/[action]
        parts = handler.path.split('/')
        if len(parts) < 5 or parts[2] != "plugins":
            return False
            
        plugin_id = parts[3]
        action = "/".join(parts[4:])
        
        if plugin_id in self.plugins:
            plugin = self.plugins[plugin_id]
            if plugin["handler"] and hasattr(plugin["handler"], "handle_request"):
                try:
                    plugin["handler"].handle_request(handler, method, action, self.workspace)
                    return True
                except Exception as e:
                    print(f"  ⚠ Plugin {plugin_id} execution error: {e}")
                    return False
        return False
