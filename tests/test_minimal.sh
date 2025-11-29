SCRIPT_DIR=$(cd $(dirname $0) && pwd)
cd $SCRIPT_DIR

rm -rf blender-*

while IFS=: read -r major_ver range || [[ -n $major_ver ]]; do
    major_ver=${major_ver//$'\r'/}

    echo "Downloading Blender $major_ver..."
    blender_url="https://download.blender.org/release/Blender$major_ver/blender-$major_ver.0-linux-x64.tar.xz"
    ( wget -qO- "$blender_url" | tar -xJf - ) &
done < releases.txt
wait
echo "Finished."

while IFS=: read -r major_ver range || [[ -n $major_ver ]]; do
    major_ver=${major_ver//$'\r'/}

    echo "Preparing symbolic link to addon directory for Blender $major_ver"
    addon_dir="$HOME/.config/blender/$major_ver/scripts/addons"
    addon_path="$addon_dir/retromancer"
    mkdir -p $addon_dir
    rm -rf $addon_path
    ln -s $(pwd)/.. $addon_path

    cd blender-$major_ver.0-linux-x64/
    ./blender --background --factory-startup --python  ../unit_tests.py
    cd ..
done < releases.txt

rm -rf blender-*