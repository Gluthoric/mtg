#!/bin/bash
# List of commit hashes
commits=(
    f284e4e
    72fd074
    b98a3b6
    8dd728b
    8399f27
    b25546f
    6cc9442
    ebc952a
    a96bdf6
    e32b0b0
    87d14c1
)

# Loop over each commit and export its diff to a text file
for commit in "${commits[@]}"
do
    git show --color=never --pretty=medium --patch "$commit" > "${commit}.txt"
    echo "Exported commit $commit to ${commit}.txt"
done
