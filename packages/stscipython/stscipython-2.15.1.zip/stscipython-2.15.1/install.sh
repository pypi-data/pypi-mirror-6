args="$*"

# for now we want to ignore astropy because it is in a git repository and we
# don't currently have provisions for handling that

new_install/stp_list | python cfgdep.py -i -order | grep -v astropy | new_install/stp_install $args

