#!/bin/sh -ex

sys_pkgs="ffmpeg ninja-build texlive graphviz"
pip_pkgs="matplotlib astropy astroquery lightkurve PyYAML"

pkgs() {
	# TODO figure out the brew/python situation
	if ! type brew >/dev/null 2>&1; then
		bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
	fi
	brew install $sys_pkgs
	pip install $pip_pkgs
}

git_hooks() {
	# TODO get root dir w/ git and use that
	cp lib/git.hooks.pre-commit .git/hooks/pre-commit
	chmod 0755 .git/hooks/pre-commit
}

if test $# -gt 0; then
	for arg; do "$arg"; done
else
	pkgs
	git_hooks
fi
