# Git repo template
This template contains useful `.gitignore` and `.gitattributes` file. Note that Git LFS should be installed before cloning this repository.

Note: the following command will remove .DS_Store files from a repo.

`find . -name .DS_Store -print0 | xargs -0 git rm -f --ignore-unmatch`
