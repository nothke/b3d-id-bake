Single command id map baker for Blender. Bakes color of all selected object's materials to a single texture.

Blender 2.8's baking workflow overhaul has made baking id maps much more complicated as the setup is much longer. This is intended to simplify this process by providing a single command.

### Installation

Install like any other blender plugin: Edit > Preferences > Add-Ons > Install.. find bake_id_map.py. Then tick it to enable it.

### Usage

Select all objects you wish to bake, making sure you uv unwrap them and make sure the uvs don't overlap.

Search "Bake id map" in commands search bar and click on it.

And that's it! The texture will be created in the same folder as your blend file, with the name of ACTIVEOBJECTNAME_id.png.

You can additionally set a custom texture size, which will cause a rebake. 512 is default.

### What does the plugin actually do?
