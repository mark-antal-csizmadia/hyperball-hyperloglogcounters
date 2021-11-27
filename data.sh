file_email=./data/email-Eu-core.txt.gz
file_wiki=./data/wiki-Vote.txt.gz

if [ -e "$file_email" ]; then
    echo "$file_email exists, skipping"
else 
    echo "$file_email does not exist, using wget to download it"
    wget http://snap.stanford.edu/data/email-Eu-core.txt.gz -P data/
    gzip -dkfv $file_email
fi

if [ -e "$file_wiki" ]; then
    echo "$file_wiki exists, skipping"
else 
    echo "$file_wiki does not exist, using wget to download it"
    wget http://snap.stanford.edu/data/wiki-Vote.txt.gz -P data/
    gzip -dkfv $file_wiki
fi
