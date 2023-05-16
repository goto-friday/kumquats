#!/bin/sh -e

sys_pkgs="ffmpeg ninja-build texlive graphviz"
pip_pkgs="matplotlib astropy astroquery lightkurve PyYAML"

pkgs() {
	apt install $sys_pkgs
	pip install $pip_pkgs
}

git_hooks() {
	cp lib/git.hooks.pre-commit .git/hooks/pre-commit
	chmod 0755 .git/hooks/pre-commit
}

if test $# -gt 0; then
	for arg; do $arg; done
else
	pkgs
	git_hooks
fi
