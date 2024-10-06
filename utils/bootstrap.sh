archive="./KMD-bootstrap.tar.gz"
dest_dir="$HOME/.komodo"
rm -rf "$dest_dir"/blocks
rm -rf "$dest_dir"/chainstate
rm -rf "$dest_dir"/notarisations
rm "$dest_dir"/komodoevents
rm "$dest_dir"/komodoevents.ind
rm "$dest_dir"/banlist.dat
rm "$dest_dir"/db.log
rm "$dest_dir"/debug.log
rm "$dest_dir"/komodostate
rm "$dest_dir"/signedmasks
tar -xzvf "$archive" -C "$dest_dir"